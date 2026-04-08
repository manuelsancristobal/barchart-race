# Plan: Bar Chart Race — ETL + Visualización Interactiva en Jekyll

## Contexto

El proyecto tiene 2 notebooks prototipo en Google Colab que generan animaciones GIF de "bar chart race" sobre movimiento aéreo internacional de Chile (datos JAC). Los notebooks comparten ~70% del código, tienen errores geográficos, y solo cubren 2 visualizaciones: destinos emisivos (pasajeros) y movimiento neto (pasajeros) — este último fue descartado para v1.

**Objetivo**: Convertir estos prototipos en un sistema modular con ETL automatizado, visualización interactiva en D3.js desplegada en el sitio Jekyll existente (`manuelsancristobal.github.io/proyectos/barchart-race/`), y documentación de las decisiones tomadas.

**Decisiones del usuario documentadas (v1.2)**:
- **Aerolíneas agrupadas por Grupo corporativo** (no por Operador individual) — se usa la columna `Grupo` existente en los datos JAC directamente como `name`. Si `Grupo` está vacío, se utiliza el **nombre del operador original** como fallback.
- **Sin movimiento neto** por ahora — solo datos reales emisivos/receptivos.
- Despliegue en **Jekyll con D3.js** (animación client-side).
- Datos descargados desde **Google Sheets** (con fallback a archivo local).
- **Labels dinámicos** en la UI: en Emisivo dice "Destinos", en Receptivo dice "Orígenes".
- **Cumsum para todas** las combinaciones: el ranking se basa estrictamente en el valor acumulado histórico. Si un destino/aerolínea no tiene movimiento *nuevo* en un año específico, se rellena con 0 internamente para mantener su valor acumulado anterior, permitiendo que la barra permanezca en el ranking si su total histórico es lo suficientemente alto.
- **Mapeo consistente**: Se aplica el **último mapeo conocido** (continente/grupo) a toda la serie histórica de cada entidad para evitar saltos de color o categoría.
- **Desktop primero**, móvil básico (sin optimización especial).
- **Script de copia automática** (`deploy.py`) para mover JSONs del repo ETL al repo Jekyll (el push a GitHub es manual por el usuario).
- **ETL con pipeline configurable** — `build_pipeline(perspectiva, dimension, metrica)` encadena filtros automáticamente.
- **Estado inicial**: primer año (1984), Play arranca desde posición del slider.
- **Cambio de selector mid-animación**: pausa automática, carga nuevos datos, e intenta **mantener el año actual**. Solo resetea al inicio si el año no existe en el nuevo set de datos.
- **Anotaciones como banner inferior** (no panel lateral) — el gráfico nunca cambia de tamaño.
- **JSONs con todos los datos** — D3 filtra a top 10 al renderizar.
- **Formato numérico español**: punto como separador de miles (1.234.567).
- **Años dinámicos** derivados de los datos (no hardcodeados).
- **Animación fluida**: Transiciones D3 de **300ms** (las barras se deslizan suavemente) manteniendo el ritmo de los notebooks originales.
- **Banner visible al mover slider** — las anotaciones aparecen siempre que el año coincida.

---

## Arquitectura General

```
[Google Sheets JAC] → [Python ETL] → [8 JSONs datos + 8 JSONs anotaciones] → [Script copia] → [Jekyll + D3.js Bar Chart Race]
```

**Flujo**:
1. Python descarga CSV desde Google Sheets (o lee Excel local como fallback).
2. ETL procesa y genera 8 JSONs de datos en `data/processed/`.
3. ETL genera un reporte temporal de "Países no mapeados" para corrección iterativa con el usuario (en `data/work/`).
4. Anotaciones cualitativas (8 JSONs) se mantienen en `data/annotations/`.
5. Script `deploy.py` copia datos + anotaciones al repo Jekyll local (`manuelsancristobal.github.io/proyectos/barchart-race/assets/`).
6. El usuario realiza el push al repo Jekyll manualmente.
7. D3.js en el navegador lee el JSON seleccionado y renderiza la animación (con fecha real de generación en los metadatos).

---

## Fase 1: Estructura del Proyecto

Crear la siguiente estructura dentro del repo `manuelsancristobal.github.io`:

