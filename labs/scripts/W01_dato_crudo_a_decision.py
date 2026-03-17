"""
W01 Lab - De Dato Crudo a Decisión
TechStyle · Big Data y Analytics · Universidad San Sebastián

Contexto: María González (Gerente de Marketing) tiene $15.000.000 CLP para
invertir en la campaña del próximo mes. Necesita saber en qué categoría
de productos invertir para maximizar ventas.

Partes:
  1. Explorar los datos brutos
  2. Transformar datos en información (tablas dinámicas equivalentes)
  3. De información a decisión
  4. Reflexión final
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch
from pathlib import Path

# ── Rutas ──────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "labs" / "data"
OUT_DIR  = Path(__file__).resolve().parent / "output_W01"
OUT_DIR.mkdir(exist_ok=True)

PRESUPUESTO = 15_000_000  # CLP

# ══════════════════════════════════════════════════════════════════════════════
# Parte 1 — Explorar los datos brutos
# ══════════════════════════════════════════════════════════════════════════════

def explorar_datos(df: pd.DataFrame):
    print("=" * 60)
    print("PARTE 1 — Exploración de datos brutos")
    print("=" * 60)
    print(f"\nArchivo: techstyle_orders.csv")
    print(f"  Filas    : {len(df):,}")
    print(f"  Columnas : {len(df.columns)}")
    print(f"  Período  : {df['fecha'].min()} → {df['fecha'].max()}")
    print(f"\nColumnas disponibles:")
    for col in df.columns:
        print(f"  · {col}")
    print(f"\nCategorías de productos: {sorted(df['categoria'].unique())}")
    print(f"Regiones              : {sorted(df['region'].unique())}")
    print(f"Trimestres            : {sorted(df['trimestre'].unique())}")

    print("""
Respuestas a la reflexión inicial:
  ¿Cuántos registros?       → {:,}
  ¿Qué período cubre?       → {} a {}
  ¿Qué categorías existen?  → {}
  ¿Puedes responder la pregunta de María solo mirando los datos?
    → No. Los datos crudos son 1.257 filas de transacciones individuales.
      Sin agregar y ordenar, es imposible identificar qué categoría
      genera más ventas o tiene mejor margen.
