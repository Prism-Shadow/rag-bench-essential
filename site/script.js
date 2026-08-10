const root = document.documentElement;
const themeToggle = document.querySelector(".theme-toggle");
const localeToggle = document.querySelector(".locale-toggle");
const tableHead = document.querySelector(".results-head");
const tableBody = document.querySelector(".results-body");
const canvas = document.querySelector("#cost-chart");
const chartTooltip = document.querySelector(".chart-tooltip");

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
    benchmarkCasesDesc: "From 15 public benchmarks.",
    publishedSettings: "Settings",
    publishedSettingsDesc: "Eight configurations across PenguinHarness, Claude Code, and Codex.",
    highestScore: "Best result",
    highestScoreDesc: "Passed 11 cases.",
    resultsEyebrow: "Results",
    resultsTitle: "15-case results",
    resultsDescription: "One run per setting. Accuracy counts hard PASS cases.",
    tableHint: "Swipe to view the full table →",
    loadingResults: "Loading published results…",
    resourceNote: "Time is averaged per case. Tokens and recorded cost cover one 15-case run. Penguin could use Gemini vision; its proxy cost was not retained. Claude Code and Codex had no auxiliary vision tool.",
    regradeNote: "Claude Code includes the 2026-08-10 BankerToolBench regrade. The other rows remain historical because their workspaces were not retained.",
    chartTitle: "Performance and cost by setup",
    chartNote: "Colors show models; labels show harness setups. Cost is shown per case on a log scale.",
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
    coverageNote: "Full benchmark leaderboards remain the source for benchmark-wide results.",
    footerText: "Data-analysis agent evaluation",
    rank: "#",
    setting: "Setting",
    model: "Model",
    accuracy: "Accuracy",
    averageTime: "Avg. time / case",
    tokens: "Tokens / run",
    recordedCost: "Recorded cost / run",
    accuracyAxis: "Accuracy (%)",
    costAxis: "Cost per case (USD, log scale)",
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
    benchmarkCasesDesc: "来自 15 个公开 benchmark。",
    publishedSettings: "配置",
    publishedSettingsDesc: "PenguinHarness、Claude Code 和 Codex 共 8 组。",
    highestScore: "最佳结果",
    highestScoreDesc: "通过 11 道。",
    resultsEyebrow: "实验结果",
    resultsTitle: "15 道任务结果表",
    resultsDescription: "每个 setting 保留一轮结果。Accuracy 为 hard PASS 数量。",
    tableHint: "滑动查看完整表格 →",
    loadingResults: "正在加载已发布结果…",
    resourceNote: "时间为单题平均值。Token 和已记录成本按 15 道题合计。Penguin 可使用 Gemini 视觉工具，代理费用未保留。Claude Code 和 Codex 没有辅助视觉工具。",
    regradeNote: "Claude Code 包含 2026-08-10 的 BankerToolBench 重评。其余行因未保留 workspace，继续使用历史结果。",
    chartTitle: "不同配置的效果与成本",
    chartNote: "颜色表示模型，标签表示 harness 配置；横轴为单题成本，使用对数刻度。",
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
    coverageNote: "各 benchmark 的完整结果以其官方 leaderboard 为准。",
    footerText: "数据分析智能体评测",
    rank: "#",
    setting: "Setting",
    model: "模型",
    accuracy: "Accuracy",
    averageTime: "平均单题耗时",
    tokens: "Token / 轮",
    recordedCost: "已记录成本 / 轮",
    accuracyAxis: "Accuracy（%）",
    costAxis: "单题成本（美元，对数刻度）",
    loadError: "无法加载已发布结果。",
    chartAria: "比较 8 个配置的 Accuracy 和单题成本；颜色表示模型，标签表示 harness 配置",
  },
};

const state = {
  locale: root.dataset.locale === "zh" ? "zh" : "en",
  results: [],
  sort: { key: "accuracy", direction: "desc" },
  chartPoints: [],
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
  canvas.setAttribute("aria-label", t.chartAria);
  renderTable();
  drawChart();
}

function applyTheme(theme) {
  root.dataset.theme = theme;
  themeToggle.setAttribute("aria-pressed", String(theme === "light"));
  document.querySelector('meta[name="theme-color"]').content = theme === "light" ? "#ffffff" : "#000000";
  drawChart();
}