```
proyectos/barchart-race/
├── index.html                    # Página Jekyll con la visualización
├── assets/
│   ├── css/
│   │   └── barchart.css          # Estilos de la visualización
│   ├── js/
│   │   └── barchart-race.js      # Lógica D3.js de la animación
│   ├── data/                     # JSONs generados por el ETL
│   │   ├── emisivo_destinos_pasajeros.json
│   │   ├── emisivo_destinos_tonelaje.json
│   │   ├── emisivo_aerolinea_pasajeros.json
│   │   ├── emisivo_aerolinea_tonelaje.json
│   │   ├── receptivo_destinos_pasajeros.json
│   │   ├── receptivo_destinos_tonelaje.json
│   │   ├── receptivo_aerolinea_pasajeros.json
│   │   └── receptivo_aerolinea_tonelaje.json
│   └── annotations/              # Anotaciones cualitativas
│       ├── emisivo_destinos_pasajeros.json
│       ├── emisivo_destinos_tonelaje.json
│       ├── emisivo_aerolinea_pasajeros.json
│       ├── emisivo_aerolinea_tonelaje.json
│       ├── receptivo_destinos_pasajeros.json
│       ├── receptivo_destinos_tonelaje.json
│       ├── receptivo_aerolinea_pasajeros.json
│       └── receptivo_aerolinea_tonelaje.json
```

Repo ETL separado (este repo actual `Barchart race/`):

```
Barchart-race/
├── README.md
├── CHANGELOG.md                  # Documentación de evolución
├── PLAN.md                       # Este archivo
├── requirements.txt
├── data/
│   ├── raw/                      # CSV/Excel JAC como fallback (.gitignore)
│   ├── processed/                # JSONs generados
│   ├── annotations/              # Anotaciones cualitativas por combinación
│   ├── reference/
│   │   └── continent_mapping.csv # Mapeo país→continente (corregido)
│   └── work/                     # Archivos temporales de trabajo
│       └── unmapped_countries.txt # Lista de países sin mapear para revisión
├── scripts/
│   └── inspect_data.py           # Script de inspección/validación de datos
├── src/
│   ├── __init__.py
│   ├── config.py                 # Constantes, rutas, colores, ruta al repo Jekyll
│   ├── etl/
│   │   ├── __init__.py
│   │   ├── extract.py            # Descarga CSV desde Google Sheets / lectura local
│   │   ├── transform.py          # Filtros y agregaciones
│   │   └── load.py               # Genera JSONs
│   ├── main.py                   # Orquestador: ejecuta ETL completo
│   ├── generate_annotations.py   # Genera borradores de anotaciones con IA
│   └── deploy.py                 # Copia JSONs + anotaciones al repo Jekyll local (manual push)
├── notebooks/
│   └── original/                 # Notebooks prototipo archivados
└── tests/
    └── test_transform.py
```

---

## Fase 2: ETL en Python

### 2.1 Extract (`src/etl/extract.py`)

- **Fuente de datos**: Google Sheets público con datos actualizados de la JAC
  - URL: `https://docs.google.com/spreadsheets/d/1U3JiVuxjDcvaIoLw9XkW3JKfuh-8_3Pc/edit?gid=499690993`
  - Archivo original: `BD_Tráfico_aéreo.xlsx`
- **Descarga**: Descargar como CSV desde Google Sheets usando URL de exportación (`/export?format=csv&gid=...`). Si falla, fallback a lectura local desde `data/raw/`.
- **Lectura**: `pd.read_csv()` o `pd.read_excel()` según formato descargado
- **Validación**: Verificar que existan las 25+ columnas esperadas. Hard fail si faltan.
- **Normalización de columnas numéricas**: Las columnas relevantes tienen formatos distintos según su naturaleza:
  - `PAX_LIB` y `PASAJEROS`: ya son `float64` en la fuente, solo redondear a entero (no existen fracciones de personas)
  - `CAR_LIB`: ya es `int64`, no necesita limpieza
  - `CARGA (Ton)`: **única columna** con comas como separador decimal (años 2022-2026), requiere conversión coma→punto antes de `pd.to_numeric()`
  - Nota: el último año disponible puede estar incompleto si el ETL se ejecuta durante ese año
