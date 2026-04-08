# Evolución del Proyecto

## v4.2 — Fix: visualización no visible en Jekyll por conflicto de rutas

### Problema
Jekyll's `_projects` collection genera `proyectos/barchart-race/index.html` desde `barchart-race.md`, sobreescribiendo el `index.html` estático de la visualización D3.js que copia `deploy.py`. El resultado: los visitantes ven la página descriptiva del proyecto en vez de la visualización.

### Corrección
- `config.py`: `JEKYLL_PAGE` cambiado de `index.html` → `viz.html`
- `deploy.py`: log message actualizado para reflejar el nuevo nombre
- Jekyll: `index.html` renombrado a `viz.html` en `proyectos/barchart-race/`
- `_projects/barchart-race.md`: embebe la visualización via `<iframe src="./viz.html">`, corregido `github_url` al repo correcto

### Decisión de diseño
Iframe embedding permite que Jekyll gestione la página del proyecto (layout, navegación, metadata) mientras la visualización D3.js vive en su propio documento sin conflicto de rutas.

## v4.1 — Fix: formato numérico chileno en datos pre-2022

### Problema
El CSV de la JAC usa formato numérico chileno (punto como separador de miles) en datos anteriores a 2022. Pandas interpretaba el punto como separador decimal, causando subreporte de ~35x en pasajeros y ~1.8x en carga pre-2022. Esto generaba un salto artificial enorme al llegar a 2022 en la visualización.

### Corrección
- `extract.py`: nueva función `_parse_chilean_int()` para parsear formato chileno (punto = miles)
- `load_raw()`: fuerza lectura de PASAJEROS como string (`dtype={"PASAJEROS": str}`)
- `normalize()`: lógica condicional por año para PASAJEROS y CARGA (Ton):
  - Pre-2022: quita puntos (separador de miles) y parsea como entero
  - Post-2022: mantiene lógica existente (enteros planos / coma decimal)
- Tests actualizados: fixtures usan año correcto para cada formato; 4 tests nuevos para formato chileno

### Impacto en datos
- PASAJEROS 2019: 315K → 26.3M (correcto)
- CARGA 2021: 231K → 461K (correcto)
- Transición 2021→2022 suave (1.82x por recuperación COVID, no 35x artificial)

## v4 — Profesionalización: pyproject.toml, type hints, accesibilidad

### Decisiones de diseño
- `run.py` como punto de entrada unico: reemplaza la necesidad de recordar multiples comandos `python -m ...` por un solo script con subcomandos (`etl`, `charts`, `ver`, `test`, `deploy`, `all`). Python puro, sin dependencias externas ni `make`
- Migración de `requirements.txt` a `pyproject.toml` (PEP 621): dependencias pinneadas con rangos mínimos, grupo `[dev]` para pytest y ruff
- Eliminación de `openpyxl` (dependencia fantasma, no se usaba en ningún import)
- `JEKYLL_REPO` configurable vía variable de entorno para portabilidad entre máquinas
- `main.py` con error handling por combinación y exit code para CI/CD

### Cambios técnicos
- Type hints (`from __future__ import annotations`) en todos los módulos de `src/`
- `pyproject.toml` con config de pytest (`pythonpath`, `testpaths`) y ruff (`select`, `target-version`)
- `conftest.py`: eliminado `sys.path.insert` hack (reemplazado por `pythonpath` en pyproject.toml)
- `scripts/analyze_traffic.py`: `sys.path.insert` reemplazado por `from src import config`
- HTML: accesibilidad básica — `<label>` para slider, `aria-pressed` en toggles, `role="img"` en chart, `alt` descriptivos en imágenes
- CSS: colores extraídos a custom properties (`:root` variables), clase `.sr-only` para labels accesibles
- `README.md`: párrafo truncado completado, instalación actualizada a `pip install -e ".[dev]"`

## v3 — Página única: animación + análisis en Jekyll

### Decisiones de diseño
- Una sola URL (`/proyectos/barchart-race/`) integra el bar chart race interactivo arriba y los 7 gráficos analíticos estáticos debajo
- Textos de contexto y hallazgos hardcodeados en HTML (contenido estático, no requiere fetch dinámico)
- Paths de datos relativos al `index.html` de Jekyll (`assets/data/`, `assets/annotations/`) en vez de paths relativos al repo ETL
- Deploy extendido: copia HTML, CSS, JS y charts además de datos JSON

