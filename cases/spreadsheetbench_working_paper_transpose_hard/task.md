# Spreadsheet Working-Paper Transposition

This is a SpreadsheetBench-style workbook manipulation task. The goal is to
complete the `destination` sheet in each workbook by transposing values from
semi-structured working-paper sheets.

## Original Benchmark Instruction

I have an Excel workbook containing multiple sheets with randomly named sheets.
Each sheet has the same format but different data. I need to transpose specific
cells from every 22 rows (or a variable number of rows) across multiple sheets
into a single sheet, placing them into multiple columns. Additionally, the data
includes merged cells which I want to retain during the transposition. The cells
to be transposed include C3, C4, C5, C7, C8, C11, C12, E9, E11, E12, C15, and
C21 from a sheet named `lap-1`, and similarly positioned cells from other sheets
with a 22-row interval. This pattern repeats for other sheets. How can I
transpose this data into another sheet named `destination` or another sheet with
a different name? For clarity, I have highlighted these cells. An attached file
contains the necessary details.

## Data

Read `data/README.md` first, then inspect the three workbooks under
`data/workbooks/`:

- `working_paper_variant_a.xlsx`
- `working_paper_variant_b.xlsx`
- `working_paper_variant_c.xlsx`

The three workbooks are independent variants of the same benchmark task. Complete
all three.

## Output Contract

Write these completed workbooks:

- `outputs/working_paper_variant_a_completed.xlsx`
- `outputs/working_paper_variant_b_completed.xlsx`
- `outputs/working_paper_variant_c_completed.xlsx`

For each completed workbook, the `destination` sheet must be filled through
range `A1:DQ8`. Preserve the existing workbook structure and formatting as much
as practical.

## Clarified Layout Rules

The original workbook includes partial examples in `destination`. In this
adapted case, those examples show the shape of the transposition, but the
completed output must follow the deterministic layout below.

For each source sheet (`lap-1`, `lap-2`, and `lap-9`), discover every repeated
working-paper block in sheet order from the repeated form structure and row
labels. Do not assume only the initially visible English labels identify all
blocks. For every block, extract values in this exact coordinate order, using
the block start as the local row 1:

```text
C3, C4, C5, C7, C8, C11, C12, E9, E11, E12, C15, C21
```

Process source sheets in this order:

```text
lap-1, lap-2, lap-9
```

Within each source sheet, keep the discovered block order from top to bottom.

Treat `destination` columns `B:DQ` as consecutive 12-column slots from left to
right. Each slot stores one extracted 12-value block in the exact coordinate
order above. Row 1 should contain slot headers `1..12` repeated across all slots
from `B1:DQ1`; leave `A1` blank.

Write data rows starting at row 2. Each destination row holds up to ten
consecutive blocks from a single source sheet, packed left to right across the
slots. Continue on the next destination row for the remaining blocks from the
same source sheet, then move to the next source sheet. Put the sequential output
row index in column A for every row that receives block data. Leave unused slots
blank.

Overwrite `destination!A1:DQ8` according to these rules. Existing `etc...` /
`etc…` markers inside that range are examples only; do not preserve them unless
the rules above write the same value.

## Working Rules

- Work only from `task.md`, `env.md`, and the files under `data/`.
- You may write helper scripts in the workspace.
- Do not use the network.
