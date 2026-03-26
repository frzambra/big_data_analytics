"""
W04 Lab — De la Planilla al Modelo
TechStyle · Big Data y Analytics · Universidad San Sebastián

Reproduce en Python el flujo de normalización del laboratorio W04:
  PASO 1 — Auditar la planilla plana (anomalías, formas normales, redundancia)
  PASO 2 — Normalizar a 1FN → 2FN → 3FN → 4 tablas relacionales
  PASO 3 — Exportar las 4 tablas normalizadas como CSV
  PASO 4 — Generar sentencias CREATE TABLE en SQL
  PASO 5 — Visualizar el antes y después
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

# ── Rutas ──────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "labs" / "data"
OUT_DIR  = Path(__file__).resolve().parent / "output_W04"
OUT_DIR.mkdir(exist_ok=True)

# ══════════════════════════════════════════════════════════════════════════════
# PASO 1 — AUDITAR: cargar la planilla plana y detectar problemas
# ══════════════════════════════════════════════════════════════════════════════

def auditar(df: pd.DataFrame) -> None:
    """Imprime diagnóstico completo de la planilla plana."""

    print("=" * 70)
    print("PASO 1 — AUDITAR LA PLANILLA PLANA")
    print("=" * 70)
    print(f"\n  Filas totales    : {len(df)}")
    print(f"  Columnas totales : {df.shape[1]}")
    print(f"  Ventas únicas    : {df['id_venta'].nunique()}")
    print(f"  Clientes únicos  : {df['cliente_id'].nunique()}")
    print(f"  Productos únicos : {df['producto_id'].nunique()}")

    # ── Anomalía de actualización ──────────────────────────────────────────────
    print("\n[ ! ] Anomalía de ACTUALIZACIÓN")
    print("      Un mismo cliente_id aparece con datos distintos en distintas filas.")
    inconsistencias = (
        df.groupby("cliente_id")[["cliente_email", "cliente_region"]]
        .nunique()
    )
    clientes_con_conflicto = inconsistencias[
        (inconsistencias["cliente_email"] > 1) |
        (inconsistencias["cliente_region"] > 1)
    ]
    if clientes_con_conflicto.empty:
        print("      No se detectaron conflictos de email/región por cliente_id.")
    else:
        print(f"      Clientes con datos inconsistentes: {list(clientes_con_conflicto.index)}")
        for cid in clientes_con_conflicto.index:
            filas = df[df["cliente_id"] == cid][
                ["id_venta", "cliente_email", "cliente_region"]
            ].drop_duplicates()
            print(filas.to_string(index=False))

    # ── Anomalía de inserción ──────────────────────────────────────────────────
    print("\n[ ! ] Anomalía de INSERCIÓN")
    print("      Para registrar un cliente nuevo sin ventas se necesitaría")
    print("      rellenar columnas de venta con valores NULL o ficticios.")
    print("      → En una tabla plana no hay forma de almacenar solo un cliente.")

    # ── Anomalía de eliminación ────────────────────────────────────────────────
    print("\n[ ! ] Anomalía de ELIMINACIÓN")
    cliente_unica_venta = (
        df.groupby("cliente_id")["id_venta"].nunique()
    )
    clientes_una_venta = cliente_unica_venta[cliente_unica_venta == 1].index.tolist()
    print(f"      Clientes con solo 1 venta: {clientes_una_venta}")
    print("      Si se elimina esa venta, se pierde toda la información del cliente.")

    # ── Redundancia ───────────────────────────────────────────────────────────
    print("\n[ ! ] REDUNDANCIA")
    for prod_id, grp in df.groupby("producto_id"):
        nombre = grp["producto_nombre"].iloc[0]
        veces  = len(grp)
        print(f"      {prod_id} '{nombre}' aparece {veces} veces en la tabla.")

    cliente_mas_compras = df.groupby("cliente_id").size().idxmax()
    n_filas_cliente = (df["cliente_id"] == cliente_mas_compras).sum()
    print(f"\n      El cliente más activo ({cliente_mas_compras}) aparece en {n_filas_cliente} filas.")
    print(f"      Cambiar su email requeriría actualizar {n_filas_cliente} filas.")

    # ── Formas normales ────────────────────────────────────────────────────────
    print("\n[ ! ] DIAGNÓSTICO DE FORMAS NORMALES")
    print("      1FN : ✓ Un valor por celda, sin grupos repetidos.")
    print("      2FN : ✗ Con clave compuesta (id_venta, producto_id),")
    print("              cliente_nombre depende solo de id_venta (dependencia parcial).")
    print("              precio_unitario_base depende solo de producto_id.")
    print("      3FN : ✗ En la tabla de ventas, cliente_email, cliente_region y")
    print("              cliente_segmento dependen de cliente_id, no de id_venta")
    print("              (dependencia transitiva).")


# ══════════════════════════════════════════════════════════════════════════════
# PASO 2 — NORMALIZAR: de la planilla plana a 4 tablas
# ══════════════════════════════════════════════════════════════════════════════

def normalizar(df: pd.DataFrame) -> tuple[
    pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame
]:
    """Aplica 1FN → 2FN → 3FN y devuelve las 4 tablas normalizadas."""

    print("\n" + "=" * 70)
    print("PASO 2 — NORMALIZAR: 1FN → 2FN → 3FN")
    print("=" * 70)

    # ── 2FN: extraer tabla CLIENTES ───────────────────────────────────────────
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
    # Conservar el email más frecuente por cliente (resuelve anomalía de actualización)
    email_canonico = (
        df.groupby(["cliente_id", "cliente_email"])
        .size()
        .reset_index(name="n")
        .sort_values("n", ascending=False)
        .drop_duplicates(subset=["cliente_id"])
        .set_index("cliente_id")["cliente_email"]
    )
    clientes["email"] = clientes["cliente_id"].map(email_canonico)
    clientes.insert(len(clientes.columns), "fecha_registro", pd.NaT)  # no disponible en el CSV plano

    print(f"\n  CLIENTES  → {len(clientes)} filas × {clientes.shape[1]} columnas")
    print(f"  Columnas  : {list(clientes.columns)}")

    # ── 2FN: extraer tabla PRODUCTOS ──────────────────────────────────────────
    productos = (
        df[["producto_id", "producto_nombre", "categoria",
            "precio_unitario", "costo_unitario"]]
        .drop_duplicates(subset=["producto_id"])
        .rename(columns={
            "producto_nombre": "nombre_producto",
            "precio_unitario": "precio_venta",
        })
        .sort_values("producto_id")
        .reset_index(drop=True)
    )
    productos.insert(len(productos.columns), "stock", 0)  # no disponible en el CSV plano

    print(f"\n  PRODUCTOS → {len(productos)} filas × {productos.shape[1]} columnas")
    print(f"  Columnas  : {list(productos.columns)}")

    # ── 3FN: extraer tabla VENTAS (sin datos del cliente repetidos) ───────────
    ventas = (
        df[["id_venta", "fecha_venta", "cliente_id"]]
        .drop_duplicates(subset=["id_venta"])
        .rename(columns={
            "id_venta":    "venta_id",
            "fecha_venta": "fecha",
        })
        .sort_values("venta_id")
        .reset_index(drop=True)
    )
    ventas["fecha"] = pd.to_datetime(ventas["fecha"])

    print(f"\n  VENTAS    → {len(ventas)} filas × {ventas.shape[1]} columnas")
    print(f"  Columnas  : {list(ventas.columns)}")

    # ── Tabla DETALLE_VENTAS (tabla puente N:M) ───────────────────────────────
    detalle_ventas = (
        df[["id_venta", "producto_id", "cantidad",
            "precio_unitario", "descuento_pct"]]
        .rename(columns={"id_venta": "venta_id"})
        .sort_values(["venta_id", "producto_id"])
        .reset_index(drop=True)
    )

    print(f"\n  DETALLE_VENTAS → {len(detalle_ventas)} filas × {detalle_ventas.shape[1]} columnas")
    print(f"  Columnas       : {list(detalle_ventas.columns)}")

    return clientes, productos, ventas, detalle_ventas


# ══════════════════════════════════════════════════════════════════════════════
# PASO 3 — EXPORTAR las 4 tablas como CSV
# ══════════════════════════════════════════════════════════════════════════════

def exportar_csv(clientes, productos, ventas, detalle_ventas) -> None:
    """Guarda las 4 tablas normalizadas en output_W04/."""

    print("\n" + "=" * 70)
    print("PASO 3 — EXPORTAR tablas normalizadas")
    print("=" * 70)

    tablas = {
        "clientes.csv":       clientes,
        "productos.csv":      productos,
        "ventas.csv":         ventas,
        "detalle_ventas.csv": detalle_ventas,
    }
    for nombre, df in tablas.items():
        ruta = OUT_DIR / nombre
        df.to_csv(ruta, index=False)
        print(f"  ✓ {ruta.name}  ({len(df)} filas)")


# ══════════════════════════════════════════════════════════════════════════════
# PASO 4 — GENERAR sentencias CREATE TABLE en SQL
# ══════════════════════════════════════════════════════════════════════════════

SQL_CLIENTES = """\
CREATE TABLE clientes (
    cliente_id      INT           PRIMARY KEY,
    nombre          VARCHAR(50)   NOT NULL,
    apellido        VARCHAR(50)   NOT NULL,
    email           VARCHAR(100)  UNIQUE NOT NULL,
    region          VARCHAR(50)   NOT NULL,
    segmento        VARCHAR(20)   CHECK (segmento IN ('Premium', 'Estándar', 'Básico')),
    fecha_registro  DATE          NOT NULL
);
"""

SQL_PRODUCTOS = """\
CREATE TABLE productos (
    producto_id      INT            PRIMARY KEY,
    nombre_producto  VARCHAR(100)   NOT NULL,
    categoria        VARCHAR(50)    NOT NULL,
    precio_venta     DECIMAL(10,2)  NOT NULL CHECK (precio_venta > 0),
    costo_unitario   DECIMAL(10,2)  NOT NULL CHECK (costo_unitario > 0),
    stock            INT            NOT NULL DEFAULT 0
);
"""

SQL_VENTAS = """\
CREATE TABLE ventas (
    venta_id    VARCHAR(10)  PRIMARY KEY,
    fecha       DATE         NOT NULL,
    cliente_id  INT          NOT NULL,
    FOREIGN KEY (cliente_id) REFERENCES clientes(cliente_id)
);
"""

SQL_DETALLE_VENTAS = """\
CREATE TABLE detalle_ventas (
    venta_id         VARCHAR(10)   NOT NULL,
    producto_id      INT           NOT NULL,
    cantidad         INT           NOT NULL CHECK (cantidad > 0),
    precio_unitario  DECIMAL(10,2) NOT NULL,
    descuento_pct    DECIMAL(5,2)  NOT NULL DEFAULT 0
                                   CHECK (descuento_pct BETWEEN 0 AND 100),
    PRIMARY KEY (venta_id, producto_id),
    FOREIGN KEY (venta_id)   REFERENCES ventas(venta_id),
    FOREIGN KEY (producto_id) REFERENCES productos(producto_id)
);
"""


def generar_sql() -> None:
    """Imprime y guarda el script SQL con las 4 sentencias CREATE TABLE."""

    print("\n" + "=" * 70)
    print("PASO 4 — SENTENCIAS CREATE TABLE")
    print("=" * 70)

    sql_completo = (
        "-- W04 · TechStyle · Modelo Relacional Normalizado\n"
        "-- Orden: tablas sin FK primero\n\n"
        + SQL_CLIENTES + "\n"
        + SQL_PRODUCTOS + "\n"
        + SQL_VENTAS + "\n"
        + SQL_DETALLE_VENTAS
    )
    print(sql_completo)

    ruta_sql = OUT_DIR / "W04_modelo.sql"
    ruta_sql.write_text(sql_completo, encoding="utf-8")
    print(f"  ✓ SQL guardado en: {ruta_sql}")


# ══════════════════════════════════════════════════════════════════════════════
# PASO 5 — VISUALIZAR: antes (planilla plana) vs después (modelo relacional)
# ══════════════════════════════════════════════════════════════════════════════

def visualizar(df_plano, clientes, productos, ventas, detalle_ventas) -> None:
    """Genera una figura comparativa del antes/después y el diagrama MER simplificado."""

    fig = plt.figure(figsize=(16, 10))
    fig.patch.set_facecolor("#f8f9fa")

    # ── Layout ────────────────────────────────────────────────────────────────
    gs = fig.add_gridspec(
        2, 3,
        left=0.04, right=0.97,
        top=0.90, bottom=0.05,
        hspace=0.45, wspace=0.35,
    )

    ax_plana   = fig.add_subplot(gs[0, :])   # tabla plana — fila superior completa
    ax_clientes  = fig.add_subplot(gs[1, 0])
    ax_productos = fig.add_subplot(gs[1, 1])
    ax_ventas    = fig.add_subplot(gs[1, 2])

    fig.suptitle(
        "W04 · TechStyle: De la Planilla Plana al Modelo Relacional",
        fontsize=14, fontweight="bold", color="#1a1a2e", y=0.97,
    )

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _tabla_ax(ax, titulo, columnas, color_header):
        ax.set_facecolor("#ffffff")
        for spine in ax.spines.values():
            spine.set_edgecolor("#cccccc")
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(titulo, fontsize=10, fontweight="bold",
                     color="white", pad=6,
                     bbox=dict(boxstyle="round,pad=0.3", facecolor=color_header))
        n = len(columnas)
        for i, col in enumerate(columnas):
            y = 1 - (i + 0.5) / max(n, 1)
            icono = "🔑 " if "(PK)" in col or "(PK, FK)" in col else \
                    "🔗 " if "(FK)" in col else "   "
            ax.text(0.08, y, icono + col, transform=ax.transAxes,
                    fontsize=8, va="center",
                    color="#c0392b" if "PK" in col else
                          "#2980b9" if "FK" in col else "#2c3e50")
            ax.axhline(y=1 - (i + 1) / max(n, 1),
                       color="#eeeeee", linewidth=0.5)

    # ── Panel superior: tabla plana ───────────────────────────────────────────
    cols_plana = list(df_plano.columns)
    _tabla_ax(ax_plana,
              f"PLANILLA PLANA  ({len(df_plano)} filas · {len(cols_plana)} columnas) "
              "— toda la información mezclada",
              cols_plana, color_header="#c0392b")

    # ── Paneles inferiores: tablas normalizadas ───────────────────────────────
    _tabla_ax(ax_clientes,
              f"CLIENTES  ({len(clientes)} filas)",
              ["cliente_id (PK)", "nombre", "apellido", "email",
               "region", "segmento", "fecha_registro"],
              color_header="#27ae60")

    _tabla_ax(ax_productos,
              f"PRODUCTOS  ({len(productos)} filas)",
              ["producto_id (PK)", "nombre_producto", "categoria",
               "precio_venta", "costo_unitario", "stock"],
              color_header="#8e44ad")

    _tabla_ax(ax_ventas,
              f"VENTAS  ({len(ventas)} filas)  +  "
              f"DETALLE_VENTAS  ({len(detalle_ventas)} filas)",
              ["venta_id (PK)", "fecha", "cliente_id (FK)",
               "──────────────",
               "venta_id (PK, FK)", "producto_id (PK, FK)",
               "cantidad", "precio_unitario", "descuento_pct"],
              color_header="#2980b9")

    # ── Flecha de antes → después ─────────────────────────────────────────────
    fig.text(0.50, 0.52, "NORMALIZACIÓN\n1FN → 2FN → 3FN",
             ha="center", va="center", fontsize=9, color="#7f8c8d",
             bbox=dict(boxstyle="round,pad=0.4", facecolor="#ecf0f1",
                       edgecolor="#bdc3c7"))
    fig.text(0.50, 0.48, "▼", ha="center", va="center",
             fontsize=14, color="#e74c3c")

    plt.savefig(OUT_DIR / "W04_antes_despues.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\n  ✓ Visualización guardada: {OUT_DIR / 'W04_antes_despues.png'}")


# ══════════════════════════════════════════════════════════════════════════════
# PUNTO DE ENTRADA
# ══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    # Cargar planilla plana
    df = pd.read_csv(DATA_DIR / "techstyle_ventas_planas.csv")
    print(f"  Archivo cargado: techstyle_ventas_planas.csv  "
          f"({len(df)} filas × {df.shape[1]} columnas)\n")

    auditar(df)
    clientes, productos, ventas, detalle_ventas = normalizar(df)
    exportar_csv(clientes, productos, ventas, detalle_ventas)
    generar_sql()
    visualizar(df, clientes, productos, ventas, detalle_ventas)

    print("\n" + "=" * 70)
    print("RESUMEN FINAL")
    print("=" * 70)
    print(f"  Planilla plana   → {len(df)} filas · {df.shape[1]} columnas")
    print(f"  clientes         → {len(clientes)} filas · {clientes.shape[1]} columnas")
    print(f"  productos        → {len(productos)} filas · {productos.shape[1]} columnas")
    print(f"  ventas           → {len(ventas)} filas · {ventas.shape[1]} columnas")
    print(f"  detalle_ventas   → {len(detalle_ventas)} filas · {detalle_ventas.shape[1]} columnas")
    print(f"\n  Salidas en: {OUT_DIR}")
    print("=" * 70)


if __name__ == "__main__":
    main()
