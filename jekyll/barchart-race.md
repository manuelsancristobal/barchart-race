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

## Transformación Estructural del Mercado Aéreo

**El mercado aéreo internacional de Chile ha experimentado una evolución profunda hacia la competitividad y la diversificación logística en las últimas cuatro décadas.** Este proyecto integra procesos ETL con una animación histórica que distingue entre el tráfico de pasajeros y el tonelaje de carga. Como se aprecia en la visualización, el sistema permite explorar el ascenso de nuevos actores y la resiliencia de las rutas estratégicas de forma directa.

<div style="position: relative; width: 100%; padding-bottom: 62%; overflow: hidden; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
  <iframe
    src="/proyectos/barchart-race/viz.html"
    style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none;"
    loading="lazy"
    title="Bar Chart Race: Movimiento Aéreo Internacional de Chile"
    allowfullscreen>
  </iframe>
</div>

## Análisis de Resiliencia y Concentración

### Estabilidad de la Carga ante Crisis
**El transporte de carga aérea demostró una inmunidad notable ante las restricciones sanitarias, alcanzando máximos históricos mientras el tráfico de pasajeros colapsaba.** Como se observa en el gráfico de tráfico total, la demanda de exportación de productos frescos hacia Norteamérica sostuvo la operación. Esta estabilidad es un factor clave analizado también en la [**Visualización de Flujos Aéreos**](/proyectos/flujos-aereos/), donde se destaca la resiliencia de los hubs logísticos internacionales.

![Evolución de pasajeros y tonelaje entre 1984 y 2026](./assets/charts/01_total_traffic.png)

### Mejora Competitiva e Índice HHI
**La entrada de aerolíneas de bajo costo ha sido el principal motor de la desconcentración del mercado de pasajeros.** El Índice HHI revela una transición desde un monopolio de facto hacia un entorno con concentración moderada. Este aumento en la competitividad influye de forma directa en la precisión de los modelos de [**Proyección Turística**](/proyectos/proyeccion-turistica/), al reducir la volatilidad de las tarifas y estabilizar los flujos de largo plazo.

![Índice HHI para mercados emisivo y receptivo](./assets/charts/02_hhi_concentration.png)

### Estacionalidad Invertida
**Los ciclos de pasajeros y carga operan bajo lógicas opuestas: el turismo responde a periodos de vacaciones, mientras la carga sigue el calendario agrícola.** Como se aprecia en los heatmaps de estacionalidad, los peaks de carga coinciden con la exportación de fruta (noviembre-enero). Este patrón de flujos base constantes es esencial para mantener la [**Competitividad Turística**](/proyectos/competitividad-turistica/) del país, al asegurar la viabilidad económica de las rutas internacionales.

![Heatmaps de estacionalidad de pasajeros y carga](./assets/charts/03a_seasonality_pax.png)

### Especialización de Destinos: Logística vs. Turismo
**La distinción entre hubs logísticos y destinos de placer es nítida en la estructura de rutas chilena.** El scatter plot muestra a Miami y Los Ángeles como ejes de carga esenciales ("Ruta de la Fruta"), mientras Cancún y Florianópolis se especializan en pasajeros. La jerarquía de estos destinos turísticos está ligada de modo estrecho a la presencia de [**Atractivos Ancla**](/proyectos/cluster-turismo/) capaces de motivar el flujo internacional.

![Scatter plot: Pasajeros vs Tonelaje por destino](./assets/charts/06_pax_vs_cargo.png)

---

### Notas Técnicas
Este proyecto utiliza D3.js para las animaciones y JavaScript para el control temporal. El código fuente está disponible en [GitHub]({{ page.github_url }}).

<div class="methodology-box" style="margin-top: 2rem; padding: 1.5rem; background: var(--bg-light); border-radius: 8px; border-left: 4px solid var(--secondary);">
    <p style="margin: 0; font-size: 0.95rem;">📌 <strong>Sobre este proyecto:</strong> Esta es una versión mejorada del análisis original. El proyecto original está disponible en <a href="https://colab.research.google.com/drive/1K883wlzwM9MwrDqLNV5MCT4f477mbF7Z?usp=sharing" target="_blank" style="color: var(--secondary); font-weight: 600;">Google Colab</a>.</p>
</div>
