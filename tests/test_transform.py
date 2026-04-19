"""Tests para el módulo transform."""

import pandas as pd
import pytest

from src.etl.transform import (
    aggregate,
    apply_continent_mapping,
    build_pipeline,
    compute_cumulative,
    filter_by_perspectiva,
    filter_international,
)


def _make_normalized_df():
    """DataFrame normalizado con datos mínimos para probar transform."""
    return pd.DataFrame(
        {
            "year": [2020, 2020, 2021, 2021, 2020, 2020],
            "month": [1, 1, 1, 1, 1, 1],
            "NAC": ["INTERNACIONAL"] * 4 + ["NACIONAL", "INTERNACIONAL"],
            "OPER_2": ["SALEN", "SALEN", "SALEN", "LLEGAN", "SALEN", "LLEGAN"],
            "ORIG_1_PAIS": ["CHILE", "CHILE", "CHILE", "ARGENTINA", "CHILE", "ESTADOS UNIDOS"],
            "DEST_1_PAIS": ["ARGENTINA", "BRASIL", "ARGENTINA", "CHILE", "SANTIAGO", "CHILE"],
            "ORIG_1_N": ["SANTIAGO", "SANTIAGO", "SANTIAGO", "BUENOS AIRES", "SANTIAGO", "MIAMI"],
            "DEST_1_N": ["BUENOS AIRES", "SAO PAULO", "BUENOS AIRES", "SANTIAGO", "TEMUCO", "SANTIAGO"],
            "Grupo": ["LATAM", "GOL", "LATAM", "AEROLINEAS ARGENTINAS", "LATAM", "AMERICAN AIRLINES"],
            "PASAJEROS_TOTAL": [1000, 500, 800, 300, 200, 400],
            "CARGA_TOTAL": [10.0, 5.0, 8.0, 3.0, 2.0, 4.0],
        }
    )


class TestFilterInternational:
    def test_only_international(self):
        df = _make_normalized_df()
        result = filter_international(df)
        assert (result["NAC"] == "INTERNACIONAL").all()
        assert len(result) == 5

    def test_removes_national(self):
        df = _make_normalized_df()
        result = filter_international(df)
        assert "NACIONAL" not in result["NAC"].values


class TestFilterByPerspectiva:
    def test_emisivo(self):
        df = filter_international(_make_normalized_df())
        result = filter_by_perspectiva(df, "emisivo")
        assert (result["ORIG_1_PAIS"] == "CHILE").all()
        assert (result["OPER_2"] == "SALEN").all()

    def test_receptivo(self):
        df = filter_international(_make_normalized_df())
        result = filter_by_perspectiva(df, "receptivo")
        assert (result["DEST_1_PAIS"] == "CHILE").all()
        assert (result["OPER_2"] == "LLEGAN").all()

    def test_invalid_raises(self):
        df = _make_normalized_df()
        with pytest.raises(ValueError, match="inválida"):
            filter_by_perspectiva(df, "neto")


class TestAggregate:
    def test_destinos_emisivo(self):
        df = filter_international(_make_normalized_df())
        df = filter_by_perspectiva(df, "emisivo")
        result = aggregate(df, "emisivo", "destinos", "pasajeros")
        assert "name" in result.columns
        assert "group" in result.columns
        assert "value" in result.columns
        assert "month" in result.columns
        # BUENOS AIRES en 2020-m1 = 1000
        ba = result[(result["name"] == "BUENOS AIRES") & (result["year"] == 2020) & (result["month"] == 1)]
        assert ba["value"].iloc[0] == 1000

    def test_aerolinea_emisivo(self):
        df = filter_international(_make_normalized_df())
        df = filter_by_perspectiva(df, "emisivo")
        result = aggregate(df, "emisivo", "aerolinea", "pasajeros")
        assert "name" in result.columns
        latam = result[(result["name"] == "LATAM") & (result["year"] == 2020)]
        assert latam["value"].iloc[0] == 1000

    def test_tonelaje(self):
        df = filter_international(_make_normalized_df())
        df = filter_by_perspectiva(df, "emisivo")
        result = aggregate(df, "emisivo", "destinos", "tonelaje")
        ba = result[(result["name"] == "BUENOS AIRES") & (result["year"] == 2020)]
        assert abs(ba["value"].iloc[0] - 10.0) < 0.01


