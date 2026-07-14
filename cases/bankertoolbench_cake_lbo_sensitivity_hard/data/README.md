# Data

This directory contains the agent-visible source packet for a BankerToolBench
investment-banking workflow.

## Files

All inputs are under `inputs/`.

| File | Role |
| --- | --- |
| `CAKE LBO Analysis_vF.xlsx` | Existing Cheesecake Factory LBO model to update. |
| `Equity_Risk_Premium_for_WACC.xlsx` | WACC support workbook. |
| `betas_by_industry_category_for_WACC.xlsx` | WACC support workbook. |

## Lineage

The task and files come from BankerToolBench task data for a financial modeling
and scenario-analysis workflow. The original task requires an updated Excel
model, a two-page PowerPoint deck, and a PDF export of that deck.

## Caution

The base workbook already contains a partial sensitivity area. The required
deliverable is not complete until all four requested 5x5 tables are present in
the Excel output and the same four table topics appear in the PPT/PDF package.
