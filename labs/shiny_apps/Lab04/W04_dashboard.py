"""
W04 Dashboard — De la Planilla al Modelo
TechStyle · Big Data y Analytics · Universidad San Sebastián

Dashboard interactivo que muestra el flujo completo del Lab W04:
  Tab 1 — Planilla Plana      : datos crudos + estadísticas generales
  Tab 2 — Auditoría           : anomalías de actualización, inserción y eliminación
  Tab 3 — Normalización       : las 4 tablas resultantes (1FN → 2FN → 3FN)
  Tab 4 — Diagrama MER        : diagrama entidad-relación con notación crow's foot
  Tab 5 — SQL                 : sentencias CREATE TABLE con restricciones
  Tab 6 — Comparación         : visualización antes/después

Uso:
    shiny run labs/shiny_apps/W04_dashboard.py
    # o desde la raíz del proyecto:
    python -m shiny run labs/shiny_apps/W04_dashboard.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
from shiny import App, render, ui

# ── Rutas ──────────────────────────────────────────────────────────────────────
CSV_PATH = Path(__file__).resolve().parent / "techstyle_ventas_planas.csv"

# ══════════════════════════════════════════════════════════════════════════════
# DATOS: cargar y normalizar al inicio (una sola vez)
# ══════════════════════════════════════════════════════════════════════════════

df_plano = pd.read_csv(CSV_PATH)


def _normalizar(df: pd.DataFrame):
    """Aplica 1FN → 2FN → 3FN y devuelve las 4 tablas normalizadas."""

    # Resolver anomalía de actualización: conservar el email más frecuente
    email_canonico = (
        df.groupby(["cliente_id", "cliente_email"])
        .size()
        .reset_index(name="n")
        .sort_values("n", ascending=False)
        .drop_duplicates(subset=["cliente_id"])
        .set_index("cliente_id")["cliente_email"]
    )

    # 3FN → CLIENTES
    clientes = (
        df[["cliente_id", "cliente_nombre", "cliente_apellido",
            "cliente_email", "cliente_region", "cliente_segmento"]]
        .drop_duplicates(subset=["cliente_id"])
        .rename(columns={
            "cliente_nombre":   "nombre",
            "cliente_apellido": "apellido",
            "cliente_email":    "email",
            "cliente_region":   "region",
            "cliente_segmento": "segmento",
        })
        .sort_values("cliente_id")
        .reset_index(drop=True)
    )
    clientes["email"] = clientes["cliente_id"].map(email_canonico)

    # 2FN → PRODUCTOS
    productos = (
        df[["producto_id", "producto_nombre", "categoria",
            "precio_unitario", "costo_unitario"]]
        .drop_duplicates(subset=["producto_id"])
        .rename(columns={
            "producto_nombre": "nombre_producto",
        })
        .sort_values("producto_id")
        .reset_index(drop=True)
    )

    # 3FN → VENTAS (sin datos del cliente repetidos)
    ventas = (
        df[["id_venta", "fecha_venta", "cliente_id"]]
        .drop_duplicates(subset=["id_venta"])
        .rename(columns={"id_venta": "venta_id", "fecha_venta": "fecha"})
        .sort_values("venta_id")
        .reset_index(drop=True)
    )

    # Tabla puente N:M → DETALLE_VENTAS
    detalle = (
        df[["id_venta", "producto_id", "cantidad", "descuento_pct"]]
        .rename(columns={"id_venta": "venta_id"})
        .sort_values(["venta_id", "producto_id"])
        .reset_index(drop=True)
    )

    return clientes, productos, ventas, detalle


clientes_df, productos_df, ventas_df, detalle_df = _normalizar(df_plano)

# ── SQL modelo completo ────────────────────────────────────────────────────────
SQL_MODELO = """\
-- ============================================================
-- MODELO RELACIONAL TECHSTYLE
-- Orden obligatorio: tablas sin FK primero
-- ============================================================

-- 1. CLIENTES (sin dependencias foráneas)
CREATE TABLE clientes (
    cliente_id      INT             PRIMARY KEY,
    nombre          VARCHAR(50)     NOT NULL,
    apellido        VARCHAR(50)     NOT NULL,
    email           VARCHAR(100)    UNIQUE NOT NULL,
    region          VARCHAR(50)     NOT NULL,
    segmento        VARCHAR(20)     CHECK (segmento IN ('Premium', 'Estándar', 'Básico'))
);

