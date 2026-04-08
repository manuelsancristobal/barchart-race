# Bar Chart Race — ETL Aéreo JAC Chile

Este proyecto comenzó el año 2024, por esa fecha estaban de moda algunas paginas de Youtube que mostraban avances comparativos entre el PIB de algunos países o participación de mercado de algunas marcas. Por esa epoca estaba aprendiendo Python y usaba Google Colab para modificar codigo que encontraba por ahí. La primera versión que me dejó orgulloso me costo una semana de trabajo despues de mi jornada laboral, el producto es lo que puedes ver en los notebooks de jupyter de este repositorio. que se basaba en mis dudas y en lo que encontraba en Stack Overflow.


Dos años después he aprendido un par de trucos, y sumado a que comencé a usar D3.js para visualizaciones interactivas, decidí reconstruir el proyecto desde cero con un ETL modular en Python y una visualización web desplegada en Jekyll.

Este repositorio contiene el sistema ETL (Extract, Transform, Load) para procesar los datos de tráfico aéreo internacional de la Junta de Aeronáutica Civil (JAC) de Chile y generar las visualizaciones interactivas de "Bar Chart Race" desplegadas en [manuelsancristobal.github.io](https://manuelsancristobal.github.io/proyectos/barchart-race/).

## Decisiones de Diseño e Implementación

- **Lógica de Ranking Acumulado**: La visualización utiliza sumas acumuladas (`cumsum`) para representar el crecimiento histórico. Si un destino o aerolínea registra 0 movimiento *nuevo* en un año específico, el sistema rellena internamente con 0 para mantener su valor acumulado anterior. Esto permite que las barras permanezcan en el ranking basándose únicamente en su total acumulado, asegurando una transición suave y coherente con el crecimiento histórico.
- **Mapeo Consistente**: Se aplica el último mapeo conocido (continente o grupo corporativo) a toda la serie histórica de cada entidad. Esto evita que una barra cambie de color o categoría si el mapeo se actualiza o si la entidad cambia de nombre/operador en el tiempo.
- **Sincronización Inteligente de UI**: Al cambiar entre perspectivas o dimensiones, el sistema intenta mantener el año actual en el slider. Solo se reseteará al inicio de la serie si el año seleccionado no existe en el nuevo conjunto de datos.
- **Animación Fluida con Granularidad Mensual**: Los datos se agregan por año+mes (~506 frames) y se animan a ~80ms por frame, logrando transiciones graduales que revelan patrones estacionales reales. El slider mantiene granularidad anual (43 posiciones) y la animación recorre los meses internamente.
- **JSON Compacto**: Formato indexado por entidad con un array de valores alineado a periodos compartidos (`periods`, `year_ranges`, `entities[].values`). Reduce el tamaño de ~11 MB a ~4.6 MB total para los 8 archivos.
- **Automatización del Despliegue**: El script `src/deploy.py` automatiza la copia de los archivos JSON y las anotaciones hacia el repositorio local de Jekyll. El usuario debe realizar el `git push` manualmente.
- **Flujo de Trabajo Iterativo**: El ETL genera un reporte de **países no mapeados** (`data/work/unmapped_countries.txt`) para revisión y corrección manual durante el desarrollo.

## Pendientes y Validaciones

- [x] **Validación de Carga**: Se confirmó que `CAR_LIB` está en Kilos y `CARGA_TON` en Toneladas. La fórmula final es `CARGA_TOTAL = (CAR_LIB / 1000) + CARGA_TON`.
- [x] **Mapeo de Aerolíneas**: Se usa la columna `Grupo` existente en los datos JAC directamente (sin archivo de mapeo externo). Si `Grupo` está vacío, se usa el nombre del operador como fallback.

## Inicio Rapido

```bash
python run.py              # Ver todos los comandos disponibles
python run.py etl          # Genera los 8 JSONs desde datos locales
python run.py etl --remote # Descarga datos frescos y ejecuta ETL
python run.py charts       # Genera graficos de analisis (PNGs)
python run.py ver          # Abre la visualizacion en el navegador
python run.py test         # Ejecuta tests + linting
python run.py deploy       # Copia archivos al repo Jekyll
python run.py all          # Pipeline completo: etl -> charts -> deploy
```

## Modo de Uso (detalle)

### Requisitos

- Python 3.10+
- Datos JAC en `data/raw/jac_data.csv`

### Instalación

```bash
python -m venv .venv
source .venv/Scripts/activate   # Windows (Git Bash)
# source .venv/bin/activate     # Linux / macOS
pip install -e ".[dev]"
```

### Ejecutar el ETL

```bash
# Genera los 8 JSONs en data/processed/ usando el CSV local
python -m src.main

# O descarga datos frescos desde Google Sheets antes de procesar
python -m src.main --remote
```

Las 8 combinaciones generadas son:

| Perspectiva | Dimensión | Métrica |
|-------------|-----------|---------|
| Emisivo | Destinos | Pasajeros |
| Emisivo | Destinos | Tonelaje |
| Emisivo | Aerolínea | Pasajeros |
| Emisivo | Aerolínea | Tonelaje |
| Receptivo | Destinos | Pasajeros |
| Receptivo | Destinos | Tonelaje |
| Receptivo | Aerolínea | Pasajeros |
| Receptivo | Aerolínea | Tonelaje |

### Ejecutar tests y linting

```bash
python -m pytest tests/ -v
ruff check src/ scripts/ tests/
```

### Generar gráficos de análisis

```bash
python scripts/analyze_traffic.py
```

Genera 7 PNGs + `captions.json` en `viz/assets/charts/`.

### Visualizar localmente

```bash
python -m http.server 8000 --bind 127.0.0.1
# Serving HTTP on 127.0.0.1 port 8000 (http://127.0.0.1:8000/) ...
```

Abrir en el navegador: `http://localhost:8000/viz/index.html`

- **Play**: recorre los ~506 frames mensuales (~80ms por frame)
- **Slider**: salta por año (43 posiciones); la animación arranca desde el primer mes del año seleccionado
- **Toggles**: 8 combinaciones de perspectiva × dimensión × métrica

### Copiar al repo Jekyll

```bash
# Opcionalmente configurar la ruta al repo Jekyll (por defecto ~/OneDrive/Documentos/manuelsancristobal.github.io)
export JEKYLL_REPO="/ruta/al/repo/jekyll"

python -m src.deploy
```

Copia datos, charts, HTML, CSS y JS al repo Jekyll local. El `git push` se realiza manualmente.

### Inspeccionar datos crudos

```bash
python scripts/inspect_data.py
```

Muestra sumas de pasajeros y carga por año para verificar la integridad de los datos.

## Estructura del Proyecto

```
Barchart-race/
├── data/
│   ├── raw/                 # CSV JAC (.gitignore)
│   ├── processed/           # JSONs generados por el ETL
│   ├── annotations/         # Anotaciones cualitativas por combinación
│   ├── reference/           # continent_mapping.csv
│   └── work/                # Archivos temporales (.gitignore)
├── scripts/
│   └── inspect_data.py      # Inspección de datos crudos
├── src/
│   ├── config.py            # Constantes, rutas, paleta de colores
│   ├── etl/
│   │   ├── extract.py       # Descarga y normalización
│   │   ├── transform.py     # Filtros, agregación, cumsum, mapeo
│   │   └── load.py          # Generación de JSONs
│   ├── main.py              # Orquestador del ETL
│   └── deploy.py            # Copia al repo Jekyll
├── notebooks/original/      # Notebooks prototipo archivados
├── viz/
│   ├── index.html            # Página de visualización
│   └── assets/
│       ├── css/barchart.css  # Estilos
│       └── js/barchart-race.js # Motor D3.js (animación mensual)
├── tests/                   # 75 tests unitarios + integración
├── PLAN.md                  # Arquitectura y mapa de ruta
├── run.py                   # Punto de entrada unico (python run.py help)
├── CHANGELOG.md             # Evolución del proyecto
└── pyproject.toml           # Metadata, dependencias, config herramientas
```

Consulta el archivo [PLAN.md](PLAN.md) para ver la arquitectura detallada y el mapa de ruta de implementación.
