"""Tests para el módulo extract."""

import pandas as pd
import pytest

from src.etl.extract import _find_year_column, normalize


def _make_raw_df(n_rows=5, years=None, months=None, carga_ton_values=None):
    """Crea un DataFrame que simula datos crudos de la JAC."""
    if years is None:
        years = [2020] * n_rows
    if months is None:
        months = [1] * n_rows
    if carga_ton_values is None:
        carga_ton_values = ["100.5"] * n_rows
    return pd.DataFrame({
        "Año": years,
        "Mes": months,
        "Cod_Operador": ["OP1"] * n_rows,
        "Operador": ["TEST AIR"] * n_rows,
        "Grupo": ["TEST GROUP"] * n_rows,
        "ORIG_1": ["SCL"] * n_rows,
        "DEST_1": ["MIA"] * n_rows,
        "ORIG_1_N": ["SANTIAGO"] * n_rows,
        "DEST_1_N": ["MIAMI"] * n_rows,
        "ORIG_1_PAIS": ["CHILE"] * n_rows,
        "DEST_1_PAIS": ["ESTADOS UNIDOS"] * n_rows,
        "ORIG_2": [None] * n_rows,
        "DEST_2": [None] * n_rows,
        "ORIG_2_N": [None] * n_rows,
        "DEST_2_N": [None] * n_rows,
        "ORIG_2_PAIS": [None] * n_rows,
        "DEST_2_PAIS": [None] * n_rows,
        "OPER_2": ["SALEN"] * n_rows,
        "NAC": ["INTERNACIONAL"] * n_rows,
        "PAX_LIB": [10.0] * n_rows,
        "PASAJEROS": [100.0] * n_rows,
        "CAR_LIB": [5000] * n_rows,
        "CARGA (Ton)": carga_ton_values,
        "CORREO": [0] * n_rows,
        "Distancia": [1000.0] * n_rows,
    })


class TestFindYearColumn:
    def test_standard_name(self):
        df = pd.DataFrame({"Año": [1], "B": [2]})
        assert _find_year_column(df) == "Año"

    def test_ascii_variant(self):
        df = pd.DataFrame({"Ano": [1], "B": [2]})
        assert _find_year_column(df) == "Ano"

    def test_missing_raises(self):
        df = pd.DataFrame({"Year": [1], "B": [2]})
        with pytest.raises(ValueError, match="columna de año"):
            _find_year_column(df)


class TestNormalize:
    def test_year_renamed(self):
        df = _make_raw_df()
        result = normalize(df)
        assert "year" in result.columns
        assert "Año" not in result.columns

    def test_month_renamed(self):
        df = _make_raw_df()
        result = normalize(df)
        assert "month" in result.columns
        assert "Mes" not in result.columns

    def test_carga_ton_comma_conversion(self):
        """CARGA (Ton) con comas decimales (post-2022) se convierte correctamente."""
        df = _make_raw_df(
            n_rows=3,
            years=[2023, 2023, 2023],
            carga_ton_values=["1234,56", "789,01", "0"],
        )
        result = normalize(df)
        assert "CARGA_TON" in result.columns
        assert abs(result["CARGA_TON"].iloc[0] - 1234.56) < 0.01
        assert abs(result["CARGA_TON"].iloc[1] - 789.01) < 0.01

    def test_pasajeros_are_integers(self):
        df = _make_raw_df()
        df["PAX_LIB"] = [10.7, 20.3, 30.0, 40.5, 50.1]
        df["PASAJEROS"] = [100.9, 200.1, 300.0, 400.4, 500.6]
        result = normalize(df)
        assert result["PAX_LIB"].dtype in [int, "int64", "int32"]
        assert result["PASAJEROS"].dtype in [int, "int64", "int32"]

    def test_pasajeros_total(self):
        df = _make_raw_df()
        result = normalize(df)
        expected = result["PAX_LIB"] + result["PASAJEROS"]
        assert (result["PASAJEROS_TOTAL"] == expected).all()

    def test_carga_total_formula(self):
        """CARGA_TOTAL = (CAR_LIB / 1000) + CARGA_TON."""
        df = _make_raw_df(
            n_rows=1, years=[2023], carga_ton_values=["50.0"],
        )
        df["CAR_LIB"] = [2000]
        result = normalize(df)
        # 2000/1000 + 50.0 = 52.0
        assert abs(result["CARGA_TOTAL"].iloc[0] - 52.0) < 0.01

    def test_carga_ton_nan_filled_with_zero_post2022(self):
        """Post-2022: valores inválidos de CARGA (Ton) se llenan con 0."""
        df = _make_raw_df(n_rows=2, years=[2023, 2023], carga_ton_values=["abc", ""])
        result = normalize(df)
        assert (result["CARGA_TON"] == 0).all()

    def test_carga_ton_nan_filled_with_zero_pre2022(self):
        """Pre-2022: valores inválidos de CARGA (Ton) se llenan con 0."""
        df = _make_raw_df(n_rows=2, years=[2020, 2020], carga_ton_values=["abc", ""])
        result = normalize(df)
        assert (result["CARGA_TON"] == 0).all()

    def test_chilean_format_pasajeros_pre2022(self):
        """Pre-2022: punto como separador de miles en PASAJEROS."""
        df = _make_raw_df(n_rows=2, years=[2019, 2019])
        df["PASAJEROS"] = ["16.716", "1.234"]
        result = normalize(df)
        assert result["PASAJEROS"].iloc[0] == 16716
        assert result["PASAJEROS"].iloc[1] == 1234

    def test_chilean_format_carga_pre2022(self):
        """Pre-2022: punto como separador de miles en CARGA (Ton)."""
        df = _make_raw_df(
            n_rows=2, years=[2019, 2019], carga_ton_values=["1.276", "500"],
        )
        result = normalize(df)
        assert result["CARGA_TON"].iloc[0] == 1276
        assert result["CARGA_TON"].iloc[1] == 500

    def test_post2022_pasajeros_unchanged(self):
        """Post-2022: PASAJEROS ya son enteros planos."""
        df = _make_raw_df(n_rows=2, years=[2023, 2023])
        df["PASAJEROS"] = ["14597", "8320"]
        result = normalize(df)
        assert result["PASAJEROS"].iloc[0] == 14597
        assert result["PASAJEROS"].iloc[1] == 8320
