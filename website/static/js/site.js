const menuButton = document.querySelector(".menu-button");
const primaryNav = document.querySelector(".primary-nav");
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

if (menuButton && primaryNav) {
  menuButton.addEventListener("click", () => {
    const open = primaryNav.classList.toggle("open");
    menuButton.setAttribute("aria-expanded", String(open));
  });
}

const plotTheme = () => {
  const dark = document.body.dataset.theme !== "light";
  return {
    paper_bgcolor: dark ? "#161E2E" : "#FFFFFF",
    plot_bgcolor: dark ? "#161E2E" : "#FFFFFF",
    font: { color: dark ? "#DCE5F2" : "#273449", family: "Inter, Segoe UI, sans-serif" },
    "xaxis.gridcolor": dark ? "#263247" : "#E5EAF2",
    "yaxis.gridcolor": dark ? "#263247" : "#E5EAF2",
  };
};

window.renderPlot = (id, figure) => {
  const element = document.getElementById(id);
  if (!element || !window.Plotly) return;
  const themedLayout = { ...figure.layout, ...plotTheme() };
  Object.keys(themedLayout).filter((key) => /^xaxis\d*$|^yaxis\d*$/.test(key)).forEach((key) => {
    themedLayout[key] = {
      ...themedLayout[key],
      gridcolor: document.body.dataset.theme === "light" ? "#E5EAF2" : "#263247",
      zerolinecolor: document.body.dataset.theme === "light" ? "#E5EAF2" : "#263247",
    };
  });
  Plotly.newPlot(element, figure.data, themedLayout, {
    responsive: true,
    displaylogo: false,
    scrollZoom: true,
    modeBarButtonsToAdd: ["drawline", "eraseshape"],
    modeBarButtonsToRemove: ["lasso2d", "select2d", "autoScale2d"],
  });
};

// Command-bar keyboard access.
const tickerSearch = document.getElementById("ticker-search");
document.addEventListener("keydown", (event) => {
  const target = event.target;
  const typing = target instanceof HTMLInputElement || target instanceof HTMLTextAreaElement || target instanceof HTMLSelectElement;
  if ((event.key === "/" && !typing) || ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k")) {
    event.preventDefault();
    tickerSearch?.focus();
    tickerSearch?.select();
  }
});

// Theme and color-blind palette.
const applyPreferences = () => {
  document.body.dataset.theme = localStorage.getItem("mf-theme") || "dark";
  document.body.dataset.palette = localStorage.getItem("mf-palette") || "standard";
};
applyPreferences();
document.querySelector("[data-theme-toggle]")?.addEventListener("click", () => {
  localStorage.setItem("mf-theme", document.body.dataset.theme === "dark" ? "light" : "dark");
  applyPreferences();
  document.querySelectorAll(".js-plotly-plot").forEach((plot) => window.Plotly?.relayout(plot, plotTheme()));
});
document.querySelector("[data-color-toggle]")?.addEventListener("click", () => {
  localStorage.setItem("mf-palette", document.body.dataset.palette === "colorblind" ? "standard" : "colorblind");
  applyPreferences();
});

// NSE calendar status and IST clock. This is not a holiday feed.
const updateClock = () => {
  const now = new Date();
  const parts = new Intl.DateTimeFormat("en-GB", {
    timeZone: "Asia/Kolkata",
    weekday: "short",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  }).formatToParts(now);
  const values = Object.fromEntries(parts.map((part) => [part.type, part.value]));
  const minutes = Number(values.hour) * 60 + Number(values.minute);
  const weekday = values.weekday;
  const tradingDay = !["Sat", "Sun"].includes(weekday);
  const state = tradingDay && minutes >= 555 && minutes <= 930 ? "NSE open*" : "NSE closed*";
  const clock = document.getElementById("market-clock");
  const status = document.getElementById("market-state");
  if (clock) clock.textContent = `${values.hour}:${values.minute}:${values.second} IST`;
  if (status) status.textContent = state;
  document.querySelector(".market-status")?.classList.toggle("is-open", state.includes("open"));
};
updateClock();
setInterval(updateClock, 1000);

// Local watchlist; no account or brokerage connection.
const watchlistKey = "mf-watchlist";
const getWatchlist = () => JSON.parse(localStorage.getItem(watchlistKey) || "[]");
const saveWatchlist = (items) => localStorage.setItem(watchlistKey, JSON.stringify([...new Set(items)].sort()));
const refreshWatchlist = () => {
  const items = getWatchlist();
  const count = document.getElementById("watchlist-count");
  if (count) count.textContent = String(items.length);
  document.querySelectorAll("[data-watch]").forEach((button) => {
    const active = items.includes(button.dataset.watch);
    button.classList.toggle("active", active);
    if (button.classList.contains("watch-star")) button.textContent = active ? "★" : "☆";
    button.setAttribute("aria-pressed", String(active));
  });
  const container = document.getElementById("watchlist-items");
  if (container) {
    container.innerHTML = items.length
      ? items.map((ticker) => `<a href="/cases?ticker=${encodeURIComponent(ticker)}"><strong>${ticker}</strong><span>Open cases</span></a>`).join("")
      : "<p>No tickers saved yet.</p>";
  }
};
document.addEventListener("click", (event) => {
  const button = event.target.closest("[data-watch]");
  if (!button) return;
  event.preventDefault();
  const ticker = button.dataset.watch;
  const items = getWatchlist();
  saveWatchlist(items.includes(ticker) ? items.filter((item) => item !== ticker) : [...items, ticker]);
  refreshWatchlist();
});
refreshWatchlist();

