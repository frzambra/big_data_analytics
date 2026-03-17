"""
W02 Lab - Parte A: Tres Dashboards por Nivel Organizacional
TechStyle · Big Data y Analytics · Universidad San Sebastián

Genera 3 dashboards en PDF/PNG simulando las 3 vistas de Power BI:
  - Página 1: Vista de Sofía (Operativa)
  - Página 2: Vista de Juan (Táctica)
  - Página 3: Vista de Roberto (Estratégica)
"""

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

# ── Carga de datos ─────────────────────────────────────────────────────────────
orders = pd.read_csv(DATA_DIR / "techstyle_orders.csv", parse_dates=["fecha"])
orders["semana"] = orders["fecha"].dt.isocalendar().week.astype(int)

# ══════════════════════════════════════════════════════════════════════════════
# Página 1 — Vista de Sofía (Operativa)
# ══════════════════════════════════════════════════════════════════════════════

def dashboard_sofia(orders: pd.DataFrame, semana: int = None, region: str = None):
    """
    Tabla operativa: order_id, fecha, nombre_producto, categoria, cantidad, region.
    Filtro por semana y segmentador por región.
    """
    df = orders.copy()

    # Filtros
    if semana:
        df = df[df["semana"] == semana]
    if region:
        df = df[df["region"] == region]

    cols = ["order_id", "fecha", "nombre_producto", "categoria", "cantidad", "region"]
    tabla = df[cols].sort_values("fecha").reset_index(drop=True).head(30)

    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor("#1e2a3a")
    ax.set_facecolor("#1e2a3a")
    ax.axis("off")

    # Título
    titulo = f"Vista de Sofía — Operativa"
    subtitulo = (f"Semana {semana}" if semana else "Todas las semanas") + \
                (f" | Región: {region}" if region else " | Todas las regiones")
    fig.text(0.5, 0.97, titulo, ha="center", va="top",
             fontsize=18, fontweight="bold", color="white")
    fig.text(0.5, 0.93, subtitulo, ha="center", va="top",
             fontsize=11, color="#a0b4c8")

    # Tabla
    encabezados = ["Order ID", "Fecha", "Producto", "Categoría", "Cantidad", "Región"]
    cell_data = [[
        str(r["order_id"]),
        r["fecha"].strftime("%Y-%m-%d"),
        r["nombre_producto"][:28],
        r["categoria"],
        str(r["cantidad"]),
        r["region"],
    ] for _, r in tabla.iterrows()]

    tbl = ax.table(
        cellText=cell_data,
        colLabels=encabezados,
        loc="center",
        cellLoc="center",
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9)
    tbl.scale(1, 1.6)

    # Estilo de encabezado
    for j in range(len(encabezados)):
        tbl[0, j].set_facecolor("#2e7d9a")
        tbl[0, j].set_text_props(color="white", fontweight="bold")

    # Filas alternadas
    for i in range(1, len(cell_data) + 1):
        color = "#2c3e50" if i % 2 == 0 else "#253545"
        for j in range(len(encabezados)):
            tbl[i, j].set_facecolor(color)
            tbl[i, j].set_text_props(color="white")
            tbl[i, j].set_edgecolor("#1e2a3a")

    # Leyenda de filas mostradas
    fig.text(0.02, 0.02,
             f"Mostrando {len(tabla)} de {len(df)} pedidos",
             fontsize=8, color="#a0b4c8")

    plt.tight_layout(rect=[0, 0.04, 1, 0.92])
    path = OUT_DIR / "W02_dashboard_sofia.png"
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"  ✓ Dashboard de Sofía guardado en: {path}")


# ══════════════════════════════════════════════════════════════════════════════
# Página 2 — Vista de Juan (Táctica)
# ══════════════════════════════════════════════════════════════════════════════

