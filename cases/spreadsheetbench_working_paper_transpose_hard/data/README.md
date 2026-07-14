# Data README

Source lineage:

- Benchmark family: SpreadsheetBench.
- Task type: sheet-level manipulation over `.xlsx` workbooks.
- Public payload here contains three independent official input variants of the
  same working-paper transposition task. Detailed upstream identifiers and
  evaluation metadata are kept outside the public payload.

Scale and structure:

- 3 `.xlsx` workbooks.
- Each workbook has 4 sheets: `destination`, `lap-1`, `lap-2`, and `lap-9`.
- Each `lap-*` sheet is a 439-row semi-structured form, not a regular flat
  table.
- Each `lap-*` sheet contains about 700 merged ranges; across the three public
  workbooks there are about 6,300 merged ranges.
- The source sheets contain repeated 22-row working-paper blocks with highlighted
  cells. The target `destination` output is a wide range: `A1:DQ8`.

Caution:

- This is intentionally not a large CSV/database task. It is kept because the
  workbook structure is dense and irregular: merged cells, repeated form blocks,
  highlighted target cells, and wide transposition. Simple header probing is not
  enough to complete the task.
- Do not flatten the workbook blindly if doing so discards sheet names,
  coordinates, merged-cell context, or highlighted cells.
- The `destination` sheet contains partial examples and `etc...` / `etc…`
  markers. Treat those as layout hints only; the authoritative output layout is
  specified in `task.md`.