- **Normalización de columnas**:
  - Renombrar `Año` → `year` inmediatamente (encoding de `ñ` puede causar problemas).
  - Renombrar `CARGA (Ton)` → `CARGA_TON` (espacios y paréntesis problemáticos).
  - Crear `PASAJEROS_TOTAL = PAX_LIB + PASAJEROS`.
  - Crear `CARGA_TOTAL = (CAR_LIB / 1000) + CARGA_TON` (Se detectó que **CAR_LIB** ("carga liberada") **está en Kilos** y **CARGA_TON está en Toneladas**, por lo que sumarlas directamente es un error de escala).
  - Loggear un resumen de la proporción de carga libre sobre la total por año para validación.

### 2.2 Transform (`src/etl/transform.py`)

Pipeline configurable — una función `build_pipeline(perspectiva, dimension, metrica)` encadena los filtros correctos automáticamente, evitando errores de orden o combinaciones inválidas.

```python
# Función principal — el caller solo pasa los 3 parámetros
def build_pipeline(df, perspectiva, dimension, metrica) -> pd.DataFrame:
    """
    Encadena: filter_international → filter_perspectiva → aggregate → cumsum → mapping
    Resuelve internamente qué columnas usar según la combinación.
    """

# Funciones internas (el pipeline las llama en orden correcto):
filter_international(df)          # NAC == 'INTERNACIONAL' — siempre se aplica primero
filter_by_perspectiva(df, persp)  # Emisivo: ORIG_1_PAIS=='CHILE' & OPER_2=='SALEN'
                                  # Receptivo: DEST_1_PAIS=='CHILE' & OPER_2=='LLEGAN'
aggregate(df, dimension, metric, perspectiva)
    # Resuelve qué columna usar como 'name':
    #   Emisivo + Destinos  → name=DEST_1_N, group=DEST_1_PAIS
    #   Receptivo + Destinos → name=ORIG_1_N, group=ORIG_1_PAIS
    #   Aerolínea (ambas)    → name=Grupo (columna existente en datos JAC), group=vacío
    # Resuelve qué columna sumar:
    #   Pasajeros → PASAJEROS_TOTAL
    #   Tonelaje  → CARGA_TOTAL
compute_cumulative(df)            # cumsum por [name, group] sobre año
apply_continent_mapping(df)       # Solo si dimension=='destinos'; para aerolíneas no aplica
```

**Combinaciones** (8 total = 2 perspectivas × 2 dimensiones × 2 métricas):

| # | Perspectiva | Dimensión | Métrica | name | group |
|---|------------|-----------|---------|------|-------|
| 1 | Emisivo | Destinos | Pasajeros | Ciudad destino | País destino |
| 2 | Emisivo | Destinos | Tonelaje | Ciudad destino | País destino |
| 3 | Emisivo | Aerolínea | Pasajeros | Grupo aéreo | — |
| 4 | Emisivo | Aerolínea | Tonelaje | Grupo aéreo | — |
| 5 | Receptivo | Destinos | Pasajeros | Ciudad origen | País origen |
| 6 | Receptivo | Destinos | Tonelaje | Ciudad origen | País origen |
| 7 | Receptivo | Aerolínea | Pasajeros | Grupo aéreo | — |
| 8 | Receptivo | Aerolínea | Tonelaje | Grupo aéreo | — |

**Nota sobre aerolíneas**: Para la vista por aerolínea no aplica el mapeo por continente. El campo `group` y `continent` quedan como `null` en el JSON. D3 detecta esto y usa una paleta ordinal única sin categoría visual. Los colores se asignan consistentemente por nombre de aerolínea. En la visualización, donde normalmente aparece el continente en gris debajo del nombre, para aerolíneas ese espacio queda vacío.

### 2.3 Load (`src/etl/load.py`)

Genera JSONs con **todos los datos** (no pre-filtrados a top N). D3 filtra al top 10 al renderizar — esto permite cambiar el N en el futuro sin regenerar JSONs.

Estructura para **destinos**:
```json
{
  "metadata": {
    "perspectiva": "emisivo",
    "dimension": "destinos",
    "metrica": "pasajeros",
    "years": [1984, 1985, "...", 2026],
    "generated": "2026-04-05"
  },
  "color_map": {
    "América": "#e48381",
    "Europa": "#90d595",
    "Asia": "#ffb3ff",
    "Medio Oriente": "#eafb50",
    "Oceanía": "#aafbff",
    "África": "#f7bb5f",
    "Antártica": "#adb0ff",  // Reservado — actualmente sin uso en los datos
    "Otro": "#cccccc"
  },
  "data": [
    {"name": "MIAMI", "group": "ESTADOS UNIDOS", "continent": "América", "year": 1984, "value": 12345}
  ]
}
```

