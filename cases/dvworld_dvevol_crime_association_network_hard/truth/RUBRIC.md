# Trace Audit Rubric

| Dimension | What to inspect in the trace | Silent failure signature |
| --- | --- | --- |
| Source routing | Agent opens `data_new.xlsx` and recognizes the source prompt asks for a network graph, not a heatmap. | Produces only a heatmap spec or ignores the workbook. |
| Workbook cleaning | Agent handles the title/header rows, removes percent-change and aggregate rows, and maps state rows to regions. | Correlation matrix includes `United States Total`, region rows, divisions, or percent-change rows. |
| Year and field binding | Agent filters to `Year == 2016` and uses the seven `*_Rate` fields, not count fields. | Edge set matches all-years or count-column decoy. |
| Correlation semantics | Agent computes Pearson correlations pairwise across the seven crime rate fields. | Uses covariance, Spearman correlation, visual similarity, or manually inferred edges. |
| Network rule | Agent keeps undirected non-self-loop edges where `abs(corr) >= 0.40`. | Edge count differs from 16 or only positive thresholding is used. |
| Encoding rule | Agent applies the exact strength bins, edge widths, sign colors, node styling, and fixed circular order. | Correct correlations but wrong bin labels, widths, colors, or layout metadata. |
| Delivery | Agent writes `answers.json`, `derived_edges.csv`, `chart_spec.json`, and `figure.png` in the workspace root. | Analysis is present in logs but one or more required artifacts are missing. |
