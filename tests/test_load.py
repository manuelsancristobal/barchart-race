"""Tests para el módulo load."""

import json

import pandas as pd

from src.etl.load import generate_json


def _make_processed_df():
    return pd.DataFrame({
        "name": ["MIAMI", "MIAMI", "MIAMI", "MIAMI",
                 "BUENOS AIRES", "BUENOS AIRES", "BUENOS AIRES", "BUENOS AIRES"],
        "group": ["ESTADOS UNIDOS"] * 4 + ["ARGENTINA"] * 4,
        "continent": ["América"] * 8,
        "year": [2020, 2020, 2021, 2021, 2020, 2020, 2021, 2021],
        "month": [1, 2, 1, 2, 1, 2, 1, 2],
        "value": [500.0, 1000.0, 1500.0, 2500.0, 300.0, 800.0, 1200.0, 1900.0],
    })


class TestGenerateJson:
    def test_structure_destinos(self):
        df = _make_processed_df()
        result = generate_json(df, "emisivo", "destinos", "pasajeros")
        assert "metadata" in result
        assert "color_map" in result
        assert "entities" in result
        assert result["metadata"]["perspectiva"] == "emisivo"
        assert result["metadata"]["dimension"] == "destinos"
        assert result["metadata"]["metrica"] == "pasajeros"
        assert result["metadata"]["years"] == [2020, 2021]
        assert result["color_map"] is not None

    def test_has_periods(self):
        df = _make_processed_df()
        result = generate_json(df, "emisivo", "destinos", "pasajeros")
        assert "periods" in result["metadata"]
        assert result["metadata"]["periods"] == [[2020, 1], [2020, 2], [2021, 1], [2021, 2]]

    def test_has_year_ranges(self):
        df = _make_processed_df()
        result = generate_json(df, "emisivo", "destinos", "pasajeros")
        yr = result["metadata"]["year_ranges"]
        assert yr["2020"] == [0, 1]
        assert yr["2021"] == [2, 3]

    def test_entities_have_values_array(self):
        df = _make_processed_df()
        result = generate_json(df, "emisivo", "destinos", "pasajeros")
        assert len(result["entities"]) == 2  # MIAMI and BUENOS AIRES
        miami = [e for e in result["entities"] if e["name"] == "MIAMI"][0]
        assert "values" in miami
        assert len(miami["values"]) == 4  # 4 periods
        assert miami["values"] == [500.0, 1000.0, 1500.0, 2500.0]

    def test_structure_aerolinea(self):
        df = pd.DataFrame({
            "name": ["LATAM", "LATAM"],
            "group": [None, None],
            "year": [2020, 2021],
            "month": [1, 1],
            "value": [5000.0, 12000.0],
        })
        result = generate_json(df, "emisivo", "aerolinea", "pasajeros")
        assert result["color_map"] is None

    def test_json_serializable(self):
        df = _make_processed_df()
        result = generate_json(df, "emisivo", "destinos", "pasajeros")
        serialized = json.dumps(result, ensure_ascii=False)
        assert len(serialized) > 0

    def test_years_are_ints(self):
        df = _make_processed_df()
        result = generate_json(df, "emisivo", "destinos", "pasajeros")
        for y in result["metadata"]["years"]:
            assert isinstance(y, int)
        for period in result["metadata"]["periods"]:
            assert isinstance(period[0], int)
            assert isinstance(period[1], int)
