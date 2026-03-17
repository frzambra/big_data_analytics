"""
W02 Lab - Parte B: Auditoría de Calidad y CMI
TechStyle · Big Data y Analytics · Universidad San Sebastián

Pasos:
  1. Detectar y clasificar problemas de calidad en techstyle_customers_dirty.csv
  2. Limpiar los datos (equivalente a Power Query)
  3. Construir el CMI con 4 KPIs usando datos limpios
  4. Comparar KPIs antes vs. después de la limpieza
"""

import re
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch
from pathlib import Path

# ── Rutas ──────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "labs" / "data"
OUT_DIR  = Path(__file__).resolve().parent / "output_W02"
OUT_DIR.mkdir(exist_ok=True)

# ══════════════════════════════════════════════════════════════════════════════
# Paso 1 & 2: Auditoría — identificar y clasificar problemas
# ══════════════════════════════════════════════════════════════════════════════

def auditoria(customers_raw: pd.DataFrame) -> pd.DataFrame:
    """Detecta problemas de calidad y devuelve tabla de hallazgos."""

    problemas = []

    # -- Email vacío (nulo) ----------------------------------------------------
    n = customers_raw["email"].isna().sum()
    problemas.append({
        "Columna": "email",
        "Problema encontrado": f"{n} emails vacíos (null/NaN)",
        "Dimensión de calidad": "Completitud",
        "KPI afectado": "Clientes únicos del mes / segmentación CRM",
        "Filas afectadas": int(n),
    })

    # -- Email con formato inválido (sin dominio o sin @) ----------------------
    valid_email = re.compile(r"^[\w\.\+\-]+@[\w\-]+\.[a-z]{2,}$", re.IGNORECASE)

    def email_invalido(e):
        if pd.isna(e):
            return False  # ya contado arriba
        return not bool(valid_email.match(str(e).strip()))

    n = customers_raw["email"].dropna().apply(email_invalido).sum()
    problemas.append({
        "Columna": "email",
        "Problema encontrado": f"{n} emails con formato inválido (@mail sin dominio, etc.)",
        "Dimensión de calidad": "Exactitud",
        "KPI afectado": "Segmentación CRM – tasa de contacto",
        "Filas afectadas": int(n),
    })

    # -- Región inconsistente -------------------------------------------------
    regiones = customers_raw["region"].value_counts()
    sospechosas = [r for r in regiones.index
                   if any(alias in str(r).lower()
                          for alias in ["stgo", "rm", "santiago", "metropolitana"])]
    n_stgo = customers_raw["region"].isin(sospechosas).sum()
    problemas.append({
        "Columna": "region",
        "Problema encontrado": f"Valores inconsistentes para la misma región: {sospechosas}",
        "Dimensión de calidad": "Consistencia",
        "KPI afectado": "Ventas por región / nuevos clientes por región",
        "Filas afectadas": int(n_stgo),
    })

    # -- Espacios en blanco en nombre / apellido --------------------------------
    n_espacios = (
        customers_raw["nombre"].str.strip().ne(customers_raw["nombre"]).sum() +
        customers_raw["apellido"].str.strip().ne(customers_raw["apellido"]).sum()
    )
    problemas.append({
        "Columna": "nombre / apellido",
        "Problema encontrado": f"{n_espacios} valores con espacios al inicio/final",
        "Dimensión de calidad": "Consistencia",
        "KPI afectado": "Deduplicación de clientes",
        "Filas afectadas": int(n_espacios),
    })

    # -- Capitalización dispar en nombre ---------------------------------------
    n_caps = customers_raw["nombre"].apply(
        lambda x: str(x) != str(x).title() if pd.notna(x) else False
    ).sum()
    problemas.append({
        "Columna": "nombre",
        "Problema encontrado": f"{n_caps} nombres con capitalización no estándar (ej: 'jUAN', 'MARIA')",
        "Dimensión de calidad": "Consistencia",
        "KPI afectado": "Reportes de clientes / nombres en dashboards",
        "Filas afectadas": int(n_caps),
    })

    # -- Segmento con valores no reconocidos ------------------------------------
    segmentos_validos = {"Estándar", "Premium", "VIP"}
    n_seg = (~customers_raw["segmento"].isin(segmentos_validos)).sum()
    if n_seg > 0:
        vals_extra = customers_raw.loc[
            ~customers_raw["segmento"].isin(segmentos_validos), "segmento"
        ].unique().tolist()
        problemas.append({
            "Columna": "segmento",
            "Problema encontrado": f"{n_seg} valores fuera del catálogo: {vals_extra}",
            "Dimensión de calidad": "Validez",
            "KPI afectado": "Análisis de segmento / tasa de conversión por segmento",
            "Filas afectadas": int(n_seg),
        })

    df_problemas = pd.DataFrame(problemas)
    return df_problemas