Estructura para **aerolíneas** (sin continent ni group):
```json
{
  "metadata": {
    "perspectiva": "emisivo",
    "dimension": "aerolinea",
    "metrica": "pasajeros",
    "years": [1984, 1985, "...", 2026],
    "generated": "2026-04-05"
  },
  "color_map": null,
  "data": [
    {"name": "LATAM", "group": null, "continent": null, "year": 1984, "value": 56789}
  ]
}
```

### 2.4 Correcciones a los notebooks originales

Errores encontrados en el mapeo de continentes:
- `BELICE` → estaba en "Africa", corregir a **"America"**
- `ISLA MARTINICA` → estaba en "Oceania", corregir a **"America"**
- `ISLA DE TAHITI` → estaba en "Asia", corregir a **"Oceania"**

Externalizar el mapeo a `data/reference/continent_mapping.csv` + log warning para países no mapeados.

### 2.5 Detalles rescatados de los notebooks (a replicar en v1)

**Transformación visual de nombres**: Los notebooks usan `name.title()` para convertir "MIAMI" → "Miami" en la visualización. El ETL debe almacenar nombres en mayúsculas (como vienen de la fuente) y D3 debe aplicar title-case al renderizar.

**Nombres de países inconsistentes en la fuente**: El diccionario de continentes tiene entradas duplicadas con variantes de escritura:
- `EMI. ARABES UNIDOS` y `EMI.ARABES UNIDOS` (con/sin espacio)
- `REP. COREA DEL SUR` y `REP.COREA DEL SUR` (con/sin espacio)

El ETL debe normalizar estos nombres antes del mapeo (trim y unificar espacios).

**Columna de año**: Los notebooks usan `Año` (mixto, con ñ), no `AÑO` en mayúsculas. El extract debe manejar ambas variantes o normalizar a `year` inmediatamente.

**Espaciado dinámico de labels**: Los notebooks calculan `dx = dff['value'].max() / 200` para posicionar los textos de las barras. D3 debe replicar esta lógica — el offset entre el nombre y el valor depende del máximo de cada frame.

**Bug en notebooks: KeyError por países no mapeados**: Si aparece un país que no está en el diccionario de continentes, el código `colores[group_continente[x]]` crashea. En v1 el ETL debe asignar categoría "Otro" con color gris (`#cccccc`) a países sin mapeo.

**Inner merge en Notebook 1 (movimiento neto)**: El `pd.merge()` usa inner join por defecto, descartando ciudades que solo tienen entradas O solo salidas. Esto es relevante si en el futuro se reactiva la vista de movimiento neto — documentar como decisión de diseño.

**Velocidad de animación**: Notebook 1 usa 300ms/frame, Notebook 2 usa 200ms/frame. Para D3, usar **300ms como default** con posibilidad de ajuste. Las transiciones D3 pueden ser más lentas que matplotlib porque interpolan posiciones (las barras se mueven suavemente).

**Parámetros visuales exactos a replicar en D3**:

| Elemento | Valor matplotlib | Equivalente D3/CSS |
|----------|-----------------|-------------------|
| Tamaño del gráfico | 15×8 inches | Ancho contenedor, ratio 15:8 |
| Nombre de barra | size=14, weight=600 | font-size: 14px, font-weight: 600 |
| Continente/grupo | size=10, color=#444444 | font-size: 10px, fill: #444444 |
| Valor numérico | size=14, format `:,.0f` | font-size: 14px, `d3.formatLocale({thousands:".",grouping:[3]}).format(",.0f")` |
| Año grande | size=46, weight=800, color=#777777 | font-size: 46px, font-weight: 800, fill: #777777 |
| Título | size=24, weight=600 | font-size: 24px, font-weight: 600 |
| Subtítulo | size=12, color=#777777 | font-size: 12px, fill: #777777 |
| Crédito autor | color=#777777, bbox blanco α=0.8 | fill: #777777, background: rgba(255,255,255,0.8) |
| Eje X | arriba, ticks color=#777777, size=12 | D3 axisTop, tick color/size matching |
| Grid | major, eje X, linestyle='-' | stroke-dasharray: none (línea sólida) |
| Bordes | plt.box(False) | Sin borde en SVG |
| Márgenes | (0, 0.01) | Padding mínimo vertical |

