# Bar Chart Race — ETL Aéreo JAC Chile

Este proyecto comenzó el año 2024, por esa fecha estaban de moda algunas páginas de Youtube que mostraban carreras de gráficos comparativas como el PIB de algunos países, o la participación de mercado de algunas marcas. Por esa época estaba aprendiendo Python y usaba Google Colab para modificar algunos trozos de código que encontraba en gallerias o en StackOverflow.

La primera versión que me dejó orgulloso me costó una semana de desarrollo pos jornada laboral, el producto es el que puedes ver en los notebooks de jupyter de este repositorio.

Dos años después he aprendido un par de trucos, y sumado a la asistencia de Claude, decidí reconstruir el proyecto desde cero, esta vez con una lógica de ETL (Extract, Transform, Load) usando Python y una visualización web desplegada en Jekyll.

Este repositorio contiene un pipeline completo para procesar los datos de tráfico aéreo internacional de la Junta de Aeronáutica Civil (JAC) de Chile y generar visualizaciones interactivas tipo "Bar Chart Race" desplegadas en [manuelsancristobal.github.io](https://manuelsancristobal.github.io/proyectos/barchart-race/).

## Decisiones de Diseño e Implementación

- **Lógica de Ranking Acumulado**: La animación utiliza sumas acumuladas (`cumsum`) para representar el crecimiento histórico. Si un destino o aerolínea registra 0 movimiento *nuevo* en un año específico, el sistema rellena internamente con 0 para mantener su valor acumulado anterior. Esto permite que las barras permanezcan en el ranking basándose únicamente en su total acumulado manteniendo una transición suave.
- **Mapeo Consistente**: Se aplica el último mapeo conocido (continente o grupo corporativo) a toda la serie histórica de cada entidad. Esto evita que una barra cambie de color o categoría si el mapeo se actualiza o si la entidad cambia de nombre/operador en el tiempo.
- **Sincronización Inteligente de UI**: Al cambiar entre perspectivas o dimensiones, el sistema intenta mantener el año actual en el slider. Solo se resetea al inicio de la serie si el año seleccionado no existe entre las perspectivas o dimensiones.
- **Animación Fluida con Granularidad Mensual**: Los datos se agregan por año+mes (~506 frames) y se animan a ~80ms por frame, logrando transiciones graduales. El slider mantiene la anualidad (43 posiciones) y la animación recorre los meses internamente.
- **JSON Compacto**: Este formato contiene un `array` de valores con los periodos compartidos (`periods`, `year_ranges`, `entities[].values`). Este formato reduce el tamaño de ~11 MB a ~4.6 MB total para los 8 archivos.
- **Automatización del Despliegue**: El script `src/deploy.py` automatiza la copia de datos, gráficos, visualización y el markdown del proyecto hacia el repositorio local de Jekyll. El usuario debe realizar el `git push` manualmente.
- **Proyecto Autocontenido**: El markdown del proyecto (`jekyll/barchart-race.md`) con los textos de análisis vive en este repo, no en el repo Jekyll. El deploy lo copia a `_projects/` del repo Jekyll. Así todo el contenido (ETL, visualización, gráficos y análisis escrito) se gestiona desde un solo lugar.
- **Flujo de Trabajo Iterativo**: El pipeline genera un reporte de **países no mapeados** (`data/work/unmapped_countries.txt`) para revisión y corrección manual durante el desarrollo.

## Pendientes y Validaciones

- [x] **Validación de Carga**: Se confirmó que `CAR_LIB` está en Kilos y `CARGA_TON` en Toneladas. La fórmula final es `CARGA_TOTAL = (CAR_LIB / 1000) + CARGA_TON`.
- [x] **Mapeo de Aerolíneas**: Se usa la columna `Grupo` existente en los datos JAC directamente (sin archivo de mapeo externo). Si `Grupo` está vacío, se usa el nombre del operador como fallback.
- [x] **Diferencia de formato**: La BD de la JAC hasta el año 2022 contiene "," como separador de miles, lo que genera un problema al importarse.

## Guía para Principiantes

### ¿Qué es `make`?

`make` es una herramienta que ejecuta comandos predefinidos. En vez de recordar comandos largos, solo escribes `make` seguido de una palabra clave. Para ver todos los comandos disponibles:

```bash
make help
```

### Requisitos Previos

1. **Python 3.10 o superior** — [Descargar aquí](https://www.python.org/downloads/)
2. **Git** — [Descargar aquí](https://git-scm.com/downloads)
3. **Make** — En Windows viene incluido con Git Bash. En macOS/Linux ya está instalado.

### Instalación paso a paso

```bash
# 1. Clonar el repositorio
git clone https://github.com/manuelsancristobal/barchart-race.git
cd barchart-race

# 2. Crear un entorno virtual (aísla las dependencias de este proyecto)
python -m venv .venv

# 3. Activar el entorno virtual
source .venv/Scripts/activate   # Windows (Git Bash)
# source .venv/bin/activate     # Linux / macOS

# 4. Instalar el proyecto y sus dependencias
make install-dev
```

### Comandos principales

Todos los comandos se ejecutan desde la carpeta raíz del proyecto, con el entorno virtual activado.

```bash
make help       # Muestra todos los comandos disponibles
make test       # Ejecuta los tests para verificar que todo funciona
make lint       # Verifica la calidad del código
make assets     # Genera los gráficos de análisis (PNGs)
make deploy     # Copia archivos al repo Jekyll (portafolio web)
make clean      # Elimina archivos temporales
```

### Flujo de trabajo típico

```bash
# 1. Generar los datos procesados (JSONs)
python run.py etl

# 2. Generar los gráficos de análisis
make assets

# 3. Abrir la visualización en el navegador
make ver

# 4. Si modificaste el análisis en jekyll/barchart-race.md:
make deploy     # Copia todo al repo Jekyll
```

### ¿Cómo actualizo el análisis en el portafolio web?

```
Tu proyecto                    Repo Jekyll                   Sitio web
─────────────                  ──────────                    ─────────

jekyll/barchart-race.md ──┐
                          ├─ make deploy ──→  _projects/barchart-race.md
viz/assets/charts/*.png ──┘                  proyectos/barchart-race/assets/
                                                    │
                                              git push ──→  manuelsancristobal.github.io
```

**Para modificar texto de análisis:**

1. Edita `jekyll/barchart-race.md` con los cambios que quieras
2. Ejecuta `make deploy` (copia los archivos al repo Jekyll local)
3. Ve a la carpeta del repo Jekyll (`~/manuelsancristobal.github.io`)
4. Ejecuta `git add . && git commit -m "actualizar análisis" && git push`
5. Espera ~1 minuto y el cambio aparece en tu sitio web

**Para agregar un gráfico nuevo:**

1. Genera el gráfico con `make assets` (el PNG queda en `viz/assets/charts/`)
2. Edita `jekyll/barchart-race.md` y agrega la referencia al gráfico:
   ```markdown
   ![Descripción del gráfico](./assets/charts/mi_grafico.png)
   ```
3. Ejecuta `make deploy` (copia el `.md` y los PNGs al repo Jekyll)
4. Ve al repo Jekyll, haz commit y push

> **Importante:** `make deploy` solo copia archivos a tu computador. El sitio web no se actualiza hasta que haces `git push` en el repo Jekyll.

---

## Inicio Rápido (referencia)

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
# Opcionalmente configurar la ruta al repo Jekyll
export JEKYLL_REPO="/ruta/al/repo/jekyll"

python -m src.deploy
```

Copia datos, charts, HTML, CSS, JS y el markdown del proyecto (`jekyll/barchart-race.md`) al repo Jekyll local. El `git push` se realiza manualmente.

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
├── jekyll/
│   └── barchart-race.md     # Markdown del proyecto (deploy lo copia a Jekyll)
├── notebooks/original/      # Notebooks prototipo archivados
├── viz/
│   ├── index.html            # Página de visualización
│   └── assets/
│       ├── css/barchart.css  # Estilos
│       └── js/barchart-race.js # Motor D3.js (animación mensual)
├── tests/                   # 79 tests unitarios + integración
├── run.py                   # Punto de entrada unico (python run.py help)
├── CHANGELOG.md             # Evolución del proyecto
└── pyproject.toml           # Metadata, dependencias, config herramientas
```
