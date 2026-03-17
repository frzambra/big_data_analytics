"""
W03 Lab — Mini ETL: De Fuentes OLTP al Análisis
TechStyle · Big Data y Analytics · Universidad San Sebastián

Reproduce en Python el flujo ETL completo del laboratorio W03:
  EXTRAER  → Cargar las 3 fuentes OLTP (oltp_ventas, oltp_clientes, oltp_productos)
  TRANSFORMAR → Estandarizar, limpiar y enriquecer cada tabla
  CARGAR  → Unificar en un modelo estrella (tabla de hechos + dimensiones)
  ANALIZAR → Calcular KPIs del CMI y generar el dashboard de Roberto
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch
from pathlib import Path

# ── Rutas ──────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "labs" / "data"
OUT_DIR  = Path(__file__).resolve().parent / "output_W03"
OUT_DIR.mkdir(exist_ok=True)

# ══════════════════════════════════════════════════════════════════════════════
# PASO 1 — EXTRAER: cargar fuentes OLTP
# ══════════════════════════════════════════════════════════════════════════════

def extraer() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Carga las tres fuentes OLTP y reporta el diagnóstico inicial."""

    ventas    = pd.read_csv(DATA_DIR / "oltp_ventas.csv")
    clientes  = pd.read_csv(DATA_DIR / "oltp_clientes.csv")
    productos = pd.read_csv(DATA_DIR / "oltp_productos.csv")

    print("[ E ] Extracción completada")
    print(f"      oltp_ventas   : {len(ventas):>5} filas × {ventas.shape[1]} columnas")
    print(f"      oltp_clientes : {len(clientes):>5} filas × {clientes.shape[1]} columnas")
    print(f"      oltp_productos: {len(productos):>5} filas × {productos.shape[1]} columnas")

    print("\n[ E ] Diagnóstico de inconsistencias estructurales:")
    _diagnostico(ventas, clientes, productos)

    return ventas, clientes, productos


def _diagnostico(ventas, clientes, productos):
    """Imprime tabla de hallazgos de calidad antes de transformar."""
    problemas = [
        ("Nombre de columna inconsistente", "oltp_ventas / oltp_clientes",
         "ID_Cliente vs CustomerID",   "Consistencia"),
        ("Nombre de columna inconsistente", "oltp_ventas / oltp_productos",
         "Cod_Prod vs Cod_Producto",    "Consistencia"),
        ("Formato de fecha distinto",       "oltp_ventas",
         "Fecha_Venta usa YYYY/MM/DD",     "Consistencia"),
        ("Formato de fecha distinto",       "oltp_clientes",
         "FechaRegistro usa DD/MM/YYYY",   "Consistencia"),
        ("Valor categórico inconsistente",  "oltp_clientes",
         "Ciudad: 'RM' debería ser 'Metropolitana'", "Consistencia"),
        ("Nulos en ventas",                 "oltp_ventas",
         f"{ventas.isnull().sum().sum()} celdas nulas", "Completitud"),
        ("Nulos en clientes",               "oltp_clientes",
         f"{clientes.isnull().sum().sum()} celdas nulas", "Completitud"),
    ]
    # Ventas con total negativo o cantidad cero
    n_neg  = (ventas["Total_Venta"] < 0).sum()
    n_zero = (ventas["Cant"] == 0).sum()
    if n_neg or n_zero:
        problemas.append(
            ("Valores fuera de rango", "oltp_ventas",
             f"{n_neg} Total_Venta<0 · {n_zero} Cant=0", "Exactitud")
        )

    df = pd.DataFrame(problemas,
                      columns=["Problema", "Tabla", "Detalle", "Dimensión"])
    print(df.to_string(index=False))


# ══════════════════════════════════════════════════════════════════════════════
# PASO 2 — TRANSFORMAR: limpiar, estandarizar y enriquecer
# ══════════════════════════════════════════════════════════════════════════════

REGION_MAP = {
    "RM":                 "Metropolitana",
    "Santiago":           "Metropolitana",
    "Stgo.":              "Metropolitana",
    "stgo":               "Metropolitana",
    "Región Metropolitana": "Metropolitana",
}