---

## Fase 3: Visualización D3.js

### 3.1 Página Jekyll (`index.html`)

Selectores en la parte superior:

```
[Emisivo | Receptivo]                ← Toggle de perspectiva
[Destinos/Orígenes | Aerolínea]      ← Toggle de dimensión (label cambia según perspectiva)
[Pasajeros | Tonelaje]               ← Toggle de métrica
[▶ Play] [⏸ Pausa] [Año: ━━●━━━]   ← Controles de animación
```

**Labels dinámicos**: Al cambiar perspectiva, el toggle de dimensión se actualiza:
- Emisivo → muestra "Destinos | Aerolínea"
- Receptivo → muestra "Orígenes | Aerolínea"

**Rango de años dinámico**: El primer y último año se derivan automáticamente de los datos (metadata del JSON: `years[0]` y `years[-1]`). No se hardcodea ningún año — si la JAC actualiza los datos, los años se ajustan solos.

**Estado inicial**: Al cargar la página, se muestra Emisivo + Destinos + Pasajeros con el frame del **primer año** disponible. El slider está en la posición inicial. El usuario da Play para ver la animación completa, o puede mover el slider a cualquier año antes de darle Play.

**Comportamiento del Play**: La animación arranca desde la posición actual del slider y avanza hasta el último año. Al llegar al final, **se detiene** mostrando el último frame. El usuario puede dar Play de nuevo para repetir desde el primer año.

**Comportamiento del slider**: El usuario puede arrastrar el slider a cualquier año en cualquier momento. Si hay una anotación para ese año, el banner aparece inmediatamente (sin fade durante exploración manual).

**Cambio de selectores mid-animación**: Si el usuario cambia perspectiva, dimensión o métrica mientras la animación corre, se **pausa automáticamente**, carga los nuevos datos, muestra el frame del año donde estaba, y espera que el usuario dé Play de nuevo.

**Títulos dinámicos** — se construyen con un template:

```
"Principales {dimensión_label} {dirección} Chile — {año_min} al {año_max}"
```

Donde:
- `dimensión_label`: Emisivo+Destinos → "destinos aéreos", Receptivo+Orígenes → "orígenes aéreos", Aerolínea → "aerolíneas en vuelos"
- `dirección`: Emisivo → "desde", Receptivo → "hacia"
- Para aerolíneas: "Principales aerolíneas en vuelos desde/hacia Chile"

**Subtítulos dinámicos**:
- Pasajeros → "Cantidad acumulada de pasajeros"
- Tonelaje → "Tonelaje acumulado de carga"

Ejemplos resultantes:
- "Principales destinos aéreos desde Chile — 1984 al 2026" / "Cantidad acumulada de pasajeros"
- "Principales orígenes aéreos hacia Chile — 1984 al 2026" / "Tonelaje acumulado de carga"
- "Principales aerolíneas desde Chile — 1984 al 2026" / "Cantidad acumulada de pasajeros"

**Diseño responsive**: Desktop primero. En móvil se mantiene funcional pero sin optimizaciones especiales — el usuario puede hacer zoom.

### 3.2 Motor de animación (`barchart-race.js`)

Replicar **lo más fielmente posible** el estilo visual de los notebooks (habrá diferencias menores por la migración de matplotlib a SVG/D3):
- Barras horizontales, top 10, ordenadas ascendente
- Colores por continente (misma paleta)
- Nombre de destino bold **dentro** de la barra (alineado a la derecha del extremo, `value - dx`)
- Grupo/continente en gris debajo del nombre (dentro de la barra)
- Valor numérico **a la derecha** de la barra (`value + dx`)
- Año grande (semi-transparente) esquina inferior derecha
- Eje X arriba con gridlines
- Título + subtítulo + crédito autor

**Transiciones D3**: Usar `d3.transition()` con duración de **300ms** por frame para interpolar entre años (las barras se mueven suavemente, no saltan). Esto mejora el efecto respecto al GIF original.

**Formato numérico español**: Usar `d3.formatLocale` con punto como separador de miles y coma decimal (1.234.567 en vez de 1,234,567). Aplica tanto al eje X como a los valores de las barras.

