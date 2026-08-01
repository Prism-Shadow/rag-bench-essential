# DV-World Network Association Graph

This case adapts a DV-World visualization-edit task. The source prompt in
`data/source_task.md` asks you to convert a correlation heatmap into a single
network association graph. Use the files in `data/` only.

## Data

- `data/data_new.xlsx`: semi-structured FBI crime table with multi-row headers.
- `data/source_fig.png`: the source visualization context.
- `data/source_task.md`: original public chart-edit instruction.
- `data/README.md`: lineage and file notes.

## Task

Create the network association graph described by the source task:

- Nodes must be exactly:
  `Murder, Rape_Revised, Robbery, Assault, Burglary, Larceny, Vehicle_Theft`.
- Edge weights are Pearson correlations computed from `Year == 2016` using the
  seven corresponding `*_Rate` fields.
- Keep only undirected non-self-loop edges with `abs(corr) >= 0.40`.
- Bin `abs_corr` with boundaries `[0.40, 0.55, 0.70]`:
  `0.40-0.54`, `0.55-0.69`, `0.70+`.
- Map those bins to edge widths `1.3`, `2.6`, and `4.0`, respectively.
- Edge color is based on correlation sign: positive `#D7191C`, negative
  `#2C7BB6`.
- Node fill is `#F2F2F2`; node border is `#333333`.
- Use a deterministic circular layout with the fixed node order above,
  anticlockwise starting from the top.
- Use the title exactly:
  `Crime Type Association Network (|corr| >= 0.40)`.

Do not use synthetic fallback data. The answer must be derived from the real
workbook in `data/data_new.xlsx`.

## Working Rules

- Work only from `task.md`, `env.md`, and files under `data/`.
- You may create helper scripts in the workspace.
- Preserve the source task's cleaning/filtering contract for `Area`: use the
  workbook labels as the filtering step sees them, and do not expand the
  correlation input by rewriting labels to make additional rows match a
  geographic category. Only apply an `Area` label rewrite if `source_task.md`
  explicitly defines that rewrite.
- Preserve numeric precision in the derived edge table; do not round correlations
  to fewer than 6 decimal places.

## Output Contract

Write exactly these two final chart artifacts in the workspace root:

1. `chart_spec.json`

Use this semantic schema:

```json
{
  "source_file": "data/data_new.xlsx",
  "year": 2016,
  "title": "Crime Type Association Network (|corr| >= 0.40)",
  "mark": "network",
  "layout": {
    "type": "circular",
    "node_order": ["Murder", "Rape_Revised", "Robbery", "Assault", "Burglary", "Larceny", "Vehicle_Theft"],
    "start": "top",
    "direction": "anticlockwise"
  },
  "nodes": {
    "values": ["Murder", "Rape_Revised", "Robbery", "Assault", "Burglary", "Larceny", "Vehicle_Theft"],
    "fill": "#F2F2F2",
    "stroke": "#333333"
  },
  "edges": {
    "values": [
      {
        "source": "Assault",
        "target": "Burglary",
        "corr": 0.0,
        "abs_corr": 0.0,
        "sign": "positive",
        "strength_bin": "0.70+",
        "edge_width": 4.0,
        "edge_color_hex": "#D7191C"
      }
    ],
    "source": "source",
    "target": "target",
    "weight": "corr",
    "threshold_abs_corr": 0.4,
    "undirected": true,
    "self_loops": false
  },
  "edge_encoding": {
    "color": {
      "field": "sign",
      "positive": "#D7191C",
      "negative": "#2C7BB6"
    },
    "width": {
      "field": "strength_bin",
      "0.40-0.54": 1.3,
      "0.55-0.69": 2.6,
      "0.70+": 4.0
    }
  }
}
```

The example edge values above illustrate the schema only. Include every retained
edge computed from the workbook. Sort `edges.values` by descending `abs_corr`,
then ascending `source`, then ascending `target`.

2. `figure.png`

Create the actual rendered PNG chart. A placeholder image does not satisfy the
task. All node labels must be readable outside their circles, the top label must
not overlap the title, and no chart content may be clipped.
