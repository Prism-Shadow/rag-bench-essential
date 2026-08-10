const root = document.documentElement;
const themeToggle = document.querySelector(".theme-toggle");
const themeIcon = document.querySelector(".theme-icon");
const localeControl = document.querySelector(".locale-control");
const localeToggle = document.querySelector(".locale-toggle");
const localeLabel = document.querySelector(".locale-label");
const localeMenu = document.querySelector(".locale-menu");
const localeSystemLabel = document.querySelector(".locale-system-label");
const tableHead = document.querySelector(".results-head");
const tableBody = document.querySelector(".results-body");
const chart = document.querySelector("#cost-chart");

const copy = {
  en: {
    title: "Data Analysis Bench",
    description: "Data Analysis Bench compares agents on 15 data-analysis tasks covering documents, spreadsheets, databases, multi-source analysis, and delivery.",
    heroTitle: 'A benchmark for <span>end-to-end data analysis.</span>',
    heroCopy: "15 tasks covering documents, spreadsheets, databases, multi-source analysis, and delivery.",
    viewResults: "View results",
    viewGithub: "View on GitHub",
    benchmarkCases: "Cases",
    benchmarkCasesDesc: "Complex data-analysis tasks spanning documents, spreadsheets, databases, and multi-source workflows.",
    publishedSettings: "Settings",
    publishedSettingsDesc: "Multiple PenguinHarness setups, plus Claude Code and Codex.",
    highestScore: "Best result",
    highestScoreDesc: "PenguinHarness v0.1.5 manual tuning.",
    resultsEyebrow: "Results",
    resultsTitle: "15-case results",
    resultsDescription: "One run per setting. Accuracy is the PASS rate.",
    tableHint: "Swipe to view the full table →",
    loadingResults: "Loading published results…",
    chartTitle: "Performance and cost by setup",
    coverageEyebrow: "Benchmark coverage",
    coverageTitle: "Core challenges in end-to-end data analysis.",
    coverageDescription: "Long-document retrieval, complex tables, cross-source verification, analytical reasoning, and delivery.",
    documentsTitle: "Documents & evidence",
    documentsDescription: "Retrieve and bind evidence across long documents, scanned pages, and multi-document collections.",
    spreadsheetsTitle: "Spreadsheets & table transformation",
    spreadsheetsDescription: "Work with hierarchical tables, formulas, workbook models, and schema normalization.",
    databasesTitle: "Databases & multi-source workflows",
    databasesDescription: "Query relational data, navigate workspace permissions, and reconcile information across sources.",
    analysisTitle: "Analytical reasoning & visualization",
    analysisDescription: "Compute derived metrics and produce or validate analytical visuals.",
    footerText: "Data-analysis agent evaluation",
    rank: "#",
    setting: "Framework",
    model: "Model",
    accuracy: "Accuracy (%)",
    tokens: "Tokens (M)",
    recordedCost: "Cost ($)",
    accuracyAxis: "Accuracy (%)",
    costAxis: "Cost per case (USD)",
    loadError: "Unable to load published results.",
    chartAria: "Scatter plot comparing accuracy and cost per case; colors show harness and model pairs",
  },
  zh: {
    title: "Data Analysis Bench 实验结果",
    description: "Data Analysis Bench 使用 15 道任务比较数据分析智能体，覆盖文档、表格、数据库、跨来源分析和交付。",
    heroTitle: '<span>端到端数据分析</span>评测。',
    heroCopy: "15 道任务，覆盖文档、电子表格、数据库、跨来源分析和交付。",
    viewResults: "查看结果",
    viewGithub: "查看 GitHub",
    benchmarkCases: "任务",
    benchmarkCasesDesc: "复杂数据分析任务，覆盖文档、电子表格、数据库与跨来源工作流。",
    publishedSettings: "配置",
    publishedSettingsDesc: "覆盖 PenguinHarness 多种配置，并加入 Claude Code 与 Codex。",
    highestScore: "最佳结果",
    highestScoreDesc: "PenguinHarness v0.1.5 手动调优。",
    resultsEyebrow: "实验结果",
    resultsTitle: "15 道任务结果表",
    resultsDescription: "每个 setting 保留一轮结果。Accuracy 为 PASS 比例。",
    tableHint: "滑动查看完整表格 →",
    loadingResults: "正在加载已发布结果…",
    chartTitle: "不同配置的效果与成本",
    coverageEyebrow: "Benchmark 覆盖",
    coverageTitle: "覆盖端到端数据分析的关键难点。",
    coverageDescription: "侧重长文档检索、复杂表格处理、多来源核对、分析推理与结果交付。",
    documentsTitle: "文档与证据",
    documentsDescription: "在长文档、扫描页面和多文档集合中检索并绑定证据。",
    spreadsheetsTitle: "电子表格与表格变换",
    spreadsheetsDescription: "处理层次表格、公式、workbook 模型和 schema 归一化。",
    databasesTitle: "数据库与跨来源工作流",
    databasesDescription: "查询关系数据、处理 workspace 权限，并对齐多来源信息。",
    analysisTitle: "分析推理与可视化",
    analysisDescription: "计算衍生指标，并生成或验证分析图表。",
    footerText: "数据分析智能体评测",
    rank: "#",
    setting: "实验框架",
    model: "模型名称",
    accuracy: "准确率（%）",
    tokens: "Token 用量（M）",
    recordedCost: "成本（$）",
    accuracyAxis: "Accuracy（%）",
    costAxis: "单题成本（美元）",
    loadError: "无法加载已发布结果。",
    chartAria: "比较 8 个配置的 Accuracy 和单题成本；颜色表示 harness 与模型组合",
  },
};