const watchlistDialog = document.getElementById("watchlist-dialog");
document.querySelectorAll("[data-watchlist-open]").forEach((button) => button.addEventListener("click", () => {
  refreshWatchlist();
  watchlistDialog?.showModal();
}));
document.querySelector("[data-dialog-close]")?.addEventListener("click", () => watchlistDialog?.close());

// Small SVG sparklines, rendered from real recent closes.
document.querySelectorAll(".sparkline").forEach((svg) => {
  let values = [];
  try { values = JSON.parse(svg.dataset.values || "[]"); } catch (_) { return; }
  if (values.length < 2) return;
  const width = 96;
  const height = 28;
  const min = Math.min(...values);
  const max = Math.max(...values);
  const scale = max === min ? 1 : max - min;
  const points = values.map((value, index) => {
    const x = (index / (values.length - 1)) * width;
    const y = height - ((value - min) / scale) * (height - 4) - 2;
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(" ");
  svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
  svg.innerHTML = `<polyline points="${points}" fill="none" stroke="currentColor" stroke-width="1.6" vector-effect="non-scaling-stroke"/>`;
});

// Count-up is skipped when reduced motion is requested.
document.querySelectorAll("[data-count]").forEach((node) => {
  const target = Number(node.dataset.count);
  const suffix = node.dataset.suffix || "";
  if (!Number.isFinite(target) || reduceMotion) {
    node.textContent = `${target.toLocaleString()}${suffix}`;
    return;
  }
  const start = performance.now();
  const duration = 650;
  const tick = (now) => {
    const progress = Math.min(1, (now - start) / duration);
    const current = target * (1 - Math.pow(1 - progress, 3));
    node.textContent = `${target % 1 ? current.toFixed(1) : Math.round(current).toLocaleString()}${suffix}`;
    if (progress < 1) requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
});

// Compact/comfortable table density.
const densityTable = document.querySelector("[data-density-table]");
const setDensity = (density) => {
  densityTable?.setAttribute("data-density", density);
  localStorage.setItem("mf-density", density);
};
setDensity(localStorage.getItem("mf-density") || "comfortable");
document.querySelectorAll("[data-density]").forEach((button) => {
  button.addEventListener("click", () => setDensity(button.dataset.density));
});

// Lightweight client-side sorting.
document.querySelectorAll("table[data-sortable] th button[data-sort]").forEach((button) => {
  button.addEventListener("click", () => {
    const table = button.closest("table");
    const index = [...button.closest("tr").children].indexOf(button.closest("th"));
    const rows = [...table.tBodies[0].rows];
    const ascending = button.dataset.direction !== "asc";
    const type = button.dataset.sort;
    rows.sort((left, right) => {
      const aCell = left.cells[index];
      const bCell = right.cells[index];
      const a = type === "number" ? Number(aCell.dataset.value) : aCell.textContent.trim();
      const b = type === "number" ? Number(bCell.dataset.value) : bCell.textContent.trim();
      return (a > b ? 1 : a < b ? -1 : 0) * (ascending ? 1 : -1);
    });
    rows.forEach((row) => table.tBodies[0].appendChild(row));
    button.dataset.direction = ascending ? "asc" : "desc";
  });
});

// Dashboard widgets can be reordered; order persists locally.
const widgetGrid = document.querySelector("[data-widget-grid]");
if (widgetGrid) {
  const savedOrder = JSON.parse(localStorage.getItem("mf-widget-order") || "[]");
  savedOrder.forEach((id) => {
    const widget = widgetGrid.querySelector(`[data-widget="${id}"]`);
    if (widget) widgetGrid.appendChild(widget);
  });
  let dragged = null;
  widgetGrid.querySelectorAll(".widget").forEach((widget) => {
    widget.addEventListener("dragstart", () => { dragged = widget; widget.classList.add("dragging"); });
    widget.addEventListener("dragend", () => {
      widget.classList.remove("dragging");
      localStorage.setItem("mf-widget-order", JSON.stringify([...widgetGrid.children].map((item) => item.dataset.widget)));
      dragged = null;
    });
    widget.addEventListener("dragover", (event) => {
      event.preventDefault();
      if (dragged && dragged !== widget) widgetGrid.insertBefore(dragged, widget);
    });
  });
}