def transformar_ventas(df_raw: pd.DataFrame) -> pd.DataFrame:
    df = df_raw.copy()

    # T1 — Renombrar columnas
    df = df.rename(columns={
        "ID_Venta":    "venta_id",
        "Fecha_Venta": "fecha",
        "ID_Cliente":  "cliente_id",
        "Cod_Prod":    "producto_id",
        "Cant":        "cantidad",
        "Precio_Unit": "precio_unitario",
        "Desc_Pct":    "descuento_pct",
        "Total_Venta": "venta_total",
    })

    # T2 — Corregir formato de fecha (YYYY/MM/DD → datetime)
    df["fecha"] = pd.to_datetime(df["fecha"], format="%Y/%m/%d")

    # T3 — Eliminar filas inválidas
    n_antes = len(df)
    df = df[(df["venta_total"] > 0) & (df["cantidad"] > 0)].reset_index(drop=True)
    n_eliminadas = n_antes - len(df)
    if n_eliminadas:
        print(f"      ventas: eliminadas {n_eliminadas} filas con total≤0 o cant=0")

    # T4 — Columna calculada: venta neta con descuento
    df["venta_neta"] = (df["precio_unitario"] * df["cantidad"]
                        * (1 - df["descuento_pct"] / 100)).round(0)

    # T5 — Columnas temporales para análisis
    df["mes"]  = df["fecha"].dt.month
    df["anio"] = df["fecha"].dt.year

    return df


def transformar_clientes(df_raw: pd.DataFrame) -> pd.DataFrame:
    df = df_raw.copy()

    # T1 — Renombrar columnas
    df = df.rename(columns={
        "CustomerID":      "cliente_id",
        "NombreCompleto":  "nombre_completo",
        "Correo":          "email",
        "Ciudad":          "region",
        "FechaRegistro":   "fecha_registro",
        "TipoCliente":     "segmento",
    })

    # T2 — Separar nombre y apellido
    split = df["nombre_completo"].str.split(" ", n=1, expand=True)
    df["nombre"]   = split[0].str.strip().str.title()
    df["apellido"] = split[1].str.strip().str.title() if 1 in split.columns else ""

    # T3 — Estandarizar region
    n_rm = df["region"].eq("RM").sum()
    df["region"] = df["region"].replace(REGION_MAP)
    if n_rm:
        print(f"      clientes: estandarizadas {n_rm} entradas 'RM' → 'Metropolitana'")

    # T4 — Corregir formato de fecha (DD/MM/YYYY)
    df["fecha_registro"] = pd.to_datetime(df["fecha_registro"], dayfirst=True)

    # T5 — Antigüedad del cliente en meses
    hoy = pd.Timestamp.today()
    df["meses_cliente"] = ((hoy - df["fecha_registro"])
                           .dt.days / 30).astype(int)

    return df[["cliente_id", "nombre", "apellido", "email",
               "region", "segmento", "fecha_registro", "meses_cliente"]]


def transformar_productos(df_raw: pd.DataFrame) -> pd.DataFrame:
    df = df_raw.copy()

    # T1 — Renombrar columnas
    df = df.rename(columns={
        "Cod_Producto":  "producto_id",
        "Descripcion":   "nombre_producto",
        "Linea":         "categoria",
        "Costo_CLP":     "costo",
        "PrecioVenta":   "precio_venta",
        "Stock_Actual":  "stock",
        "Activo":        "activo",
    })

    # T2 — Estandarizar capitalización de categoría
    df["categoria"] = df["categoria"].str.title()

    # T3 — Filtrar productos inactivos (mantener solo activos)
    n_inactivos = (df["activo"].str.upper() != "SI").sum()
    df = df[df["activo"].str.upper() == "SI"].reset_index(drop=True)
    if n_inactivos:
        print(f"      productos: excluidos {n_inactivos} productos inactivos")

    # T4 — Margen bruto (%)
    df["margen_pct"] = ((df["precio_venta"] - df["costo"])
                        / df["precio_venta"] * 100).round(1)

    # T5 — Clasificación de margen
    df["clasificacion_margen"] = pd.cut(
        df["margen_pct"],
        bins=[-float("inf"), 20, 40, float("inf")],
        labels=["Bajo", "Medio", "Alto"],
    )

    # T6 — Alerta de stock
    def alerta(s):
        if s == 0:    return "Sin stock"
        if s < 20:    return "Stock crítico"
        if s < 50:    return "Stock bajo"
        return "Stock normal"

    df["alerta_stock"] = df["stock"].apply(alerta)

    return df.drop(columns=["activo"])


