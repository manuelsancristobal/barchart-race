# Barchart Race - Tráfico Aéreo Internacional Chile

## Contexto
Este proyecto nació en el año 2024, por esa época estaban de moda las animaciones de carreras de gráficos donde mostraban el avance del PIB de los países, facturación de marcas, tamaño de población, esas cosas.

## Impacto y Valor del Proyecto
Esta herramienta te proporciona una dinámica visual de la evolución del mercado aéreo internacional en Chile durante las últimas décadas. Al transformar datos estadísticos de la JAC en visualizaciones "Race" interactivas, te permite identificar, de forma rápida, el ascenso de nuevas aerolíneas, la consolidación de hubs regionales y el impacto de eventos disruptivos globales.

## Stack Tecnológico
- **Lenguaje**: Python 3.10+
- **Librerías Clave**: `Pandas` (ETL), `Numpy`, `Matplotlib`.
- **Frontend**: D3.js (Animaciones dinámicas), HTML5/CSS3.
- **Calidad de Código**: `Ruff`, `Pytest`.
- **CI/CD**: GitHub Actions.

## Arquitectura de Datos y Metodología
1. **Pipeline ETL**: Limpieza masiva de datos históricos de la JAC, normalización de nombres de operadores y países.
2. **Enriquecimiento**: Mapeo geográfico de países a continentes para análisis agregado.
3. **Generación de Frames**: Cálculo de rankings acumulados mensuales para 8 combinaciones de métricas (Pasajeros/Carga x Aerolínea/Destino).
4. **Visualización**: Renderizado dinámico con D3.js, permitiéndote el cambio de perspectiva en tiempo real.

## Quick Start (Reproducibilidad)
1. `git clone https://github.com/manuelsancristobal/barchart-race`
2. `pip install -e .` (Instala dependencias)
3. `make test` (Ejecuta validaciones)
4. `python run.py etl` (Procesa los datos desde Google Sheets o local)
5. `python run.py ver` (Visualiza el Barchart Race)

## Estructura del Proyecto
- `src/`: Core del pipeline ETL y configuración de mapeos.
- `data/`: Estructura estándar (`raw/`, `processed/`, `external/`, `annotations/`).
- `viz/`: Visualización interactiva D3.js.
- `scripts/`: Utilidades de inspección y análisis rápido.

---
**Autor**: Manuel San Cristóbal Opazo 
**Licencia**: MIT
