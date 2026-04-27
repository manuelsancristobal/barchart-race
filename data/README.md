# Datos: Barchart Race Tráfico Aéreo

## Origen
- **Tráfico Aéreo Internacional**: JAC (Junta de Aeronáutica Civil, Chile).
- **Fuente**: Datos públicos de transporte aéreo comercial.
- **Mapeo de Continentes**: Archivo de referencia interno.

## Estructura
- `raw/`: Datos originales en CSV y listas de países no mapeados.
- `processed/`: Archivos JSON generados para la visualización D3.js (series temporales por aerolínea y destino).
- `external/`: `continent_mapping.csv` para la clasificación geográfica.
- `annotations/`: Metadata para eventos específicos en la animación (hitos históricos, cambios de mercado).

## Diccionario de Datos Clave
- `PASAJEROS`: Cantidad de pasajeros transportados.
- `CARGA (Ton)`: Tonelaje de carga.
- `PAIS`: País de origen/destino internacional.
