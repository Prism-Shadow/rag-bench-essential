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

const tableBody = document.querySelector(".results-body");
const sortButtons = [...document.querySelectorAll("[data-sort]")];
let activeSort = { key: "accuracy", direction: "desc" };

function updateRanks() {
  [...tableBody.rows].forEach((row, index) => {
    const badge = row.querySelector(".rank-badge");
    badge.textContent = index + 1;
    badge.className = `rank-badge${index < 3 ? ` rank-${index + 1}` : ""}`;
  });
}

function updateActiveColumn(key) {
  document.querySelectorAll("[data-column]").forEach((cell) => {
    cell.classList.toggle("is-active", cell.dataset.column === key);
  });
}

function sortResults(key, direction) {
  const multiplier = direction === "asc" ? 1 : -1;
  const rows = [...tableBody.rows];
  rows.sort((a, b) => {
    const difference = (Number(a.dataset[key]) - Number(b.dataset[key])) * multiplier;
    return difference || Number(a.dataset.order) - Number(b.dataset.order);
  });
  rows.forEach((row) => tableBody.append(row));
  activeSort = { key, direction };
  sortButtons.forEach((button) => {
    button.querySelector(".sort-arrow").textContent = button.dataset.sort === key ? (direction === "asc" ? "↑" : "↓") : "↕";
  });
  updateActiveColumn(key);
  updateRanks();
}

sortButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const key = button.dataset.sort;
    const defaultDirection = key === "accuracy" ? "desc" : "asc";
    const direction = activeSort.key === key ? (activeSort.direction === "asc" ? "desc" : "asc") : defaultDirection;
    sortResults(key, direction);
  });
});