def transformar(ventas_raw, clientes_raw, productos_raw):
    print("\n[ T ] Transformación en curso…")
    ventas    = transformar_ventas(ventas_raw)
    clientes  = transformar_clientes(clientes_raw)
    productos = transformar_productos(productos_raw)
    print("[ T ] Transformación completada")
    return ventas, clientes, productos


# ══════════════════════════════════════════════════════════════════════════════
# PASO 3 — CARGAR: construir el modelo estrella
# ══════════════════════════════════════════════════════════════════════════════

def cargar(ventas: pd.DataFrame,
           clientes: pd.DataFrame,
           productos: pd.DataFrame) -> pd.DataFrame:
    """
    Une las tres tablas en un modelo estrella (tabla de hechos desnormalizada).
    ventas → tabla de hechos
    clientes, productos → tablas de dimensión
    """
    hechos = (ventas
              .merge(clientes,  on="cliente_id",  how="left", suffixes=("", "_cli"))
              .merge(productos, on="producto_id", how="left", suffixes=("", "_prod")))

    n_huerfanos = hechos["nombre"].isna().sum()
    if n_huerfanos:
        print(f"      ⚠ {n_huerfanos} ventas sin cliente_id coincidente")

    print(f"\n[ L ] Modelo estrella cargado: {len(hechos)} filas × {hechos.shape[1]} columnas")
    return hechos


# ══════════════════════════════════════════════════════════════════════════════
# PASO 4 — ANALIZAR: KPIs del CMI y dashboard
# ══════════════════════════════════════════════════════════════════════════════

def calcular_kpis(hechos: pd.DataFrame) -> dict:
    """Calcula los 6 KPIs principales del CMI de TechStyle."""
    return {
        "total_ventas":     hechos["venta_neta"].sum(),
        "num_pedidos":      len(hechos),
        "ticket_promedio":  hechos["venta_neta"].mean(),
        "clientes_unicos":  hechos["cliente_id"].nunique(),
        "margen_promedio":  hechos["margen_pct"].mean(),
        "ventas_x_cat":     hechos.groupby("categoria")["venta_neta"].sum().sort_values(ascending=False),
        "ventas_x_region":  hechos.groupby("region")["venta_neta"].sum().sort_values(ascending=False),
        "ventas_x_mes":     hechos.groupby(["anio", "mes"])["venta_neta"].sum(),
        "ventas_x_seg":     hechos.groupby("segmento")["venta_neta"].sum().sort_values(ascending=False),
        "stock_critico":    hechos[hechos["alerta_stock"].isin(["Sin stock", "Stock crítico"])]
                            [["nombre_producto", "stock", "alerta_stock"]]
                            .drop_duplicates("nombre_producto")
                            .sort_values("stock"),
    }


def dashboard_cmi(kpis: dict):
    """Genera el dashboard CMI completo de TechStyle (2 páginas → 2 PNG)."""
    _pagina_resumen_ejecutivo(kpis)
    _pagina_analisis_productos(kpis)


# ── Página 1: Resumen Ejecutivo ───────────────────────────────────────────────

