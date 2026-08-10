const root = document.documentElement;
const toggle = document.querySelector(".theme-toggle");
const stored = localStorage.getItem("rag-bench-theme");
const preferred = window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";

function applyTheme(theme) {
  root.dataset.theme = theme;
  toggle.setAttribute("aria-pressed", String(theme === "light"));
  document.querySelector('meta[name="theme-color"]').content = theme === "light" ? "#f5f8fc" : "#07111f";
}

applyTheme(stored || preferred);
toggle.addEventListener("click", () => {
  const theme = root.dataset.theme === "dark" ? "light" : "dark";
  localStorage.setItem("rag-bench-theme", theme);
  applyTheme(theme);
});