""".format(
        len(df),
        df['fecha'].min(), df['fecha'].max(),
        ", ".join(sorted(df['categoria'].unique()))
    ))


# ══════════════════════════════════════════════════════════════════════════════
# Parte 2 — Transformar datos en información (tablas dinámicas)
# ══════════════════════════════════════════════════════════════════════════════

def tabla_dinamica_1(df: pd.DataFrame) -> pd.DataFrame:
    """Tabla dinámica 1: venta_neta, cantidad y margen_pct por categoría."""
    td = df.groupby("categoria").agg(
        venta_neta=("venta_neta", "sum"),
        cantidad=("cantidad", "sum"),
        margen_pct=("margen_pct", "mean"),
    ).sort_values("venta_neta", ascending=False).round(2)
    return td


def tabla_dinamica_2(df: pd.DataFrame) -> pd.DataFrame:
    """Tabla dinámica 2: venta_neta por categoría × trimestre."""
    td = df.pivot_table(
        index="categoria",
        columns="trimestre",
        values="venta_neta",
        aggfunc="sum",
        fill_value=0,
    )[["T1", "T2", "T3", "T4"]]
    return td


def tabla_dinamica_3(df: pd.DataFrame) -> pd.DataFrame:
    """Tabla dinámica 3: venta_neta por región × categoría."""
    td = df.pivot_table(
        index="region",
        columns="categoria",
        values="venta_neta",
        aggfunc="sum",
        fill_value=0,
    )
    return td


# ══════════════════════════════════════════════════════════════════════════════
# Parte 3 — Tabla de análisis + recomendación
# ══════════════════════════════════════════════════════════════════════════════

def tabla_analisis(td1: pd.DataFrame, td2: pd.DataFrame) -> pd.DataFrame:
    """
    Construye la tabla de análisis combinando ventas, margen y tendencia T3→T4.
    """
    analisis = td1.copy()
    analisis["tendencia_T3_T4"] = td2["T4"] - td2["T3"]
    analisis["tendencia_pct"]   = (analisis["tendencia_T3_T4"] / td2["T3"] * 100).round(1)
    analisis["buena_inversion"] = analisis.apply(
        lambda r: "Sí"  if (r["margen_pct"] >= analisis["margen_pct"].mean()
                             and r["tendencia_T3_T4"] > 0)
                  else "Revisar" if r["tendencia_T3_T4"] > 0
                  else "No",
        axis=1
    )
    return analisis


def recomendar(analisis: pd.DataFrame) -> str:
    """Selecciona la mejor categoría según ventas + margen + tendencia positiva."""
    candidatas = analisis[analisis["buena_inversion"] == "Sí"]
    if candidatas.empty:
        candidatas = analisis
    mejor = candidatas["venta_neta"].idxmax()
    r = analisis.loc[mejor]
    return (
        f"Recomiendo invertir los ${PRESUPUESTO:,.0f} CLP en la categoría "
        f"**{mejor}** porque lidera en ventas totales (${r['venta_neta']:,.0f} CLP), "
        f"tiene un margen promedio de {r['margen_pct']:.1f}% "
        f"y mostró una tendencia {'positiva' if r['tendencia_T3_T4'] > 0 else 'negativa'} "
        f"de T3 a T4 ({r['tendencia_pct']:+.1f}%)."
    )


# ══════════════════════════════════════════════════════════════════════════════
# Visualizaciones
# ══════════════════════════════════════════════════════════════════════════════

COLORES_CAT = {
    "Electrónica": "#58a6ff",
    "Ropa":        "#f97316",
    "Hogar":       "#4ade80",
    "Accesorios":  "#f472b6",
}


def grafico_resumen(td1: pd.DataFrame, td2: pd.DataFrame, td3: pd.DataFrame,
                    analisis: pd.DataFrame, recomendacion: str):
    """
    Dashboard de una sola figura con 4 paneles:
      A. Barras: venta_neta por categoría
      B. Agrupadas: venta_neta por categoría × trimestre
      C. Mapa de calor: venta_neta por región × categoría
      D. Tabla resumen con recomendación
    """
    fig = plt.figure(figsize=(18, 13))
    fig.patch.set_facecolor("#0d1117")
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.48, wspace=0.38)

    fig.text(0.5, 0.98,
             "TechStyle — Análisis de Ventas 2023 para Decisión de Campaña",
             ha="center", fontsize=16, fontweight="bold", color="white", va="top")
    fig.text(0.5, 0.955,
             f"Presupuesto disponible: ${PRESUPUESTO:,.0f} CLP  ·  Gerente: María González",
             ha="center", fontsize=9.5, color="#8b949e", va="top")

    # ── A: Ventas totales por categoría ───────────────────────────────────────
    ax_a = fig.add_subplot(gs[0, 0])
    ax_a.set_facecolor("#161b22")

    cats   = td1.index.tolist()
    ventas = td1["venta_neta"].values
    colores = [COLORES_CAT.get(c, "#aaa") for c in cats]

    bars = ax_a.bar(cats, ventas, color=colores, alpha=0.88, width=0.55)
    ax_a.set_title("Venta Neta Total por Categoría", fontsize=11,
                   color="white", pad=8)
    ax_a.tick_params(colors="white")
    ax_a.yaxis.set_tick_params(labelcolor="white")
    ax_a.set_xticklabels(cats, color="white", fontsize=9)
    for spine in ax_a.spines.values():
        spine.set_edgecolor("#30363d")

    for bar, val, mar in zip(bars, ventas, td1["margen_pct"].values):
        ax_a.text(bar.get_x() + bar.get_width() / 2,
                  bar.get_height() + max(ventas) * 0.01,
                  f"${val/1e6:.1f}M\n({mar:.0f}% mg)",
                  ha="center", fontsize=8, color="white")

    # ── B: Tendencia por trimestre ─────────────────────────────────────────────
    ax_b = fig.add_subplot(gs[0, 1])
    ax_b.set_facecolor("#161b22")

    trimestres = ["T1", "T2", "T3", "T4"]
    n_cats = len(cats)
    x = range(len(trimestres))
    bar_w = 0.8 / n_cats

    for idx, cat in enumerate(cats):
        offset = (idx - n_cats / 2 + 0.5) * bar_w
        vals = [td2.loc[cat, t] for t in trimestres]
        ax_b.bar([xi + offset for xi in x], vals,
                 width=bar_w * 0.9,
                 color=COLORES_CAT.get(cat, "#aaa"),
                 label=cat, alpha=0.85)

    ax_b.set_xticks(list(x))
    ax_b.set_xticklabels(trimestres, color="white", fontsize=10)
    ax_b.set_title("Venta Neta por Categoría × Trimestre", fontsize=11,
                   color="white", pad=8)
    ax_b.tick_params(colors="white")
    ax_b.yaxis.set_tick_params(labelcolor="white")
    ax_b.legend(fontsize=8, labelcolor="white",
                facecolor="#0d1117", edgecolor="#30363d", ncol=2)
    for spine in ax_b.spines.values():
        spine.set_edgecolor("#30363d")

    # ── C: Mapa de calor región × categoría ───────────────────────────────────
    ax_c = fig.add_subplot(gs[1, 0])
    ax_c.set_facecolor("#161b22")

    data_hm  = td3.values / 1e6  # en millones
    regiones = td3.index.tolist()
    cat_cols = td3.columns.tolist()

    im = ax_c.imshow(data_hm, cmap="YlOrRd", aspect="auto")
    ax_c.set_xticks(range(len(cat_cols)))
    ax_c.set_xticklabels(cat_cols, color="white", fontsize=9)
    ax_c.set_yticks(range(len(regiones)))
    ax_c.set_yticklabels(regiones, color="white", fontsize=8)
    ax_c.set_title("Venta Neta por Región × Categoría (millones CLP)",
                   fontsize=10, color="white", pad=8)

    for i in range(len(regiones)):
        for j in range(len(cat_cols)):
            val = data_hm[i, j]
            color_txt = "black" if val > data_hm.max() * 0.5 else "white"
            ax_c.text(j, i, f"{val:.1f}", ha="center", va="center",
                      fontsize=7.5, color=color_txt, fontweight="bold")

    plt.colorbar(im, ax=ax_c, fraction=0.03, pad=0.04).ax.yaxis.set_tick_params(colors="white")

    # ── D: Tabla resumen + recomendación ──────────────────────────────────────
    ax_d = fig.add_subplot(gs[1, 1])
    ax_d.set_facecolor("#161b22")
    ax_d.axis("off")

    ax_d.set_title("Tabla Resumen de Análisis", fontsize=11,
                   color="white", pad=8)

    headers = ["Categoría", "Ventas (M$)", "Margen %", "T3→T4", "¿Invertir?"]
    rows = []
    for cat, row in analisis.iterrows():
        tend = f"{row['tendencia_pct']:+.1f}%"
        rows.append([
            cat,
            f"${row['venta_neta']/1e6:.2f}M",
            f"{row['margen_pct']:.1f}%",
            tend,
            row["buena_inversion"],
        ])

    tbl = ax_d.table(
        cellText=rows,
        colLabels=headers,
        loc="upper center",
        cellLoc="center",
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9)
    tbl.scale(1.05, 1.9)

    for j in range(len(headers)):
        tbl[0, j].set_facecolor("#1f6feb")
        tbl[0, j].set_text_props(color="white", fontweight="bold")

    color_inv = {"Sí": "#22c55e", "Revisar": "#f59e0b", "No": "#ef4444"}
    for i, (cat, row) in enumerate(analisis.iterrows(), start=1):
        bg = "#1e293b" if i % 2 else "#162032"
        for j in range(len(headers)):
            tbl[i, j].set_facecolor(bg)
            tbl[i, j].set_text_props(color="white")
            tbl[i, j].set_edgecolor("#30363d")
        # Colorear columna "¿Invertir?"
        inv_val = row["buena_inversion"]
        tbl[i, 4].set_text_props(color=color_inv.get(inv_val, "white"),
                                  fontweight="bold")

    # Recomendación como texto
    rec_limpia = recomendacion.replace("**", "")
    ax_d.text(0.5, 0.04, rec_limpia,
              transform=ax_d.transAxes,
              ha="center", va="bottom",
              fontsize=7.8, color="#94a3b8",
              style="italic", wrap=True,
              bbox=dict(boxstyle="round,pad=0.4",
                        facecolor="#0f172a", edgecolor="#334155", alpha=0.9))

    path = OUT_DIR / "W01_analisis_decision.png"
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"  ✓ Dashboard guardado en: {path}")


def grafico_tendencia_lineal(td2: pd.DataFrame):
    """Gráfico de líneas: evolución trimestral por categoría."""
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#161b22")

    trimestres = ["T1", "T2", "T3", "T4"]
    for cat in td2.index:
        vals = [td2.loc[cat, t] / 1e6 for t in trimestres]
        ax.plot(trimestres, vals,
                marker="o", linewidth=2.2, markersize=7,
                color=COLORES_CAT.get(cat, "#aaa"),
                label=cat)
        ax.annotate(f"${vals[-1]:.1f}M",
                    xy=(trimestres[-1], vals[-1]),
                    xytext=(8, 0), textcoords="offset points",
                    fontsize=8, color=COLORES_CAT.get(cat, "#aaa"), va="center")

    ax.set_title("Evolución Trimestral de Venta Neta por Categoría (millones CLP)",
                 fontsize=12, color="white", pad=10)
    ax.tick_params(colors="white")
    ax.yaxis.set_tick_params(labelcolor="white")
    ax.set_xticklabels(trimestres, color="white")
    ax.legend(fontsize=9, labelcolor="white",
              facecolor="#0d1117", edgecolor="#30363d")
    for spine in ax.spines.values():
        spine.set_edgecolor("#30363d")

    path = OUT_DIR / "W01_tendencia_trimestral.png"
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"  ✓ Tendencia trimestral guardada en: {path}")


# ══════════════════════════════════════════════════════════════════════════════
# Exportar tablas dinámicas a CSV
# ══════════════════════════════════════════════════════════════════════════════

def exportar_tablas(td1, td2, td3, analisis):
    td1.to_csv(OUT_DIR / "W01_TD1_venta_por_categoria.csv")
    td2.to_csv(OUT_DIR / "W01_TD2_venta_categoria_trimestre.csv")
    td3.to_csv(OUT_DIR / "W01_TD3_venta_region_categoria.csv")
    analisis.to_csv(OUT_DIR / "W01_tabla_analisis.csv")
    print(f"  ✓ Tablas dinámicas exportadas como CSV en: {OUT_DIR}/")


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    df = pd.read_csv(DATA_DIR / "techstyle_orders.csv", parse_dates=["fecha"])

    # ── Parte 1 ────────────────────────────────────────────────────────────────
    explorar_datos(df)

    # ── Parte 2 ────────────────────────────────────────────────────────────────
    print("=" * 60)
    print("PARTE 2 — Tablas dinámicas")
    print("=" * 60)

    td1 = tabla_dinamica_1(df)
    td2 = tabla_dinamica_2(df)
    td3 = tabla_dinamica_3(df)

    print("\nTD1 — Venta neta, cantidad y margen por categoría (orden ↓ ventas):")
    print(td1.to_string())

    print("\nTD2 — Venta neta por categoría × trimestre:")
    print(td2.to_string())

    print("\nTD3 — Venta neta por región × categoría (primeras filas):")
    print(td3.to_string())

    # ── Parte 3 ────────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("PARTE 3 — Tabla de análisis y recomendación")
    print("=" * 60)

    analisis = tabla_analisis(td1, td2)
    print("\nTabla de análisis completa:")
    print(analisis[["venta_neta", "margen_pct", "tendencia_T3_T4",
                    "tendencia_pct", "buena_inversion"]].to_string())

    recomendacion = recomendar(analisis)
    print(f"\nRECOMENDACIÓN PARA MARÍA:")
    print(f"  {recomendacion}")

    # ── Gráficos ───────────────────────────────────────────────────────────────
    print("\n[ Generando visualizaciones… ]")
    grafico_resumen(td1, td2, td3, analisis, recomendacion)
    grafico_tendencia_lineal(td2)
    exportar_tablas(td1, td2, td3, analisis)

    # ── Parte 4 ────────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("PARTE 4 — Reflexión final")
    print("=" * 60)

    mejor_cat = analisis["venta_neta"].idxmax()
    td1_str   = f"1.257 filas de transacciones individuales sin estructura analítica"
    info_str  = "Tablas agregadas por categoría, trimestre y región con ventas, margen y tendencia"
    conoc_str = "Relación entre margen, volumen y tendencia de crecimiento para evaluar rentabilidad futura"

    print(f"""
1. ¿Podrías haber respondido la pregunta de María sin procesar los datos?
   → No. Con 1.257 filas de transacciones crudas es imposible identificar
     qué categoría tiene mejor desempeño. Los datos necesitan ser agregados,
     comparados y ordenados para convertirse en información útil.

2. Transformación realizada:
   · Datos crudos       → {td1_str}
   · Información        → {info_str}
   · Conocimiento       → {conoc_str}

3. Límite de Excel — escalabilidad:
   · Este archivo tiene {len(df):,} filas → manejable en Excel.
   · TechStyle real: 8.750.000 registros → Excel colapsa (~1M filas máx).
   · Con 3× los datos actuales (~3.750 filas) Excel aún funciona, pero
     con 10× o 100× se vuelve inmanejable: lentitud, errores de memoria,
     fórmulas que tardan minutos. Ahí entran las bases de datos, SQL,
     y las arquitecturas de Big Data que veremos en este curso.

Categoría recomendada para la campaña de María: {mejor_cat}
""")

    print(f"\nTodos los archivos de salida en: {OUT_DIR}/")