-- 2. PRODUCTOS (sin dependencias foráneas)
CREATE TABLE productos (
    producto_id      INT             PRIMARY KEY,
    nombre_producto  VARCHAR(100)    NOT NULL,
    categoria        VARCHAR(50)     NOT NULL,
    precio_unitario     DECIMAL(10,2)   NOT NULL CHECK (precio_unitario > 0),
    costo_unitario   DECIMAL(10,2)   NOT NULL CHECK (costo_unitario > 0)
);

-- 3. VENTAS (depende de CLIENTES)
CREATE TABLE ventas (
    venta_id    VARCHAR(10)  PRIMARY KEY,
    fecha       DATE         NOT NULL,
    cliente_id  INT          NOT NULL,
    FOREIGN KEY (cliente_id) REFERENCES clientes(cliente_id)
);

-- 4. DETALLE_VENTAS (depende de VENTAS y PRODUCTOS)
CREATE TABLE detalle_ventas (
    venta_id        VARCHAR(10)    NOT NULL,
    producto_id     INT            NOT NULL,
    cantidad        INT            NOT NULL CHECK (cantidad > 0),
    descuento_pct   DECIMAL(5,2)   NOT NULL DEFAULT 0
                    CHECK (descuento_pct >= 0 AND descuento_pct <= 100),
    PRIMARY KEY (venta_id, producto_id),
    FOREIGN KEY (venta_id)    REFERENCES ventas(venta_id),
    FOREIGN KEY (producto_id) REFERENCES productos(producto_id)
);
"""

# ══════════════════════════════════════════════════════════════════════════════
# UI
# ══════════════════════════════════════════════════════════════════════════════

_NAVBAR_CSS = ui.tags.style("""
    /* Nav links in top navbar: high-contrast white */
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
    # ── TAB 1: Planilla Plana ──────────────────────────────────────────────────
    ui.nav_panel(
        "Planilla Plana",
        ui.layout_column_wrap(
            ui.value_box(
                "Filas totales",
                str(len(df_plano)),
                theme="bg-gradient-blue-purple",
            ),
            ui.value_box(
                "Ventas únicas",
                str(df_plano["id_venta"].nunique()),
                theme="bg-gradient-blue-purple",
            ),
            ui.value_box(
                "Clientes únicos",
                str(df_plano["cliente_id"].nunique()),
                theme="bg-gradient-blue-purple",
            ),
            ui.value_box(
                "Productos únicos",
                str(df_plano["producto_id"].nunique()),
                theme="bg-gradient-blue-purple",
            ),
            width=1 / 4,
        ),
        ui.card(
            ui.card_header(
                ui.tags.b("techstyle_ventas_planas.csv"),
                " — toda la información en una sola tabla plana",
            ),
            ui.output_data_frame("tabla_plana"),
            full_screen=True,
        ),
    ),
    # ── TAB 2: Auditoría ──────────────────────────────────────────────────────
    ui.nav_panel(
        "Auditoria",
        ui.navset_tab(
            ui.nav_panel(
                "Anomalia de Actualizacion",
                ui.layout_column_wrap(
                    ui.card(
                        ui.card_header(
                            "Cliente C001 con dos emails distintos"
                        ),
                        ui.p(
                            ui.tags.b("Problema:"),
                            " Juan Perez (C001) aparece con ",
                            ui.tags.code("juan.perez@gmail.com"),
                            " en unas filas y ",
                            ui.tags.code("juanperez@gmail.com"),
                            " en otras. Si se actualiza el email en una fila, las demas quedan desactualizadas.",
                        ),
                        ui.output_data_frame("anomalia_actualizacion"),
                    ),
                    ui.card(
                        ui.card_header("Todos los clientes con datos inconsistentes"),
                        ui.output_data_frame("inconsistencias_tabla"),
                    ),
                    width=1 / 2,
                ),
            ),
            ui.nav_panel(
                "Anomalia de Insercion",
                ui.card(
                    ui.card_header(
                        "Por que no se puede insertar un producto sin venta"
                    ),
                    ui.p(
                        "Para registrar un nuevo producto (ej. 'Bolso Cuero') sin ventas, "
                        "habria que crear una fila con datos de venta inventados o vacios. "
                        "No hay forma de almacenar solo un producto en la tabla plana."
                    ),
                    ui.p(
                        ui.tags.b("Ejemplo de lo que ocurriria:"),
                        " columnas de venta quedarian con NULL o valores ficticios.",
                    ),
                    ui.output_data_frame("anomalia_insercion"),
                ),
            ),
            ui.nav_panel(
                "Anomalia de Eliminacion",
                ui.card(
                    ui.card_header(
                        "Clientes en riesgo: eliminar su unica venta borra todo su perfil"
                    ),
                    ui.p(
                        "Si se eliminan todas las ventas de un cliente, se pierde su nombre, "
                        "email, region y segmento — informacion que no deberia depender de las ventas."
                    ),
                    ui.output_data_frame("anomalia_eliminacion"),
                ),
            ),
            ui.nav_panel(
                "Redundancia y Formas Normales",
                ui.layout_column_wrap(
                    ui.card(
                        ui.card_header("Redundancia de productos en la tabla plana"),
                        ui.output_data_frame("redundancia_tabla"),
                    ),
                    ui.card(
                        ui.card_header("Diagnostico de Formas Normales"),
                        ui.output_data_frame("formas_normales"),
                    ),
                    width=1 / 2,
                ),
            ),
        ),
    ),
    # ── TAB 3: Normalización ──────────────────────────────────────────────────
    ui.nav_panel(
        "Normalizacion",
        ui.p(
            "Resultado de aplicar 1FN → 2FN → 3FN a la planilla plana. "
            "Una tabla con ",
            ui.tags.b(f"{len(df_plano)} filas y {df_plano.shape[1]} columnas"),
            " se convierte en 4 tablas limpias y sin redundancia.",
        ),
        ui.navset_tab(
            ui.nav_panel(
                "CLIENTES",
                ui.card(
                    ui.card_header(
                        f"Tabla CLIENTES — {len(clientes_df)} filas "
                        "(extraida aplicando 3FN: eliminar dependencia transitiva)"
                    ),
                    ui.output_data_frame("tabla_clientes"),
                ),
            ),
            ui.nav_panel(
                "PRODUCTOS",
                ui.card(
                    ui.card_header(
                        f"Tabla PRODUCTOS — {len(productos_df)} filas "
                        "(extraida aplicando 2FN: eliminar dependencia parcial)"
                    ),
                    ui.output_data_frame("tabla_productos"),
                ),
            ),
            ui.nav_panel(
                "VENTAS",
                ui.card(
                    ui.card_header(
                        f"Tabla VENTAS — {len(ventas_df)} filas "
                        "(sin datos de cliente repetidos)"
                    ),
                    ui.output_data_frame("tabla_ventas"),
                ),
            ),
            ui.nav_panel(
                "DETALLE_VENTAS",
                ui.card(
                    ui.card_header(
                        f"Tabla DETALLE_VENTAS — {len(detalle_df)} filas "
                        "(tabla puente que resuelve la relacion N:M entre VENTAS y PRODUCTOS)"
                    ),
                    ui.output_data_frame("tabla_detalle"),
                ),
            ),
        ),
    ),
    # ── TAB 4: Diagrama MER ───────────────────────────────────────────────────
    ui.nav_panel(
        "Diagrama MER",
        ui.card(
            ui.card_header("Diagrama Entidad-Relacion — Notacion Crow's Foot"),
            ui.output_plot("diagrama_mer", height="560px"),
            full_screen=True,
        ),
    ),
    # ── TAB 5: SQL ────────────────────────────────────────────────────────────
    ui.nav_panel(
        "SQL",
        ui.card(
            ui.card_header(
                "CREATE TABLE — Orden correcto: tablas sin FK primero"
            ),
            ui.output_ui("sql_code"),
        ),
        ui.card(
            ui.card_header("Integridad referencial — preguntas clave"),
            ui.output_data_frame("integridad_tabla"),
        ),
    ),
    # ── TAB 6: Comparación ────────────────────────────────────────────────────
    ui.nav_panel(
        "Comparacion",
        ui.layout_column_wrap(
            ui.card(
                ui.card_header("Antes vs Despues: reduccion de redundancia"),
                ui.output_data_frame("comparacion_tabla"),
            ),
            width=1,
        ),
        ui.card(
            ui.card_header("Visualizacion: planilla plana → modelo relacional"),
            ui.output_plot("comparacion_plot", height="580px"),
            full_screen=True,
        ),
    ),
    title="W04 · TechStyle: De la Planilla al Modelo",
    navbar_options=ui.navbar_options(bg="#1a1a2e"),
)