def dashboard_juan(orders: pd.DataFrame):
    """
    - Barras: venta_neta por categoria × semana
    - Top 10 productos (cantidad)
    - KPI: total unidades vs. total venta_neta
    """
    fig = plt.figure(figsize=(16, 10))
    fig.patch.set_facecolor("#1a1a2e")
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.35)

    # ── KPI cards (fila 0, col 0-1 unificadas) ────────────────────────────────
    ax_kpi = fig.add_subplot(gs[0, :])
    ax_kpi.set_facecolor("#1a1a2e")
    ax_kpi.axis("off")

    total_unidades = int(orders["cantidad"].sum())
    total_ventas   = orders["venta_neta"].sum()

    kpis = [
        ("Total Unidades Vendidas", f"{total_unidades:,}"),
        ("Monto Total (venta neta)", f"${total_ventas:,.0f}"),
    ]
    for i, (label, valor) in enumerate(kpis):
        x = 0.18 + i * 0.5
        fancy = FancyBboxPatch((x - 0.15, 0.1), 0.3, 0.75,
                               boxstyle="round,pad=0.02",
                               facecolor="#16213e", edgecolor="#0f3460", linewidth=2,
                               transform=ax_kpi.transAxes)
        ax_kpi.add_patch(fancy)
        ax_kpi.text(x, 0.67, label, transform=ax_kpi.transAxes,
                    ha="center", fontsize=10, color="#8892b0")
        ax_kpi.text(x, 0.35, valor, transform=ax_kpi.transAxes,
                    ha="center", fontsize=22, fontweight="bold", color="#64ffda")

    fig.text(0.5, 0.97, "Vista de Juan — Táctica", ha="center",
             fontsize=17, fontweight="bold", color="white")

    # ── Barras: venta_neta por categoría × semana ─────────────────────────────
    ax_bar = fig.add_subplot(gs[1, 0])
    ax_bar.set_facecolor("#16213e")

    pivot = (orders.groupby(["semana", "categoria"])["venta_neta"]
             .sum().unstack(fill_value=0))
    semanas = pivot.index.tolist()
    categorias = pivot.columns.tolist()
    colores = ["#64ffda", "#f97316", "#a78bfa", "#fbbf24", "#34d399", "#f472b6"]

    x = range(len(semanas))
    bar_w = 0.8 / max(len(categorias), 1)
    for idx, cat in enumerate(categorias):
        offset = (idx - len(categorias) / 2 + 0.5) * bar_w
        ax_bar.bar([xi + offset for xi in x], pivot[cat],
                   width=bar_w * 0.9,
                   color=colores[idx % len(colores)],
                   label=cat, alpha=0.85)

    ax_bar.set_xticks(list(x))
    ax_bar.set_xticklabels([f"S{s}" for s in semanas], fontsize=7, color="white")
    ax_bar.set_title("Venta Neta por Categoría × Semana",
                     fontsize=10, color="white", pad=6)
    ax_bar.tick_params(colors="white")
    ax_bar.yaxis.set_tick_params(labelcolor="white")
    ax_bar.set_facecolor("#16213e")
    for spine in ax_bar.spines.values():
        spine.set_edgecolor("#0f3460")
    ax_bar.legend(fontsize=6, labelcolor="white",
                  facecolor="#1a1a2e", edgecolor="#0f3460",
                  loc="upper left", ncol=2)

    # ── Top 10 productos ──────────────────────────────────────────────────────
    ax_top = fig.add_subplot(gs[1, 1])
    ax_top.set_facecolor("#16213e")

    top10 = (orders.groupby("nombre_producto")["cantidad"]
             .sum().nlargest(10).sort_values())

    bars = ax_top.barh(range(len(top10)), top10.values,
                       color="#f97316", alpha=0.85)
    ax_top.set_yticks(range(len(top10)))
    ax_top.set_yticklabels([t[:22] for t in top10.index],
                           fontsize=7.5, color="white")
    ax_top.set_title("Top 10 Productos Más Vendidos (unidades)",
                     fontsize=10, color="white", pad=6)
    ax_top.tick_params(colors="white")
    ax_top.xaxis.set_tick_params(labelcolor="white")
    for spine in ax_top.spines.values():
        spine.set_edgecolor("#0f3460")

    # Etiquetas de valor
    for bar, val in zip(bars, top10.values):
        ax_top.text(val + max(top10.values) * 0.01, bar.get_y() + bar.get_height() / 2,
                    str(int(val)), va="center", fontsize=7, color="white")

    path = OUT_DIR / "W02_dashboard_juan.png"
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"  ✓ Dashboard de Juan guardado en: {path}")


# ══════════════════════════════════════════════════════════════════════════════
# Página 3 — Vista de Roberto (Estratégica)
# ══════════════════════════════════════════════════════════════════════════════

