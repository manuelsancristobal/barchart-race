"""Batería de 7 gráficos analíticos complementarios al Barchart Race.

Genera PNGs en viz/assets/charts/ a partir de los JSONs procesados.
Cada gráfico revela insights ocultos por la acumulación del barchart.
"""

import json

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

from src import config

CHARTS_DIR = config.PROJECT_ROOT / "viz" / "assets" / "charts"
CHARTS_DIR.mkdir(parents=True, exist_ok=True)

FIGSIZE = (14, 7)
DPI = 150

# ── Estilo global ─────────────────────────────────────────
plt.style.use("seaborn-v0_8-whitegrid")
plt.rcParams.update({
    "figure.figsize": FIGSIZE,
    "figure.dpi": DPI,
    "axes.titlesize": 14,
    "axes.labelsize": 12,
    "font.size": 10,
})

# Mapeo país → continente (reutiliza config)
COUNTRY_TO_CONTINENT = config.CONTINENT_MAP
CONTINENT_COLORS = config.CONTINENT_COLORS
MONTH_NAMES = config.MONTH_NAMES_ES


# ══════════════════════════════════════════════════════════
# UTILIDADES
# ══════════════════════════════════════════════════════════

def load_json(filename: str) -> dict:
    """Carga un JSON procesado."""
    path = config.DATA_PROCESSED / filename
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_all_data() -> dict:
    """Carga los 8 JSONs, retorna dict indexado por nombre de archivo (sin ext)."""
    files = [
        f"{p}_{d}_{m}"
        for p in config.PERSPECTIVAS
        for d in config.DIMENSIONES
        for m in config.METRICAS
    ]
    return {name: load_json(f"{name}.json") for name in files}


def decumulate(values: list[float]) -> list[float]:
    """Convierte acumulado a flujo mensual."""
    flow = [values[0]]
    for i in range(1, len(values)):
        flow.append(values[i] - values[i - 1])
    return flow


def get_periods(data: dict) -> list[tuple[int, int]]:
    """Retorna lista de (year, month) desde metadata."""
    return [tuple(p) for p in data["metadata"]["periods"]]


def annual_total_flow(data: dict) -> dict[int, float]:
    """Suma de-cumulada de todas las entidades, agrupada por año."""
    periods = get_periods(data)
    yearly = {}
    for entity in data["entities"]:
        flow = decumulate(entity["values"])
        for (yr, _mo), val in zip(periods, flow):
            yearly[yr] = yearly.get(yr, 0) + val
    return dict(sorted(yearly.items()))


def country_to_continent(country: str) -> str:
    """Mapea país a continente usando config."""
    return COUNTRY_TO_CONTINENT.get(country, "Otro")


def savefig(fig, name: str):
    """Guarda figura y cierra."""
    path = CHARTS_DIR / f"{name}.png"
    fig.savefig(path, bbox_inches="tight", dpi=DPI)
    plt.close(fig)
    print(f"  OK: {path.name}")


# ══════════════════════════════════════════════════════════
# GRÁFICO 1: Evolución del tráfico aéreo total
# ══════════════════════════════════════════════════════════