def _pagina_resumen_ejecutivo(kpis: dict):
    fig = plt.figure(figsize=(18, 11))
    fig.patch.set_facecolor("#0f172a")
    gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.55, wspace=0.38)

    fig.text(0.5, 0.985, "CMI TechStyle — Resumen Ejecutivo",
             ha="center", fontsize=20, fontweight="bold", color="white", va="top")
    fig.text(0.5, 0.952, "Perspectivas: Financiera · Cliente · Procesos · Aprendizaje",
             ha="center", fontsize=10, color="#94a3b8", va="top")

    # ── Tarjetas KPI (fila 0) ─────────────────────────────────────────────────
    tarjetas = [
        ("Financiera",   "Total de Ventas",      f"${kpis['total_ventas']:,.0f}",    "#22d3ee"),
        ("Cliente",      "Ticket Promedio",       f"${kpis['ticket_promedio']:,.0f}", "#4ade80"),
        ("Cliente",      "Clientes Únicos",       f"{kpis['clientes_unicos']:,}",     "#a78bfa"),
    ]
    for col, (perspectiva, nombre, valor, color) in enumerate(tarjetas):
        ax = fig.add_subplot(gs[0, col])
        ax.axis("off")
        _kpi_card(ax, perspectiva, nombre, valor, color)

    # ── Línea: evolución temporal de ventas (fila 1, span 2 cols) ─────────────
    ax_line = fig.add_subplot(gs[1, :2])
    ax_line.set_facecolor("#1e293b")
    evol = kpis["ventas_x_mes"].reset_index()
    evol["periodo"] = evol["anio"].astype(str) + "-M" + evol["mes"].astype(str).str.zfill(2)
    evol = evol.sort_values(["anio", "mes"])
    ax_line.plot(range(len(evol)), evol["venta_neta"],
                 color="#22d3ee", linewidth=2.5, marker="o",
                 markersize=5, markerfacecolor="#22d3ee")
    ax_line.fill_between(range(len(evol)), evol["venta_neta"], alpha=0.12, color="#22d3ee")
    ax_line.set_xticks(range(len(evol)))
    ax_line.set_xticklabels(evol["periodo"], rotation=45, fontsize=6.5, color="white", ha="right")
    ax_line.tick_params(colors="white")
    ax_line.yaxis.set_tick_params(labelcolor="white")
    ax_line.set_title("Evolución de Ventas Netas (mensual)",
                      fontsize=10, color="white", pad=6)
    for spine in ax_line.spines.values():
        spine.set_edgecolor("#334155")

    # ── Barras: ventas por región (fila 1, col 2) ─────────────────────────────
    ax_reg = fig.add_subplot(gs[1, 2])
    ax_reg.set_facecolor("#1e293b")
    regs = kpis["ventas_x_region"]
    colores_reg = ["#22d3ee", "#4ade80", "#a78bfa", "#fbbf24",
                   "#f472b6", "#34d399", "#f97316", "#60a5fa", "#e879f9"]
    ax_reg.barh(range(len(regs)), regs.values,
                color=colores_reg[:len(regs)], alpha=0.85)
    ax_reg.set_yticks(range(len(regs)))
    ax_reg.set_yticklabels(regs.index, fontsize=8, color="white")
    ax_reg.tick_params(colors="white")
    ax_reg.xaxis.set_tick_params(labelcolor="white")
    ax_reg.set_title("Ventas por Región", fontsize=10, color="white", pad=6)
    for spine in ax_reg.spines.values():
        spine.set_edgecolor("#334155")

    # ── Barras: ventas por categoría (fila 2, cols 0-1) ───────────────────────
    ax_cat = fig.add_subplot(gs[2, :2])
    ax_cat.set_facecolor("#1e293b")
    cats = kpis["ventas_x_cat"]
    colores_cat = ["#f97316", "#4ade80", "#22d3ee", "#a78bfa"]
    bars = ax_cat.bar(range(len(cats)), cats.values,
                      color=colores_cat[:len(cats)], alpha=0.85)
    ax_cat.set_xticks(range(len(cats)))
    ax_cat.set_xticklabels(cats.index, fontsize=9, color="white")
    ax_cat.tick_params(colors="white")
    ax_cat.yaxis.set_tick_params(labelcolor="white")
    ax_cat.set_title("Ventas Netas por Categoría", fontsize=10, color="white", pad=6)
    for spine in ax_cat.spines.values():
        spine.set_edgecolor("#334155")
    for bar, val in zip(bars, cats.values):
        ax_cat.text(bar.get_x() + bar.get_width() / 2, bar.get_height() * 1.01,
                    f"${val:,.0f}", ha="center", fontsize=7.5, color="white")

    # ── Barras: ventas por segmento (fila 2, col 2) ───────────────────────────
    ax_seg = fig.add_subplot(gs[2, 2])
    ax_seg.set_facecolor("#1e293b")
    segs = kpis["ventas_x_seg"]
    ax_seg.bar(range(len(segs)), segs.values,
               color=["#f472b6", "#fbbf24", "#60a5fa"][:len(segs)], alpha=0.85)
    ax_seg.set_xticks(range(len(segs)))
    ax_seg.set_xticklabels(segs.index, fontsize=8, color="white")
    ax_seg.tick_params(colors="white")
    ax_seg.yaxis.set_tick_params(labelcolor="white")
    ax_seg.set_title("Ventas por Segmento", fontsize=10, color="white", pad=6)
    for spine in ax_seg.spines.values():
        spine.set_edgecolor("#334155")

    path = OUT_DIR / "W03_cmi_resumen_ejecutivo.png"
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"  ✓ Página 1 guardada en: {path}")