# ══════════════════════════════════════════════════════════════════════════════
# SERVER
# ══════════════════════════════════════════════════════════════════════════════

def server(input, output, session):

    # ── Tab 1: Planilla plana ──────────────────────────────────────────────────
    @render.data_frame
    def tabla_plana():
        return render.DataGrid(df_plano, height="460px")

    # ── Tab 2: Auditoría ───────────────────────────────────────────────────────
    @render.data_frame
    def anomalia_actualizacion():
        datos = df_plano[df_plano["cliente_id"] == "C001"][
            ["id_venta", "cliente_id", "cliente_nombre", "cliente_email"]
        ].drop_duplicates()
        return render.DataGrid(datos)

    @render.data_frame
    def inconsistencias_tabla():
        inc = (
            df_plano.groupby("cliente_id")[["cliente_email", "cliente_region"]]
            .nunique()
            .reset_index()
        )
        inc.columns = ["cliente_id", "emails_distintos", "regiones_distintas"]
        conflictos = inc[
            (inc["emails_distintos"] > 1) | (inc["regiones_distintas"] > 1)
        ].copy()
        conflictos["problema"] = "Anomalia de actualizacion detectada"
        return render.DataGrid(conflictos)

    @render.data_frame
    def anomalia_insercion():
        ejemplo = pd.DataFrame(
            {
                "id_venta": ["???"],
                "fecha_venta": ["???"],
                "cliente_id": ["???"],
                "producto_id": ["P_NUEVO"],
                "producto_nombre": ["Bolso Cuero (nuevo)"],
                "categoria": ["Accesorios"],
                "precio_unitario": [79990],
                "costo_unitario": [35000],
                "cantidad": ["NULL — sin ventas aun"],
                "descuento_pct": ["NULL"],
            }
        )
        return render.DataGrid(ejemplo)

    @render.data_frame
    def anomalia_eliminacion():
        ventas_por_cliente = (
            df_plano.groupby("cliente_id")["id_venta"]
            .nunique()
            .reset_index()
        )
        ventas_por_cliente.columns = ["cliente_id", "ventas_unicas"]
        info = df_plano[
            ["cliente_id", "cliente_nombre", "cliente_apellido",
             "cliente_region", "cliente_segmento"]
        ].drop_duplicates()
        resultado = ventas_por_cliente.merge(info, on="cliente_id")
        resultado["riesgo"] = resultado["ventas_unicas"].apply(
            lambda x: "ALTO — eliminar la unica venta borra el cliente" if x == 1
            else "Bajo"
        )
        return render.DataGrid(resultado.sort_values("ventas_unicas"))

    @render.data_frame
    def redundancia_tabla():
        red = (
            df_plano.groupby(["producto_id", "producto_nombre"])
            .size()
            .reset_index(name="apariciones_en_tabla_plana")
        )
        red["filas_a_modificar_si_cambia_precio"] = red["apariciones_en_tabla_plana"]
        return render.DataGrid(red)

    @render.data_frame
    def formas_normales():
        fn = pd.DataFrame(
            {
                "Forma Normal": ["1FN", "2FN", "3FN"],
                "Cumple": ["Si", "No", "No"],
                "Diagnostico": [
                    "Un valor por celda, sin grupos repetidos en columnas",
                    "Con clave (id_venta, producto_id): cliente_nombre depende solo de id_venta — dependencia parcial",
                    "cliente_email depende de cliente_id, no de id_venta — dependencia transitiva",
                ],
                "Solucion": [
                    "—",
                    "Extraer tabla PRODUCTOS (depende solo de producto_id)",
                    "Extraer tabla CLIENTES (depende solo de cliente_id)",
                ],
            }
        )
        return render.DataGrid(fn)

    # ── Tab 3: Normalización ───────────────────────────────────────────────────
    @render.data_frame
    def tabla_clientes():
        return render.DataGrid(clientes_df)

    @render.data_frame
    def tabla_productos():
        return render.DataGrid(productos_df)

    @render.data_frame
    def tabla_ventas():
        return render.DataGrid(ventas_df)

    @render.data_frame
    def tabla_detalle():
        return render.DataGrid(detalle_df)

    # ── Tab 4: Diagrama MER ────────────────────────────────────────────────────
    @render.plot
    def diagrama_mer():
        fig, ax = plt.subplots(figsize=(13, 8))
        fig.patch.set_facecolor("#f0f4f8")
        ax.set_facecolor("#f0f4f8")
        ax.set_xlim(0, 12)
        ax.set_ylim(0, 9)
        ax.axis("off")

        def draw_entity(x, y, title, attrs, header_color):
            """Dibuja una entidad con cabecera coloreada y lista de atributos."""
            row_h = 0.38
            body_h = len(attrs) * row_h + 0.15
            # Sombra
            ax.add_patch(plt.Rectangle(
                (x + 0.07, y - 0.07), 2.8, body_h + 0.55,
                facecolor="#cccccc", edgecolor="none", zorder=1,
            ))
            # Cabecera
            ax.add_patch(plt.Rectangle(
                (x, y + body_h), 2.8, 0.55,
                facecolor=header_color, edgecolor="#333333",
                linewidth=1.5, zorder=2,
            ))
            ax.text(
                x + 1.4, y + body_h + 0.275, title,
                ha="center", va="center", fontsize=10, fontweight="bold",
                color="white", zorder=3,
            )
            # Cuerpo
            ax.add_patch(plt.Rectangle(
                (x, y), 2.8, body_h,
                facecolor="white", edgecolor="#333333",
                linewidth=1.5, zorder=2,
            ))
            for i, (attr, is_pk, is_fk) in enumerate(attrs):
                yp = y + body_h - (i + 0.5) * row_h - 0.08
                if is_pk:
                    prefix, color_t, style = "PK ", "#c0392b", "bold"
                elif is_fk:
                    prefix, color_t, style = "FK ", "#2980b9", "normal"
                else:
                    prefix, color_t, style = "     ", "#2c3e50", "normal"
                ax.text(
                    x + 0.18, yp, prefix + attr,
                    fontsize=8, va="center", color=color_t,
                    fontweight=style, zorder=3,
                )
                if i < len(attrs) - 1:
                    ax.axhline(
                        y=yp - row_h / 2, xmin=(x) / 12, xmax=(x + 2.8) / 12,
                        color="#dddddd", linewidth=0.6, zorder=2,
                    )

        # ── Entidades ──────────────────────────────────────────────────────────
        #  CLIENTES (izquierda, arriba)
        draw_entity(0.3, 4.8, "CLIENTES", [
            ("cliente_id", True, False),
            ("nombre", False, False),
            ("apellido", False, False),
            ("email", False, False),
            ("region", False, False),
            ("segmento", False, False),
        ], "#27ae60")

        #  VENTAS (centro, arriba)
        draw_entity(4.3, 4.8, "VENTAS", [
            ("venta_id", True, False),
            ("fecha", False, False),
            ("cliente_id", False, True),
        ], "#2980b9")

        #  DETALLE_VENTAS (centro, abajo)
        draw_entity(4.3, 0.6, "DETALLE_VENTAS", [
            ("venta_id", True, True),
            ("producto_id", True, True),
            ("cantidad", False, False),
            ("descuento_pct", False, False),
        ], "#e67e22")

        #  PRODUCTOS (derecha, abajo)
        draw_entity(8.5, 0.6, "PRODUCTOS", [
            ("producto_id", True, False),
            ("nombre_producto", False, False),
            ("categoria", False, False),
            ("precio_unitario", False, False),
            ("costo_unitario", False, False),
        ], "#8e44ad")

        # ── Líneas de relación ─────────────────────────────────────────────────
        # CLIENTES —1— VENTAS
        ax.annotate("", xy=(4.3, 6.3), xytext=(3.1, 6.3),
                    arrowprops=dict(arrowstyle="-", color="#555555", lw=1.8),
                    zorder=4)
        ax.text(3.3, 6.5, "1", fontsize=10, fontweight="bold", color="#27ae60")
        ax.text(4.0, 6.5, "N", fontsize=10, fontweight="bold", color="#2980b9")
        ax.text(3.5, 6.1, "tiene", fontsize=7.5, color="#777777", style="italic")

        # VENTAS —1— DETALLE_VENTAS
        ax.annotate("", xy=(5.7, 2.5), xytext=(5.7, 4.8),
                    arrowprops=dict(arrowstyle="-", color="#555555", lw=1.8),
                    zorder=4)
        ax.text(5.85, 4.5, "1", fontsize=10, fontweight="bold", color="#2980b9")
        ax.text(5.85, 2.7, "N", fontsize=10, fontweight="bold", color="#e67e22")
        ax.text(5.95, 3.6, "incluye", fontsize=7.5, color="#777777",
                style="italic", rotation=90)

        # PRODUCTOS —1— DETALLE_VENTAS
        ax.annotate("", xy=(7.1, 1.8), xytext=(8.5, 1.8),
                    arrowprops=dict(arrowstyle="-", color="#555555", lw=1.8),
                    zorder=4)
        ax.text(8.6, 2.0, "1", fontsize=10, fontweight="bold", color="#8e44ad")
        ax.text(7.2, 2.0, "N", fontsize=10, fontweight="bold", color="#e67e22")
        ax.text(7.7, 1.5, "referencia", fontsize=7.5, color="#777777",
                style="italic")

        # ── Notación crow's foot (pequeños indicadores) ────────────────────────
        for (x1, y1, x2, y2) in [
            (3.1, 6.3, 3.35, 6.3),   # 1 lado CLIENTES
            (4.0, 6.3, 3.75, 6.3),   # N lado VENTAS
        ]:
            ax.plot([x1, x2], [y1, y2], color="#555555", lw=1.2, zorder=4)

        ax.set_title(
            "Diagrama Entidad-Relacion · TechStyle · 4 tablas en 3FN",
            fontsize=13, fontweight="bold", color="#1a1a2e", pad=12,
        )

        pk_patch = mpatches.Patch(color="#c0392b", label="PK — Clave Primaria")
        fk_patch = mpatches.Patch(color="#2980b9", label="FK — Clave Foranea")
        ax.legend(
            handles=[pk_patch, fk_patch],
            loc="lower right", fontsize=9,
            framealpha=0.9,
        )

        plt.tight_layout(pad=0.5)
        return fig

    # ── Tab 5: SQL ─────────────────────────────────────────────────────────────
    @render.ui
    def sql_code():
        return ui.tags.pre(
            SQL_MODELO,
            style=(
                "background:#1e1e2e; color:#cdd6f4; padding:1.2rem; "
                "border-radius:8px; font-size:0.82rem; line-height:1.5; "
                "overflow-x:auto; font-family:'Courier New', monospace;"
            ),
        )

    @render.data_frame
    def integridad_tabla():
        ir = pd.DataFrame(
            {
                "Pregunta": [
                    "Por que DETALLE_VENTAS se crea despues de VENTAS y PRODUCTOS?",
                    "Que pasa si insertas un venta_id inexistente en DETALLE_VENTAS?",
                    "Que pasa si eliminas un cliente con ventas en VENTAS?",
                ],
                "Respuesta": [
                    "Tiene FK que referencian esas tablas. MySQL no puede crear una FK hacia una tabla que no existe.",
                    "MySQL lanza ERROR 1452: Cannot add or update a child row — la insercion es rechazada.",
                    "MySQL rechaza con ERROR 1451: Cannot delete or update a parent row. Hay que eliminar sus ventas primero.",
                ],
            }
        )
        return render.DataGrid(ir)

    # ── Tab 6: Comparación ─────────────────────────────────────────────────────
    @render.data_frame
    def comparacion_tabla():
        comp = pd.DataFrame(
            {
                "Dimension": [
                    "Donde vive el email de un cliente",
                    "Como se actualiza el precio de un producto",
                    "Que pasa si eliminas todas las ventas de un cliente",
                    "Puede haber dos productos con el mismo codigo",
                ],
                "Planilla Excel plana": [
                    f"En cada fila de sus ventas — hasta {df_plano.groupby('cliente_id').size().max()} copias para el cliente mas activo",
                    "Hay que buscar y modificar TODAS las filas que contienen ese producto",
                    "Se pierde toda su informacion: nombre, email, region, segmento",
                    "Si — Excel no lo impide",
                ],
                "Modelo relacional 3FN": [
                    "En UNA SOLA fila de la tabla clientes",
                    "Se modifica UNA SOLA fila en productos; el historial de ventas no se altera",
                    "Nada — el cliente sigue en clientes. Solo se eliminan ventas y detalle_ventas",
                    "No — la PRIMARY KEY en productos garantiza unicidad. MySQL rechaza el duplicado",
                ],
            }
        )
        return render.DataGrid(comp)

    @render.plot
    def comparacion_plot():
        fig = plt.figure(figsize=(16, 9))
        fig.patch.set_facecolor("#f8f9fa")

        gs = fig.add_gridspec(
            2, 3,
            left=0.03, right=0.97,
            top=0.91, bottom=0.04,
            hspace=0.50, wspace=0.30,
        )
        ax_plana    = fig.add_subplot(gs[0, :])
        ax_clientes = fig.add_subplot(gs[1, 0])
        ax_productos = fig.add_subplot(gs[1, 1])
        ax_ventas   = fig.add_subplot(gs[1, 2])

        fig.suptitle(
            "W04 · TechStyle: De la Planilla Plana al Modelo Relacional",
            fontsize=13, fontweight="bold", color="#1a1a2e", y=0.97,
        )

        def _tabla_ax(ax, titulo, columnas, color_header):
            ax.set_facecolor("#ffffff")
            for spine in ax.spines.values():
                spine.set_edgecolor("#cccccc")
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_title(
                titulo, fontsize=8.5, fontweight="bold",
                color="white", pad=5,
                bbox=dict(boxstyle="round,pad=0.3", facecolor=color_header),
            )
            n = max(len(columnas), 1)
            for i, col in enumerate(columnas):
                y_pos = 1 - (i + 0.5) / n
                prefix = "PK " if "(PK)" in col or "(PK, FK)" in col else (
                    "FK " if "(FK)" in col else "    "
                )
                color_t = (
                    "#c0392b" if "PK" in col else
                    "#2980b9" if "FK" in col else
                    "#2c3e50"
                )
                ax.text(
                    0.06, y_pos, prefix + col,
                    transform=ax.transAxes,
                    fontsize=7.8, va="center", color=color_t,
                )
                ax.axhline(
                    y=1 - (i + 1) / n,
                    color="#eeeeee", linewidth=0.5,
                )

        _tabla_ax(
            ax_plana,
            f"PLANILLA PLANA  ({len(df_plano)} filas · {df_plano.shape[1]} columnas) — toda la informacion mezclada",
            list(df_plano.columns), "#c0392b",
        )
        _tabla_ax(
            ax_clientes,
            f"CLIENTES  ({len(clientes_df)} filas)",
            ["cliente_id (PK)", "nombre", "apellido", "email",
             "region", "segmento"],
            "#27ae60",
        )
        _tabla_ax(
            ax_productos,
            f"PRODUCTOS  ({len(productos_df)} filas)",
            ["producto_id (PK)", "nombre_producto", "categoria",
             "precio_unitario", "costo_unitario"],
            "#8e44ad",
        )
        _tabla_ax(
            ax_ventas,
            f"VENTAS ({len(ventas_df)} f.) + DETALLE_VENTAS ({len(detalle_df)} f.)",
            ["venta_id (PK)", "fecha", "cliente_id (FK)",
             "——————————————",
             "venta_id (PK, FK)", "producto_id (PK, FK)",
             "cantidad", "descuento_pct"],
            "#2980b9",
        )

        fig.text(
            0.50, 0.535, "NORMALIZACION\n1FN → 2FN → 3FN",
            ha="center", va="center", fontsize=9, color="#555555",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#ecf0f1",
                      edgecolor="#bdc3c7"),
        )
        fig.text(0.50, 0.49, "▼", ha="center", va="center",
                 fontsize=16, color="#e74c3c")

        return fig


# ══════════════════════════════════════════════════════════════════════════════
# PUNTO DE ENTRADA
# ══════════════════════════════════════════════════════════════════════════════

app = App(app_ui, server)
