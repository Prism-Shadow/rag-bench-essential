Change:
1) Convert the current “correlation heatmap” into a **single Network Association Graph (node-link diagram)**:
- Nodes = 7 crime types:
  `Murder, Rape_Revised, Robbery, Assault, Burglary, Larceny, Vehicle_Theft`
  (derived from the `*_Rate` fields by removing the `_Rate` suffix).
- Edges are constructed from the 2016 data:
  compute the **Pearson correlation** among the 7 `*_Rate` fields, and for every distinct pair `(i, j)` create an **undirected** edge with weight `corr = corr(i, j)`.

2) **DataOps = CHANGE_BINS (required)**: bin the edge strength `abs_corr = |corr|`, and use it to control edge thickness (edge width).
- **Edge filter threshold:** keep only edges with `abs_corr >= 0.40`; all weaker edges must be excluded from the network.
- **Bin boundaries (must match exactly):** `[0.40, 0.55, 0.70]`
  (meaning 3 levels: `0.40-0.54`, `0.55-0.69`, `0.70+`).
- **Edge width mapping (must match exactly):**
  - `0.40-0.54` → `linewidth = 1.3`
  - `0.55-0.69` → `linewidth = 2.6`
  - `0.70+` → `linewidth = 4.0`

3) **EncodeOps = CHANGE_COLOR_FIELD**: encode edge color by the **sign** of the correlation (based on the sign of `corr`).
- `corr >= 0` (Positive) → edge color must be **#D7191C**
- `corr < 0` (Negative) → edge color must be **#2C7BB6**
- Node styling must remain fixed:
  node fill `#F2F2F2`, node border `#333333`.

4) **Update the title to reflect the network graph semantics (must not reuse the old heatmap title):**
- The chart title text must be exactly:
  **Crime Type Association Network (|corr| ≥ 0.40)**

5) **Fix title/label overlap issues (must be objectively checkable):**
- No node text label (e.g., `Murder`) may **overlap** with its node circle.
- The top node label (e.g., `Murder`) must **not overlap** with the title.
- Labels must be placed outside the node circles by applying a **radial outward offset**
  (i.e., label positions must be outside the node coordinate ring), so every label is clearly separated from its circle.

6) The network layout must be stable and evaluable: use a **deterministic circular layout** with the node order fixed as:
`[Murder, Rape_Revised, Robbery, Assault, Burglary, Larceny, Vehicle_Theft]`,
placed evenly anticlockwise starting from the top.

Preserve:
1) The node set must remain exactly the same **7 crime types**
   (no new nodes, no removed nodes, no “Others” node).
2) The correlation definition must remain unchanged:
   Pearson correlation computed from `Year == 2016` using the `*_Rate` fields (edge weight = `corr`).
3) Network structure constraint:
   edges must be **undirected**, and **no self-loops** are allowed (`source != target`).
4) Layout rule must remain fixed:
   the same deterministic “circular layout + fixed node order + top start angle”.
5) Keep the existing data loading/cleaning logic unchanged
   (including Excel candidate discovery, start-row detection, region mapping/filtering),
   ensuring compatibility with the same input file.
   