class TestComputeCumulative:
    def test_cumsum_across_months(self):
        """Cumsum works across months within the same year."""
        df = pd.DataFrame(
            {
                "name": ["A", "A", "A"],
                "group": ["G1", "G1", "G1"],
                "year": [2020, 2020, 2020],
                "month": [1, 2, 3],
                "value": [100, 200, 50],
            }
        )
        result = compute_cumulative(df)
        a_m3 = result[(result["name"] == "A") & (result["year"] == 2020) & (result["month"] == 3)]
        assert a_m3["value"].iloc[0] == 350  # 100 + 200 + 50

    def test_cumsum_across_years(self):
        df = pd.DataFrame(
            {
                "name": ["A", "A", "B", "B"],
                "group": ["G1", "G1", "G2", "G2"],
                "year": [2020, 2021, 2020, 2021],
                "month": [1, 1, 1, 1],
                "value": [100, 200, 50, 30],
            }
        )
        result = compute_cumulative(df)
        a_2021 = result[(result["name"] == "A") & (result["year"] == 2021)]
        assert a_2021["value"].iloc[0] == 300  # 100 + 200

    def test_fills_missing_periods(self):
        """If an entity has no data in a period, it is filled with 0 and keeps cumulative."""
        df = pd.DataFrame(
            {
                "name": ["A", "A", "B"],
                "group": ["G1", "G1", "G2"],
                "year": [2020, 2021, 2020],
                "month": [1, 1, 1],
                "value": [100, 200, 50],
            }
        )
        result = compute_cumulative(df)
        # B should have entry for 2021-m1 with value = 50 (keeps cumulative)
        b_2021 = result[(result["name"] == "B") & (result["year"] == 2021)]
        assert len(b_2021) == 1
        assert b_2021["value"].iloc[0] == 50


class TestApplyContinentMapping:
    def test_known_countries(self):
        df = pd.DataFrame(
            {
                "name": ["MIAMI", "BUENOS AIRES"],
                "group": ["ESTADOS UNIDOS", "ARGENTINA"],
                "year": [2020, 2020],
                "value": [100, 200],
            }
        )
        result = apply_continent_mapping(df)
        assert (result["continent"] == "América").all()

    def test_unknown_country_gets_otro(self):
        df = pd.DataFrame(
            {
                "name": ["CITY_X"],
                "group": ["PAIS_INVENTADO"],
                "year": [2020],
                "value": [100],
            }
        )
        result = apply_continent_mapping(df)
        assert result["continent"].iloc[0] == "Otro"

    def test_normalizes_spaces(self):
        """EMI. ARABES UNIDOS y EMI.ARABES UNIDOS deben mapearse igual."""
        df = pd.DataFrame(
            {
                "name": ["DUBAI", "ABU DHABI"],
                "group": ["EMI. ARABES UNIDOS", "EMI.ARABES UNIDOS"],
                "year": [2020, 2020],
                "value": [100, 200],
            }
        )
        result = apply_continent_mapping(df)
        assert (result["continent"] == "Medio Oriente").all()


class TestBuildPipeline:
    def test_full_pipeline_emisivo_destinos_pasajeros(self):
        df = _make_normalized_df()
        result = build_pipeline(df, "emisivo", "destinos", "pasajeros")
        assert "name" in result.columns
        assert "continent" in result.columns
        assert "value" in result.columns
        assert len(result) > 0
        # Values must be cumulative: BA 2020-m1 = 1000, 2021-m1 = 1800
        ba_2021 = result[(result["name"] == "BUENOS AIRES") & (result["year"] == 2021)]
        assert ba_2021["value"].iloc[0] == 1800  # 1000 + 800

    def test_full_pipeline_aerolinea(self):
        df = _make_normalized_df()
        result = build_pipeline(df, "emisivo", "aerolinea", "pasajeros")
        assert "continent" not in result.columns
        latam_2021 = result[(result["name"] == "LATAM") & (result["year"] == 2021)]
        assert latam_2021["value"].iloc[0] == 1800  # 1000 + 800

    def test_full_pipeline_receptivo(self):
        df = _make_normalized_df()
        result = build_pipeline(df, "receptivo", "destinos", "pasajeros")
        assert len(result) > 0
        names = result["name"].unique()
        assert "BUENOS AIRES" in names or "MIAMI" in names