def dashboard_roberto(orders: pd.DataFrame):
    """
    - Tarjetas: ventas totales del mes, ticket promedio, margen promedio
    - Línea: evolución de venta_neta mes a mes
    - Tabla: ventas por región
    """
    fig = plt.figure(figsize=(16, 10))
    fig.patch.set_facecolor("#0d1117")
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.35)

    # ── KPI cards ─────────────────────────────────────────────────────────────
    ax_kpi = fig.add_subplot(gs[0, :])
    ax_kpi.set_facecolor("#0d1117")
    ax_kpi.axis("off")

    mes_actual = orders["mes"].max()
    df_mes = orders[orders["mes"] == mes_actual]

    ventas_mes    = df_mes["venta_neta"].sum()
    ticket_prom   = df_mes["precio_unitario"].mean()
    margen_prom   = df_mes["margen_pct"].mean()

    kpis = [
        ("Ventas Totales del Mes",    f"${ventas_mes:,.0f}",  "#58a6ff"),
        ("Ticket Promedio",           f"${ticket_prom:,.0f}", "#3fb950"),
        ("Margen Promedio (%)",       f"{margen_prom:.1f}%",  "#f97316"),
    ]
    for i, (label, valor, color) in enumerate(kpis):
        x = 0.14 + i * 0.36
        fancy = FancyBboxPatch((x - 0.13, 0.05), 0.27, 0.85,
                               boxstyle="round,pad=0.02",
                               facecolor="#161b22", edgecolor=color, linewidth=2,
                               transform=ax_kpi.transAxes)
        ax_kpi.add_patch(fancy)
        ax_kpi.text(x, 0.72, label, transform=ax_kpi.transAxes,
                    ha="center", fontsize=9.5, color="#8b949e")
        ax_kpi.text(x, 0.38, valor, transform=ax_kpi.transAxes,
                    ha="center", fontsize=22, fontweight="bold", color=color)
        ax_kpi.text(x, 0.15, f"Mes {mes_actual}", transform=ax_kpi.transAxes,
                    ha="center", fontsize=8, color="#484f58")

    fig.text(0.5, 0.97, "Vista de Roberto — Estratégica", ha="center",
             fontsize=17, fontweight="bold", color="white")

    # ── Línea: evolución mensual ───────────────────────────────────────────────
    ax_line = fig.add_subplot(gs[1, 0])
    ax_line.set_facecolor("#161b22")

    evol = orders.groupby("mes")["venta_neta"].sum().sort_index()
    ax_line.plot(evol.index, evol.values,
                 color="#58a6ff", linewidth=2.5, marker="o",
                 markersize=6, markerfacecolor="#58a6ff")
    ax_line.fill_between(evol.index, evol.values, alpha=0.15, color="#58a6ff")
    ax_line.set_xticks(evol.index)
    ax_line.set_xticklabels([f"Mes {m}" for m in evol.index],
                            fontsize=7.5, rotation=30, color="white")
    ax_line.set_title("Evolución de Venta Neta por Mes",
                      fontsize=10, color="white", pad=6)
    ax_line.tick_params(colors="white")
    ax_line.yaxis.set_tick_params(labelcolor="white")
    ax_line.set_facecolor("#161b22")
    for spine in ax_line.spines.values():
        spine.set_edgecolor("#30363d")

    # ── Tabla: ventas por región ───────────────────────────────────────────────
    ax_tbl = fig.add_subplot(gs[1, 1])
    ax_tbl.set_facecolor("#161b22")
    ax_tbl.axis("off")

    ventas_region = (orders.groupby("region")["venta_neta"]
                     .sum().sort_values(ascending=False))
    total = ventas_region.sum()
    cell_data = [
        [r, f"${v:,.0f}", f"{v / total * 100:.1f}%"]
        for r, v in ventas_region.items()
    ]

    tbl = ax_tbl.table(
        cellText=cell_data,
        colLabels=["Región", "Venta Neta", "% Total"],
        loc="center",
        cellLoc="center",
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9)
    tbl.scale(1.1, 1.8)

    for j in range(3):
        tbl[0, j].set_facecolor("#1f6feb")
        tbl[0, j].set_text_props(color="white", fontweight="bold")
    for i in range(1, len(cell_data) + 1):
        bg = "#161b22" if i % 2 else "#1c2128"
        for j in range(3):
            tbl[i, j].set_facecolor(bg)
            tbl[i, j].set_text_props(color="white")
            tbl[i, j].set_edgecolor("#30363d")

    ax_tbl.set_title("Ventas por Región", fontsize=10,
                     color="white", pad=10)

    path = OUT_DIR / "W02_dashboard_roberto.png"
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"  ✓ Dashboard de Roberto guardado en: {path}")


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n=== W02 Parte A: Dashboards por Nivel Organizacional ===\n")

    # Sofía: ejemplo filtrando semana 10, todas las regiones
    semana_ejemplo = orders["semana"].mode()[0]
    dashboard_sofia(orders, semana=semana_ejemplo)

    # Juan: visión táctica completa
    dashboard_juan(orders)

    # Roberto: visión estratégica completa
    dashboard_roberto(orders)

    print(f"\nTodos los dashboards guardados en: {OUT_DIR}/")

    # ── Respuestas a preguntas de reflexión ───────────────────────────────────
    print("\n── Preguntas de reflexión ──────────────────────────────────────────")
    print("""
1. Columnas relevantes para Sofía pero NO para Roberto:
   order_id, nombre_producto, cantidad, region (nivel de detalle operativo).
   Roberto solo necesita agregados (venta_neta total, margen_pct promedio).

2. "Total de ventas" se muestra de forma distinta porque:
   - Sofía: fila por pedido (necesita saber QUÉ despachar hoy).
   - Juan:  suma semanal por categoría (necesita detectar TENDENCIAS).
   - Roberto: suma mensual global (necesita evaluar DESEMPEÑO financiero).
   El nivel de agregación cambia según el horizonte temporal y el rol.

3. Tipo de SI por vista:
   - Sofía  → TPS (Transaction Processing System): datos operativos en tiempo real.
   - Juan   → BI / DSS (Business Intelligence / Decision Support System): análisis táctico.
   - Roberto → EIS (Executive Information System): KPIs estratégicos de alto nivel.
""")