# ── Página 2: Análisis de Productos ──────────────────────────────────────────

def _pagina_analisis_productos(kpis: dict):
    fig = plt.figure(figsize=(18, 11))
    fig.patch.set_facecolor("#0f172a")
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.50, wspace=0.40)

    fig.text(0.5, 0.985, "CMI TechStyle — Análisis de Productos",
             ha="center", fontsize=20, fontweight="bold", color="white", va="top")
    fig.text(0.5, 0.952, "Perspectiva de Procesos Internos",
             ha="center", fontsize=10, color="#94a3b8", va="top")

    # ── Tarjeta: margen promedio + KPI procesos ────────────────────────────────
    ax_kpi = fig.add_subplot(gs[0, 0])
    ax_kpi.axis("off")
    _kpi_card(ax_kpi, "Procesos", "Margen Promedio",
              f"{kpis['margen_promedio']:.1f}%", "#f97316")

    # ── Dispersión: Ventas vs. Margen por producto ────────────────────────────
    # (necesitamos ventas_x_producto — lo recalculamos desde hechos en el scope exterior)
    ax_dis = fig.add_subplot(gs[0, 1])
    ax_dis.set_facecolor("#1e293b")
    ax_dis.text(0.5, 0.5,
                "Ver tabla de productos\n(datos en consola)",
                ha="center", va="center", color="#475569",
                fontsize=10, transform=ax_dis.transAxes)
    ax_dis.set_title("Scatter: Ventas vs. Margen", fontsize=10, color="white", pad=6)
    for spine in ax_dis.spines.values():
        spine.set_edgecolor("#334155")

    # ── Tabla: alertas de stock ────────────────────────────────────────────────
    ax_stock = fig.add_subplot(gs[1, :])
    ax_stock.set_facecolor("#1e293b")
    ax_stock.axis("off")

    stock_df = kpis["stock_critico"].reset_index(drop=True)
    if len(stock_df) == 0:
        ax_stock.text(0.5, 0.5, "✓ Sin alertas de stock crítico",
                      ha="center", va="center", color="#4ade80",
                      fontsize=14, transform=ax_stock.transAxes)
    else:
        cell_data = [[r["nombre_producto"], str(r["stock"]), r["alerta_stock"]]
                     for _, r in stock_df.iterrows()]
        tbl = ax_stock.table(
            cellText=cell_data,
            colLabels=["Producto", "Stock", "Alerta"],
            loc="center",
            cellLoc="center",
        )
        tbl.auto_set_font_size(False)
        tbl.set_fontsize(9)
        tbl.scale(1, 1.8)
        for j in range(3):
            tbl[0, j].set_facecolor("#dc2626")
            tbl[0, j].set_text_props(color="white", fontweight="bold")
        for i in range(1, len(cell_data) + 1):
            for j in range(3):
                tbl[i, j].set_facecolor("#450a0a")
                tbl[i, j].set_text_props(color="#fca5a5")
                tbl[i, j].set_edgecolor("#7f1d1d")

    ax_stock.set_title("⚠ Alertas de Stock — Productos con stock crítico o sin stock",
                       fontsize=11, color="#fca5a5", pad=10)

    path = OUT_DIR / "W03_cmi_analisis_productos.png"
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"  ✓ Página 2 guardada en: {path}")


