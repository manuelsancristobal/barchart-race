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

Durante los últimos doce meses (entre febrero 2025 y febrero 2026), Estambul creció +436% como mercado emisivo y +485% como mercado receptivo. Turkish Airlines pasó de 9 mil a 43 mil pasajeros anuales, siendo la ruta intercontinental emergente más dinámica. Por otro lado, LATAM se consolida frente a las Low-cost, con un +5% en pasajeros recibidos (152 mil), al contrario de SKY (-9% o 73 mil pax) y Jetsmart (-4% o 26 mil pax).

También, vemos una reorganización de los viajes a Brasil, donde Sao Paulo se reduce un 6% (48 mil pax), frente a destinos como Rio de Janeiro +7% (31 mil pax), Florianópolis +11% (30 mil pax) y Porto Alegre +416% (34 mil pax) gracias a la reapertura post inundaciones ocurridas en abril y mayo de 2024.

Por último, durante Enero 2026, la Ruta Santiago-Sydney recupera sus niveles pre-pandemia con 15 mil pasajeros, siendo su record anterior en enero de 2020 con 16 mil pasajeros.

### Concentración de mercado: Índice Herfindahl-Hirschman

El Índice HHI mide la concentración de mercado sumando los cuadrados de las cuotas de participación de cada aerolínea. Valores bajo 1500 indican un mercado competitivo; entre 1500 y 2500, moderadamente concentrado; sobre 2500, altamente concentrado.

![Gráfico de líneas del índice HHI para mercados emisivo y receptivo, mostrando transición de alta concentración a mercado competitivo](./assets/charts/02_hhi_concentration.png)

El mercado aéreo chileno ha transitado por fases: alta concentración inicial (dominado por pocas aerolíneas), una liberalización progresiva, y la entrada de operadores low-cost como SKY y JetSMART que han intensificado la competencia en años recientes.

### Estacionalidad del tráfico aéreo emisivo

El heatmap muestra el flujo mensual de pasajeros emisivos a lo largo de cada año. Los colores más intensos indican mayor tráfico. La estructura año × mes revela patrones estacionales recurrentes.

![Heatmap año por mes mostrando estacionalidad del tráfico emisivo, con peaks en enero y julio y franjas claras en 2020-2021](./assets/charts/03_seasonality_heatmap.png)

Se observa un patrón estacional claro con peaks en enero (verano austral) y julio (vacaciones de invierno). La amplitud estacional crece con el tiempo, reflejando un mercado más grande. Los años 2020-2021 aparecen como franjas claras, evidenciando el impacto COVID.

### Participación continental en el tráfico emisivo

Muestra cómo se distribuye el tráfico emisivo de pasajeros entre los distintos continentes de destino, tanto en valores absolutos como en participación porcentual.

![Dos gráficos de área apilada mostrando participación continental absoluta y porcentual, con América dominante y Europa creciendo](./assets/charts/04_continental_share.png)

América domina ampliamente como destino del tráfico emisivo chileno. Sin embargo, la participación de Europa ha crecido de forma sostenida, mientras que Oceanía y Asia mantienen nichos menores pero crecientes. La composición continental revela la diversificación progresiva de las rutas internacionales.

### Ciclos de vida de las principales aerolíneas

Diagrama de Gantt que muestra el período de actividad de las 25 aerolíneas con mayor volumen de pasajeros emisivos. La longitud de cada barra indica el tiempo de operación.

![Diagrama de Gantt horizontal mostrando períodos de actividad de las 25 aerolíneas con mayor volumen emisivo](./assets/charts/05_airline_lifecycle.png)

Se identifican oleadas de entrada/salida de aerolíneas: las legacy carriers operan durante décadas, mientras que muchas aerolíneas tienen ciclos cortos. Las entradas recientes de low-cost (SKY, JetSMART) marcan una nueva era competitiva.

### Relación pasajeros vs. carga por destino

Scatter plot en escala logarítmica que compara el acumulado total de pasajeros y tonelaje por cada destino emisivo. Cada punto es una ciudad, coloreada por continente.

![Scatter plot log-log comparando acumulado de pasajeros vs tonelaje por destino, coloreado por continente](./assets/charts/06_pax_vs_cargo.png)

La mayoría de los destinos siguen una correlación positiva entre pasajeros y carga, pero existen outliers notables: destinos con alta carga relativa sugieren hubs logísticos/comerciales, mientras que destinos con alto flujo de pasajeros pero baja carga indican rutas predominantemente turísticas.

### Crecimiento interanual: Top 5 destinos

Muestra la tasa de crecimiento año a año del flujo de pasajeros de los 5 destinos emisivos más importantes. Este análisis revela la dinámica oculta por los valores acumulados del barchart race.

![Gráfico de líneas mostrando crecimiento interanual de los 5 destinos principales, con caídas extremas en 2020 y recuperación posterior](./assets/charts/07_yoy_growth_top5.png)

Las tasas de crecimiento revelan fases de aceleración y desaceleración no visibles en datos acumulados. El crash COVID genera caídas extremas seguidas de rebounds igualmente intensos. La velocidad de recuperación post-COVID varía significativamente entre destinos.
