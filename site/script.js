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
    description: "Data Analysis Bench is a reproducible suite of 15 difficult tasks spanning documents, spreadsheets, databases, multi-source analysis, and delivery.",
    navResults: "Results",
    navCases: "Cases",
    heroTitle: 'A reproducible benchmark for <span>end-to-end data analysis.</span>',
    heroCopy: "Fifteen production-shaped tasks spanning documents, spreadsheets, databases, multi-source analysis, and delivery.",
    viewResults: "View results",
    viewGithub: "View on GitHub",
    benchmarkCases: "Benchmark cases",
    benchmarkCasesDesc: "The same 15 tasks are used for every setting.",
    publishedSettings: "Published settings",
    publishedSettingsDesc: "Eight agent, version, model, and skill configurations.",
    highestScore: "Highest hard-PASS score",
    highestScoreDesc: "The best setting passed every required gate on 11 cases.",
    resultsEyebrow: "Results",
    resultsTitle: "Current 15-case scoreboard",
    resultsDescription: "One retained run per setting. Accuracy is official hard PASS, not partial rubric credit.",
    tableHint: "Swipe to view the full table →",
    loadingResults: "Loading published results…",
    resourceNote: "Time is averaged per case; tokens and recorded cost are full-suite values. Penguin settings could use Gemini vision, but its proxy cost was not retained; Claude Code and Codex did not have that auxiliary tool.",
    regradeNote: "Claude Code includes the BankerToolBench regrade under the 2026-08-10 evaluator fix. Historical rows could not be regraded without their saved workspaces.",
    chartEyebrow: "Efficiency view",
    chartTitle: "Accuracy vs. recorded cost",
    chartNote: "The cost axis is logarithmic because provider prices differ by orders of magnitude. Recorded cost is not a pure harness-efficiency measure.",
    coverageEyebrow: "Benchmark coverage",
    coverageTitle: "Fifteen hard cases from fifteen public benchmark families.",
    coverageDescription: "Each case keeps the source task recognizable while focusing on end-to-end analysis, evidence, and delivery.",
    documentsTitle: "Documents & evidence",
    documentsDescription: "Retrieve and bind evidence across long documents, scanned pages, and multi-document collections.",
    spreadsheetsTitle: "Spreadsheets & table transformation",
    spreadsheetsDescription: "Work with hierarchical tables, formulas, workbook models, and schema normalization.",
    databasesTitle: "Databases & multi-source workflows",
    databasesDescription: "Query relational data, navigate workspace permissions, and reconcile information across sources.",
    analysisTitle: "Analytical reasoning & visualization",
    analysisDescription: "Compute derived metrics and produce or validate analytical visuals.",
    coverageNote: "This is a curated hard-case suite, not a replacement for each source benchmark’s full leaderboard.",
    footerText: "Reproducible data-analysis agent evaluation",
    rank: "#",
    setting: "Setting",
    model: "Model",
    accuracy: "Accuracy",
    averageTime: "Avg. time / case",
    tokens: "Tokens / run",
    recordedCost: "Recorded cost / run",
    currentEvaluator: "Current evaluator",
    historicalEvaluator: "Historical evaluator",
    currentEvaluatorTitle: "Scored with the current evaluator, including the BankerToolBench fix",
    historicalEvaluatorTitle: "Retained historical score; the saved workspace was unavailable for regrading",
    accuracyAxis: "Accuracy (%)",
    costAxis: "Recorded cost / run (USD, log scale)",
    loadError: "Unable to load published results.",
    chartAria: "Scatter plot comparing accuracy and recorded cost for eight agent settings",
  },
  zh: {
    title: "Data Analysis Bench 实验结果",
    description: "Data Analysis Bench 是一套可复现的 15 道高难度数据分析智能体任务，覆盖文档、表格、数据库、跨来源分析和交付。",
    navResults: "结果",
    navCases: "任务",
    heroTitle: '一套可复现的<span>端到端数据分析</span>评测。',
    heroCopy: "15 道接近真实工作流程的任务，覆盖文档、电子表格、数据库、跨来源分析和交付。",
    viewResults: "查看结果",
    viewGithub: "查看 GitHub",
    benchmarkCases: "Benchmark 任务",
    benchmarkCasesDesc: "所有 setting 都使用同一组 15 道任务。",
    publishedSettings: "已发布 setting",
    publishedSettingsDesc: "8 种 agent、版本、模型和 Skill 配置。",
    highestScore: "最高 hard-PASS 成绩",
    highestScoreDesc: "最佳 setting 在 11 道题上通过了全部必要门槛。",
    resultsEyebrow: "实验结果",
    resultsTitle: "15 道任务结果表",
    resultsDescription: "每个 setting 保留一轮结果。Accuracy 按官方 hard PASS 统计，不是局部 rubric 得分。",
    tableHint: "滑动查看完整表格 →",
    loadingResults: "正在加载已发布结果…",
    resourceNote: "时间为每题平均值；Token 和已记录成本为全套合计。Penguin setting 可使用 Gemini 视觉工具，但没有保留其代理费用；Claude Code 和 Codex 没有该辅助工具。",
    regradeNote: "Claude Code 已包含 2026-08-10 修复 evaluator 后的 BankerToolBench 重评。历史结果行因没有保留 workspace 产物而无法重评。",
    chartEyebrow: "效率视图",
    chartTitle: "Accuracy 与已记录成本",
    chartNote: "不同 provider 的价格相差多个数量级，因此成本轴使用对数刻度。已记录成本不能单独解释为 harness 效率。",
    coverageEyebrow: "Benchmark 覆盖",
    coverageTitle: "15 道难题，来自 15 个公开 benchmark family。",
    coverageDescription: "每道题都保留上游任务的可识别性，同时聚焦端到端分析、证据和交付。",
    documentsTitle: "文档与证据",
    documentsDescription: "在长文档、扫描页面和多文档集合中检索并绑定证据。",
    spreadsheetsTitle: "电子表格与表格变换",
    spreadsheetsDescription: "处理层次表格、公式、workbook 模型和 schema 归一化。",
    databasesTitle: "数据库与跨来源工作流",
    databasesDescription: "查询关系数据、处理 workspace 权限，并对齐多来源信息。",
    analysisTitle: "分析推理与可视化",
    analysisDescription: "计算衍生指标，并生成或验证分析图表。",
    coverageNote: "这是一套精选的高难度任务，不代替各上游 benchmark 的完整 leaderboard。",
    footerText: "可复现的数据分析智能体评测",
    rank: "#",
    setting: "Setting",
    model: "模型",
    accuracy: "Accuracy",
    averageTime: "平均单题耗时",
    tokens: "Token / 轮",
    recordedCost: "已记录成本 / 轮",
    currentEvaluator: "当前 evaluator",
    historicalEvaluator: "历史 evaluator",
    currentEvaluatorTitle: "使用当前 evaluator 评分，包含 BankerToolBench 修复",
    historicalEvaluatorTitle: "保留的历史分数；因缺少 workspace 而无法重评",
    accuracyAxis: "Accuracy（%）",
    costAxis: "已记录成本 / 轮（美元，对数刻度）",
    loadError: "无法加载已发布结果。",
    chartAria: "比较 8 个 agent setting 的 Accuracy 和已记录成本的散点图",
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
      const basisCurrent = row.result_basis === "current-evaluator";
      const basisLabel = basisCurrent ? t.currentEvaluator : t.historicalEvaluator;
      const basisTitle = basisCurrent ? t.currentEvaluatorTitle : t.historicalEvaluatorTitle;
      const rankClass = index < 3 ? ` rank-${index + 1}` : "";
      return `<tr>
        <td class="rank-cell"><span class="rank-badge${rankClass}">${index + 1}</span></td>
        <td>
          <span class="setup-cell">${frameworkLogo(row)}${escapeHtml(setup)}</span>
          <span class="config-meta" title="${escapeHtml(configuration)}">${escapeHtml(configuration)}</span>
        </td>
        <td>${escapeHtml(row.model)}</td>
        <td class="numeric accuracy-cell ${state.sort.key === "accuracy" ? "is-active" : ""}" data-column="accuracy">
          <span class="accuracy-stack">
            <span class="accuracy-measure">
              <span class="accuracy-track" aria-hidden="true"><span class="accuracy-fill" style="--accuracy:${percentage}%"></span></span>
              <strong>${row.accuracy_passes}/${row.accuracy_total}</strong>
            </span>
            <span class="basis-badge ${basisCurrent ? "basis-current" : "basis-historical"}" title="${escapeHtml(basisTitle)}">${basisLabel}</span>
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

function chartColor(framework) {
  if (framework === "Claude Code") return "#f59e0b";
  if (framework === "Codex") return "#10b981";
  return "#6ea8fe";
}

function drawChart() {
  if (!state.results.length || !canvas.clientWidth) return;
  const styles = getComputedStyle(root);
  const textColor = styles.getPropertyValue("--text").trim();
  const mutedColor = styles.getPropertyValue("--muted").trim();
  const lineColor = styles.getPropertyValue("--line").trim();
  const surfaceColor = styles.getPropertyValue("--surface").trim();
  const width = canvas.clientWidth;
  const height = canvas.clientHeight;
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  canvas.width = Math.round(width * dpr);
  canvas.height = Math.round(height * dpr);
  const context = canvas.getContext("2d");
  context.setTransform(dpr, 0, 0, dpr, 0, 0);
  context.clearRect(0, 0, width, height);

  const compact = width < 620;
  const margin = { top: 24, right: 22, bottom: 58, left: compact ? 54 : 66 };
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const costs = state.results.map((row) => row.recorded_cost_usd_per_run);
  const minLog = Math.log10(Math.min(...costs) / 1.25);
  const maxLog = Math.log10(Math.max(...costs) * 1.25);
  const yMin = 50;
  const yMax = 80;
  const xPosition = (value) => margin.left + ((Math.log10(value) - minLog) / (maxLog - minLog)) * plotWidth;
  const yPosition = (value) => margin.top + ((yMax - value) / (yMax - yMin)) * plotHeight;

  context.font = `${compact ? 10 : 11}px ui-sans-serif, system-ui, sans-serif`;
  context.lineWidth = 1;
  context.textBaseline = "middle";
  context.textAlign = "right";
  [50, 60, 70, 80].forEach((tick) => {
    const y = yPosition(tick);
    context.strokeStyle = lineColor;
    context.beginPath();
    context.moveTo(margin.left, y);
    context.lineTo(width - margin.right, y);
    context.stroke();
    context.fillStyle = mutedColor;
    context.fillText(String(tick), margin.left - 10, y);
  });

  const xTicks = [0.2, 0.5, 1, 2, 5, 10, 20, 40].filter((tick) => Math.log10(tick) >= minLog && Math.log10(tick) <= maxLog);
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
    const x = xPosition(row.recorded_cost_usd_per_run);
    const y = yPosition(accuracyPercent(row));
    context.beginPath();
    context.arc(x, y, 6.5, 0, Math.PI * 2);
    context.fillStyle = chartColor(row.framework);
    context.fill();
    context.lineWidth = 2;
    context.strokeStyle = surfaceColor;
    context.stroke();
    return { x, y, row };
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
  chartTooltip.innerHTML = `<strong>${escapeHtml(setting)}</strong><span>${escapeHtml(row.model)}</span><span>${row.accuracy_passes}/${row.accuracy_total} · ${formatCost(row.recorded_cost_usd_per_run)}</span>`;
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
