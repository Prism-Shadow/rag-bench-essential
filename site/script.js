const root = document.documentElement;
const toggle = document.querySelector(".theme-toggle");
const stored = localStorage.getItem("rag-bench-theme");

function applyTheme(theme) {
  root.dataset.theme = theme;
  toggle.setAttribute("aria-pressed", String(theme === "light"));
  document.querySelector('meta[name="theme-color"]').content = theme === "light" ? "#ffffff" : "#000000";
}

applyTheme(stored || "dark");
toggle.addEventListener("click", () => {
  const theme = root.dataset.theme === "dark" ? "light" : "dark";
  localStorage.setItem("rag-bench-theme", theme);
  applyTheme(theme);
});

const chartRoot = document.querySelector("[data-results-charts]");
const resultRows = [...document.querySelectorAll("tbody tr[data-chart-label]")].map((row) => {
  const cells = row.querySelectorAll("td");
  const [passed, total] = cells[2].textContent.trim().split("/").map(Number);
  return {
    label: row.dataset.chartLabel,
    accuracy: (passed / total) * 100,
    accuracyLabel: cells[2].textContent.trim(),
    tokens: Number.parseFloat(cells[4].textContent),
    tokensLabel: cells[4].textContent.trim(),
    cost: Number.parseFloat(cells[5].textContent.replace("$", "")),
    costLabel: cells[5].textContent.trim(),
    highlight: row.classList.contains("highlight"),
  };
});

const chartSpecs = [
  { key: "accuracy", labelKey: "accuracyLabel", title: "Accuracy", hint: "higher is better ↑" },
  { key: "tokens", labelKey: "tokensLabel", title: "Tokens", hint: "lower is better ↓" },
  { key: "cost", labelKey: "costLabel", title: "Cost", hint: "lower is better ↓" },
];

chartSpecs.forEach(({ key, labelKey, title, hint }) => {
  const max = key === "accuracy" ? 100 : Math.max(...resultRows.map((row) => row[key]));
  const figure = document.createElement("figure");
  figure.className = "chart-panel";
  figure.innerHTML = `<figcaption><strong>${title}</strong><span>${hint}</span></figcaption>`;

  const rows = document.createElement("div");
  rows.className = "chart-rows";
  resultRows.forEach((row) => {
    const item = document.createElement("div");
    item.className = `chart-row${row.highlight ? " is-highlight" : ""}`;
    item.innerHTML = `
      <span class="chart-label">${row.label}</span>
      <span class="chart-track"><i style="--bar:${Math.max(1.5, (row[key] / max) * 100)}%"></i></span>
      <b>${row[labelKey]}</b>
    `;
    rows.append(item);
  });
  figure.append(rows);
  chartRoot.append(figure);
});
