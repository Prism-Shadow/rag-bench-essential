const root = document.documentElement;
const themeToggle = document.querySelector(".theme-toggle");
const localeToggle = document.querySelector(".locale-toggle");
const tableHead = document.querySelector(".results-head");
const tableBody = document.querySelector(".results-body");
const chart = document.querySelector("#cost-chart");

const copy = {
  en: {
    title: "Data Analysis Bench",
    description: "Data Analysis Bench compares agents on 15 data-analysis tasks covering documents, spreadsheets, databases, multi-source analysis, and delivery.",
    navResults: "Results",
    navCases: "Cases",
    heroTitle: 'A benchmark for <span>end-to-end data analysis.</span>',
    heroCopy: "15 tasks covering documents, spreadsheets, databases, multi-source analysis, and delivery.",
    viewResults: "View results",
    viewGithub: "View on GitHub",
    benchmarkCases: "Cases",
    publishedSettings: "Settings",
    highestScore: "Best result",
    resultsEyebrow: "Results",
    resultsTitle: "15-case results",
    resultsDescription: "One run per setting. Accuracy counts hard PASS cases.",
    tableHint: "Swipe to view the full table →",
    loadingResults: "Loading published results…",
    resourceNote: "Time is averaged per case. Tokens and recorded cost cover one 15-case run. Penguin could use Gemini vision; its proxy cost was not retained. Claude Code and Codex had no auxiliary vision tool.",
    regradeNote: "Claude Code includes the 2026-08-10 BankerToolBench regrade. The other rows remain historical because their workspaces were not retained.",
    chartTitle: "Performance and cost by setup",
    coverageEyebrow: "Benchmark coverage",
    coverageTitle: "15 cases from 15 public benchmarks.",
    coverageDescription: "One selected case from each benchmark.",
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
    setting: "Setting",
    model: "Model",
    accuracy: "Accuracy",
    averageTime: "Avg. time / case",
    tokens: "Tokens / run",
    recordedCost: "Recorded cost / run",
    accuracyAxis: "Accuracy (%)",
    costAxis: "Cost per case (USD)",
    loadError: "Unable to load published results.",
    chartAria: "Scatter plot comparing accuracy and cost per case; colors show models and labels show harness setups",
  },
  zh: {
    title: "Data Analysis Bench 实验结果",
    description: "Data Analysis Bench 使用 15 道任务比较数据分析智能体，覆盖文档、表格、数据库、跨来源分析和交付。",
    navResults: "结果",
    navCases: "任务",
    heroTitle: '<span>端到端数据分析</span>评测。',
    heroCopy: "15 道任务，覆盖文档、电子表格、数据库、跨来源分析和交付。",
    viewResults: "查看结果",
    viewGithub: "查看 GitHub",
    benchmarkCases: "任务",
    publishedSettings: "配置",
    highestScore: "最佳结果",
    resultsEyebrow: "实验结果",
    resultsTitle: "15 道任务结果表",
    resultsDescription: "每个 setting 保留一轮结果。Accuracy 为 hard PASS 数量。",
    tableHint: "滑动查看完整表格 →",
    loadingResults: "正在加载已发布结果…",
    resourceNote: "时间为单题平均值。Token 和已记录成本按 15 道题合计。Penguin 可使用 Gemini 视觉工具，代理费用未保留。Claude Code 和 Codex 没有辅助视觉工具。",
    regradeNote: "Claude Code 包含 2026-08-10 的 BankerToolBench 重评。其余行因未保留 workspace，继续使用历史结果。",
    chartTitle: "不同配置的效果与成本",
    coverageEyebrow: "Benchmark 覆盖",
    coverageTitle: "15 道任务，来自 15 个公开 benchmark。",
    coverageDescription: "每个 benchmark 选取一道代表性任务。",
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
    setting: "Setting",
    model: "模型",
    accuracy: "Accuracy",
    averageTime: "平均单题耗时",
    tokens: "Token / 轮",
    recordedCost: "已记录成本 / 轮",
    accuracyAxis: "Accuracy（%）",
    costAxis: "单题成本（美元）",
    loadError: "无法加载已发布结果。",
    chartAria: "比较 8 个配置的 Accuracy 和单题成本；颜色表示模型，标签表示 harness 配置",
  },
};

const state = {
  locale: root.dataset.locale === "zh" ? "zh" : "en",
  results: [],
  sort: { key: "accuracy", direction: "desc" },
};

const sortableColumns = {
  accuracy: { label: "accuracy", defaultDirection: "desc" },
  minutes_per_case: { label: "averageTime", defaultDirection: "asc" },
  tokens_m_per_run: { label: "tokens", defaultDirection: "asc" },
  recorded_cost_usd_per_run: { label: "recordedCost", defaultDirection: "asc" },
};

function minutesPerCase(row) {
  return row.time_seconds_per_run / 60 / row.accuracy_total;
}

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
  if (key === "minutes_per_case") return minutesPerCase(row);
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