**Dependencia D3.js**: Cargar D3 v7 desde CDN (`https://d3js.org/d3.v7.min.js`). No requiere instalación local ni npm.

### 3.3 Banner de anotaciones cualitativas

**Layout**: Banner inferior debajo del gráfico. El gráfico **nunca cambia de tamaño** — siempre ocupa el 100% del ancho.

```
┌─────────────────────────────┐
│                             │
│   [BAR CHART RACE 100%]     │
│   ████████████ Miami        │
│   ██████████ B. Aires       │
│                        2001 │
├─────────────────────────────┤
│ Atentado 11-S: caída del    │
│ tráfico aéreo internacional │
└─────────────────────────────┘
```

**Comportamiento**:
- Cuando la animación llega a un año con anotación, el banner aparece **debajo del gráfico** con **fade-in** (~500ms)
- La anotación permanece visible durante **2-3 frames** (años) y luego desaparece con **fade-out**
- **Cuando no hay anotación, el banner NO existe**: sin recuadro, sin título, sin borde, sin espacio reservado. Solo está el gráfico. Esto evita cualquier elemento huérfano que confunda al usuario.
- Si llega una nueva anotación mientras la anterior aún se muestra, se hace **crossfade** (el banner ya está visible, solo cambia el texto)

**Estructura de datos de anotaciones** (`data/annotations/emisivo_destinos_pasajeros.json`):

```json
[
  {
    "year": 2001,
    "duration": 3,
    "text": "Atentado 11-S: caída drástica del tráfico aéreo internacional. Las rutas hacia EE.UU. se contraen significativamente."
  },
  {
    "year": 2008,
    "duration": 2,
    "text": "Crisis financiera global: la demanda de vuelos internacionales se resiente, especialmente hacia Europa y Norteamérica."
  },
  {
    "year": 2020,
    "duration": 3,
    "text": "Pandemia COVID-19: cierre de fronteras y colapso casi total del tráfico aéreo internacional."
  }
]
```

- `year`: Año en que aparece la anotación
- `duration`: Cantidad de frames (años) que permanece visible
- `text`: Texto descriptivo breve (máx ~150 caracteres para que quepa en el banner)

**Generación de contenido**:
- Un script genera borradores de anotaciones usando IA, basándose en eventos históricos conocidos (crisis, pandemias, apertura de rutas, acuerdos bilaterales, entrada/salida de aerolíneas)
- El usuario revisa y edita cada anotación antes de incluirla
- Cada combinación tiene su propio archivo de anotaciones (8 archivos)
- Eventos universales (COVID, 11-S, crisis 2008) se comparten entre combinaciones pero con texto adaptado al contexto específico

**Criterio para incluir una anotación**: Solo incluir cuando hay un cambio visible en el gráfico. Si el evento no se refleja en los datos, no anotar — evitar ruido.

### 3.4 Flujo de interacción

1. Página carga → se cargan datos y anotaciones de la combinación por defecto (emisivo + destinos + pasajeros)
2. Se muestra el frame del primer año, slider en posición inicial
3. Usuario puede mover el slider para explorar años individuales — si el año tiene anotación, el banner aparece instantáneamente (sin fade)
4. Al dar **Play**, la animación arranca desde la posición del slider y avanza año por año (300ms por frame)
5. En cada frame, D3 verifica si hay anotación → si la hay, fade-in del banner inferior (~500ms)
6. Al llegar al **último año**, la animación **se detiene**. Play vuelve a estar disponible (reinicia desde el primer año)
7. Si el usuario **cambia un selector**: pausa → carga nuevos datos/anotaciones → muestra frame del año actual → espera Play
8. JS construye los nombres de archivo automáticamente: `{perspectiva}_{dimension}_{metrica}.json` para datos y anotaciones

---

## Fase 4: Documentación

### 4.1 CHANGELOG.md