# ══════════════════════════════════════════════════════════════════════════════
# Paso 3: Limpieza (equivalente a transformaciones Power Query)
# ══════════════════════════════════════════════════════════════════════════════

REGION_MAP = {
    "Stgo.":         "Metropolitana",
    "Santiago":      "Metropolitana",
    "RM":            "Metropolitana",
    "stgo":          "Metropolitana",
    "santiago":      "Metropolitana",
    "rm":            "Metropolitana",
}


def limpiar_customers(df_raw: pd.DataFrame) -> pd.DataFrame:
    df = df_raw.copy()

    # T1: Recortar espacios en blanco (Texto.Recortar)
    for col in ["nombre", "apellido", "email", "region", "segmento"]:
        df[col] = df[col].str.strip()

    # T2: Estandarizar capitalización en nombre y apellido (Texto.MayúscMinú → title)
    df["nombre"]   = df["nombre"].str.title()
    df["apellido"] = df["apellido"].str.title()

    # T3: Estandarizar región (reemplazar "Stgo.", "RM", "Santiago" → "Metropolitana")
    df["region"] = df["region"].replace(REGION_MAP)

    # T4: Eliminar filas con email vacío (filtrar nulls)
    df = df[df["email"].notna()].reset_index(drop=True)

    # T5: Marcar emails con formato inválido (no se eliminan, se registran)
    valid_email = re.compile(r"^[\w\.\+\-]+@[\w\-]+\.[a-z]{2,}$", re.IGNORECASE)
    df["email_valido"] = df["email"].apply(
        lambda e: bool(valid_email.match(str(e).strip())) if pd.notna(e) else False
    )

    return df


# ══════════════════════════════════════════════════════════════════════════════
# Paso 4: CMI en Power BI — 4 KPIs
# ══════════════════════════════════════════════════════════════════════════════

def calcular_kpis(orders: pd.DataFrame, customers: pd.DataFrame, label: str) -> dict:
    """Calcula los 4 KPIs del CMI. label = 'Antes' o 'Después'."""
    mes_actual = orders["mes"].max()
    df_mes = orders[orders["mes"] == mes_actual]

    # KPI 1 — Financiera: Ventas totales del mes
    ventas_totales = df_mes["venta_neta"].sum()

    # KPI 2 — Cliente: Clientes únicos del mes
    clientes_unicos = df_mes["cliente_id"].nunique()

    # KPI 3 — Procesos: Margen promedio por categoría
    margen_por_cat = df_mes.groupby("categoria")["margen_pct"].mean().round(2)

    # KPI 4 — Aprendizaje: Nuevos clientes registrados este mes
    customers["fecha_registro"] = pd.to_datetime(customers["fecha_registro"])
    nuevos = customers[
        (customers["fecha_registro"].dt.year  == df_mes["fecha"].dt.year.max()) &
        (customers["fecha_registro"].dt.month == mes_actual)
    ].shape[0]

    return {
        "label": label,
        "mes": mes_actual,
        "ventas_totales": ventas_totales,
        "clientes_unicos": clientes_unicos,
        "margen_por_cat": margen_por_cat,
        "nuevos_clientes": nuevos,
    }