def chart_01_total_traffic(all_data: dict):
    """Líneas de tráfico total anual: 4 series (emisivo/receptivo × pax/ton)."""
    series = {
        "Emisivo - Pasajeros": "emisivo_destinos_pasajeros",
        "Receptivo - Pasajeros": "receptivo_destinos_pasajeros",
        "Emisivo - Tonelaje": "emisivo_destinos_tonelaje",
        "Receptivo - Tonelaje": "receptivo_destinos_tonelaje",
    }

    pax_series = {}
    ton_series = {}
    for label, key in series.items():
        yearly = annual_total_flow(all_data[key])
        if "Pasajeros" in label:
            pax_series[label] = yearly
        else:
            ton_series[label] = yearly

    fig, ax1 = plt.subplots(figsize=FIGSIZE)
    ax2 = ax1.twinx()

    colors_pax = ["#2171b5", "#6baed6"]
    colors_ton = ["#cb181d", "#fb6a4a"]

    for (label, yearly), color in zip(pax_series.items(), colors_pax):
        years = list(yearly.keys())
        vals = list(yearly.values())
        ax1.plot(years, vals, color=color, linewidth=2, label=label)

    for (label, yearly), color in zip(ton_series.items(), colors_ton):
        years = list(yearly.keys())
        vals = list(yearly.values())
        ax2.plot(years, vals, color=color, linewidth=2, linestyle="--", label=label)

    ax1.set_xlabel("Año")
    ax1.set_ylabel("Pasajeros", color="#2171b5")
    ax2.set_ylabel("Tonelaje", color="#cb181d")
    ax1.set_title("Evolución del tráfico aéreo internacional de Chile (1984–2026)")
    ax1.tick_params(axis="y", labelcolor="#2171b5")
    ax2.tick_params(axis="y", labelcolor="#cb181d")

    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x / 1e6:.1f}M"))
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x / 1e3:.0f}K"))

    # Combinar leyendas
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", framealpha=0.9)

    # Anotar COVID (restricciones hasta ~oct 2022)
    ax1.axvspan(2020, 2022.83, alpha=0.15, color="gray", label="COVID-19")
    ax1.text(2021.4, ax1.get_ylim()[1] * 0.8, "COVID-19", ha="center",
             fontsize=9, color="gray", fontstyle="italic")

    # Detectar año incompleto al final de la serie
    all_periods = get_periods(all_data["emisivo_destinos_pasajeros"])
    last_year = all_periods[-1][0]
    first_year = all_periods[0][0]
    months_in_last_year = [mo for yr, mo in all_periods if yr == last_year]

    if len(months_in_last_year) < 12 and last_year != first_year:
        ax1.axvspan(last_year - 0.5, last_year + 0.5, alpha=0.12, color="orange")
        first_mo = MONTH_NAMES[min(months_in_last_year)].lower()
        last_mo = MONTH_NAMES[max(months_in_last_year)].lower()
        ax1.text(last_year, ax1.get_ylim()[1] * 0.85, f"{last_year}\n({first_mo}-{last_mo})",
                 ha="center", fontsize=8, color="darkorange", fontstyle="italic")

    savefig(fig, "01_total_traffic")


# ══════════════════════════════════════════════════════════
# GRÁFICO 2: Índice Herfindahl-Hirschman (concentración)
# ══════════════════════════════════════════════════════════

def chart_02_hhi(all_data: dict):
    """HHI anual para aerolíneas emisivo y receptivo."""
    def compute_hhi(data: dict) -> dict[int, float]:
        periods = get_periods(data)
        # Flujo anual por aerolínea
        airline_yearly: dict[str, dict[int, float]] = {}
        for entity in data["entities"]:
            flow = decumulate(entity["values"])
            name = entity["name"]
            if name not in airline_yearly:
                airline_yearly[name] = {}
            for (yr, _), val in zip(periods, flow):
                airline_yearly[name][yr] = airline_yearly[name].get(yr, 0) + val

        # HHI por año
        all_years = sorted(set(yr for d in airline_yearly.values() for yr in d))
        hhi = {}
        for yr in all_years:
            total = sum(d.get(yr, 0) for d in airline_yearly.values())
            if total <= 0:
                hhi[yr] = 0
                continue
            shares = [(d.get(yr, 0) / total) for d in airline_yearly.values()]
            hhi[yr] = sum(s ** 2 for s in shares) * 10000
        return hhi

    hhi_em = compute_hhi(all_data["emisivo_aerolinea_pasajeros"])
    hhi_re = compute_hhi(all_data["receptivo_aerolinea_pasajeros"])

    fig, ax = plt.subplots(figsize=FIGSIZE)

    years_em = list(hhi_em.keys())
    vals_em = list(hhi_em.values())
    years_re = list(hhi_re.keys())
    vals_re = list(hhi_re.values())

    ax.plot(years_em, vals_em, linewidth=2, color="#2171b5", label="Emisivo")
    ax.plot(years_re, vals_re, linewidth=2, color="#cb181d", label="Receptivo")

    # Bandas de referencia HHI
    ax.axhspan(0, 1500, alpha=0.08, color="green")
    ax.axhspan(1500, 2500, alpha=0.08, color="orange")
    ax.axhspan(2500, max(max(vals_em), max(vals_re)) * 1.1, alpha=0.08, color="red")

    ax.text(1985, 750, "Competitivo (<1500)", fontsize=9, color="green", alpha=0.7)
    ax.text(1985, 2000, "Moderado (1500–2500)", fontsize=9, color="orange", alpha=0.7)
    ax.text(1985, 2750, "Concentrado (>2500)", fontsize=9, color="red", alpha=0.7)

    ax.set_xlabel("Año")
    ax.set_ylabel("Índice HHI")
    ax.set_title("Concentración de mercado aéreo: Índice Herfindahl-Hirschman (1984–2026)")
    ax.legend(loc="upper right")

    savefig(fig, "02_hhi_concentration")


