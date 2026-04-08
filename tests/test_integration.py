"""Tests de integración con datos reales (requiere data/raw/jac_data.csv)."""

import json

import pytest

from src.config import CSV_LOCAL
from src.etl.extract import extract
from src.etl.load import generate_json
from src.etl.transform import build_pipeline

pytestmark = pytest.mark.skipif(
    not CSV_LOCAL.exists(),
    reason="Requiere data/raw/jac_data.csv",
)


@pytest.fixture(scope="module")
def raw_df():
    return extract(use_remote=False)


class TestExtractReal:
    def test_has_expected_columns(self, raw_df):
        expected = {"year", "month", "PASAJEROS_TOTAL", "CARGA_TOTAL", "CARGA_TON",
                    "NAC", "OPER_2", "ORIG_1_PAIS", "DEST_1_PAIS",
                    "ORIG_1_N", "DEST_1_N", "Grupo"}
        assert expected.issubset(set(raw_df.columns))

    def test_year_range(self, raw_df):
        assert raw_df["year"].min() == 1984
        assert raw_df["year"].max() >= 2025

    def test_month_range(self, raw_df):
        assert raw_df["month"].min() == 1
        assert raw_df["month"].max() == 12

    def test_no_negative_passengers(self, raw_df):
        assert (raw_df["PASAJEROS_TOTAL"] >= 0).all()

    def test_pasajeros_are_integers(self, raw_df):
        assert raw_df["PAX_LIB"].dtype in [int, "int64", "int32"]

    def test_carga_ton_no_commas(self, raw_df):
        """CARGA_TON debe ser numérica, sin comas."""
        assert raw_df["CARGA_TON"].dtype == "float64"


class TestPipelineReal:
    COMBOS = [
        ("emisivo", "destinos", "pasajeros"),
        ("emisivo", "destinos", "tonelaje"),
        ("emisivo", "aerolinea", "pasajeros"),
        ("emisivo", "aerolinea", "tonelaje"),
        ("receptivo", "destinos", "pasajeros"),
        ("receptivo", "destinos", "tonelaje"),
        ("receptivo", "aerolinea", "pasajeros"),
        ("receptivo", "aerolinea", "tonelaje"),
    ]

    @pytest.mark.parametrize("perspectiva,dimension,metrica", COMBOS)
    def test_pipeline_produces_data(self, raw_df, perspectiva, dimension, metrica):
        result = build_pipeline(raw_df, perspectiva, dimension, metrica)
        assert len(result) > 0
        assert "name" in result.columns
        assert "value" in result.columns
        assert "year" in result.columns
        assert "month" in result.columns

    @pytest.mark.parametrize("perspectiva,dimension,metrica", COMBOS)
    def test_cumsum_non_decreasing(self, raw_df, perspectiva, dimension, metrica):
        """El valor acumulado nunca debe disminuir para una entidad."""
        result = build_pipeline(raw_df, perspectiva, dimension, metrica)
        for name in result["name"].unique()[:5]:  # Probar 5 entidades
            entity = result[result["name"] == name].sort_values(["year", "month"])
            diffs = entity["value"].diff().dropna()
            assert (diffs >= -0.01).all(), f"{name}: cumsum decreció"

    @pytest.mark.parametrize("perspectiva,dimension,metrica", COMBOS)
    def test_json_generation(self, raw_df, perspectiva, dimension, metrica):
        result = build_pipeline(raw_df, perspectiva, dimension, metrica)
        payload = generate_json(result, perspectiva, dimension, metrica)
        serialized = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        parsed = json.loads(serialized)
        assert len(parsed["entities"]) > 0
        assert len(parsed["metadata"]["years"]) > 30
        assert len(parsed["metadata"]["periods"]) > 400
        # Compact JSON size check: < 5MB
        assert len(serialized) < 5 * 1024 * 1024, "JSON exceeds 5MB"

    @pytest.mark.parametrize("perspectiva,dimension,metrica", COMBOS)
    def test_periods_count(self, raw_df, perspectiva, dimension, metrica):
        """Should have ~506 periods (1984-2025 full + 2026 partial)."""
        result = build_pipeline(raw_df, perspectiva, dimension, metrica)
        periods = result[["year", "month"]].drop_duplicates()
        assert len(periods) > 400  # At least 400 monthly periods

    def test_destinos_have_continents(self, raw_df):
        result = build_pipeline(raw_df, "emisivo", "destinos", "pasajeros")
        assert "continent" in result.columns
        assert "América" in result["continent"].values

    def test_aerolinea_no_continent(self, raw_df):
        result = build_pipeline(raw_df, "emisivo", "aerolinea", "pasajeros")
        assert "continent" not in result.columns

    def test_miami_in_top_emisivo(self, raw_df):
        """MIAMI debería ser uno de los destinos emisivos principales."""
        result = build_pipeline(raw_df, "emisivo", "destinos", "pasajeros")
        last_year = result["year"].max()
        last_month = result[result["year"] == last_year]["month"].max()
        top = result[(result["year"] == last_year) & (result["month"] == last_month)].nlargest(10, "value")
        assert "MIAMI" in top["name"].values