```markdown
# Evolución del Proyecto

## v0 — Prototipos en Jupyter Notebook (Google Colab)
- 2 notebooks independientes con ~70% código duplicado
- Solo 2 visualizaciones: destinos emisivos y movimiento neto
- Mapeo de continentes hardcodeado con 3 errores geográficos
- Datos cargados manualmente via upload de Colab
- Output: archivos GIF estáticos

## v1 — Sistema Modular + Visualización Web Interactiva
### Decisiones de diseño
- Aerolíneas agrupadas por Grupo corporativo (no Operador individual)
  para evitar fragmentación del ranking
- Movimiento neto descartado por ahora — solo datos reales emisivos/receptivos
- Migración de matplotlib GIF a D3.js interactivo en Jekyll
- Labels dinámicos: "Destinos" en emisivo, "Orígenes" en receptivo
- Cumsum (acumulado histórico) para todas las combinaciones
- Desktop primero, móvil funcional sin optimizaciones especiales
- Script de copia automática entre repo ETL y repo Jekyll
- Banner inferior con anotaciones cualitativas generadas con IA y revisadas por el autor

### Cambios técnicos
- ETL modular en Python (extract → transform → load)
- 8 combinaciones de visualización (2×2×2)
- Mapeo de continentes externalizado y corregido
- Descarga automática desde Google Sheets (datos JAC)
- Animación D3.js con transiciones suaves en navegador
- Selectores interactivos de perspectiva, dimensión y métrica
- Banner inferior con anotaciones cualitativas contextuales por año
  (generadas con IA, revisadas y editadas por el autor)

### Correcciones de datos
- Belice: Africa → America
- Isla Martinica: Oceania → America
- Isla de Tahiti: Asia → Oceania
- Normalización de nombres duplicados (EMI. ARABES UNIDOS / EMI.ARABES UNIDOS, etc.)
- Normalización de `CARGA (Ton)` con comas decimales (2022-2026)
- Protección contra países no mapeados (categoría "Otro" en vez de crash)
```

### 4.2 README.md

Además de setup, dependencias y cómo ejecutar, el README debe incluir:

#### Descripción de los prototipos originales (notebooks)

**Notebook 1 — "Movimiento aéreo neto de pasajeros" (60 celdas)**

Este fue el primer intento de visualizar cómo se mueve la gente entre Chile y el mundo. La idea era simple pero potente: tomar todos los pasajeros que llegaron a Chile desde cada país, restarle los que salieron hacia ese mismo país, y ver el resultado acumulado a lo largo de las décadas. Si el número es positivo, significa que históricamente han llegado más personas desde ese país de las que han partido hacia allá. El notebook filtra solo vuelos internacionales, separa entradas de salidas, las cruza por ciudad y país, y calcula el neto acumulado año a año. El resultado es una animación GIF donde las barras van cambiando de posición según qué destinos ganan o pierden relevancia con el tiempo, coloreadas por continente.

**Notebook 2 — "Destinos preferidos" (37 celdas)**

Este notebook es más directo: muestra hacia dónde viajan los chilenos. Toma solo los vuelos que salen de Chile al extranjero, suma los pasajeros por ciudad de destino y año, y va acumulando el total desde el primer año disponible. Es básicamente un ranking histórico de los destinos más populares desde Chile. La animación muestra cómo Miami, Buenos Aires y otras ciudades van compitiendo por el primer lugar a lo largo de décadas. Usa la misma estética visual que el Notebook 1 (top 10, barras horizontales, colores por continente).

#### Hallazgos importantes durante el análisis

**Los notebooks comparten ~70% del código.** Ambos repiten las mismas importaciones, el mismo diccionario de continentes (con más de 60 países mapeados a mano), la misma función de dibujo `draw_barchart`, y la misma lógica de animación. La única diferencia real está en cómo filtran y transforman los datos antes de graficar. Esto significa que cualquier corrección (como un error en el mapeo de continentes) había que hacerla en dos lugares, y cualquier mejora visual había que replicarla manualmente. La modularización en v1 elimina esta duplicación por completo.

**Se encontraron 3 errores geográficos en el mapeo de continentes.** El diccionario hardcodeado en ambos notebooks tenía a Belice clasificado como África (es América Central), Isla Martinica como Oceanía (es Caribe, América), e Isla de Tahití como Asia (es Oceanía, Polinesia Francesa). Estos errores afectan los colores de las barras en la animación y podrían pasar desapercibidos porque estos destinos rara vez aparecen en el top 10. En v1 se corrigen y se externaliza el mapeo a un CSV editable, con un sistema de advertencias para países nuevos que no estén mapeados.

