"""
W03 Dashboard — Mini-ETL: De Fuentes OLTP al Análisis
TechStyle · Big Data y Analytics · Universidad San Sebastián

Dashboard interactivo que muestra el flujo completo del Lab W03:
  Tab 1 — Fuentes OLTP    : las 3 tablas crudas con sus problemas identificados
  Tab 2 — Auditoría       : diagnóstico de inconsistencias, calidad y llaves de unión
  Tab 3 — Transformar     : tablas limpias y enriquecidas (E → T → L)
  Tab 4 — Modelo Estrella : esquema estrella y medidas DAX
  Tab 5 — Análisis CMI    : visualizaciones del dashboard ejecutivo final

Uso:
    shiny run labs/shiny_apps/Lab03/W03_dashboard.py
    # o desde la raíz del proyecto:
    python -m shiny run labs/shiny_apps/Lab03/W03_dashboard.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np
from shiny import App, render, ui

# ── Rutas ──────────────────────────────────────────────────────────────────────
# Los CSV viven junto al script para que el deploy a shinyapps.io funcione sin
# depender de la estructura del repositorio en el servidor remoto.
DATA_DIR = Path(__file__).resolve().parent

# ══════════════════════════════════════════════════════════════════════════════
# DATOS: cargar fuentes crudas al inicio (una sola vez)
# ══════════════════════════════════════════════════════════════════════════════

df_ventas_raw   = pd.read_csv(DATA_DIR / "oltp_ventas.csv")
df_clientes_raw = pd.read_csv(DATA_DIR / "oltp_clientes.csv")
df_productos_raw = pd.read_csv(DATA_DIR / "oltp_productos.csv")


# ══════════════════════════════════════════════════════════════════════════════
# ETL: Transformaciones
# ══════════════════════════════════════════════════════════════════════════════

def _transformar_ventas(df: pd.DataFrame) -> pd.DataFrame:
    t = df.rename(columns={
        "ID_Venta":    "venta_id",
        "Fecha_Venta": "fecha",
        "ID_Cliente":  "cliente_id",
        "Cod_Prod":    "producto_id",
        "Cant":        "cantidad",
        "Precio_Unit": "precio_unitario",
        "Desc_Pct":    "descuento_pct",
        "Total_Venta": "venta_total",
    })
    t["fecha"] = pd.to_datetime(t["fecha"], format="%Y/%m/%d")
    t = t[t["venta_total"] > 0].copy()
    t = t[t["cantidad"] > 0].copy()
    t["venta_neta"] = (
        t["precio_unitario"] * t["cantidad"] * (1 - t["descuento_pct"] / 100)
    ).round(0).astype(int)
    t["mes"]  = t["fecha"].dt.strftime("%B")
    t["anio"] = t["fecha"].dt.year
    t["mes_num"] = t["fecha"].dt.month
    return t.reset_index(drop=True)


def _transformar_clientes(df: pd.DataFrame) -> pd.DataFrame:
    t = df.rename(columns={
        "CustomerID":    "cliente_id",
        "NombreCompleto": "_nombre_completo",
        "Correo":        "email",
        "Ciudad":        "region",
        "FechaRegistro": "fecha_registro",
        "TipoCliente":   "segmento",
    })
    # Separar nombre y apellido
    split = t["_nombre_completo"].str.split(" ", n=1, expand=True)
    t.insert(1, "nombre",   split[0])
    t.insert(2, "apellido", split[1].fillna(""))
    t = t.drop(columns=["_nombre_completo"])

    # Estandarizar región
    region_map = {
        "RM":                   "Metropolitana",
        "STGO.":                "Metropolitana",
        "SANTIAGO":             "Metropolitana",
        "REGION METROPOLITANA": "Metropolitana",
        "VINA DEL MAR":         "Valparaíso",
    }
    t["region"] = t["region"].replace(region_map)

    # Corregir fecha de registro
    t["fecha_registro"] = pd.to_datetime(t["fecha_registro"], dayfirst=True, errors="coerce")

    # Validar email
    t["email_valido"] = t["email"].str.contains("@") & t["email"].str.contains(r"\.")

    # Meses como cliente (desde fecha_registro hasta hoy)
    hoy = pd.Timestamp.now()
    t["meses_cliente"] = (
        ((hoy - t["fecha_registro"]).dt.days / 30).fillna(0).astype(int)
    )
    return t.reset_index(drop=True)


def _transformar_productos(df: pd.DataFrame) -> pd.DataFrame:
    t = df.rename(columns={
        "Cod_Producto": "producto_id",
        "Descripcion":  "nombre_producto",
        "Linea":        "categoria",
        "Costo_CLP":    "costo",
        "PrecioVenta":  "precio_venta",
        "Stock_Actual": "stock",
        "Activo":       "activo",
    })
    # Filtrar inactivos
    t = t[t["activo"].str.upper() == "SI"].copy()
    t = t.drop(columns=["activo"])

    # Estandarizar categoría
    t["categoria"] = t["categoria"].str.title()

    # Margen
    t["margen_pct"] = (
        (t["precio_venta"] - t["costo"]) / t["precio_venta"] * 100
    ).round(1)

    # Clasificación de margen
    def _clasif_margen(m):
        if m >= 40: return "Alto"
        if m >= 20: return "Medio"
        return "Bajo"
    t["clasificacion_margen"] = t["margen_pct"].apply(_clasif_margen)

    # Alerta de stock
    def _alerta_stock(s):
        if s == 0:   return "Sin stock"
        if s < 20:   return "Stock crítico"
        if s < 50:   return "Stock bajo"
        return "Stock normal"
    t["alerta_stock"] = t["stock"].apply(_alerta_stock)

    return t.reset_index(drop=True)


ventas_df   = _transformar_ventas(df_ventas_raw)
clientes_df = _transformar_clientes(df_clientes_raw)
productos_df = _transformar_productos(df_productos_raw)

# Tabla analítica integrada (join estrella)
analitico_df = (
    ventas_df
    .merge(clientes_df[["cliente_id", "nombre", "apellido", "region", "segmento"]],
           on="cliente_id", how="left")
    .merge(productos_df[["producto_id", "nombre_producto", "categoria",
                          "precio_venta", "costo", "margen_pct"]],
           on="producto_id", how="left")
)

# ── Medidas agregadas ──────────────────────────────────────────────────────────
total_ventas     = int(ventas_df["venta_neta"].sum())
num_pedidos      = len(ventas_df)
ticket_promedio  = int(total_ventas / num_pedidos) if num_pedidos else 0
clientes_unicos  = ventas_df["cliente_id"].nunique()
margen_promedio  = round(productos_df["margen_pct"].mean(), 1)

# ══════════════════════════════════════════════════════════════════════════════
# UI
# ══════════════════════════════════════════════════════════════════════════════

_NAVBAR_CSS = ui.tags.style("""
    .navbar-nav .nav-link {
        color: #ffffff !important;
        opacity: 1 !important;
    }
    .navbar-nav .nav-link:hover,
    .navbar-nav .nav-link:focus {
        color: #ffd700 !important;
    }
    .navbar-nav .nav-link.active {
        color: #ffd700 !important;
        font-weight: 700 !important;
    }
