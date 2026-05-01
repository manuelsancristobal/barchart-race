---
layout: project
title: "Bar Chart Race: Movimiento Aéreo"
category: Visualización de Datos
description: Animación de la evolución del tráfico aéreo internacional, desde y hacia Chile, entre el periodo 1984 y 2026.
github_url: "https://github.com/manuelsancristobal/barchart-race"
tech_stack:
  - JavaScript
  - D3.js
  - CSS
---

## Visualización Interactiva

Este proyecto es un ETL combinado con una animación de la evolución histórica del mercado aéreo internacional en Chile, incluye visualizaciones del tráfico emisivo y receptivo, tanto por destinos como por aerolíneas, y distingue cantidad de pasajeros viajados y el tonelaje de carga trasladado.

<div style="position: relative; width: 100%; padding-bottom: 62%; overflow: hidden; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
  <iframe
    src="/proyectos/barchart-race/viz.html"
    style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none;"
    loading="lazy"
    title="Bar Chart Race: Movimiento Aéreo Internacional de Chile"
    allowfullscreen>
  </iframe>
</div>

## Análisis complementario

### Evolución del tráfico aéreo internacional de Chile

Este gráfico muestra el volumen total de pasajeros y carga del tráfico aéreo internacional de Chile entre 1984 y 2026, distinguiendo entre tráfico emisivo (desde Chile) y receptivo (hacia Chile). El doble eje permite comparar la evolución de pasajeros y tonelaje simultáneamente.

![Gráfico de líneas con doble eje mostrando la evolución de pasajeros y tonelaje entre 1984 y 2026, con caída visible en 2020 por COVID-19](./assets/charts/01_total_traffic.png)

El tráfico de pasajeros muestra un crecimiento sostenido con una caída dramática en marzo de 2020 debido al cierre de fronteras provocado por la pandemia del COVID-19. Durante este periodo (Febrero 2020 a Octubre 2020), LATAM mantuvo conectividad con vuelos humanitarios y repatriaciones principalmente desde Sydney (928 pax), Sao Paulo (623 pax) y Miami (478 pax). La reapertura formal en Noviembre 2020 trajo de vuelta a SKY, JetSmart, United y Air France como las primeras en retomar operaciones regulares receptivas hacia Chile.

En el mismo periodo, el transporte de carga no se ve afectado, llegando incluso a un máximo histórico en julio de 2021 con 16 mil toneladas recibidas, provenientes principalmente de Sao Paulo, Buenos Aires y Miami, trasladadas por Kalitta Air, Atlas Air, Southern Air, y Martinair, aerolíneas que operan sin pasajeros. Más investigación se necesita para confirmar o descartar el efecto del primer retiro de los fondos de pensiones ocurridos durante julio de 2020 y su efecto en este tonelaje recibido. En esta misma línea, pese al cierre de fronteras, la carga emisiva crece un 5% impulsada por la demanda de productos frescos, con destino principalmente en Miami, Sao Paulo y Los Ángeles.

Durante los últimos doce meses (entre febrero 2025 y febrero 2026), Estambul creció +430% como mercado emisivo y +480% como mercado receptivo. Turkish Airlines pasó de 9 mil a 43 mil pasajeros anuales, consolidándose como la "Anomalía de Estambul": una ruta intercontinental que irrumpe con fuerza no solo por el destino en sí, sino como un hub alternativo hacia el Sudeste Asiático y Europa del Este. Esta explosión sugiere un cambio en la jerarquía histórica de las rutas de larga distancia, aunque se requiere más análisis para confirmar si este crecimiento está capturando nuevos viajeros o si existe una canibalización de pasajeros que antes volaban vía Madrid o París. Por otro lado, LATAM se consolida frente a las Low-cost, con un +5% en pasajeros recibidos (152 mil), al contrario de SKY (-9% o 73 mil pax) y Jetsmart (-4% o 26 mil pax).

También, vemos una reorganización de los viajes a Brasil, donde Sao Paulo se reduce un 6% (48 mil pax), frente a destinos como Rio de Janeiro +7% (31 mil pax), Florianópolis +11% (30 mil pax) y Porto Alegre +416% (34 mil pax) gracias a la reapertura post inundaciones ocurridas en abril y mayo de 2024.

Por último, durante Enero 2026, la Ruta Santiago-Sydney recupera sus niveles pre-pandemia con 15 mil pasajeros, siendo su record anterior en enero de 2020 con 16 mil pasajeros.