# ══════════════════════════════════════════════════════════
# GRÁFICO 3: Heatmap de estacionalidad
# ══════════════════════════════════════════════════════════

def chart_03_seasonality(all_data: dict):
    """Heatmap año × mes del tráfico emisivo de pasajeros."""
    data = all_data["emisivo_destinos_pasajeros"]
    periods = get_periods(data)

    # Flujo mensual total
    monthly: dict[tuple[int, int], float] = {}
    for entity in data["entities"]:
        flow = decumulate(entity["values"])
        for (yr, mo), val in zip(periods, flow):
            monthly[(yr, mo)] = monthly.get((yr, mo), 0) + val

    years = sorted(set(yr for yr, _ in monthly))
    months = list(range(1, 13))

    matrix = np.zeros((len(years), 12))
    for i, yr in enumerate(years):
        for j, mo in enumerate(months):
            matrix[i, j] = monthly.get((yr, mo), 0)

    fig, ax = plt.subplots(figsize=FIGSIZE)
    from matplotlib.colors import PowerNorm
    # PowerNorm con gamma<1 comprime los valores altos, revelando los bajos
    vmax = matrix.max()
    im = ax.imshow(matrix, aspect="auto", cmap="YlOrRd", interpolation="nearest",
                   norm=PowerNorm(gamma=0.4, vmin=0, vmax=vmax))
    cbar = fig.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("Pasajeros")

    ax.set_xticks(range(12))
    ax.set_xticklabels(MONTH_NAMES[1:])

    # Mostrar solo cada 5 años en eje Y
    yticks = [i for i, yr in enumerate(years) if yr % 5 == 0]
    ax.set_yticks(yticks)
    ax.set_yticklabels([years[i] for i in yticks])

    ax.set_title("Estacionalidad del tráfico aéreo emisivo de pasajeros (1984–2026)")
    ax.set_xlabel("Mes")
    ax.set_ylabel("Año")

    savefig(fig, "03_seasonality_heatmap")


# ══════════════════════════════════════════════════════════
# GRÁFICO 4: Participación continental (stacked area)
# ══════════════════════════════════════════════════════════

def chart_04_continental_share(all_data: dict):
    """Stacked area: flujo anual por continente (emisivo pasajeros)."""
    data = all_data["emisivo_destinos_pasajeros"]
    periods = get_periods(data)

    # Flujo anual por continente
    continent_yearly: dict[str, dict[int, float]] = {}
    for entity in data["entities"]:
        flow = decumulate(entity["values"])
        continent = country_to_continent(entity["group"])
        if continent not in continent_yearly:
            continent_yearly[continent] = {}
        for (yr, _), val in zip(periods, flow):
            continent_yearly[continent][yr] = continent_yearly[continent].get(yr, 0) + val

    years = sorted(set(yr for d in continent_yearly.values() for yr in d))

    # Ordenar continentes por total descendente
    totals = {c: sum(d.values()) for c, d in continent_yearly.items()}
    continents = sorted(totals, key=totals.get, reverse=True)

    # Matriz para stackplot
    values = np.array([[continent_yearly[c].get(yr, 0) for yr in years] for c in continents])
    colors = [CONTINENT_COLORS.get(c, "#cccccc") for c in continents]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))

    # Absoluto
    ax1.stackplot(years, values, labels=continents, colors=colors, alpha=0.85)
    ax1.set_title("Tráfico emisivo por continente (absoluto)")
    ax1.set_xlabel("Año")
    ax1.set_ylabel("Pasajeros")
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x / 1e6:.1f}M"))
    ax1.legend(loc="upper left", fontsize=8)

    # Porcentual
    totals_by_year = values.sum(axis=0)
    totals_by_year[totals_by_year == 0] = 1  # evitar div/0
    pct = values / totals_by_year * 100
    ax2.stackplot(years, pct, labels=continents, colors=colors, alpha=0.85)
    ax2.set_title("Tráfico emisivo por continente (%)")
    ax2.set_xlabel("Año")
    ax2.set_ylabel("Participación (%)")
    ax2.set_ylim(0, 100)
    ax2.legend(loc="upper left", fontsize=8)

    fig.suptitle("Participación continental en el tráfico aéreo emisivo (1984–2026)", fontsize=14, y=1.02)
    fig.tight_layout()

    savefig(fig, "04_continental_share")