""")

app_ui = ui.page_navbar(
    ui.head_content(_NAVBAR_CSS),

    # ── TAB 1: Fuentes OLTP ───────────────────────────────────────────────────
    ui.nav_panel(
        "Fuentes OLTP",
        ui.layout_column_wrap(
            ui.value_box("Filas oltp_ventas",   str(len(df_ventas_raw)),   theme="bg-gradient-blue-purple"),
            ui.value_box("Filas oltp_clientes", str(len(df_clientes_raw)), theme="bg-gradient-blue-purple"),
            ui.value_box("Filas oltp_productos",str(len(df_productos_raw)),theme="bg-gradient-blue-purple"),
            ui.value_box("Tablas OLTP",         "3",                       theme="bg-gradient-blue-purple"),
            width=1/4,
        ),
        ui.navset_tab(
            ui.nav_panel(
                "oltp_ventas",
                ui.card(
                    ui.card_header(
                        ui.tags.b("oltp_ventas.csv"),
                        " — tabla de transacciones cruda",
                    ),
                    ui.p(
                        ui.tags.b("Problemas identificados: "),
                        "Columnas abreviadas (Cant, Cod_Prod), fecha en formato ",
                        ui.tags.code("YYYY/MM/DD"),
                        " (barras, no guiones), llave ",
                        ui.tags.code("ID_Cliente"),
                        " no coincide con la columna ",
                        ui.tags.code("CustomerID"),
                        " de oltp_clientes.",
                    ),
                    ui.output_data_frame("tabla_ventas_raw"),
                    full_screen=True,
                ),
            ),
            ui.nav_panel(
                "oltp_clientes",
                ui.card(
                    ui.card_header(
                        ui.tags.b("oltp_clientes.csv"),
                        " — tabla de clientes cruda",
                    ),
                    ui.p(
                        ui.tags.b("Problemas identificados: "),
                        "Nombre y apellido en un solo campo ",
                        ui.tags.code("NombreCompleto"),
                        ", columna de ciudad llamada ",
                        ui.tags.code("Ciudad"),
                        " (debería ser ",
                        ui.tags.code("region"),
                        "), fecha en formato ",
                        ui.tags.code("DD/MM/YYYY"),
                        " (chileno), llave ",
                        ui.tags.code("CustomerID"),
                        " con nombre distinto al de oltp_ventas.",
                    ),
                    ui.output_data_frame("tabla_clientes_raw"),
                    full_screen=True,
                ),
            ),
            ui.nav_panel(
                "oltp_productos",
                ui.card(
                    ui.card_header(
                        ui.tags.b("oltp_productos.csv"),
                        " — tabla de productos cruda",
                    ),
                    ui.p(
                        ui.tags.b("Problemas identificados: "),
                        "Categoría llamada ",
                        ui.tags.code("Linea"),
                        " (debería ser ",
                        ui.tags.code("categoria"),
                        "), columna de descripción llamada ",
                        ui.tags.code("Descripcion"),
                        " (debería ser ",
                        ui.tags.code("nombre_producto"),
                        "), llave ",
                        ui.tags.code("Cod_Producto"),
                        " con nombre distinto al ",
                        ui.tags.code("Cod_Prod"),
                        " de oltp_ventas.",
                    ),
                    ui.output_data_frame("tabla_productos_raw"),
                    full_screen=True,
                ),
            ),
        ),
    ),

    # ── TAB 2: Auditoría ──────────────────────────────────────────────────────
    ui.nav_panel(
        "Auditoria",
        ui.navset_tab(
            ui.nav_panel(
                "Inconsistencias",
                ui.card(
                    ui.card_header("Tabla de diagnóstico de inconsistencias entre fuentes"),
                    ui.output_data_frame("tabla_inconsistencias"),
                ),
            ),
            ui.nav_panel(
                "Calidad de Datos",
                ui.card(
                    ui.card_header(
                        "Auditoría de calidad — 4 dimensiones × 3 tablas"
                    ),
                    ui.output_data_frame("tabla_calidad"),
                ),
            ),
            ui.nav_panel(
                "Llaves de Union",
                ui.layout_column_wrap(
                    ui.card(
                        ui.card_header("Compatibilidad de llaves de unión"),
                        ui.output_data_frame("tabla_llaves"),
                    ),
                    ui.card(
                        ui.card_header("¿Por qué importa el nombre de la llave?"),
                        ui.p(
                            "Power BI (y cualquier motor SQL) une tablas por el ",
                            ui.tags.b("nombre de la columna"),
                            " al definir la relación, no por el valor. "
                            "Si las llaves tienen nombres distintos, la relación no se puede crear automáticamente "
                            "y puede pasar desapercibida, generando resultados incorrectos silenciosamente.",
                        ),
                        ui.p(
                            ui.tags.b("Ejemplo: "),
                            ui.tags.code("oltp_ventas[ID_Cliente]"),
                            " y ",
                            ui.tags.code("oltp_clientes[CustomerID]"),
                            " contienen los mismos valores numéricos, pero Power BI no los une automáticamente "
                            "por tener nombres distintos. Hay que renombrar uno de los dos antes de crear la relación.",
                        ),
                    ),
                    width=1/2,
                ),
            ),
            ui.nav_panel(
                "Formas Normales",
                ui.card(
                    ui.card_header("Resumen de renombres requeridos — 3 tablas"),
                    ui.output_data_frame("tabla_renombres"),
                ),
            ),
        ),
    ),

    # ── TAB 3: Transformar ────────────────────────────────────────────────────
    ui.nav_panel(
        "Transformar",
        ui.p(
            "Resultado de aplicar el paso ",
            ui.tags.b("T (Transform)"),
            " del pipeline ETL. Cada tabla fue renombrada, corregida y enriquecida con nuevas columnas calculadas.",
        ),
        ui.navset_tab(
            ui.nav_panel(
                "oltp_ventas limpia",
                ui.card(
                    ui.card_header(
                        f"oltp_ventas transformada — {len(ventas_df)} filas · "
                        "columnas renombradas, fecha corregida, venta_neta calculada"
                    ),
                    ui.output_data_frame("tabla_ventas_limpia"),
                    full_screen=True,
                ),
            ),
            ui.nav_panel(
                "oltp_clientes limpia",
                ui.card(
                    ui.card_header(
                        f"oltp_clientes transformada — {len(clientes_df)} filas · "
                        "nombre/apellido separados, región estandarizada, email validado"
                    ),
                    ui.output_data_frame("tabla_clientes_limpia"),
                    full_screen=True,
                ),
            ),
            ui.nav_panel(
                "oltp_productos limpia",
                ui.card(
                    ui.card_header(
                        f"oltp_productos transformada — {len(productos_df)} filas · "
                        "categoría estandarizada, margen_pct y alertas calculadas"
                    ),
                    ui.output_data_frame("tabla_productos_limpia"),
                    full_screen=True,
                ),
            ),
            ui.nav_panel(
                "Resumen de transformaciones",
                ui.layout_column_wrap(
                    ui.card(
                        ui.card_header("oltp_ventas — transformaciones aplicadas"),
                        ui.output_data_frame("resumen_ventas"),
                    ),
                    ui.card(
                        ui.card_header("oltp_clientes — transformaciones aplicadas"),
                        ui.output_data_frame("resumen_clientes"),
                    ),
                    ui.card(
                        ui.card_header("oltp_productos — transformaciones aplicadas"),
                        ui.output_data_frame("resumen_productos"),
                    ),
                    width=1/3,
                ),
            ),
        ),
    ),

    # ── TAB 4: Diagrama MER ───────────────────────────────────────────────────
    ui.nav_panel(
        "Diagrama MER",
        ui.layout_column_wrap(
            ui.card(
                ui.card_header("Diagrama Entidad-Relacion — Notacion Crow's Foot"),
                ui.output_plot("diagrama_mer", height="480px"),
                full_screen=True,
            ),
            ui.card(
                ui.card_header("Medidas DAX implementadas"),
                ui.output_data_frame("tabla_dax"),
                ui.hr(),
                ui.card_header("Relaciones del modelo — cardinalidad"),
                ui.output_data_frame("tabla_integridad"),
            ),
            width=1/2,
        ),
    ),

    # ── TAB 5: Análisis CMI ───────────────────────────────────────────────────
    ui.nav_panel(
        "Analisis CMI",
        ui.layout_column_wrap(
            ui.value_box(
                "Total Ventas",
                f"${total_ventas:,.0f}".replace(",", "."),
                theme="bg-gradient-green-teal",
            ),
            ui.value_box(
                "Num Pedidos",
                str(num_pedidos),
                theme="bg-gradient-green-teal",
            ),
            ui.value_box(
                "Ticket Promedio",
                f"${ticket_promedio:,.0f}".replace(",", "."),
                theme="bg-gradient-green-teal",
            ),
            ui.value_box(
                "Clientes Unicos",
                str(clientes_unicos),
                theme="bg-gradient-green-teal",
            ),
            ui.value_box(
                "Margen Promedio",
                f"{margen_promedio}%",
                theme="bg-gradient-green-teal",
            ),
            width=1/5,
        ),
        ui.navset_tab(
            ui.nav_panel(
                "Resumen Ejecutivo",
                ui.output_plot("plot_resumen", height="580px"),
            ),
            ui.nav_panel(
                "Analisis de Productos",
                ui.layout_column_wrap(
                    ui.card(
                        ui.card_header("Top 10 productos por venta neta"),
                        ui.output_data_frame("tabla_top_productos"),
                    ),
                    ui.card(
                        ui.card_header("Stock crítico"),
                        ui.output_data_frame("tabla_stock_critico"),
                    ),
                    width=1/2,
                ),
                ui.card(
                    ui.card_header("Ventas vs Margen por producto"),
                    ui.output_plot("plot_scatter", height="420px"),
                    full_screen=True,
                ),
            ),
            ui.nav_panel(
                "Reflexion",
                ui.card(
                    ui.card_header("Reflexión final — preguntas y respuestas esperadas"),
                    ui.output_data_frame("tabla_reflexion"),
                ),
            ),
        ),
    ),

    title="W03 · TechStyle: Mini-ETL — De Fuentes OLTP al Análisis",
    navbar_options=ui.navbar_options(bg="#1a1a2e"),
)


# ══════════════════════════════════════════════════════════════════════════════
# SERVER
# ══════════════════════════════════════════════════════════════════════════════

def server(input, output, session):

    # ── Tab 1: Fuentes crudas ─────────────────────────────────────────────────
    @render.data_frame
    def tabla_ventas_raw():
        return render.DataGrid(df_ventas_raw, height="460px")

    @render.data_frame
    def tabla_clientes_raw():
        return render.DataGrid(df_clientes_raw, height="460px")

    @render.data_frame
    def tabla_productos_raw():
        return render.DataGrid(df_productos_raw, height="460px")

    # ── Tab 2: Auditoría ───────────────────────────────────────────────────────
    @render.data_frame
    def tabla_inconsistencias():
        data = pd.DataFrame({
            "Problema detectado": [
                "Nombre de columna inconsistente",
                "Nombre de columna inconsistente",
                "Formato de fecha distinto",
                "Llave de unión con nombres distintos",
                "Llave de unión con nombres distintos",
                "Categoría con nombre inconsistente",
                "Columna de nombre compuesto",
                "Formato de fecha distinto",
            ],
            "Tabla afectada": [
                "oltp_ventas", "oltp_ventas", "oltp_ventas",
                "oltp_ventas / oltp_clientes",
                "oltp_ventas / oltp_productos",
                "oltp_productos", "oltp_clientes", "oltp_clientes",
            ],
            "Columna": [
                "Cant", "Cod_Prod", "Fecha_Venta",
                "ID_Cliente / CustomerID",
                "Cod_Prod / Cod_Producto",
                "Linea", "NombreCompleto", "FechaRegistro",
            ],
            "Detalle del problema": [
                "Abreviación — debe renombrarse a cantidad",
                "Debe renombrarse a producto_id para coincidir con oltp_productos",
                "Formato YYYY/MM/DD (barras), distinto al estándar ISO",
                "Mismo valor, distinto nombre. Hay que renombrar una",
                "Distinto nombre para la misma llave de unión",
                "Nombre diferente al estándar — debe renombrarse a categoria",
                "Nombre y apellido juntos — debe separarse en nombre y apellido",
                "Formato DD/MM/YYYY — distinto al de oltp_ventas",
            ],
        })
        return render.DataGrid(data)

    @render.data_frame
    def tabla_calidad():
        data = pd.DataFrame({
            "Dimension": ["Exactitud", "Completitud", "Consistencia", "Oportunidad"],
            "oltp_ventas": [
                "Precios y montos positivos; sin valores negativos detectados",
                "~100% de campos con valor; revisar si hay Total_Venta con nulos",
                "Formato de fecha YYYY/MM/DD inconsistente con ISO; columnas abreviadas",
                "Datos de 2023; verificar si reflejan el período de análisis requerido",
            ],
            "oltp_clientes": [
                "Emails con formato válido; nombres con capitalización variada",
                "Algunos campos pueden tener nulos; revisar Correo",
                "Ciudad en vez de region; NombreCompleto en vez de campos separados",
                "Fecha de registro en formato chileno (DD/MM/YYYY)",
            ],
            "oltp_productos": [
                "Precios y costos positivos; márgenes calculables y razonables",
                "Activo presente en todas las filas; sin nulos obvios",
                "Linea en vez de categoria; capitalización puede variar entre filas",
                "Sin columna de fecha de actualización de precios — oportunidad no verificable",
            ],
        })
        return render.DataGrid(data)

    @render.data_frame
    def tabla_llaves():
        data = pd.DataFrame({
            "Relacion": [
                "Ventas → Clientes",
                "Ventas → Productos",
            ],
            "Columna en oltp_ventas": ["ID_Cliente", "Cod_Prod"],
            "Columna en dimension":   ["CustomerID", "Cod_Producto"],
            "Compatible": [
                "No — mismo valor, distinto nombre. Hay que renombrar una",
                "No — mismo valor, distinto nombre. Hay que renombrar una",
            ],
        })
        return render.DataGrid(data)

    @render.data_frame
    def tabla_renombres():
        data = pd.DataFrame({
            "Tabla": [
                "oltp_ventas", "oltp_ventas", "oltp_ventas", "oltp_ventas",
                "oltp_ventas", "oltp_ventas", "oltp_ventas", "oltp_ventas",
                "oltp_clientes", "oltp_clientes", "oltp_clientes",
                "oltp_clientes", "oltp_clientes", "oltp_clientes",
                "oltp_productos", "oltp_productos", "oltp_productos",
                "oltp_productos", "oltp_productos", "oltp_productos", "oltp_productos",
            ],
            "Nombre original": [
                "ID_Venta", "Fecha_Venta", "ID_Cliente", "Cod_Prod",
                "Cant", "Precio_Unit", "Desc_Pct", "Total_Venta",
                "CustomerID", "NombreCompleto", "Correo",
                "Ciudad", "FechaRegistro", "TipoCliente",
                "Cod_Producto", "Descripcion", "Linea",
                "Costo_CLP", "PrecioVenta", "Stock_Actual", "Activo",
            ],
            "Nombre estandarizado": [
                "venta_id", "fecha", "cliente_id", "producto_id",
                "cantidad", "precio_unitario", "descuento_pct", "venta_total",
                "cliente_id", "nombre + apellido", "email",
                "region", "fecha_registro", "segmento",
                "producto_id", "nombre_producto", "categoria",
                "costo", "precio_venta", "stock", "activo",
            ],
        })
        return render.DataGrid(data)

    # ── Tab 3: Tablas transformadas ────────────────────────────────────────────
    @render.data_frame
    def tabla_ventas_limpia():
        return render.DataGrid(ventas_df.drop(columns=["mes_num"]), height="460px")

    @render.data_frame
    def tabla_clientes_limpia():
        return render.DataGrid(clientes_df, height="460px")

    @render.data_frame
    def tabla_productos_limpia():
        return render.DataGrid(productos_df, height="460px")

    @render.data_frame
    def resumen_ventas():
        data = pd.DataFrame({
            "Transformacion": [
                "Renombrar 8 columnas",
                "Corregir tipo de fecha",
                "Filtrar valores invalidos",
                "Columna calculada venta_neta",
                "Columna mes (nombre)",
                "Columna anio (numero)",
            ],
            "Descripcion": [
                "Estandarizar a minusculas y snake_case",
                "Fecha_Venta de texto YYYY/MM/DD a tipo Fecha",
                "Filtrar venta_total > 0 y cantidad > 0",
                "precio_unitario * cantidad * (1 - descuento_pct / 100)",
                "Nombre del mes para análisis temporal",
                "Año numérico para segmentación",
            ],
        })
        return render.DataGrid(data)

    @render.data_frame
    def resumen_clientes():
        data = pd.DataFrame({
            "Transformacion": [
                "Renombrar 6 columnas",
                "Separar NombreCompleto",
                "Estandarizar region",
                "Corregir fecha_registro",
                "Columna email_valido",
                "Columna meses_cliente",
            ],
            "Descripcion": [
                "CustomerID → cliente_id, Correo → email, etc.",
                "Dividir por primer espacio → nombre y apellido",
                "RM → Metropolitana (y otras variantes)",
                "DD/MM/YYYY → tipo Fecha",
                "Verifica que el email contenga @ y punto",
                "Días desde fecha_registro / 30 → entero",
            ],
        })
        return render.DataGrid(data)

    @render.data_frame
    def resumen_productos():
        data = pd.DataFrame({
            "Transformacion": [
                "Renombrar 7 columnas",
                "Estandarizar categoria",
                "Filtrar productos inactivos",
                "Columna margen_pct",
                "Columna clasificacion_margen",
                "Columna alerta_stock",
            ],
            "Descripcion": [
                "Cod_Producto → producto_id, Linea → categoria, etc.",
                "Title case: Electrónica, Ropa, Hogar, Accesorios",
                "Conservar solo activo = SI",
                "(precio_venta - costo) / precio_venta * 100",
                ">=40% → Alto | >=20% → Medio | else → Bajo",
                "0 → Sin stock | <20 → Stock critico | <50 → Stock bajo | else → Normal",
            ],
        })
        return render.DataGrid(data)

    # ── Tab 4: Diagrama MER ────────────────────────────────────────────────────
    @render.plot
    def diagrama_mer():
        fig, ax = plt.subplots(figsize=(13, 8))
        fig.patch.set_facecolor("#f0f4f8")
        ax.set_facecolor("#f0f4f8")
        ax.set_xlim(0, 13)
        ax.set_ylim(0, 9)
        ax.axis("off")

        def draw_entity(x, y, title, attrs, header_color, w=2.8):
            """Dibuja una entidad y devuelve (x_left, x_right, y_top, y_mid, y_bot)."""
            row_h = 0.37
            body_h = len(attrs) * row_h + 0.13
            # Sombra
            ax.add_patch(plt.Rectangle(
                (x + 0.07, y - 0.07), w, body_h + 0.53,
                facecolor="#cccccc", edgecolor="none", zorder=1,
            ))
            # Cabecera
            ax.add_patch(plt.Rectangle(
                (x, y + body_h), w, 0.53,
                facecolor=header_color, edgecolor="#333333",
                linewidth=1.5, zorder=2,
            ))
            ax.text(
                x + w / 2, y + body_h + 0.265, title,
                ha="center", va="center", fontsize=9.5, fontweight="bold",
                color="white", zorder=3,
            )
            # Cuerpo
            ax.add_patch(plt.Rectangle(
                (x, y), w, body_h,
                facecolor="white", edgecolor="#333333",
                linewidth=1.5, zorder=2,
            ))
            for i, (attr, is_pk, is_fk) in enumerate(attrs):
                yp = y + body_h - (i + 0.5) * row_h - 0.06
                if is_pk:
                    prefix, color_t, style = "PK ", "#c0392b", "bold"
                elif is_fk:
                    prefix, color_t, style = "FK ", "#2980b9", "normal"
                else:
                    prefix, color_t, style = "    ", "#2c3e50", "normal"
                ax.text(x + 0.18, yp, prefix + attr,
                        fontsize=7.8, va="center", color=color_t,
                        fontweight=style, zorder=3)
                if i < len(attrs) - 1:
                    ax.axhline(
                        y=yp - row_h / 2,
                        xmin=x / 13, xmax=(x + w) / 13,
                        color="#dddddd", linewidth=0.5, zorder=2,
                    )
            total_h = body_h + 0.53
            return x, x + w, y + total_h, y + total_h / 2, y

        def crow_foot_one(x, y, direction="right"):
            """Dibuja la marca '1' (barra simple) de crow's foot."""
            dx = 0.0 if direction in ("up", "down") else 0.18
            dy = 0.18 if direction in ("up", "down") else 0.0
            ax.plot([x - dx, x + dx] if direction in ("left", "right") else [x, x],
                    [y, y] if direction in ("left", "right") else [y - dy, y + dy],
                    color="#555555", lw=2.0, zorder=5)

        def crow_foot_many(x, y, direction="right"):
            """Dibuja la marca 'N' (tres líneas en abanico) de crow's foot."""
            if direction == "right":
                for dy in (-0.15, 0.0, 0.15):
                    ax.plot([x - 0.18, x], [y + dy, y], color="#555555", lw=1.5, zorder=5)
            elif direction == "left":
                for dy in (-0.15, 0.0, 0.15):
                    ax.plot([x + 0.18, x], [y + dy, y], color="#555555", lw=1.5, zorder=5)
            elif direction == "down":
                for dx in (-0.15, 0.0, 0.15):
                    ax.plot([x + dx, x], [y + 0.18, y], color="#555555", lw=1.5, zorder=5)
            elif direction == "up":
                for dx in (-0.15, 0.0, 0.15):
                    ax.plot([x + dx, x], [y - 0.18, y], color="#555555", lw=1.5, zorder=5)

        # ── Posiciones ────────────────────────────────────────────────────────
        # Layout:
        #   CLIENTES (izq, arriba)   VENTAS (centro, arriba)   PRODUCTOS (der, abajo)
        #                            DETALLE_VENTAS (centro, abajo)

        # CLIENTES — izquierda, arriba
        cl = draw_entity(0.2, 4.6, "CLIENTES", [
            ("cliente_id",     True,  False),
            ("nombre",         False, False),
            ("apellido",       False, False),
            ("email",          False, False),
            ("region",         False, False),
            ("segmento",       False, False),
            ("fecha_registro", False, False),
        ], "#27ae60")
        # cl: (x_left, x_right, y_top, y_mid, y_bot)

        # VENTAS — centro, arriba
        vt = draw_entity(4.3, 5.2, "VENTAS", [
            ("venta_id",   True,  False),
            ("fecha",      False, False),
            ("cliente_id", False, True),
        ], "#2980b9")

        # DETALLE_VENTAS — centro, abajo  (entidad de conexión)
        dv = draw_entity(4.3, 0.9, "DETALLE_VENTAS", [
            ("venta_id",        True,  True),
            ("producto_id",     True,  True),
            ("cantidad",        False, False),
            ("precio_unitario", False, False),
            ("descuento_pct",   False, False),
            ("venta_neta",      False, False),
        ], "#e67e22")

        # PRODUCTOS — derecha, abajo
        pr = draw_entity(9.5, 0.9, "PRODUCTOS", [
            ("producto_id",     True,  False),
            ("nombre_producto", False, False),
            ("categoria",       False, False),
            ("precio_venta",    False, False),
            ("costo",           False, False),
            ("margen_pct",      False, False),
            ("alerta_stock",    False, False),
        ], "#8e44ad")

        # ── Relación 1: CLIENTES (1) ——— (N) VENTAS ───────────────────────────
        y_h = vt[2] - 0.3   # altura de la línea horizontal (cerca de la parte superior de VENTAS)
        x_cl_right = cl[1]
        x_vt_left  = vt[0]
        ax.plot([x_cl_right, x_vt_left], [y_h, y_h],
                color="#555555", lw=1.8, zorder=4)
        crow_foot_one(x_cl_right, y_h, direction="left")
        crow_foot_many(x_vt_left, y_h, direction="left")
        ax.text((x_cl_right + x_vt_left) / 2, y_h + 0.18,
                "realiza", fontsize=7.5, ha="center", color="#777777", style="italic")
        ax.text(x_cl_right - 0.25, y_h + 0.18, "1", fontsize=10,
                fontweight="bold", color="#27ae60")
        ax.text(x_vt_left  + 0.10, y_h + 0.18, "N", fontsize=10,
                fontweight="bold", color="#2980b9")

        # ── Relación 2: VENTAS (1) ——— (N) DETALLE_VENTAS ─────────────────────
        x_vt_cx  = (vt[0] + vt[1]) / 2
        x_dv_cx  = (dv[0] + dv[1]) / 2
        y_vt_bot = vt[4]
        y_dv_top = dv[2]
        ax.plot([x_vt_cx, x_dv_cx], [y_vt_bot, y_dv_top],
                color="#555555", lw=1.8, zorder=4)
        crow_foot_one(x_vt_cx, y_vt_bot, direction="down")
        crow_foot_many(x_dv_cx, y_dv_top, direction="up")
        ax.text(x_vt_cx + 0.22, (y_vt_bot + y_dv_top) / 2,
                "incluye", fontsize=7.5, color="#777777", style="italic", rotation=90)
        ax.text(x_vt_cx + 0.22, y_vt_bot - 0.35, "1", fontsize=10,
                fontweight="bold", color="#2980b9")
        ax.text(x_dv_cx + 0.22, y_dv_top + 0.10, "N", fontsize=10,
                fontweight="bold", color="#e67e22")

        # ── Relación 3: PRODUCTOS (1) ——— (N) DETALLE_VENTAS ──────────────────
        x_pr_left = pr[0]
        x_dv_right = dv[1]
        y_h2 = (dv[2] + dv[4]) / 2  # mitad vertical de DETALLE_VENTAS
        ax.plot([x_dv_right, x_pr_left], [y_h2, y_h2],
                color="#555555", lw=1.8, zorder=4)
        crow_foot_many(x_dv_right, y_h2, direction="right")
        crow_foot_one(x_pr_left, y_h2, direction="right")
        ax.text((x_dv_right + x_pr_left) / 2, y_h2 + 0.18,
                "referenciado en", fontsize=7.5, ha="center", color="#777777", style="italic")
        ax.text(x_dv_right + 0.10, y_h2 + 0.18, "N", fontsize=10,
                fontweight="bold", color="#e67e22")
        ax.text(x_pr_left  - 0.30, y_h2 + 0.18, "1", fontsize=10,
                fontweight="bold", color="#8e44ad")

        ax.set_title(
            "Diagrama Entidad-Relacion · TechStyle · ETL W03  "
            "(DETALLE_VENTAS resuelve la relacion N:M)",
            fontsize=12, fontweight="bold", color="#1a1a2e", pad=12,
        )

        pk_patch  = mpatches.Patch(color="#c0392b", label="PK — Clave Primaria")
        fk_patch  = mpatches.Patch(color="#2980b9", label="FK — Clave Foranea")
        con_patch = mpatches.Patch(color="#e67e22", label="DETALLE_VENTAS — entidad de conexion N:M")
        ax.legend(handles=[pk_patch, fk_patch, con_patch],
                  loc="lower right", fontsize=8.5, framealpha=0.9)

        plt.tight_layout(pad=0.5)
        return fig

    @render.data_frame
    def tabla_dax():
        data = pd.DataFrame({
            "Medida DAX": [
                "Total Ventas",
                "Num Pedidos",
                "Ticket Promedio",
                "Clientes Unicos",
                "Ventas Mes Actual",
                "Margen Promedio",
            ],
            "Formula": [
                "SUM(oltp_ventas[venta_neta])",
                "COUNTROWS(oltp_ventas)",
                "DIVIDE([Total Ventas], [Num Pedidos], 0)",
                "DISTINCTCOUNT(oltp_ventas[cliente_id])",
                "CALCULATE([Total Ventas], MONTH(oltp_ventas[fecha])=MONTH(TODAY()), YEAR(...)=YEAR(TODAY()))",
                "AVERAGE(oltp_productos[margen_pct])",
            ],
            f"Valor con datos actuales": [
                f"${total_ventas:,.0f}".replace(",", "."),
                str(num_pedidos),
                f"${ticket_promedio:,.0f}".replace(",", "."),
                str(clientes_unicos),
                "0 (datos 2023, hoy es 2026)",
                f"{margen_promedio}%",
            ],
        })
        return render.DataGrid(data)

    @render.data_frame
    def tabla_integridad():
        data = pd.DataFrame({
            "Relacion": [
                "CLIENTES — VENTAS",
                "VENTAS — DETALLE_VENTAS",
                "PRODUCTOS — DETALLE_VENTAS",
            ],
            "Cardinalidad": [
                "1:N — un cliente realiza muchas ventas",
                "1:N — una venta tiene muchas lineas de detalle",
                "1:N — un producto puede aparecer en muchas lineas de detalle",
            ],
            "Llave de union": ["cliente_id", "venta_id", "producto_id"],
            "Nota": [
                "FK cliente_id en VENTAS referencia PK de CLIENTES",
                "FK venta_id en DETALLE_VENTAS referencia PK de VENTAS",
                "FK producto_id en DETALLE_VENTAS referencia PK de PRODUCTOS — "
                "DETALLE_VENTAS es la entidad de conexion que resuelve el N:M entre VENTAS y PRODUCTOS",
            ],
        })
        return render.DataGrid(data)

    # ── Tab 5: Análisis CMI ────────────────────────────────────────────────────
    @render.plot
    def plot_resumen():
        fig = plt.figure(figsize=(16, 9))
        fig.patch.set_facecolor("#f8f9fa")
        gs = fig.add_gridspec(2, 2, left=0.07, right=0.97,
                              top=0.90, bottom=0.07,
                              hspace=0.45, wspace=0.35)

        ax_linea  = fig.add_subplot(gs[0, :])
        ax_cat    = fig.add_subplot(gs[1, 0])
        ax_region = fig.add_subplot(gs[1, 1])

        fig.suptitle("W03 · TechStyle — Dashboard Ejecutivo CMI",
                     fontsize=13, fontweight="bold", color="#1a1a2e", y=0.96)

        # ── Ventas mensuales ──────────────────────────────────────────────────
        mensual = (
            analitico_df.groupby(["anio", "mes_num", "mes"])["venta_neta"]
            .sum()
            .reset_index()
            .sort_values(["anio", "mes_num"])
        )
        etiquetas = mensual["mes"].str[:3] + " " + mensual["anio"].astype(str).str[-2:]
        ax_linea.plot(range(len(mensual)), mensual["venta_neta"],
                      color="#2980b9", linewidth=2.2, marker="o", markersize=5)
        ax_linea.fill_between(range(len(mensual)), mensual["venta_neta"],
                               alpha=0.15, color="#2980b9")
        ax_linea.set_xticks(range(len(mensual)))
        ax_linea.set_xticklabels(etiquetas, fontsize=7, rotation=45, ha="right")
        ax_linea.set_title("Evolucion mensual de ventas netas (CLP)",
                           fontsize=9, fontweight="bold")
        ax_linea.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda x, _: f"${x/1_000_000:.1f}M"))
        ax_linea.set_facecolor("#ffffff")
        ax_linea.grid(axis="y", color="#eeeeee", linewidth=0.6)

        # ── Ventas por categoría ───────────────────────────────────────────────
        por_cat = (
            analitico_df.groupby("categoria")["venta_neta"]
            .sum()
            .sort_values(ascending=False)
        )
        colores_cat = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12"]
        ax_cat.bar(por_cat.index, por_cat.values / 1e6,
                   color=colores_cat[:len(por_cat)], edgecolor="white")
        ax_cat.set_title("Ventas netas por categoría (M CLP)",
                         fontsize=9, fontweight="bold")
        ax_cat.set_facecolor("#ffffff")
        ax_cat.grid(axis="y", color="#eeeeee", linewidth=0.6)
        ax_cat.tick_params(axis="x", labelsize=8)
        for bar, val in zip(ax_cat.patches, por_cat.values):
            ax_cat.text(bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + 0.05,
                        f"${val/1e6:.1f}M", ha="center", fontsize=7.5)

        # ── Ventas por región ──────────────────────────────────────────────────
        por_region = (
            analitico_df.groupby("region")["venta_neta"]
            .sum()
            .sort_values()
        )
        ax_region.barh(por_region.index, por_region.values / 1e6,
                       color="#8e44ad", edgecolor="white")
        ax_region.set_title("Ventas netas por region (M CLP)",
                            fontsize=9, fontweight="bold")
        ax_region.set_facecolor("#ffffff")
        ax_region.grid(axis="x", color="#eeeeee", linewidth=0.6)
        ax_region.tick_params(axis="y", labelsize=7.5)
        for bar, val in zip(ax_region.patches, por_region.values):
            ax_region.text(bar.get_width() + 0.02,
                           bar.get_y() + bar.get_height() / 2,
                           f"${val/1e6:.1f}M", va="center", fontsize=7)

        return fig

    @render.data_frame
    def tabla_top_productos():
        top = (
            analitico_df.groupby(["producto_id", "nombre_producto", "categoria"])
            .agg(
                total_ventas=("venta_neta", "sum"),
                num_pedidos=("venta_id", "count"),
            )
            .reset_index()
            .merge(
                productos_df[["producto_id", "margen_pct", "clasificacion_margen"]],
                on="producto_id", how="left"
            )
            .sort_values("total_ventas", ascending=False)
            .head(10)
        )
        top["total_ventas"] = top["total_ventas"].apply(
            lambda x: f"${x:,.0f}".replace(",", "."))
        return render.DataGrid(top.drop(columns=["producto_id"]))

    @render.data_frame
    def tabla_stock_critico():
        critico = productos_df[
            productos_df["alerta_stock"].isin(["Sin stock", "Stock crítico"])
        ][["nombre_producto", "stock", "alerta_stock"]].sort_values("stock")
        return render.DataGrid(critico)

    @render.plot
    def plot_scatter():
        fig, ax = plt.subplots(figsize=(12, 5))
        fig.patch.set_facecolor("#f8f9fa")
        ax.set_facecolor("#ffffff")

        por_prod = (
            analitico_df.groupby("producto_id")["venta_neta"]
            .sum()
            .reset_index()
            .merge(productos_df[["producto_id", "nombre_producto", "categoria",
                                  "margen_pct", "clasificacion_margen"]],
                   on="producto_id")
        )

        color_map = {"Electrónica": "#e74c3c", "Ropa": "#3498db",
                     "Hogar": "#2ecc71", "Accesorios": "#f39c12"}
        for cat, grp in por_prod.groupby("categoria"):
            ax.scatter(grp["margen_pct"], grp["venta_neta"] / 1e3,
                       label=cat, color=color_map.get(cat, "#95a5a6"),
                       s=80, alpha=0.8, edgecolors="white", linewidth=0.5)

        ax.set_xlabel("Margen % del producto", fontsize=9)
        ax.set_ylabel("Venta neta total (miles CLP)", fontsize=9)
        ax.set_title("Dispersion: Ventas totales vs Margen por producto",
                     fontsize=10, fontweight="bold")
        ax.legend(title="Categoria", fontsize=8)
        ax.grid(color="#eeeeee", linewidth=0.6)
        plt.tight_layout()
        return fig

    @render.data_frame
    def tabla_reflexion():
        data = pd.DataFrame({
            "Pregunta": [
                "¿Qué paso del ETL fue más largo?",
                "¿Dimensión de calidad más problemática?",
                "Si se ejecutara cada noche, ¿qué arquitectura sería?",
                "¿Qué cambiaría con 8,5 millones de filas?",
                "¿El modelo estrella es OLTP u OLAP?",
                "¿Qué KPI no pudiste calcular?",
            ],
            "Respuesta esperada": [
                "Transform — la estandarización de columnas, fechas y regiones requiere más pasos que la extracción o la carga",
                "Consistencia — nombres de columna distintos, formatos de fecha distintos, variantes de región",
                "ETL batch nocturno (batch pipeline). En empresas: Azure Data Factory, dbt, Apache Airflow",
                "Power Query no escalaría. Se necesitaría Spark, Databricks, BigQuery o Snowflake",
                "OLAP — optimizado para consultas analíticas agregadas, no para transacciones individuales",
                "Aprendizaje/Crecimiento del CMI — no hay datos sobre capacitación ni nuevos clientes registrados",
            ],
        })
        return render.DataGrid(data)


# ══════════════════════════════════════════════════════════════════════════════
# PUNTO DE ENTRADA
# ══════════════════════════════════════════════════════════════════════════════

app = App(app_ui, server)