function chartColor(model) {
  if (model === "Claude Opus 4.8") return "#ef4444";
  if (model === "GPT-5.5") return "#10b981";
  return "#2563eb";
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

function drawChart() {
  if (!state.results.length || !canvas.clientWidth) return;
  const textColor = "#0f172a";
  const mutedColor = "#64748b";
  const lineColor = "#e2e8f0";
  const surfaceColor = "#ffffff";
  const width = canvas.clientWidth;
  const height = canvas.clientHeight;
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  canvas.width = Math.round(width * dpr);
  canvas.height = Math.round(height * dpr);
  const context = canvas.getContext("2d");
  context.setTransform(dpr, 0, 0, dpr, 0, 0);
  context.clearRect(0, 0, width, height);

  const compact = width < 620;
  const margin = { top: 24, right: 28, bottom: 58, left: compact ? 52 : 64 };
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const costs = state.results.map(costPerCase);
  const minLog = Math.log10(Math.min(...costs) / 1.5);
  const maxLog = Math.log10(Math.max(...costs) * 1.4);
  const yMin = 50;
  const yMax = 76;
  const xPosition = (value) => margin.left + ((Math.log10(value) - minLog) / (maxLog - minLog)) * plotWidth;
  const yPosition = (value) => margin.top + ((yMax - value) / (yMax - yMin)) * plotHeight;

  context.font = `${compact ? 10 : 11}px ui-sans-serif, system-ui, sans-serif`;
  context.lineWidth = 1;
  context.textBaseline = "middle";
  context.textAlign = "right";
  [50, 60, 70].forEach((tick) => {
    const y = yPosition(tick);
    context.strokeStyle = lineColor;
    context.beginPath();
    context.moveTo(margin.left, y);
    context.lineTo(width - margin.right, y);
    context.stroke();
    context.fillStyle = mutedColor;
    context.fillText(String(tick), margin.left - 10, y);
  });

  const xTicks = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 3].filter((tick) => Math.log10(tick) >= minLog && Math.log10(tick) <= maxLog);
  context.textAlign = "center";
  xTicks.forEach((tick) => {
    const x = xPosition(tick);
    context.strokeStyle = lineColor;
    context.beginPath();
    context.moveTo(x, margin.top);
    context.lineTo(x, height - margin.bottom);
    context.stroke();
    context.fillStyle = mutedColor;
    context.fillText(`$${tick}`, x, height - margin.bottom + 18);
  });

  const t = copy[state.locale];
  context.fillStyle = mutedColor;
  context.font = `11px ui-sans-serif, system-ui, sans-serif`;
  context.fillText(t.costAxis, margin.left + plotWidth / 2, height - 12);
  context.save();
  context.translate(14, margin.top + plotHeight / 2);
  context.rotate(-Math.PI / 2);
  context.fillText(t.accuracyAxis, 0, 0);
  context.restore();

  state.chartPoints = state.results.map((row) => {
    const x = xPosition(costPerCase(row));
    const y = yPosition(accuracyPercent(row));
    context.beginPath();
    context.arc(x, y, 6.5, 0, Math.PI * 2);
    context.fillStyle = chartColor(row.model);
    context.fill();
    context.lineWidth = 2;
    context.strokeStyle = surfaceColor;
    context.stroke();
    return { x, y, row };
  });

  const labelOffsets = {
    "penguin-015-manual": -13,
    "penguin-015-manual-goal": 13,
    "penguin-015-auto-state": -9,
    "penguin-015-original": -11,
    "penguin-001-manual": 12,
    "penguin-001-original": -9,
    "claude-opus-48": -11,
    "codex-gpt-55": 12,
  };
  context.font = `${compact ? 9 : 10}px ui-sans-serif, system-ui, sans-serif`;
  context.fillStyle = textColor;
  context.textAlign = "left";
  state.chartPoints.forEach(({ x, y, row }) => {
    const label = chartLabel(row);
    const labelWidth = context.measureText(label).width;
    const preferLeft = row.id === "claude-opus-48" || x + labelWidth + 14 > width - margin.right;
    const labelX = preferLeft ? x - labelWidth - 11 : x + 11;
    const labelY = y + labelOffsets[row.id];
    context.fillText(label, labelX, labelY);
  });
}

function hideChartTooltip() {
  chartTooltip.hidden = true;
}

function showChartTooltip(event) {
  const bounds = canvas.getBoundingClientRect();
  const x = event.clientX - bounds.left;
  const y = event.clientY - bounds.top;
  const point = state.chartPoints.find((candidate) => Math.hypot(candidate.x - x, candidate.y - y) <= 12);
  if (!point) {
    hideChartTooltip();
    return;
  }
  const row = point.row;
  const setting = state.locale === "zh" ? row.setting_zh : row.setting;
  chartTooltip.innerHTML = `<strong>${escapeHtml(setting)}</strong><span>${escapeHtml(row.model)}</span><span>${row.accuracy_passes}/${row.accuracy_total} · ${formatCaseCost(costPerCase(row))}/case</span>`;
  chartTooltip.hidden = false;
  const tooltipWidth = chartTooltip.offsetWidth;
  const tooltipHeight = chartTooltip.offsetHeight;
  chartTooltip.style.left = `${Math.min(Math.max(point.x + 12, 8), bounds.width - tooltipWidth - 8)}px`;
  chartTooltip.style.top = `${Math.max(point.y - tooltipHeight - 12, 8)}px`;
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

canvas.addEventListener("pointermove", showChartTooltip);
canvas.addEventListener("pointerleave", hideChartTooltip);

let resizeFrame;
const redrawOnResize = () => {
  cancelAnimationFrame(resizeFrame);
  resizeFrame = requestAnimationFrame(drawChart);
};
if ("ResizeObserver" in window) {
  new ResizeObserver(redrawOnResize).observe(canvas);
} else {
  window.addEventListener("resize", redrawOnResize);
}

applyTheme(root.dataset.theme === "light" ? "light" : "dark");
applyLocale();

try {
  const payload = JSON.parse(document.querySelector("#results-data").textContent);
  if (!Array.isArray(payload.results)) throw new Error("embedded results are missing");
  state.results = payload.results;
  renderTable();
  drawChart();
} catch (error) {
  console.error(copy[state.locale].loadError, error);
  tableBody.innerHTML = `<tr><td class="loading-cell" colspan="7">${copy[state.locale].loadError}</td></tr>`;
}