**La columna `CARGA (Ton)` usa comas como separador decimal en años recientes (2022-2026).** Las demás columnas numéricas (`PAX_LIB`, `PASAJEROS` como float64, `CAR_LIB` como int64) ya vienen en formatos limpios. La única limpieza real necesaria es convertir coma→punto en `CARGA (Ton)` y redondear pasajeros a enteros (no existen fracciones de personas). Los datos cubren desde 1984 hasta 2026, aunque el último año puede estar incompleto si el ETL se ejecuta durante ese año.

---

## Fase 5: Implementación (Orden de ejecución)

| Paso | Descripción | Archivos |
|------|-------------|----------|
| 1 | Scaffolding: git init, estructura carpetas, .gitignore, requirements.txt | Proyecto raíz |
| 2 | Archivar notebooks originales en `notebooks/original/` | Mover .ipynb |
| 3 | `continent_mapping.csv` corregido | `data/reference/` |
| 4 | `config.py` con constantes | `src/config.py` |
| 5 | `extract.py` — descarga CSV/Excel y validación | `src/etl/extract.py` |
| 6 | `transform.py` — pipeline configurable + funciones internas | `src/etl/transform.py` |
| 7 | `load.py` — generación de JSONs | `src/etl/load.py` |
| 8 | `main.py` — orquestador | `src/main.py` |
| 8b | `deploy.py` — copia JSONs al repo Jekyll | `src/deploy.py` |
| 9 | Tests con datos sintéticos | `tests/test_transform.py` |
| 10 | `barchart-race.js` — motor D3.js (sin anotaciones aún) | `assets/js/` |
| 11 | `barchart.css` — estilos | `assets/css/` |
| 12 | `index.html` — página Jekyll con selectores | `proyectos/barchart-race/` |
| 13 | **Verificar visualización funcional** — probar las 8 combinaciones | — |
| 14 | `generate_annotations.py` — genera borradores con IA | `src/generate_annotations.py` |
| 15 | Revisión y edición manual de anotaciones por el usuario | `data/annotations/` |
| 16 | Agregar lógica de banner al JS | `assets/js/barchart-race.js` |
| 17 | CHANGELOG.md y README.md | Raíz |

---

## Verificación

1. **ETL**: Ejecutar `python src/main.py` → debe generar 8 JSONs en `data/processed/`
2. **Validación de datos**: Comparar el JSON `emisivo_destinos_pasajeros.json` contra el output del Notebook 2 para los mismos años — los valores acumulados deben coincidir
3. **Visual**: Abrir `index.html` localmente (`jekyll serve` o live server) → los selectores deben cambiar la visualización
4. **Animación**: La animación D3.js debe replicar lo más fielmente posible el estilo de los GIFs originales (top 10, colores, tipografía, layout)
5. **Anotaciones**: Verificar que el banner aparece/desaparece correctamente, que el texto es legible, y que no queda ningún elemento visible cuando no hay anotación
6. **Despliegue**: Push al repo → verificar en `manuelsancristobal.github.io/proyectos/barchart-race/`

---

## Riesgos y Mitigaciones

| Riesgo | Mitigación |
|--------|------------|
| Google Sheets no accesible o cambia de URL | Fallback a archivo local en `data/raw/`; URL configurable en `config.py` |
| `CARGA_TOTAL` no es `CAR_LIB + CARGA_TON` | Verificar con datos reales antes de implementar; preguntar al usuario |
| Tonelaje con datos escasos/nulos | Log de cobertura en extract; warning si <10% tiene datos |
| Países nuevos sin mapeo de continente | Log warning + categoría "Otro" con color gris |
| JSONs pesados (todos los datos, no solo top 10) | Los datos están agregados (~60 países × 43 años ≈ 2.500 filas por JSON). Estimar ~100-200KB por archivo, total ~1.5MB. Aceptable para GitHub Pages; usar gzip en el servidor |
| D3.js bar chart race es complejo | Basarse en implementaciones existentes (d3-bar-chart-race patterns) |
| El archivo en Google Drive es un .xlsx subido, no un Sheet nativo — la URL de exportación CSV podría no funcionar igual | Probar exportación en extract.py; si falla, descargar como .xlsx y leer con openpyxl |
| Aerolíneas con >10 grupos comparten colores | Paleta combinada `schemeCategory10` + `schemeSet3` (22 colores); si aún insuficiente, generar hash-based colors |
