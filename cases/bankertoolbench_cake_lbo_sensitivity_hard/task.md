# CAKE LBO Sensitivity Analysis

This case is adapted from a BankerToolBench investment-banking workflow. You
are an analyst in the M&A group at XYZ Bank. The team is advising Sponsor ABC
on a potential take-private of The Cheesecake Factory (NYSE: CAKE).

## Data

Read `data/README.md`, then use the files under `data/inputs/`.

The main model is:

```text
data/inputs/CAKE LBO Analysis_vF.xlsx
```

The folder also includes WACC support workbooks.

## Task

Your MD wants sensitivity tables based on the current LBO model and a short
client discussion deck.

Build four 5x5 sensitivity tables around Y5 Exit IRR. The Y5 Exit IRR is the
Sponsor Returns line in cell `J184` of the `CAKE-US LBO` sheet.

The four sensitivity tables are:

1. Entry Share Price Premium vs. Exit Multiple.
2. Revenue Growth vs. Exit Multiple.
3. COGS vs. Exit Multiple.
4. Term Loan Leverage vs. Exit Multiple.

For every table, Exit EBITDA Multiple is the y-axis. The center value is 14.7x,
with -1.0x steps upward and +1.0x steps downward:

```text
12.7x, 13.7x, 14.7x, 15.7x, 16.7x
```

The x-axis values are:

| Table | Center | Left values | Right values |
| --- | ---: | --- | --- |
| Entry Share Price Premium | 20.0% | 15.0%, 17.5% | 22.5%, 25.0% |
| Revenue Growth | 6.0% | 2.0%, 4.0% | 8.0%, 10.0% |
| COGS | 83.0% | 78.0%, 80.5% | 85.5%, 88.0% |
| Term Loan Leverage | 4.0x | 2.0x, 3.0x | 5.0x, 6.0x |

The sensitivity tables should be built into the existing LBO model and placed
after the current model output area. Do not change the rest of the LBO model.

Then build a two-page PowerPoint deck:

- Page 1: Entry Share Price Premium vs. Exit Multiple, and Term Loan Leverage
  vs. Exit Multiple.
- Page 2: Revenue Growth vs. Exit Multiple, and COGS vs. Exit Multiple.

Each table in the deck should have a short text box with 3-4 bullets summarizing
the conclusion or insight from the table. Slide headlines should state a
conclusion, not just the topic. Include a source footnote on each slide.

## Formatting Rules

- Excel model font should remain Arial 12 where practical.
- Highlight the center IRR cell in blue and bold it.
- Highlight the surrounding 3x3 base-case area in gray.
- PPT font should be Montserrat where available.
- PPT titles use size 24, table headers size 14, normal text size 12, footnotes
  size 8.
- PPT sensitivity tables should be native/editable slide content, not a pasted
  screenshot when possible.
- Negative numbers should display in parentheses.
- Exit multiple and term loan leverage should display with one decimal place
  followed by `x`.
- Entry Share Price Premium, IRR, Revenue Growth, and COGS should display as
  percentages.

## Working Rules

- Work only from `task.md`, `env.md`, and `data/`.
- You may write helper scripts in the workspace.

## Output Contract

Produce all three deliverables in the workspace root:

```text
CAKE Sensitivity Analysis_vF.xlsx
CAKE Sensitivity Analysis_vF.pptx
CAKE Sensitivity Analysis_vF.pdf
```