def dashboard_cmi(kpi_antes: dict, kpi_despues: dict):
    """Genera el dashboard del CMI con comparación antes/después."""
    fig = plt.figure(figsize=(16, 11))
    fig.patch.set_facecolor("#0f172a")
    gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.55, wspace=0.4)

    fig.text(0.5, 0.98, "CMI TechStyle — Cuadro de Mando Integral",
             ha="center", fontsize=18, fontweight="bold", color="white", va="top")
    fig.text(0.5, 0.945, f"Mes {kpi_despues['mes']} · Datos limpios vs. datos sucios",
             ha="center", fontsize=10, color="#94a3b8", va="top")

    # ── KPI 1: Financiera ─────────────────────────────────────────────────────
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.axis("off")
    _kpi_card(ax1,
              perspectiva="Financiera",
              nombre="Ventas Totales del Mes",
              antes=f"${kpi_antes['ventas_totales']:,.0f}",
              despues=f"${kpi_despues['ventas_totales']:,.0f}",
              color_acento="#22d3ee",
              nota="venta_neta (orders)")

    # ── KPI 2: Cliente ────────────────────────────────────────────────────────
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.axis("off")
    _kpi_card(ax2,
              perspectiva="Cliente",
              nombre="Clientes Únicos del Mes",
              antes=str(kpi_antes["clientes_unicos"]),
              despues=str(kpi_despues["clientes_unicos"]),
              color_acento="#4ade80",
              nota="cliente_id (orders, únicos)")

    # ── KPI 4: Aprendizaje ────────────────────────────────────────────────────
    ax4 = fig.add_subplot(gs[0, 2])
    ax4.axis("off")
    _kpi_card(ax4,
              perspectiva="Aprendizaje",
              nombre="Nuevos Clientes Registrados",
              antes=str(kpi_antes["nuevos_clientes"]),
              despues=str(kpi_despues["nuevos_clientes"]),
              color_acento="#f472b6",
              nota="fecha_registro (customers)")

    # ── KPI 3: Procesos — Margen por categoría (barras) ───────────────────────
    ax3 = fig.add_subplot(gs[1:, :])
    ax3.set_facecolor("#1e293b")

    cats = kpi_despues["margen_por_cat"].index.tolist()
    vals_antes   = [kpi_antes["margen_por_cat"].get(c, 0) for c in cats]
    vals_despues = [kpi_despues["margen_por_cat"].get(c, 0) for c in cats]

    x = range(len(cats))
    w = 0.35
    bars_a = ax3.bar([xi - w / 2 for xi in x], vals_antes,  width=w,
                     color="#64748b", label="Antes limpieza", alpha=0.85)
    bars_d = ax3.bar([xi + w / 2 for xi in x], vals_despues, width=w,
                     color="#a78bfa", label="Después limpieza", alpha=0.85)

    ax3.set_xticks(list(x))
    ax3.set_xticklabels(cats, fontsize=9, color="white")
    ax3.tick_params(colors="white")
    ax3.yaxis.set_tick_params(labelcolor="white")
    ax3.set_title("Perspectiva Procesos — Margen Promedio (%) por Categoría",
                  fontsize=11, color="white", pad=8)
    ax3.legend(fontsize=9, labelcolor="white",
               facecolor="#0f172a", edgecolor="#334155")
    for spine in ax3.spines.values():
        spine.set_edgecolor("#334155")

    for bar in bars_d:
        ax3.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                 f"{bar.get_height():.1f}%", ha="center", fontsize=8, color="white")

    path = OUT_DIR / "W02_cmi.png"
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"  ✓ CMI guardado en: {path}")


def _kpi_card(ax, perspectiva, nombre, antes, despues, color_acento, nota):
    """Dibuja una tarjeta KPI con comparación antes/después."""
    fancy = FancyBboxPatch((0.05, 0.05), 0.90, 0.90,
                           boxstyle="round,pad=0.02",
                           facecolor="#1e293b", edgecolor=color_acento, linewidth=2,
                           transform=ax.transAxes)
    ax.add_patch(fancy)
    ax.text(0.5, 0.90, perspectiva.upper(), transform=ax.transAxes,
            ha="center", fontsize=7.5, color=color_acento, fontweight="bold")
    ax.text(0.5, 0.78, nombre, transform=ax.transAxes,
            ha="center", fontsize=9, color="#cbd5e1", wrap=True)

    ax.text(0.28, 0.52, "Antes", transform=ax.transAxes,
            ha="center", fontsize=8, color="#64748b")
    ax.text(0.28, 0.35, antes, transform=ax.transAxes,
            ha="center", fontsize=15, fontweight="bold", color="#64748b")

    ax.text(0.72, 0.52, "Después", transform=ax.transAxes,
            ha="center", fontsize=8, color=color_acento)
    ax.text(0.72, 0.35, despues, transform=ax.transAxes,
            ha="center", fontsize=15, fontweight="bold", color=color_acento)

    ax.text(0.5, 0.14, nota, transform=ax.transAxes,
            ha="center", fontsize=7, color="#475569", style="italic")