### Concentración de mercado: Índice Herfindahl-Hirschman

El [Índice HHI](https://www.justice.gov/atr/file/810276/dl?inline=) mide la concentración de mercado sumando los cuadrados de las cuotas de participación de cada aerolínea. Según las [Horizontal Merger Guidelines (2010) pág 19](https://www.justice.gov/atr/file/810276/dl?inline=) del DOJ/FTC, valores bajo 1500 indican un mercado competitivo; entre 1500 y 2500, moderadamente concentrado; sobre 2500, altamente concentrado.

![Gráfico de líneas del índice HHI para mercados emisivo y receptivo, mostrando transición de alta concentración a mercado competitivo](./assets/charts/02_hhi_concentration.png)

El mercado aéreo chileno de pasajeros ha transitado por fases de concentración claramente identificables. SKY fue la primera aerolínea low-cost en operar rutas internacionales desde Chile, iniciando operaciones en septiembre de 2002 con apenas 831 pasajeros ese año (0.1% del mercado). Su impacto en la competitividad no fue inmediato: el HHI se mantuvo sobre 3,000 durante toda la década, mientras SKY crecía gradualmente hasta alcanzar un 5.8% de cuota en 2015 (241 mil pax). La entrada de JetSmart en diciembre de 2017 aceleró la desconcentración, llevando el HHI de 3,596 (2017) a 3,329 (2019). La competencia entre ambas low-cost y LATAM ha sido el principal motor de la mejora competitiva del mercado de pasajeros.

En el mercado de carga, la dinámica es distinta. El peak de concentración ocurrió en 2010, con un HHI de 4,158 (emisivo) y 4,251 (receptivo), cuando LATAM concentraba aproximadamente el 63% del tonelaje trasladado en ambas direcciones, seguida por Centurion Air Cargo (~10%) y Atlas Air (~6%). La desconcentración posterior fue impulsada por la expansión de Atlas Air Cargo (que duplicó su cuota de 6.7% a 14.5% emisivo hacia 2016), la entrada de SKY al segmento de carga con ~5% de participación, y la llegada de operadores especializados como Korean Air (2015, ruta Asia), Oceanair (2015, conexión Brasil), y UPS (2015, logística de paquetería). Para 2016, LATAM había bajado a ~51% y el número de aerolíneas con más del 1% de cuota pasó de 8-9 a 13-15, reflejando un mercado significativamente más diversificado.

La pandemia de COVID-19 aceleró esta tendencia estructural en ambos mercados, revelando lo que podría llamarse la "Paradoja de la Democratización Logística". En pasajeros, pese a que el número de aerolíneas activas cayó de 29 a 22, el HHI bajó de 3,329 (2019) a 2,303 (2021), situándose en el rango de mercado moderadamente concentrado. Sin embargo, la verdadera disrupción ocurrió en la carga receptiva: el HHI cruzó por primera vez al territorio plenamente competitivo con 1,965 en 2021. Este fenómeno, impulsado por el boom de importaciones post-pandemia y la entrada de cargueros especializados como Atlas Air (20.9%) y Kalitta Air (8.9%) ante la falta de capacidad en aviones de pasajeros, demuestra que hoy la cadena de suministro aérea de Chile es estructuralmente más diversificada y menos dependiente de un solo actor que nuestra propia red de conectividad turística.

### Ciclos de vida de las principales aerolíneas

Diagrama de Gantt que muestra el período de actividad de las 25 aerolíneas con mayor volumen de pasajeros emisivos. La longitud de cada barra indica el tiempo de operación.

![Diagrama de Gantt horizontal mostrando períodos de actividad de las 25 aerolíneas con mayor volumen emisivo](./assets/charts/05_airline_lifecycle.png)

El diagrama confirma visualmente lo expresado en el análisis de concentración: las legacy carriers como LATAM operan de forma ininterrumpida durante las cuatro décadas, mientras que las entradas de SKY (2002) y JetSmart (2017) — identificadas como los principales motores de desconcentración en el HHI — aparecen como barras recientes que conviven con operadores de ciclos cortos que no lograron sostenerse. Se distinguen oleadas generacionales: una primera generación de aerolíneas que operó entre los años 80 y 90 y fue desapareciendo, una segunda generación que se consolidó en los 2000, y la era low-cost que inicia a partir de 2002 y se intensifica desde 2017.

### Estacionalidad del tráfico de pasajeros

Como hemos visto en la evolución del tráfico total, el volumen de pasajeros creció de forma sostenida hasta el quiebre de 2020. Los heatmaps de estacionalidad permiten descomponer ese crecimiento mes a mes, revelando los ciclos internos que la vista anual no captura.

![Heatmaps comparativos de estacionalidad de pasajeros emisivo y receptivo, con peaks en enero y julio y franjas claras en 2020-2021](./assets/charts/03a_seasonality_pax.png)

Ambos heatmaps revelan un patrón estacional simétrico entre emisivo y receptivo: los peaks coinciden en enero (verano austral) con un peak secundario en julio (vacaciones de invierno), y la amplitud estacional crece con el tiempo reflejando un mercado más grande. La relación peak/trough es moderada (1.4x emisivo, 1.3x receptivo), indicando que el tráfico de pasajeros mantiene un flujo base sostenido durante todo el año. El impacto COVID es visible como franjas claras en 2020-2021: el tráfico cayó un 72% en 2020 (de 5.6M a 1.6M pax emisivos), tocó fondo en 2021 (1.1M), y no recuperó niveles pre-pandemia hasta 2023 (5.0M). Enero de 2026 marca el récord histórico con 678 mil pasajeros emisivos y 615 mil receptivos en un solo mes.

### Estacionalidad del tráfico de carga

En línea con lo observado en el gráfico de tráfico total — donde la carga no solo resistió la pandemia sino que creció — el heatmap de tonelaje permite confirmar y profundizar esa observación, desagregando el comportamiento mes a mes.

![Heatmaps comparativos de estacionalidad de carga emisivo y receptivo](./assets/charts/03b_seasonality_ton.png)

La estacionalidad de la carga muestra un patrón radicalmente distinto al de pasajeros. El tonelaje emisivo tiene una estacionalidad invertida y más pronunciada (ratio 1.8x): los peaks ocurren entre noviembre y enero, coincidiendo con la temporada de exportación de fruta fresca del hemisferio sur (cerezas, arándanos, uva de mesa), y el trough se produce en junio-julio. El tonelaje receptivo, en cambio, es notablemente plano a lo largo del año (ratio 1.3x), sugiriendo que las importaciones aéreas responden a demanda industrial y comercial constante más que a ciclos estacionales.

El contraste más revelador aparece durante COVID-19: mientras los pasajeros colapsaron, la carga emisiva no solo no cayó sino que creció — de 230 mil toneladas en 2019 a 242 mil en 2020 y 255 mil en 2021, impulsada por la demanda global de productos frescos chilenos. En carga receptiva, el peak histórico ocurrió en julio de 2021 (16 mil toneladas en un solo mes), coincidiendo con el boom de importaciones asociado a los retiros de fondos de pensiones y el auge del comercio electrónico durante la pandemia.

### Participación continental en el tráfico emisivo

Con el volumen y la temporalidad ya caracterizados, corresponde analizar la dimensión geográfica del tráfico: hacia dónde viajan los pasajeros que salen de Chile.

![Gráficos de área apilada mostrando participación continental emisiva absoluta y porcentual](./assets/charts/04a_continental_share_emisivo.png)

América concentra el 86.5% del tráfico emisivo acumulado, una dominancia que se ha mantenido notablemente estable durante cuatro décadas (entre 83% y 88% en cualquier año). Europa ocupa el segundo lugar con un 10.4%, mostrando un crecimiento absoluto sostenido — de 40 mil pasajeros en 1984 a 581 mil en 2025 — aunque su participación porcentual ha fluctuado entre 8% y 14% sin una tendencia clara de ganancia. Oceanía, impulsada casi exclusivamente por la ruta Santiago-Sydney, pasó de 9 mil pasajeros en 1984 a un peak de 244 mil en 2019 (4.4%), consolidándose como el tercer mercado continental.

La recuperación post-COVID reveló velocidades asimétricas por continente: América recuperó sus niveles pre-pandemia en 2025 (114% del volumen de 2019), Europa alcanzó el 104%, pero Oceanía permanece rezagada con solo el 85%. Este rezago de Oceanía refleja la lenta restitución de frecuencias en la ruta transpacífica, la más larga y costosa de operar desde Chile.

### Participación continental en el tráfico receptivo

Como ya se anticipó en el análisis del tráfico total, los flujos entre Chile y el mundo son esencialmente bidireccionales. La composición continental del tráfico receptivo permite verificar esta hipótesis.

![Gráficos de área apilada mostrando participación continental receptiva absoluta y porcentual](./assets/charts/04b_continental_share_receptivo.png)

La composición continental del tráfico receptivo es prácticamente un espejo del emisivo: América concentra el 87.1%, Europa el 10.0% y Oceanía el 2.9%. Esta simetría indica que los flujos de pasajeros entre Chile y el mundo son esencialmente bidireccionales — los mismos destinos que los chilenos visitan son los orígenes de quienes visitan Chile.

La principal diferencia aparece en la velocidad de recuperación post-COVID. Mientras América emisiva ya superó los niveles de 2019 en un 114%, América receptiva lo hizo en un 113%, mostrando equilibrio. Sin embargo, Europa receptiva (98% de 2019) se recupera más lento que la emisiva (104%), y Oceanía receptiva apenas alcanza el 82% versus el 85% emisivo. Esto sugiere que la demanda de turismo europeo y oceánico hacia Chile aún no se ha recuperado completamente, posiblemente por la competencia de destinos más cercanos a esos mercados de origen.

### Relación pasajeros vs. carga por destino

Los análisis anteriores han tratado pasajeros y carga como mercados separados. Este gráfico los cruza por primera vez, revelando qué destinos son predominantemente turísticos y cuáles funcionan como hubs logísticos — una distinción coherente con la estacionalidad invertida observada entre ambas métricas.

![Scatter plot log-log comparando acumulado de pasajeros vs tonelaje por destino, coloreado por continente](./assets/charts/06_pax_vs_cargo.png)

La mayoría de los destinos siguen una correlación positiva entre pasajeros y carga, pero los outliers cuentan la historia más interesante. Destinos como Miami y Los Ángeles aparecen desplazados hacia la carga, revelando el motor invisible de la "Ruta de la Fruta": hubs logísticos esenciales para la exportación de productos frescos. Esta ruta es tan crítica que explica por qué el flujo de tonelaje no se detuvo durante la pandemia. No obstante, se requiere un análisis más detallado para determinar qué tan dependientes son económicamente estas rutas de la temporada de cerezas (noviembre-enero) y si su rentabilidad anual se sostiene principalmente sobre este peak estacional. En el otro extremo, destinos como Cancún, Punta Cana y Florianópolis se desplazan hacia los pasajeros con baja carga relativa, revelando su naturaleza predominantemente turística. Esta dualidad refuerza la tesis central: pasajeros y carga operan como dos mercados con lógicas distintas que comparten infraestructura pero responden a demandas diferentes.

### Crecimiento interanual: Top 5 destinos

Los gráficos anteriores muestran acumulados, participaciones y estructuras. Este último análisis revela la dinámica oculta por la acumulación: las tasas de crecimiento interanual que confirman las velocidades asimétricas de recuperación post-COVID ya identificadas en el análisis continental.

![Gráfico de líneas mostrando crecimiento interanual de los 5 destinos principales, con caídas extremas en 2020 y recuperación posterior](./assets/charts/07_yoy_growth_top5.png)

Con esto se confirma que el crash COVID no fue un evento homogéneo: las caídas de 2020 fueron similares en magnitud para todos los destinos principales (-70% a -90%), pero la velocidad de recuperación varió significativamente. Los destinos regionales americanos rebotaron más rápido, en línea con la recuperación continental del 114% ya documentada, mientras que las rutas de largo alcance mostraron una recuperación más gradual. Las tasas de crecimiento también revelan fases de aceleración previas a la pandemia — períodos de +20% a +40% anual — que no son visibles en los datos acumulados del barchart race y que explican los cambios de ranking que la animación muestra.


<div class="methodology-box" style="margin-top: 2rem; padding: 1.5rem; background: var(--bg-light); border-radius: 8px; border-left: 4px solid var(--secondary);">
    <p style="margin: 0; font-size: 0.95rem;">📌 <strong>Sobre este proyecto:</strong> Esta es una versión mejorada del análisis original, rediseñado como aplicación interactiva. El proyecto original está disponible en
    <a href="https://colab.research.google.com/drive/1K883wlzwM9MwrDqLNV5MCT4f477mbF7Z?usp=sharing" target="_blank" style="color: var(--secondary); font-weight: 600;">Google Colab</a>.</p>
</div>
