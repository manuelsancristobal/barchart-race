"""Transform: filtros, agregaciones, cumsum y mapeo de continentes."""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from src.config import CONTINENT_MAP, DATA_WORK

logger = logging.getLogger(__name__)


# ── Pipeline principal ─────────────────────────────────


def build_pipeline(
    df: pd.DataFrame,
    perspectiva: str,
    dimension: str,
    metrica: str,
) -> pd.DataFrame:
    """
    Encadena: filter_international → filter_perspectiva → aggregate → cumsum → mapping.
    Resuelve internamente qué columnas usar según la combinación.
    """
    df = filter_international(df)
    df = filter_by_perspectiva(df, perspectiva)
    df = aggregate(df, perspectiva, dimension, metrica)
    df = compute_cumulative(df)
    if dimension == "destinos":
        df = apply_continent_mapping(df)
    return df


# ── Filtros ────────────────────────────────────────────


def filter_international(df: pd.DataFrame) -> pd.DataFrame:
    """Solo vuelos internacionales."""
    result = df[df["NAC"] == "INTERNACIONAL"].copy()
    logger.debug("filter_international: %d → %d filas", len(df), len(result))
    return result


def filter_by_perspectiva(df: pd.DataFrame, perspectiva: str) -> pd.DataFrame:
    """
    Emisivo: origen Chile, vuelos que SALEN.
    Receptivo: destino Chile, vuelos que LLEGAN.
    """
    if perspectiva == "emisivo":
        mask = (df["ORIG_1_PAIS"] == "CHILE") & (df["OPER_2"] == "SALEN")
    elif perspectiva == "receptivo":
        mask = (df["DEST_1_PAIS"] == "CHILE") & (df["OPER_2"] == "LLEGAN")
    else:
        raise ValueError(f"Perspectiva inválida: {perspectiva}")
    result = df[mask].copy()
    logger.debug("filter_by_perspectiva(%s): %d → %d filas", perspectiva, len(df), len(result))
    return result


# ── Agregación ─────────────────────────────────────────


def _resolve_columns(
    perspectiva: str, dimension: str, metrica: str,
) -> tuple[str, str | None, str]:
    """Retorna (name_col, group_col, value_col) según la combinación."""
    if dimension == "destinos":
        if perspectiva == "emisivo":
            name_col, group_col = "DEST_1_N", "DEST_1_PAIS"
        else:
            name_col, group_col = "ORIG_1_N", "ORIG_1_PAIS"
    elif dimension == "aerolinea":
        name_col, group_col = "Grupo", None
    else:
        raise ValueError(f"Dimensión inválida: {dimension}")

    value_col = "PASAJEROS_TOTAL" if metrica == "pasajeros" else "CARGA_TOTAL"
    return name_col, group_col, value_col


def aggregate(
    df: pd.DataFrame,
    perspectiva: str,
    dimension: str,
    metrica: str,
) -> pd.DataFrame:
    """Agrupa por year + name (+ group) y suma la métrica."""
    name_col, group_col, value_col = _resolve_columns(perspectiva, dimension, metrica)

    group_by = ["year", "month", name_col]
    if group_col:
        group_by.append(group_col)

    agg = df.groupby(group_by, as_index=False)[value_col].sum()
    agg = agg.rename(columns={name_col: "name", value_col: "value"})
    if group_col:
        agg = agg.rename(columns={group_col: "group"})
    else:
        agg["group"] = None

    logger.debug("aggregate: %d filas agregadas", len(agg))
    return agg


# ── Cumsum ─────────────────────────────────────────────


def compute_cumulative(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula el valor acumulado histórico por entidad (granularidad mensual)."""
    df = df.copy()
    # Reemplazar None en group con cadena centinela para groupby
    _sentinel = "__NO_GROUP__"
    df["group"] = df["group"].fillna(_sentinel)

    df = df.sort_values(["name", "group", "year", "month"])

    # Asegurar que todas las entidades tengan entrada para todos los periodos year+month
    all_periods = df[["year", "month"]].drop_duplicates().sort_values(["year", "month"])
    entities = df[["name", "group"]].drop_duplicates()
    full_index = entities.merge(all_periods, how="cross")
    df = full_index.merge(df, on=["name", "group", "year", "month"], how="left")
    df["value"] = df["value"].fillna(0)

    df = df.sort_values(["name", "group", "year", "month"])
    df["value"] = df.groupby(["name", "group"])["value"].cumsum()

    # Restaurar None
    df["group"] = df["group"].replace(_sentinel, None)

    logger.debug("compute_cumulative: %d filas con cumsum", len(df))
    return df


# ── Mapeo de continentes ──────────────────────────────


def apply_continent_mapping(df: pd.DataFrame) -> pd.DataFrame:
    """Asigna continente según el país (group). Reporta países no mapeados."""
    # Normalizar espacios en group para unificar variantes
    df = df.copy()
    df["group"] = df["group"].str.strip().str.replace(r"\s+", " ", regex=True)

    df["continent"] = df["group"].map(CONTINENT_MAP).fillna("Otro")

    unmapped = df.loc[df["continent"] == "Otro", "group"].dropna().unique()
    if len(unmapped) > 0:
        logger.warning("Países sin mapeo de continente (asignados a 'Otro'): %s", list(unmapped))
        _save_unmapped(unmapped)

    return df


def _save_unmapped(unmapped: np.ndarray) -> None:
    """Guarda lista de países no mapeados para revisión."""
    DATA_WORK.mkdir(parents=True, exist_ok=True)
    path = DATA_WORK / "unmapped_countries.txt"
    with open(path, "w", encoding="utf-8") as f:
        for country in sorted(unmapped):
            f.write(f"{country}\n")
    logger.info("Países no mapeados guardados en %s", path)