# ══════════════════════════════════════════════════════════
# GRÁFICO 5: Ciclos de vida de aerolíneas (Gantt)
# ══════════════════════════════════════════════════════════

def chart_05_airline_lifecycle(all_data: dict):
    """Gantt timeline: período activo de las top 20-25 aerolíneas."""
    data = all_data["emisivo_aerolinea_pasajeros"]
    periods = get_periods(data)

    airlines = []
    for entity in data["entities"]:
        flow = decumulate(entity["values"])
        total = sum(flow)
        # Años con flujo > 0
        active_years = set()
        for (yr, _), val in zip(periods, flow):
            if val > 0:
                active_years.add(yr)
        if active_years and total > 0:
            airlines.append({
                "name": entity["name"],
                "total": total,
                "start": min(active_years),
                "end": max(active_years),
            })

    # Top 25 por volumen
    airlines.sort(key=lambda x: x["total"], reverse=True)
    airlines = airlines[:25]
    airlines.sort(key=lambda x: x["start"])  # Ordenar por año de inicio

    fig, ax = plt.subplots(figsize=FIGSIZE)

    for i, a in enumerate(airlines):
        duration = a["end"] - a["start"] + 1
        ax.barh(i, duration, left=a["start"], height=0.6, alpha=0.8,
                color=plt.cm.tab20(i % 20), edgecolor="white", linewidth=0.5)

    ax.set_yticks(range(len(airlines)))
    ax.set_yticklabels([a["name"] for a in airlines], fontsize=8)
    ax.set_xlabel("Año")
    ax.set_title("Ciclos de vida: Top 25 aerolíneas por volumen emisivo de pasajeros")
    ax.invert_yaxis()
    ax.set_xlim(1984, 2027)

    savefig(fig, "05_airline_lifecycle")


# ══════════════════════════════════════════════════════════
# GRÁFICO 6: Pasajeros vs Carga (scatter log-log)
# ══════════════════════════════════════════════════════════

def chart_06_pax_vs_cargo(all_data: dict):
    """Scatter log-log: acumulado final pax vs ton por destino."""
    data_pax = all_data["emisivo_destinos_pasajeros"]
    data_ton = all_data["emisivo_destinos_tonelaje"]

    # Mapear nombre → acumulado final
    pax_final = {e["name"]: e["values"][-1] for e in data_pax["entities"]}
    ton_final = {e["name"]: e["values"][-1] for e in data_ton["entities"]}

    # País para color
    pax_group = {e["name"]: e["group"] for e in data_pax["entities"]}

    common = set(pax_final) & set(ton_final)
    # Filtrar > 0 en ambos
    points = []
    for name in common:
        pax = pax_final[name]
        ton = ton_final[name]
        if pax > 0 and ton > 0:
            continent = country_to_continent(pax_group.get(name, ""))
            points.append((name, pax, ton, continent))

    fig, ax = plt.subplots(figsize=FIGSIZE)

    for _name, pax, ton, continent in points:
        color = CONTINENT_COLORS.get(continent, "#cccccc")
        ax.scatter(pax, ton, c=color, s=50, alpha=0.7, edgecolors="white", linewidth=0.5)

    # Etiquetar top 15 por pasajeros
    points.sort(key=lambda x: x[1], reverse=True)
    for name, pax, ton, _ in points[:15]:
        ax.annotate(name.title(), (pax, ton), fontsize=7,
                    xytext=(5, 5), textcoords="offset points", alpha=0.8)

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Pasajeros (acumulado total, escala log)")
    ax.set_ylabel("Tonelaje (acumulado total, escala log)")
    ax.set_title("Relación pasajeros vs. carga por destino (emisivo, acumulado 1984–2026)")

    # Leyenda de continentes
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor=c, markersize=8, label=cont)
        for cont, c in CONTINENT_COLORS.items()
        if cont in {p[3] for p in points}
    ]
    ax.legend(handles=legend_elements, loc="upper left", fontsize=8)

    savefig(fig, "06_pax_vs_cargo")