const state = {
  localePreference: ["en", "zh", "system"].includes(root.dataset.localePref) ? root.dataset.localePref : "system",
  locale: root.dataset.locale === "zh" ? "zh" : "en",
  themeMode: ["light", "dark", "system"].includes(root.dataset.themeMode) ? root.dataset.themeMode : "system",
  results: [],
  sort: { key: "accuracy", direction: "desc" },
};

const localeNames = {
  en: { en: "English", zh: "中文", system: "Follow system", language: "Language" },
  zh: { en: "English", zh: "中文", system: "跟随系统", language: "语言" },
};

const themeNames = {
  en: { light: "Light", dark: "Dark", system: "Follow system", label: "Theme" },
  zh: { light: "浅色", dark: "深色", system: "跟随系统", label: "主题" },
};

const themeIcons = {
  light: '<svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"></circle><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"></path></svg>',
  dark: '<svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"></path></svg>',
  system: '<svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2"></rect><path d="M8 21h8M12 17v4"></path></svg>',
};

function systemLocale() {
  return navigator.language.toLowerCase().startsWith("zh") ? "zh" : "en";
}

function resolvedTheme(mode) {
  if (mode !== "system") return mode;
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

const sortableColumns = {
  accuracy: { label: "accuracy", defaultDirection: "desc" },
  tokens_m_per_run: { label: "tokens", defaultDirection: "asc" },
  recorded_cost_usd_per_run: { label: "recordedCost", defaultDirection: "asc" },
};

function tokensMPerRun(row) {
  return row.tokens_per_run / 1_000_000;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function accuracyPercent(row) {
  return (row.accuracy_passes / row.accuracy_total) * 100;
}

function valueForSort(row, key) {
  if (key === "accuracy") return row.accuracy_passes;
  if (key === "tokens_m_per_run") return tokensMPerRun(row);
  return row[key];
}

function sortedResults() {
  const multiplier = state.sort.direction === "asc" ? 1 : -1;
  return [...state.results].sort((left, right) => {
    const difference = (valueForSort(left, state.sort.key) - valueForSort(right, state.sort.key)) * multiplier;
    return difference || left.order - right.order;
  });
}

function frameworkLogo(row) {
  if (row.framework === "PenguinHarness") {
    return '<img src="https://penguin.ooo/penguin-logo.svg" alt="" />';
  }
  const slug = row.framework === "Claude Code" ? "anthropic" : "openai";
  return `<img class="vendor-logo" src="https://cdn.jsdelivr.net/npm/simple-icons@v14/icons/${slug}.svg" alt="" />`;
}

function formatRunCost(value) {
  return value < 1 ? `$${value.toFixed(4)}` : `$${value.toFixed(2)}`;
}

function sortableHeader(key) {
  const t = copy[state.locale];
  const column = sortableColumns[key];
  const active = state.sort.key === key;
  const direction = active ? state.sort.direction : "none";
  const ariaSort = direction === "asc" ? "ascending" : direction === "desc" ? "descending" : "none";
  const arrow = !active ? "↕" : direction === "asc" ? "↑" : "↓";
  return `<th class="numeric sortable ${active ? "is-active" : ""}" data-column="${key}" aria-sort="${ariaSort}">
    <button type="button" data-sort="${key}">${t[column.label]} <span class="sort-arrow" aria-hidden="true">${arrow}</span></button>
  </th>`;
}

function renderTable() {
  if (!state.results.length) return;
  const t = copy[state.locale];
  tableHead.innerHTML = `<tr>
    <th class="rank-column">${t.rank}</th>
    <th>${t.setting}</th>
    <th>${t.model}</th>
    ${sortableHeader("accuracy")}
    ${sortableHeader("tokens_m_per_run")}
    ${sortableHeader("recorded_cost_usd_per_run")}
  </tr>`;

  tableBody.innerHTML = sortedResults()
    .map((row, index) => {
      const configuration = state.locale === "zh" ? row.configuration_zh : row.configuration;
      const setup = row.framework === "PenguinHarness" ? `${row.framework} ${row.version}` : row.framework;
      const percentage = accuracyPercent(row);
      const rankClass = index < 3 ? ` rank-${index + 1}` : "";
      return `<tr>
        <td class="rank-cell"><span class="rank-badge${rankClass}">${index + 1}</span></td>
        <td>
          <span class="setup-cell">${frameworkLogo(row)}${escapeHtml(setup)}</span>
          <span class="config-meta" title="${escapeHtml(configuration)}">${escapeHtml(configuration)}</span>
        </td>
        <td>${escapeHtml(row.model)}</td>
        <td class="numeric accuracy-cell ${state.sort.key === "accuracy" ? "is-active" : ""}" data-column="accuracy">
          <span class="accuracy-measure">
            <span class="accuracy-track" aria-hidden="true"><span class="accuracy-fill" style="--accuracy:${percentage}%"></span></span>
            <strong>${percentage.toFixed(1)}%</strong>
          </span>
        </td>
        <td class="numeric ${state.sort.key === "tokens_m_per_run" ? "is-active" : ""}" data-column="tokens_m_per_run">${tokensMPerRun(row).toFixed(2)}</td>
        <td class="numeric ${state.sort.key === "recorded_cost_usd_per_run" ? "is-active" : ""}" data-column="recorded_cost_usd_per_run">${formatRunCost(row.recorded_cost_usd_per_run)}</td>
      </tr>`;
    })
    .join("");
}

function applyLocale() {
  const t = copy[state.locale];
  root.dataset.locale = state.locale;
  root.lang = state.locale === "zh" ? "zh-CN" : "en";
  document.title = t.title;
  document.querySelector('meta[name="description"]').content = t.description;
  document.querySelectorAll("[data-i18n]").forEach((element) => {
    const value = t[element.dataset.i18n];
    if (value) element.textContent = value;
  });
  document.querySelectorAll("[data-i18n-html]").forEach((element) => {
    const value = t[element.dataset.i18nHtml];
    if (value) element.innerHTML = value;
  });
  const names = localeNames[state.locale];
  localeLabel.textContent = names[state.localePreference];
  localeSystemLabel.textContent = names.system;
  localeToggle.title = names.language;
  localeToggle.setAttribute("aria-label", names.language);
  localeMenu.querySelectorAll("[data-locale-pref]").forEach((option) => {
    option.setAttribute("aria-checked", String(option.dataset.localePref === state.localePreference));
  });
  applyTheme(state.themeMode);
  chart.setAttribute("aria-label", t.chartAria);
  renderTable();
  renderChart();
}

function applyTheme(mode) {
  state.themeMode = mode;
  const theme = resolvedTheme(mode);
  root.dataset.themeMode = mode;
  root.dataset.theme = theme;
  themeIcon.innerHTML = themeIcons[mode];
  const names = themeNames[state.locale];
  const label = `${names.label}: ${names[mode]}`;
  themeToggle.title = label;
  themeToggle.setAttribute("aria-label", label);
  document.querySelector('meta[name="theme-color"]').content = theme === "light" ? "#ffffff" : "#000000";
}

function chartModelClass(model) {
  if (model === "Claude Opus 4.8") return "model-opus";
  if (model === "GPT-5.5") return "model-gpt";
  return "model-deepseek";
}

function costPerCase(row) {
  return row.recorded_cost_usd_per_run / row.accuracy_total;
}

function formatCaseCost(value) {
  return value < 0.1 ? `$${value.toFixed(4)}` : `$${value.toFixed(2)}`;
}

function renderChart() {
  if (!state.results.length) return;
  const t = copy[state.locale];
  const xMin = Math.log10(0.01);
  const xMax = Math.log10(3);
  const yMin = 50;
  const yMax = 76;
  const xPosition = (value) => ((Math.log10(value) - xMin) / (xMax - xMin)) * 100;
  const yPosition = (value) => ((value - yMin) / (yMax - yMin)) * 100;
  const xTicks = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 3];
  const yTicks = [50, 60, 70];
  const verticalGrid = xTicks.map((tick) => `
    <span class="chart-grid chart-grid-x" style="--position:${xPosition(tick)}%">
      <span class="chart-tick chart-tick-x">$${tick}</span>
    </span>`).join("");
  const horizontalGrid = yTicks.map((tick) => `
    <span class="chart-grid chart-grid-y" style="--position:${yPosition(tick)}%">
      <span class="chart-tick chart-tick-y">${tick}</span>
    </span>`).join("");
  const points = state.results.map((row) => {
    const configuration = state.locale === "zh" ? row.configuration_zh : row.configuration;
    const setup = row.framework === "PenguinHarness" ? `${row.framework} ${row.version}` : row.framework;
    const details = `${setup}, ${configuration}, ${row.model}, ${row.accuracy_passes}/${row.accuracy_total}, ${formatCaseCost(costPerCase(row))}`;
    const tooltipSide = xPosition(costPerCase(row)) > 72 ? " tooltip-left" : "";
    return `<button class="chart-point ${chartModelClass(row.model)}${tooltipSide}" style="--x:${xPosition(costPerCase(row))}%;--y:${yPosition(accuracyPercent(row))}%" type="button" aria-label="${escapeHtml(details)}">
      <span class="chart-point-dot" aria-hidden="true"></span>
      <span class="chart-point-tooltip" aria-hidden="true"><strong>${escapeHtml(setup)}</strong><span>${escapeHtml(configuration)}</span></span>
    </button>`;
  }).join("");
  chart.innerHTML = `<div class="chart-plot">
    ${verticalGrid}${horizontalGrid}${points}
    <span class="chart-axis-title chart-axis-x">${escapeHtml(t.costAxis)}</span>
    <span class="chart-axis-title chart-axis-y">${escapeHtml(t.accuracyAxis)}</span>
  </div>`;
}

themeToggle.addEventListener("click", () => {
  const next = { light: "dark", dark: "system", system: "light" }[state.themeMode];
  localStorage.setItem("data-analysis-bench.theme", next);
  applyTheme(next);
});

localeToggle.addEventListener("click", () => {
  const open = localeMenu.hidden;
  localeMenu.hidden = !open;
  localeToggle.setAttribute("aria-expanded", String(open));
});

localeMenu.addEventListener("click", (event) => {
  const option = event.target.closest("[data-locale-pref]");
  if (!option) return;
  state.localePreference = option.dataset.localePref;
  state.locale = state.localePreference === "system" ? systemLocale() : state.localePreference;
  root.dataset.localePref = state.localePreference;
  localStorage.setItem("data-analysis-bench.locale", state.localePreference);
  localeMenu.hidden = true;
  localeToggle.setAttribute("aria-expanded", "false");
  applyLocale();
});

document.addEventListener("mousedown", (event) => {
  if (!localeMenu.hidden && !localeControl.contains(event.target)) {
    localeMenu.hidden = true;
    localeToggle.setAttribute("aria-expanded", "false");
  }
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !localeMenu.hidden) {
    localeMenu.hidden = true;
    localeToggle.setAttribute("aria-expanded", "false");
    localeToggle.focus();
  }
});

window.addEventListener("languagechange", () => {
  if (state.localePreference !== "system") return;
  state.locale = systemLocale();
  applyLocale();
});

window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => {
  if (state.themeMode === "system") applyTheme("system");
});

tableHead.addEventListener("click", (event) => {
  const button = event.target.closest("[data-sort]");
  if (!button) return;
  const key = button.dataset.sort;
  if (state.sort.key === key) {
    state.sort.direction = state.sort.direction === "asc" ? "desc" : "asc";
  } else {
    state.sort = { key, direction: sortableColumns[key].defaultDirection };
  }
  renderTable();
});

applyTheme(state.themeMode);
applyLocale();

try {
  const payload = JSON.parse(document.querySelector("#results-data").textContent);
  if (!Array.isArray(payload.results)) throw new Error("embedded results are missing");
  state.results = payload.results;
  renderTable();
  renderChart();
} catch (error) {
  console.error(copy[state.locale].loadError, error);
  tableBody.innerHTML = `<tr><td class="loading-cell" colspan="6">${copy[state.locale].loadError}</td></tr>`;
}
