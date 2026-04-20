import pandas as pd


def inspect_jac_consistency():
    print("Cargando datos...")
    df = pd.read_csv("data/raw/jac_data.csv", low_memory=False)

    # Solo CARGA (Ton) necesita limpieza: comas decimales en años 2022-2026
    # CAR_LIB ya es int64, PAX_LIB y PASAJEROS ya son float64
    df["CARGA_TON_VAL"] = pd.to_numeric(df["CARGA (Ton)"].astype(str).str.replace(",", "."), errors="coerce").fillna(0)

    for year in [1984, 2022, 2024, 2026]:
        df_year = df[df["Año"] == year]
        if df_year.empty:
            print(f"\n--- AÑO {year} --- (sin datos)")
            continue
        print(f"\n--- AÑO {year} ---")
        print(f"Suma CAR_LIB:       {df_year['CAR_LIB'].sum():,.2f}")
        print(f"Suma CARGA (Ton):    {df_year['CARGA_TON_VAL'].sum():,.2f}")
        print(f"Suma PAX_LIB:       {df_year['PAX_LIB'].sum():,.0f}")
        print(f"Suma PASAJEROS:     {df_year['PASAJEROS'].sum():,.0f}")

    print("\n--- EJEMPLO POR FILA (2024) ---")
    row = df[(df["Año"] == 2024) & (df["CAR_LIB"] > 0)].head(1)
    if not row.empty:
        print(f"Fila 2024: {row['Operador'].values[0]}")
        print(f"CAR_LIB:   {row['CAR_LIB'].values[0]}")
        print(f"CARGA_TON: {row['CARGA_TON_VAL'].values[0]}")
        print(f"PAX_LIB:   {row['PAX_LIB'].values[0]}")
        print(f"PASAJEROS: {row['PASAJEROS'].values[0]}")


if __name__ == "__main__":
    inspect_jac_consistency()