# ══════════════════════════════════════════════════════════════════════════════
# Exportar tabla de problemas a CSV
# ══════════════════════════════════════════════════════════════════════════════

def exportar_tabla_problemas(df_problemas: pd.DataFrame):
    path = OUT_DIR / "W02_tabla_problemas_calidad.csv"
    df_problemas.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"  ✓ Tabla de problemas exportada en: {path}")


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n=== W02 Parte B: Auditoría de Calidad y CMI ===\n")

    # Cargar datos crudos
    customers_raw = pd.read_csv(DATA_DIR / "techstyle_customers_dirty.csv")
    orders        = pd.read_csv(DATA_DIR / "techstyle_orders.csv", parse_dates=["fecha"])

    # ── Paso 2: Auditoría ──────────────────────────────────────────────────────
    print("[ Paso 2 ] Auditoría de calidad…")
    df_problemas = auditoria(customers_raw)
    print(df_problemas[["Columna", "Problema encontrado",
                         "Dimensión de calidad", "Filas afectadas"]].to_string(index=False))
    exportar_tabla_problemas(df_problemas)

    # ── Paso 3: Limpieza ───────────────────────────────────────────────────────
    print("\n[ Paso 3 ] Limpieza de datos…")
    customers_clean = limpiar_customers(customers_raw)

    n_antes  = len(customers_raw)
    n_despues = len(customers_clean)
    print(f"  Filas antes de limpieza : {n_antes}")
    print(f"  Filas después de limpieza: {n_despues} "
          f"(eliminadas {n_antes - n_despues} por email vacío)")
    print(f"  Emails con formato inválido restantes: "
          f"{(~customers_clean['email_valido']).sum()}")

    # ── Paso 4: CMI ────────────────────────────────────────────────────────────
    print("\n[ Paso 4 ] Calculando KPIs del CMI…")
    kpi_antes   = calcular_kpis(orders, customers_raw.copy(), "Antes")
    kpi_despues = calcular_kpis(orders, customers_clean.copy(), "Después")

    print("\n  KPI 1 — Ventas Totales del Mes:")
    print(f"    Antes : ${kpi_antes['ventas_totales']:,.0f}")
    print(f"    Después: ${kpi_despues['ventas_totales']:,.0f}")

    print("\n  KPI 2 — Clientes Únicos del Mes:")
    print(f"    Antes : {kpi_antes['clientes_unicos']}")
    print(f"    Después: {kpi_despues['clientes_unicos']}")

    print("\n  KPI 3 — Margen Promedio por Categoría (después limpieza):")
    print(kpi_despues["margen_por_cat"].to_string())

    print("\n  KPI 4 — Nuevos Clientes Registrados este Mes:")
    print(f"    Antes : {kpi_antes['nuevos_clientes']}")
    print(f"    Después: {kpi_despues['nuevos_clientes']}")

    dashboard_cmi(kpi_antes, kpi_despues)

    # ── Pregunta final ─────────────────────────────────────────────────────────
    print("\n── Pregunta final ──────────────────────────────────────────────────")
    print(f"""
¿Cuál de los 4 KPIs del CMI está afectado por los problemas de calidad?

→ KPI 4 (Nuevos clientes registrados): el conteo cambia al eliminar
  filas con email vacío, ya que esas filas corresponden a registros
  incompletos que no deberían contarse como clientes válidos.
  Antes:  {kpi_antes['nuevos_clientes']}
  Después: {kpi_despues['nuevos_clientes']}

→ KPI 2 (Clientes únicos del mes): puede verse afectado si clientes
  duplicados por inconsistencias de región o nombre aparecen como
  entidades distintas en el join con orders.

La limpieza también mejora la confiabilidad de los KPIs de región
al unificar "Stgo.", "RM" y "Santiago" en "Metropolitana".
""")

    print(f"\nTodos los archivos de salida en: {OUT_DIR}/")
