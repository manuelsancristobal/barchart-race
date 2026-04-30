# Changelog

En este archivo puedes encontrar todos los cambios notables de este proyecto.
Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/).

## [Unreleased]

## [4.4.0] - 2026-04-16

### Añadido
- `jekyll/barchart-race.md`: copia del markdown del proyecto, ahora versionado en este repo.
- `config.py`: nuevas constantes `JEKYLL_PROJECT_MD` y `JEKYLL_PROJECTS_DIR`.
- `deploy.py`: nuevo paso que copia `jekyll/barchart-race.md` → `{JEKYLL_REPO}/_projects/barchart-race.md`.

### Cambiado
- Unificación del markdown del proyecto: El repo `barchart-race` pasa a ser la fuente única de verdad para todo el proyecto (ETL, visualización, gráficos y análisis escrito). El repo Jekyll queda como vitrina que consume lo que produce `deploy.py`.

## [4.3.0] - 2026-04-08

### Corregido
- `_projects/barchart-race.md`: bloque `<div><iframe>` envuelto en delimitadores `{::nomarkdown}` / `{:/nomarkdown}` para evitar que Kramdown (Jekyll) elimine el tag iframe.

## [4.2.0] - 2026-04-08

### Corregido
- Solución a conflicto de rutas en Jekyll: `config.py` actualiza `JEKYLL_PAGE` de `index.html` → `viz.html`.
- `_projects/barchart-race.md`: embebe la visualización via `<iframe src="./viz.html">`, corregido `github_url` al repo correcto.

## [4.1.0] - 2026-04-07

### Corregido
- Formato numérico chileno en datos pre-2022: `extract.py` incluye nueva función `_parse_chilean_int()` para corregir subreporte de pasajeros (~35x) y carga (~1.8x).
- `load_raw()`: fuerza lectura de PASAJEROS como string.
- `normalize()`: lógica condicional por año para PASAJEROS y CARGA.
- Tests actualizados: 4 tests nuevos para formato chileno y fixtures corregidos.

## [4.0.0] - 2025-01-03

### Añadido
- `run.py` como punto de entrada único con subcomandos (`etl`, `charts`, `ver`, `test`, `deploy`, `all`).
- Migración de `requirements.txt` a `pyproject.toml` (PEP 621).
- Type hints (`from __future__ import annotations`) en todos los módulos de `src/`.
- Accesibilidad HTML: `<label>` para slider, `aria-pressed` en toggles, `role="img"`, `alt` descriptivos.
- CSS: custom properties (`:root`) y clase `.sr-only`.

### Cambiado
- Eliminación de `openpyxl` (dependencia no utilizada).
- `JEKYLL_REPO` configurable vía variable de entorno.
- `conftest.py`: eliminado `sys.path.insert` hack (reemplazado por `pythonpath` en pyproject.toml).

## [3.0.0] - 2025-01-02

### Añadido
- Integración de página única en Jekyll: visualización interactiva + 7 gráficos analíticos estáticos.
- `deploy.py` extendido: copia de HTML, CSS, JS, charts y datos JSON al repo Jekyll.
- `barchart.css`: nuevos estilos `.analysis-*` para la sección analítica.

### Cambiado
- `barchart-race.js`: `DATA_BASE` y `ANNOTATION_BASE` apuntan a `assets/data/`.
- `config.py`: nuevas constantes para directorios de Jekyll y archivos de visualización.

## [2.0.0] - 2025-01-01

### Añadido
- Granularidad mensual (~506 frames) para transiciones más fluidas, revelando patrones estacionales.
- Nuevo formato JSON compacto indexado por entidad para minimizar tamaño (~4 MB total vs 11 MB previo).

### Cambiado
- `extract.py` y `transform.py`: agregación y cumsum por `[year, month]`.
- `barchart-race.js`: motor de animación basado en `periodIndex`.

## [1.0.0] - 2024-01-02

### Añadido
- Sistema modular Python (extract → transform → load).
- Visualización web interactiva con D3.js en Jekyll.
- 8 combinaciones de visualización (2×2×2).
- Mapeo de continentes corregido y externalizado.
- 62 tests automatizados.

### Cambiado
- Aerolíneas agrupadas por Grupo corporativo.

### Corregido
- Normalización de nombres de países y formatos numéricos en `CARGA (Ton)`.

## [0.1.0] - 2024-01-01

### Añadido
- Prototipos en Jupyter Notebook (Google Colab).
- Visualizaciones de destinos emisivos y movimiento neto.
- Output de archivos GIF estáticos.