# ══════════════════════════════════════════════════════════
# GRÁFICO 7: Crecimiento interanual Top 5 destinos
# ══════════════════════════════════════════════════════════

def chart_07_yoy_growth(all_data: dict):
    """YoY % growth del flujo anual de los top 5 destinos emisivo pax."""
    data = all_data["emisivo_destinos_pasajeros"]
    periods = get_periods(data)

    # Flujo anual por destino
    dest_yearly: dict[str, dict[int, float]] = {}
    for entity in data["entities"]:
        flow = decumulate(entity["values"])
        name = entity["name"]
        dest_yearly[name] = {}
        for (yr, _), val in zip(periods, flow):
            dest_yearly[name][yr] = dest_yearly[name].get(yr, 0) + val

    # Top 5 por total
    totals = {name: sum(d.values()) for name, d in dest_yearly.items()}
    top5 = sorted(totals, key=totals.get, reverse=True)[:5]

    fig, ax = plt.subplots(figsize=FIGSIZE)

    colors = ["#2171b5", "#cb181d", "#238b45", "#6a51a3", "#d94801"]
    for name, color in zip(top5, colors):
        yearly = dest_yearly[name]
        years = sorted(yearly.keys())
        vals = [yearly[yr] for yr in years]

        # YoY growth
        yoy_years = []
        yoy_vals = []
        for i in range(1, len(years)):
            if vals[i - 1] > 100:  # umbral mínimo para evitar %inf
                growth = (vals[i] - vals[i - 1]) / vals[i - 1] * 100
                # Limitar a ±200% para legibilidad
                growth = max(-200, min(200, growth))
                yoy_years.append(years[i])
                yoy_vals.append(growth)

        ax.plot(yoy_years, yoy_vals, linewidth=1.5, color=color,
                label=name.title(), alpha=0.8)

    ax.axhline(y=0, color="black", linewidth=0.5, linestyle="-")
    ax.axvspan(2020, 2021, alpha=0.15, color="gray")
    ax.set_xlabel("Año")
    ax.set_ylabel("Crecimiento interanual (%)")
    ax.set_title("Crecimiento interanual: Top 5 destinos emisivos por pasajeros")
    ax.legend(loc="lower left", fontsize=9)
    ax.set_ylim(-210, 210)

    savefig(fig, "07_yoy_growth_top5")


# ══════════════════════════════════════════════════════════
# CAPTIONS
# ══════════════════════════════════════════════════════════