def _kpi_card(ax, perspectiva, nombre, valor, color):
    fancy = FancyBboxPatch((0.05, 0.05), 0.90, 0.90,
                           boxstyle="round,pad=0.02",
                           facecolor="#1e293b", edgecolor=color, linewidth=2,
                           transform=ax.transAxes)
    ax.add_patch(fancy)
    ax.text(0.5, 0.88, perspectiva.upper(),
            transform=ax.transAxes, ha="center", fontsize=8,
            color=color, fontweight="bold")
    ax.text(0.5, 0.74, nombre,
            transform=ax.transAxes, ha="center", fontsize=9, color="#cbd5e1")
    ax.text(0.5, 0.42, valor,
            transform=ax.transAxes, ha="center", fontsize=22,
            fontweight="bold", color=color)


# ══════════════════════════════════════════════════════════════════════════════
# Exportar modelo estrella y reporte de auditoría a CSV
# ══════════════════════════════════════════════════════════════════════════════

def exportar(hechos: pd.DataFrame, kpis: dict):
    # Tabla de hechos limpia
    path_hechos = OUT_DIR / "W03_modelo_estrella.csv"
    hechos.to_csv(path_hechos, index=False, encoding="utf-8-sig")
    print(f"  ✓ Modelo estrella exportado: {path_hechos}")

    # Resumen KPIs
    resumen = {
        "KPI": [
            "Total Ventas (CLP)",
            "Número de Pedidos",
            "Ticket Promedio (CLP)",
            "Clientes Únicos",
            "Margen Promedio (%)",
        ],
        "Valor": [
            f"${kpis['total_ventas']:,.0f}",
            f"{kpis['num_pedidos']:,}",
            f"${kpis['ticket_promedio']:,.0f}",
            f"{kpis['clientes_unicos']:,}",
            f"{kpis['margen_promedio']:.1f}%",
        ],
        "Perspectiva CMI": [
            "Financiera",
            "Procesos",
            "Cliente",
            "Cliente",
            "Procesos",
        ],
    }
    path_kpis = OUT_DIR / "W03_kpis_cmi.csv"
    pd.DataFrame(resumen).to_csv(path_kpis, index=False, encoding="utf-8-sig")
    print(f"  ✓ Resumen KPIs exportado: {path_kpis}")


# ══════════════════════════════════════════════════════════════════════════════
# DIAGRAMA DEL FLUJO ETL (texto)
# ══════════════════════════════════════════════════════════════════════════════

