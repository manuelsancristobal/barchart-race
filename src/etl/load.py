"""Load: genera JSONs de datos procesados en formato compacto."""

from __future__ import annotations

import json
import logging
from datetime import date

import pandas as pd

from src.config import CONTINENT_COLORS, DATA_PROCESSED

logger = logging.getLogger(__name__)


def generate_json(
    df: pd.DataFrame,
    perspectiva: str,
    dimension: str,
    metrica: str,
) -> dict:
    """Construye la estructura JSON compacta para una combinación."""
    # Build sorted periods list
    periods_df = df[["year", "month"]].drop_duplicates().sort_values(["year", "month"])
    periods = [[int(r["year"]), int(r["month"])] for _, r in periods_df.iterrows()]

    # Build period index for fast lookup
    period_to_idx = {(y, m): i for i, (y, m) in enumerate(periods)}

    # Year ranges: map each year to [first_index, last_index] in periods
    years = sorted(df["year"].unique().tolist())
    year_ranges = {}
    for y in years:
        indices = [i for i, (py, _) in enumerate(periods) if py == y]
        year_ranges[str(int(y))] = [indices[0], indices[-1]]

    color_map = CONTINENT_COLORS if dimension == "destinos" else None

    # Build entities with aligned value arrays
    has_continent = "continent" in df.columns
    df_work = df.copy()
    _sentinel = "__NO_GROUP__"
    df_work["group"] = df_work["group"].fillna(_sentinel)
    group_cols = ["name", "group", "continent"] if has_continent else ["name", "group"]
    entity_groups = df_work.groupby(group_cols)
    entities = []
    for keys, group in entity_groups:
        if has_continent:
            name, grp, continent = keys
        else:
            name, grp = keys
            continent = None
        grp = None if grp == _sentinel else grp

        # Build values array aligned to periods
        values = [0.0] * len(periods)
        for _, row in group.iterrows():
            idx = period_to_idx.get((int(row["year"]), int(row["month"])))
            if idx is not None:
                values[idx] = round(float(row["value"]), 2)

        entity = {"name": name, "group": grp if grp is not None else None, "values": values}
        if has_continent:
            entity["continent"] = continent
        entities.append(entity)

    return {
        "metadata": {
            "perspectiva": perspectiva,
            "dimension": dimension,
            "metrica": metrica,
            "years": [int(y) for y in years],
            "periods": periods,
            "year_ranges": year_ranges,
            "generated": date.today().isoformat(),
        },
        "color_map": color_map,
        "entities": entities,
    }


def save_json(
    payload: dict, perspectiva: str, dimension: str, metrica: str,
) -> str:
    """Guarda el JSON en data/processed/ y retorna el path."""
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    filename = f"{perspectiva}_{dimension}_{metrica}.json"
    path = DATA_PROCESSED / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
    size_kb = path.stat().st_size / 1024
    logger.info("JSON guardado: %s (%d entidades, %.0f KB)", path, len(payload["entities"]), size_kb)
    return str(path)


def load(df: pd.DataFrame, perspectiva: str, dimension: str, metrica: str) -> str:
    """Pipeline completo de carga: genera JSON y lo guarda."""
    payload = generate_json(df, perspectiva, dimension, metrica)
    return save_json(payload, perspectiva, dimension, metrica)
