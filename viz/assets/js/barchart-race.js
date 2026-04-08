/* ── Bar Chart Race — D3.js Engine (Monthly) ──────────── */
(function () {
  "use strict";

  // ── Config ────────────────────────────────────────
  const TOP_N = 10;
  const FRAME_MS = 80;
  const TRANSITION_MS = FRAME_MS;
  const MARGIN = { top: 60, right: 80, bottom: 30, left: 10 };
  const BAR_PADDING = 0.12;
  const DATA_BASE = "assets/data/";
  const ANNOTATION_BASE = "assets/annotations/";

  // Formato numérico español (punto = miles)
  const esLocale = d3.formatLocale({
    decimal: ",",
    thousands: ".",
    grouping: [3],
    currency: ["", " €"],
  });
  const fmtInt = esLocale.format(",.0f");
  const fmtDec = esLocale.format(",.1f");

  // ── State ─────────────────────────────────────────
  let state = {
    perspectiva: "emisivo",
    dimension: "destinos",
    metrica: "pasajeros",
    playing: false,
    periodIndex: 0,
    periods: [],
    years: [],
    yearRanges: {},
    entities: [],
    colorMap: null,
    annotations: [],
    timer: null,
  };

  // ── DOM refs ──────────────────────────────────────
  const chartEl = document.getElementById("chart");
  const slider = document.getElementById("year-slider");
  const yearLabel = document.getElementById("year-label");
  const btnPlay = document.getElementById("btn-play");
  const banner = document.getElementById("annotation-banner");
  const dimDestinosBtn = document.getElementById("dim-destinos");

  // ── SVG setup ─────────────────────────────────────
  const width = 940;
  const barAreaHeight = TOP_N * 38;
  const height = barAreaHeight + MARGIN.top + MARGIN.bottom;

  const svg = d3.select("#chart")
    .append("svg")
    .attr("viewBox", `0 0 ${width} ${height}`)
    .attr("preserveAspectRatio", "xMidYMid meet");

  const gBars = svg.append("g").attr("transform", `translate(${MARGIN.left},${MARGIN.top})`);
  const gAxis = svg.append("g").attr("transform", `translate(${MARGIN.left},${MARGIN.top})`);
  const gGrid = svg.append("g").attr("class", "grid").attr("transform", `translate(${MARGIN.left},${MARGIN.top})`);

  // Title & subtitle
  const titleText = svg.append("text")
    .attr("class", "chart-title")
    .attr("x", MARGIN.left)
    .attr("y", 22);

  const subtitleText = svg.append("text")
    .attr("class", "chart-subtitle")
    .attr("x", MARGIN.left)
    .attr("y", 40);

  // Year watermark
  const yearText = svg.append("text")
    .attr("class", "year-bg")
    .attr("x", width - MARGIN.right)
    .attr("y", height - 25);

  // Credit
  svg.append("text")
    .attr("class", "chart-credit")
    .attr("x", width - MARGIN.right)
    .attr("y", height - 0)
    .attr("text-anchor", "end")
    .text("Manuel San Cristóbal Opazo · Datos: JAC Chile");

  // Scales
  const x = d3.scaleLinear().range([0, width - MARGIN.left - MARGIN.right]);
  const y = d3.scaleBand().range([0, barAreaHeight]).padding(BAR_PADDING);

  // Ordinal color scale for airlines (no continent mapping)
  const airlineColor = d3.scaleOrdinal(
    d3.schemeCategory10.concat(d3.schemeSet3)
  );

  const MONTH_NAMES = ["", "Ene", "Feb", "Mar", "Abr", "May", "Jun",
    "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"];

  // ── Data loading ──────────────────────────────────

  async function loadData() {
    const filename = `${state.perspectiva}_${state.dimension}_${state.metrica}.json`;
    const resp = await fetch(DATA_BASE + filename);
    if (!resp.ok) throw new Error(`No se pudo cargar ${filename}`);
    const json = await resp.json();

    state.years = json.metadata.years;
    state.periods = json.metadata.periods;
    state.yearRanges = json.metadata.year_ranges;
    state.colorMap = json.color_map;
    state.entities = json.entities;

    // Try loading annotations (may not exist yet)
    try {
      const annResp = await fetch(ANNOTATION_BASE + filename);
      if (annResp.ok) {
        state.annotations = await annResp.json();
      } else {
        state.annotations = [];
      }
    } catch {
      state.annotations = [];
    }

    // Setup slider (by year)
    slider.min = 0;
    slider.max = state.years.length - 1;

    // Try to keep current year position
    const currentYear = getCurrentYear();
    const newYearIdx = state.years.indexOf(currentYear);
    if (newYearIdx >= 0) {
      state.periodIndex = state.yearRanges[String(state.years[newYearIdx])][0];
    } else {
      state.periodIndex = 0;
    }
    slider.value = yearIndexFromPeriod(state.periodIndex);

    updateTitle();
    renderFrame(false);
  }

  // ── Helpers ─────────────────────────────────────

  function getCurrentYear() {
    if (state.periods.length === 0) return null;
    return state.periods[state.periodIndex][0];
  }

  function yearIndexFromPeriod(periodIdx) {
    const year = state.periods[periodIdx][0];
    return state.years.indexOf(year);
  }

  function getFrameData(periodIndex) {
    return state.entities
      .map(e => ({
        name: e.name,
        group: e.group,
        continent: e.continent,
        value: e.values[periodIndex]
      }))
      .filter(d => d.value > 0)
      .sort((a, b) => b.value - a.value)
      .slice(0, TOP_N);
  }

  // ── Title logic ───────────────────────────────────

  function updateTitle() {
    const yearMin = state.years[0];
    const yearMax = state.years[state.years.length - 1];
    const dir = state.perspectiva === "emisivo" ? "desde" : "hacia";

    let dimLabel;
    if (state.dimension === "destinos") {
      dimLabel = state.perspectiva === "emisivo" ? "destinos aéreos" : "orígenes aéreos";
    } else {
      dimLabel = "aerolíneas en vuelos";
    }

    titleText.text(`Principales ${dimLabel} ${dir} Chile — ${yearMin} al ${yearMax}`);
    subtitleText.text(
      state.metrica === "pasajeros"
        ? "Cantidad acumulada de pasajeros"
        : "Tonelaje acumulado de carga (toneladas)"
    );
  }

  // ── Render frame ──────────────────────────────────

  function renderFrame(animate = true) {
    const period = state.periods[state.periodIndex];
    const year = period[0];
    const month = period[1];

    // Update year label and slider
    yearLabel.textContent = year;
    slider.value = yearIndexFromPeriod(state.periodIndex);

    // Get top N for this period
    const frameData = getFrameData(state.periodIndex);

    // Update scales
    const maxVal = frameData.length > 0 ? frameData[0].value : 1;
    x.domain([0, maxVal * 1.15]);
    y.domain(frameData.map((d) => d.name));

    // Axis
    const axisTop = d3.axisTop(x)
      .ticks(5)
      .tickFormat(state.metrica === "pasajeros" ? fmtInt : fmtDec)
      .tickSize(-barAreaHeight);

    (animate ? gAxis.transition().duration(TRANSITION_MS) : gAxis).call(axisTop);

    gAxis.selectAll(".tick line").attr("stroke", "#e8e8e8");
    gAxis.select(".domain").attr("stroke", "#ccc");

    // Year watermark
    yearText.text(year);

    // ── Bars ──
    const bars = gBars.selectAll(".bar-g").data(frameData, (d) => d.name);

    // Enter
    const enter = bars.enter().append("g").attr("class", "bar-g");

    enter.append("rect").attr("class", "bar-rect");
    enter.append("text").attr("class", "bar-name");
    enter.append("text").attr("class", "bar-group");
    enter.append("text").attr("class", "bar-value");

    // Merge
    const merged = enter.merge(bars);

    const dur = animate ? TRANSITION_MS : 0;

    merged
      .transition()
      .duration(dur)
      .attr("transform", (d) => `translate(0, ${y(d.name)})`);

    merged
      .select(".bar-rect")
      .transition()
      .duration(dur)
      .attr("x", 0)
      .attr("width", (d) => Math.max(0, x(d.value)))
      .attr("height", y.bandwidth())
      .attr("rx", 3)
      .attr("fill", (d) => getColor(d));

    merged
      .select(".bar-name")
      .transition()
      .duration(dur)
      .attr("x", (d) => Math.max(0, x(d.value)) - 8)
      .attr("y", y.bandwidth() / 2 - 3)
      .attr("text-anchor", "end")
      .text((d) => toTitleCase(d.name));

    merged
      .select(".bar-group")
      .transition()
      .duration(dur)
      .attr("x", (d) => Math.max(0, x(d.value)) - 8)
      .attr("y", y.bandwidth() / 2 + 11)
      .attr("text-anchor", "end")
      .text((d) => {
        if (state.dimension === "aerolinea") return "";
        return d.continent || "";
      });

    merged
      .select(".bar-value")
      .transition()
      .duration(dur)
      .attr("x", (d) => Math.max(0, x(d.value)) + 6)
      .attr("y", y.bandwidth() / 2 + 4)
      .text((d) =>
        state.metrica === "pasajeros" ? fmtInt(d.value) : fmtDec(d.value)
      );

    // Exit
    bars
      .exit()
      .transition()
      .duration(dur)
      .attr("transform", `translate(0, ${barAreaHeight + 40})`)
      .style("opacity", 0)
      .remove();

    // Annotation (by year)
    showAnnotation(year);
  }

  // ── Colors ────────────────────────────────────────

  function getColor(d) {
    if (state.colorMap && d.continent) {
      return state.colorMap[d.continent] || "#cccccc";
    }
    // Airline: ordinal palette
    return airlineColor(d.name);
  }

  // ── Annotations ───────────────────────────────────

  let annotationTimeout = null;

  function showAnnotation(year) {
    const ann = state.annotations.find((a) => {
      if (a.year === year) return true;
      if (a.duration && year >= a.year && year < a.year + a.duration) return true;
      return false;
    });

    if (ann) {
      banner.textContent = ann.text;
      banner.classList.add("visible");
      clearTimeout(annotationTimeout);
    } else {
      banner.classList.remove("visible");
    }
  }

  // ── Utilities ─────────────────────────────────────

  function toTitleCase(str) {
    return str
      .toLowerCase()
      .replace(/(^|\s)\S/g, (c) => c.toUpperCase());
  }

  // ── Playback ──────────────────────────────────────

  function play() {
    if (state.playing) return;
    state.playing = true;
    btnPlay.innerHTML = "&#9646;&#9646; Pausa";
    btnPlay.classList.add("playing");

    // If at end, restart
    if (state.periodIndex >= state.periods.length - 1) {
      state.periodIndex = 0;
    }

    tick();
  }

  function pause() {
    state.playing = false;
    btnPlay.innerHTML = "&#9654; Play";
    btnPlay.classList.remove("playing");
    clearTimeout(state.timer);
  }

  function tick() {
    if (!state.playing) return;
    if (state.periodIndex >= state.periods.length - 1) {
      pause();
      return;
    }
    state.periodIndex++;
    renderFrame(true);
    state.timer = setTimeout(tick, FRAME_MS);
  }

  // ── Event handlers ────────────────────────────────

  btnPlay.addEventListener("click", () => {
    state.playing ? pause() : play();
  });

  slider.addEventListener("input", () => {
    pause();
    const yearIdx = parseInt(slider.value);
    const year = state.years[yearIdx];
    // Jump to first month of selected year
    state.periodIndex = state.yearRanges[String(year)][0];
    renderFrame(false);
  });

  // Toggle groups
  function setupToggle(groupId, stateKey, onChange) {
    const group = document.getElementById(groupId);
    group.querySelectorAll("button").forEach((btn) => {
      btn.addEventListener("click", () => {
        if (btn.classList.contains("active")) return;
        group.querySelectorAll("button").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        state[stateKey] = btn.dataset.value;
        if (onChange) onChange();
        pause();
        loadData();
      });
    });
  }

  setupToggle("perspectiva-toggle", "perspectiva", () => {
    // Update dimension label
    dimDestinosBtn.textContent =
      state.perspectiva === "emisivo" ? "Destinos" : "Orígenes";
  });
  setupToggle("dimension-toggle", "dimension");
  setupToggle("metrica-toggle", "metrica");

  // ── Init ──────────────────────────────────────────
  loadData();
})();
