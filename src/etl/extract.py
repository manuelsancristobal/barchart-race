"""Extract: descarga/lectura de datos JAC y normalización de columnas."""

from __future__ import annotations

import logging
import urllib.request
from pathlib import Path

import pandas as pd

from src.config import CSV_LOCAL, EXPECTED_COLUMNS, GSHEET_URL

logger = logging.getLogger(__name__)


def download_csv(url: str = GSHEET_URL, dest: Path = CSV_LOCAL) -> Path:
    """Descarga CSV desde Google Sheets. Retorna path al archivo."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    logger.info("Descargando CSV desde Google Sheets...")
    try:
        urllib.request.urlretrieve(url, dest)
        logger.info("CSV descargado: %s", dest)
    except Exception as exc:
        logger.warning("No se pudo descargar: %s. Usando archivo local.", exc)
        if not dest.exists():
            raise FileNotFoundError(f"No hay CSV local en {dest}") from exc
    return dest


def load_raw(path: Path = CSV_LOCAL) -> pd.DataFrame:
    """Lee CSV crudo y valida columnas esperadas."""
    logger.info("Leyendo %s ...", path)
    df = pd.read_csv(path, low_memory=False, dtype={"PASAJEROS": str})
    _validate_columns(df)
    return df


def _validate_columns(df: pd.DataFrame) -> None:
    """Verifica que existan las columnas esperadas."""
    # La columna Año puede leerse con encoding distinto
    actual = set(df.columns)
    year_col = _find_year_column(df)
    # Normalizar: reemplazar la variante encontrada por "Año"
    expected = set(EXPECTED_COLUMNS)
    if year_col != "Año":
        expected = {c if c != "Año" else year_col for c in expected}
    missing = expected - actual
    if missing:
        raise ValueError(f"Columnas faltantes en los datos: {missing}")


def _find_year_column(df: pd.DataFrame) -> str:
    """Encuentra la columna de año (puede tener encoding distinto de ñ)."""
    for col in df.columns:
        if col.lower().startswith("a") and col.lower().endswith("o") and len(col) <= 4:
            return col
    raise ValueError("No se encontró columna de año (Año/Ano)")


def _parse_chilean_int(val) -> int:
    """Parsea número en formato chileno (punto como separador de miles)."""
    s = str(val).strip()
    if not s or s in ("nan", "None", ""):
        return 0
    try:
        return int(s.replace(".", ""))
    except ValueError:
        return 0


def normalize(df: pd.DataFrame) -> pd.DataFrame:
    """Normaliza columnas y tipos del DataFrame crudo."""
    df = df.copy()

    # Renombrar Año → year (evitar problemas con ñ), Mes → month
    year_col = _find_year_column(df)
    df = df.rename(columns={year_col: "year", "Mes": "month"})

    # CARGA (Ton): formato chileno pre-2022 (punto = miles), coma decimal post-2022
    pre2022 = df["year"] < 2022
    carga_str = df["CARGA (Ton)"].astype(str)
    carga_result = pd.Series(0.0, index=df.index)
    if pre2022.any():
        carga_result[pre2022] = carga_str[pre2022].apply(_parse_chilean_int).astype(float)
    if (~pre2022).any():
        carga_result[~pre2022] = pd.to_numeric(
            carga_str[~pre2022].str.replace(",", "."), errors="coerce"
        ).fillna(0)
    df["CARGA_TON"] = carga_result
    df = df.drop(columns=["CARGA (Ton)"])

    # PASAJEROS: formato chileno pre-2022 (punto = miles), entero post-2022
    pax_str = df["PASAJEROS"].astype(str)
    pax_result = pd.Series(0, index=df.index)
    if pre2022.any():
        pax_result[pre2022] = pax_str[pre2022].apply(_parse_chilean_int)
    if (~pre2022).any():
        pax_result[~pre2022] = pd.to_numeric(
            pax_str[~pre2022], errors="coerce"
        ).fillna(0).astype(int)
    df["PASAJEROS"] = pax_result

    df["PAX_LIB"] = df["PAX_LIB"].fillna(0).round().astype(int)

    # Columnas derivadas
    df["PASAJEROS_TOTAL"] = df["PAX_LIB"] + df["PASAJEROS"]
    df["CARGA_TOTAL"] = (df["CAR_LIB"] / 1000) + df["CARGA_TON"]

    # Log proporción de carga libre
    by_year = df.groupby("year").agg(
        car_lib=("CAR_LIB", "sum"),
        carga_total_sum=("CARGA_TOTAL", "sum"),
    )
    by_year["pct_car_lib"] = (
        (by_year["car_lib"] / 1000) / by_year["carga_total_sum"] * 100
    ).round(1)
    logger.info(
        "Proporción carga libre (CAR_LIB/1000) sobre CARGA_TOTAL por año:\n%s",
        by_year["pct_car_lib"].to_string(),
    )

    return df


def extract(*, use_remote: bool = False) -> pd.DataFrame:
    """Pipeline completo de extracción: descarga (opcional) + lectura + normalización."""
    if use_remote:
        download_csv()
    df = load_raw()
    df = normalize(df)
    logger.info("Extract completado: %d filas, años %d-%d", len(df), df["year"].min(), df["year"].max())
    return df