function formatCost(value) {
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
    ${sortableHeader("minutes_per_case")}
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
            <strong>${row.accuracy_passes}/${row.accuracy_total}</strong>
          </span>
        </td>
        <td class="numeric ${state.sort.key === "minutes_per_case" ? "is-active" : ""}" data-column="minutes_per_case">${minutesPerCase(row).toFixed(2)}m</td>
        <td class="numeric ${state.sort.key === "tokens_m_per_run" ? "is-active" : ""}" data-column="tokens_m_per_run">${tokensMPerRun(row).toFixed(2)}M</td>
        <td class="numeric ${state.sort.key === "recorded_cost_usd_per_run" ? "is-active" : ""}" data-column="recorded_cost_usd_per_run">${formatCost(row.recorded_cost_usd_per_run)}</td>
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
  localeToggle.textContent = state.locale === "zh" ? "EN" : "中";
  localeToggle.setAttribute("aria-label", state.locale === "zh" ? "Switch to English" : "切换到中文");
  themeToggle.setAttribute("aria-label", state.locale === "zh" ? "切换颜色主题" : "Switch color theme");
  chart.setAttribute("aria-label", t.chartAria);
  renderTable();
  renderChart();
}

function applyTheme(theme) {
  root.dataset.theme = theme;
  themeToggle.setAttribute("aria-pressed", String(theme === "light"));
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

function chartLabel(row) {
  const labels = {
    en: {
      "penguin-015-manual": "PH .1.5 · manual",
      "penguin-015-manual-goal": "PH .1.5 · manual + Goal",
      "penguin-015-auto-state": "PH .1.5 · auto state",
      "penguin-015-original": "PH .1.5 · no skill",
      "penguin-001-manual": "PH .0.1 · manual",
      "penguin-001-original": "PH .0.1 · no skill",
      "claude-opus-48": "Claude Code",
      "codex-gpt-55": "Codex",
    },
    zh: {
      "penguin-015-manual": "PH .1.5 · 手写 Skill",
      "penguin-015-manual-goal": "PH .1.5 · 手写 Skill + Goal",
      "penguin-015-auto-state": "PH .1.5 · 自动优化 State",
      "penguin-015-original": "PH .1.5 · 无 Skill",
      "penguin-001-manual": "PH .0.1 · 手写 Skill",
      "penguin-001-original": "PH .0.1 · 无 Skill",
      "claude-opus-48": "Claude Code",
      "codex-gpt-55": "Codex",
    },
  };
  return labels[state.locale][row.id];
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
  const labelPositions = {
    "penguin-015-manual": { side: "right", offset: -26 },
    "penguin-015-manual-goal": { side: "right", offset: 10 },
    "penguin-015-auto-state": { side: "right", offset: -18 },
    "penguin-015-original": { side: "right", offset: -22 },
    "penguin-001-manual": { side: "right", offset: 10 },
    "penguin-001-original": { side: "right", offset: -18 },
    "claude-opus-48": { side: "left", offset: -20 },
    "codex-gpt-55": { side: "right", offset: 10 },
  };
  const verticalGrid = xTicks.map((tick) => `
    <span class="chart-grid chart-grid-x" style="--position:${xPosition(tick)}%">
      <span class="chart-tick chart-tick-x">$${tick}</span>
    </span>`).join("");
  const horizontalGrid = yTicks.map((tick) => `
    <span class="chart-grid chart-grid-y" style="--position:${yPosition(tick)}%">
      <span class="chart-tick chart-tick-y">${tick}</span>
    </span>`).join("");
  const points = state.results.map((row) => {
    const labelPosition = labelPositions[row.id];
    const setting = state.locale === "zh" ? row.setting_zh : row.setting;
    const details = `${setting}, ${row.model}, ${row.accuracy_passes}/${row.accuracy_total}, ${formatCaseCost(costPerCase(row))}`;
    return `<button class="chart-point ${chartModelClass(row.model)} label-${labelPosition.side}" style="--x:${xPosition(costPerCase(row))}%;--y:${yPosition(accuracyPercent(row))}%;--label-y:${labelPosition.offset}px" type="button" aria-label="${escapeHtml(details)}" title="${escapeHtml(details)}">
      <span class="chart-point-dot" aria-hidden="true"></span>
      <span class="chart-point-label" aria-hidden="true">${escapeHtml(chartLabel(row))}</span>
    </button>`;
  }).join("");
  chart.innerHTML = `<div class="chart-plot">
    ${verticalGrid}${horizontalGrid}${points}
    <span class="chart-axis-title chart-axis-x">${escapeHtml(t.costAxis)}</span>
    <span class="chart-axis-title chart-axis-y">${escapeHtml(t.accuracyAxis)}</span>
  </div>`;
}

themeToggle.addEventListener("click", () => {
  const theme = root.dataset.theme === "dark" ? "light" : "dark";
  localStorage.setItem("data-analysis-bench.theme", theme);
  applyTheme(theme);
});

localeToggle.addEventListener("click", () => {
  state.locale = state.locale === "zh" ? "en" : "zh";
  localStorage.setItem("data-analysis-bench.locale", state.locale);
  applyLocale();
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

applyTheme(root.dataset.theme === "light" ? "light" : "dark");
applyLocale();

try {
  const payload = JSON.parse(document.querySelector("#results-data").textContent);
  if (!Array.isArray(payload.results)) throw new Error("embedded results are missing");
  state.results = payload.results;
  renderTable();
  renderChart();
} catch (error) {
  console.error(copy[state.locale].loadError, error);
  tableBody.innerHTML = `<tr><td class="loading-cell" colspan="7">${copy[state.locale].loadError}</td></tr>`;
}