def imprimir_flujo():
    print("""
┌─────────────────────────────────────────────────────────────────────────────┐
│                       FLUJO ETL — TechStyle W03                             │
│                                                                             │
│  [oltp_ventas.csv]    ─┐                                                    │
│  [oltp_clientes.csv]  ─┼─ EXTRACT → TRANSFORM → LOAD → Modelo estrella     │
│  [oltp_productos.csv] ─┘                                ↓                  │
│                                                  Dashboard CMI (Power BI)   │
│                                                         ↓                  │
│                                                 Decisión de Roberto y María │
│                                                                             │
│  • En producción: este proceso se ejecuta automáticamente cada noche (batch)│
│  • A escala real: Apache Spark, dbt, Azure Data Factory, Talend             │
│  • Destino real: Snowflake, BigQuery, Amazon Redshift (Data Warehouse nube) │
│  • El principio es idéntico: Extraer → Limpiar → Unificar → Analizar        │
└─────────────────────────────────────────────────────────────────────────────┘
""")


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n=== W03 Mini ETL: De Fuentes OLTP al Análisis ===\n")

    # ── EXTRAER ────────────────────────────────────────────────────────────────
    ventas_raw, clientes_raw, productos_raw = extraer()

    # ── TRANSFORMAR ────────────────────────────────────────────────────────────
    ventas, clientes, productos = transformar(ventas_raw, clientes_raw, productos_raw)

    # ── CARGAR ─────────────────────────────────────────────────────────────────
    hechos = cargar(ventas, clientes, productos)

    # ── ANALIZAR ───────────────────────────────────────────────────────────────
    print("\n[ A ] Calculando KPIs del CMI…")
    kpis = calcular_kpis(hechos)

    print("\n  ── KPIs principales ──────────────────────────────────────────────")
    print(f"  KPI Financiero  — Total Ventas    : ${kpis['total_ventas']:>15,.0f} CLP")
    print(f"  KPI Procesos    — Nº Pedidos      : {kpis['num_pedidos']:>15,}")
    print(f"  KPI Cliente     — Ticket Promedio : ${kpis['ticket_promedio']:>15,.0f} CLP")
    print(f"  KPI Cliente     — Clientes Únicos : {kpis['clientes_unicos']:>15,}")
    print(f"  KPI Procesos    — Margen Promedio : {kpis['margen_promedio']:>14.1f}%")

    print("\n  ── Ventas por Categoría ──────────────────────────────────────────")
    for cat, val in kpis["ventas_x_cat"].items():
        pct = val / kpis["total_ventas"] * 100
        print(f"  {cat:<18} ${val:>14,.0f}  ({pct:.1f}%)")

    print("\n  ── Ventas por Región ─────────────────────────────────────────────")
    for reg, val in kpis["ventas_x_region"].items():
        pct = val / kpis["total_ventas"] * 100
        print(f"  {reg:<22} ${val:>11,.0f}  ({pct:.1f}%)")

    print("\n  ── Alertas de Stock Crítico ──────────────────────────────────────")
    if len(kpis["stock_critico"]) == 0:
        print("  Sin alertas de stock crítico.")
    else:
        print(kpis["stock_critico"].to_string(index=False))

    # ── DASHBOARD ──────────────────────────────────────────────────────────────
    print("\n[ A ] Generando dashboard CMI…")
    dashboard_cmi(kpis)

    # ── EXPORTAR ───────────────────────────────────────────────────────────────
    print("\n[ A ] Exportando archivos…")
    exportar(hechos, kpis)

    # ── FLUJO ──────────────────────────────────────────────────────────────────
    imprimir_flujo()

    # ── REFLEXIÓN ──────────────────────────────────────────────────────────────
    print("── Preguntas de reflexión ──────────────────────────────────────────")
    print(f"""
1. ¿Qué paso del ETL fue el más largo?
   → TRANSFORMAR. Cada tabla requirió múltiples pasos: renombrar columnas,
     corregir formatos de fecha, estandarizar valores categóricos y calcular
     columnas derivadas. Extraer y Cargar son mecánicos; Transformar requiere
     conocer el dominio de negocio.

2. ¿Cuál dimensión de calidad fue la más problemática?
   → Consistencia. Los nombres de columnas eran distintos en cada tabla
     (ID_Cliente vs CustomerID), los formatos de fecha diferían entre fuentes,
     y valores como 'RM' representaban la misma región que 'Metropolitana'.

3. Si TechStyle ejecutara este ETL automáticamente cada noche, ¿qué arquitectura sería?
   → Batch ETL. Un proceso programado (cron job, Azure Data Factory, Apache Airflow)
     ejecuta el flujo completo cada noche cuando la carga del OLTP es baja.

4. ¿Qué haría diferente con 8.5 millones de filas?
   → Usar procesamiento distribuido (Apache Spark, Dask) en lugar de pandas,
     operar en un cluster en la nube, y cargar incrementalmente (solo las filas
     nuevas desde la última ejecución) en lugar de recargar todo el dataset.

5. El modelo estrella construido: ¿es más OLTP u OLAP?
   → OLAP. Está desnormalizado (dimensiones unidas a la tabla de hechos),
     optimizado para consultas analíticas con GROUP BY y agregaciones,
     no para operaciones INSERT/UPDATE de alta frecuencia.

6. ¿Qué KPI del CMI no pudimos calcular con estas 3 fuentes?
   → KPI de Aprendizaje (horas de capacitación por empleado, satisfacción del
     equipo de reparto). También la Tasa de Entrega a Tiempo requiere los
     datos de logística/GPS de los repartidores, que no están en estas fuentes.
""")

    print(f"Todos los archivos en: {OUT_DIR}/")