### Cambios técnicos
- `barchart-race.js`: `DATA_BASE` y `ANNOTATION_BASE` apuntan a `assets/data/` y `assets/annotations/`
- `config.py`: `JEKYLL_REPO` corregido a ruta real (`OneDrive/Documentos/`); nuevas constantes `JEKYLL_CHARTS_DIR`, `JEKYLL_CSS_DIR`, `JEKYLL_JS_DIR`, `JEKYLL_PAGE`, `VIZ_DIR`
- `deploy.py`: copia charts (7 PNGs + captions.json), CSS, JS e index.html al repo Jekyll
- `index.html`: sección `.analysis-section` con 7 bloques (título, contexto, imagen, hallazgos)
- `barchart.css`: estilos `.analysis-*` para la sección analítica
- Imágenes con `loading="lazy"` para performance

## v2 — Granularidad mensual y formato JSON compacto

### Decisiones de diseño
- Migración de agregación anual (~43 frames) a mensual (~506 frames) para transiciones más fluidas
- Datos reales mes a mes (no interpolación), revelando patrones estacionales
- JSON compacto indexado por entidad: un array de valores alineado a periodos compartidos
- Slider mantiene granularidad por año (43 posiciones); animación recorre meses internamente
- ~80ms por frame mensual ≈ 1 seg/año ≈ 43 seg totales de animación

### Cambios técnicos
- `extract.py`: rename `Mes` → `month` en normalización
- `transform.py`: agregación y cumsum por `[year, month]` en vez de solo `[year]`
- `load.py`: formato JSON compacto con `periods`, `year_ranges`, y `entities[].values` array
- `barchart-race.js`: motor de animación basado en `periodIndex`, slider por año vía `yearRanges`
- JSON sin indentación (`separators=(",",":")`) para minimizar tamaño

### Resultados
- 8 JSONs generados: 327–865 KB cada uno (~4 MB total vs 11 MB previo)
- 506 periodos mensuales (1984-01 a 2026-02)
- 75 tests automatizados pasando (unitarios + integración)

## v0 — Prototipos en Jupyter Notebook (Google Colab)
- 2 notebooks independientes con ~70% código duplicado
- Solo 2 visualizaciones: destinos emisivos y movimiento neto
- Mapeo de continentes hardcodeado con 3 errores geográficos
- Datos cargados manualmente via upload de Colab
- Output: archivos GIF estáticos

## v1 — Sistema Modular + Visualización Web Interactiva
### Decisiones de diseño
- Aerolíneas agrupadas por Grupo corporativo (columna `Grupo` existente en datos JAC)
- Movimiento neto descartado por ahora — solo datos reales emisivos/receptivos
- Migración de matplotlib GIF a D3.js interactivo en Jekyll
- Labels dinámicos: "Destinos" en emisivo, "Orígenes" en receptivo
- Cumsum (acumulado histórico) para todas las combinaciones
- Desktop primero, móvil funcional sin optimizaciones especiales
- Script de copia automática entre repo ETL y repo Jekyll
- Banner inferior con anotaciones cualitativas generadas con IA y revisadas por el autor
- Datos desde 1984 hasta 2026 (último año puede estar incompleto)

### Cambios técnicos
- ETL modular en Python (extract → transform → load)
- 8 combinaciones de visualización (2×2×2)
- Mapeo de continentes externalizado y corregido
- Descarga automática desde Google Sheets (datos JAC)
- 62 tests automatizados (unitarios + integración con datos reales)
- Reorganización de carpetas: `scripts/`, `notebooks/original/`, `tests/`

### Correcciones de datos
- Belice: Africa → America
- Isla Martinica: Oceania → America
- Isla de Tahiti: Asia → Oceania
- Normalización de nombres duplicados (EMI. ARABES UNIDOS / EMI.ARABES UNIDOS, etc.)
- Normalización de `CARGA (Ton)` con comas decimales (2022-2026)
- Protección contra países no mapeados (categoría "Otro" en vez de crash)