def generate_captions():
    """Genera captions.json con textos sugeridos para la página Jekyll."""
    captions = {
        "01_total_traffic": {
            "titulo": "Evolución del tráfico aéreo internacional de Chile",
            "contexto": "Este gráfico muestra el volumen total de pasajeros y carga del tráfico aéreo internacional de Chile entre 1984 y 2026, distinguiendo entre tráfico emisivo (desde Chile) y receptivo (hacia Chile). El doble eje permite comparar la evolución de pasajeros y tonelaje simultáneamente.",
            "hallazgos": "El tráfico de pasajeros muestra un crecimiento sostenido con una caída dramática en 2020 por COVID-19. La recuperación post-pandemia es notable, especialmente en el tráfico emisivo. El tonelaje tiende a seguir patrones similares pero con menor volatilidad, sugiriendo que la carga aérea es más resiliente a shocks."
        },
        "02_hhi_concentration": {
            "titulo": "Concentración de mercado: Índice Herfindahl-Hirschman",
            "contexto": "El Índice HHI mide la concentración de mercado sumando los cuadrados de las cuotas de participación de cada aerolínea. Valores bajo 1500 indican un mercado competitivo; entre 1500 y 2500, moderadamente concentrado; sobre 2500, altamente concentrado.",
            "hallazgos": "El mercado aéreo chileno ha transitado por fases: alta concentración inicial (dominancia de pocas aerolíneas estatales/legacy), liberalización progresiva, y la entrada de operadores low-cost como SKY y JetSMART que han intensificado la competencia en años recientes."
        },
        "03_seasonality_heatmap": {
            "titulo": "Estacionalidad del tráfico aéreo emisivo",
            "contexto": "El heatmap muestra el flujo mensual de pasajeros emisivos a lo largo de cada año. Los colores más intensos indican mayor tráfico. La estructura año × mes revela patrones estacionales recurrentes.",
            "hallazgos": "Se observa un patrón estacional claro con peaks en enero (verano austral) y julio (vacaciones de invierno). La amplitud estacional crece con el tiempo, reflejando un mercado más grande. Los años 2020-2021 aparecen como franjas claras, evidenciando el impacto COVID."
        },
        "04_continental_share": {
            "titulo": "Participación continental en el tráfico emisivo",
            "contexto": "Muestra cómo se distribuye el tráfico emisivo de pasajeros entre los distintos continentes de destino, tanto en valores absolutos como en participación porcentual.",
            "hallazgos": "América domina ampliamente como destino del tráfico emisivo chileno. Sin embargo, la participación de Europa ha crecido de forma sostenida, mientras que Oceanía y Asia mantienen nichos menores pero crecientes. La composición continental revela la diversificación progresiva de las rutas internacionales."
        },
        "05_airline_lifecycle": {
            "titulo": "Ciclos de vida de las principales aerolíneas",
            "contexto": "Diagrama de Gantt que muestra el período de actividad de las 25 aerolíneas con mayor volumen de pasajeros emisivos. La longitud de cada barra indica el tiempo de operación.",
            "hallazgos": "Se identifican oleadas de entrada/salida de aerolíneas: las legacy carriers operan durante décadas, mientras que muchas aerolíneas tienen ciclos cortos. Las entradas recientes de low-cost (SKY, JetSMART) marcan una nueva era competitiva."
        },
        "06_pax_vs_cargo": {
            "titulo": "Relación pasajeros vs. carga por destino",
            "contexto": "Scatter plot en escala logarítmica que compara el acumulado total de pasajeros y tonelaje por cada destino emisivo. Cada punto es una ciudad, coloreada por continente.",
            "hallazgos": "La mayoría de los destinos siguen una correlación positiva entre pasajeros y carga, pero existen outliers notables: destinos con alta carga relativa sugieren hubs logísticos/comerciales, mientras que destinos con alto flujo de pasajeros pero baja carga indican rutas predominantemente turísticas."
        },
        "07_yoy_growth_top5": {
            "titulo": "Crecimiento interanual: Top 5 destinos",
            "contexto": "Muestra la tasa de crecimiento año a año del flujo de pasajeros de los 5 destinos emisivos más importantes. Este análisis revela la dinámica oculta por los valores acumulados del barchart race.",
            "hallazgos": "Las tasas de crecimiento revelan fases de aceleración y desaceleración no visibles en datos acumulados. El crash COVID genera caídas extremas seguidas de rebounds igualmente intensos. La velocidad de recuperación post-COVID varía significativamente entre destinos."
        }
    }

    path = CHARTS_DIR / "captions.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(captions, f, ensure_ascii=False, indent=2)
    print(f"  OK: {path.name}")


# ══════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════

def main():
    print("Cargando datos...")
    all_data = load_all_data()
    print(f"  {len(all_data)} datasets cargados.\n")

    print("Generando gráficos:")
    chart_01_total_traffic(all_data)
    chart_02_hhi(all_data)
    chart_03_seasonality(all_data)
    chart_04_continental_share(all_data)
    chart_05_airline_lifecycle(all_data)
    chart_06_pax_vs_cargo(all_data)
    chart_07_yoy_growth(all_data)

    print("\nGenerando captions:")
    generate_captions()

    print(f"\nListo. 7 graficos + captions.json en {CHARTS_DIR}")


if __name__ == "__main__":
    main()
