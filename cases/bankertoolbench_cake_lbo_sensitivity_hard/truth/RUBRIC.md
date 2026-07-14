# Rubric

This case adapts a BankerToolBench LBO sensitivity workflow. The original task
is an expert-graded Office deliverable; this bench lab validator captures the
deterministic gates that are most useful for agentic RAG evaluation.

## Scoring Dimensions

| Dimension | Gate | Failure signature |
| --- | --- | --- |
| D1 Excel table coverage | Four requested 5x5 sensitivity tables are present in the `CAKE-US LBO` sheet. | Agent only edits the pre-existing single sensitivity table. |
| D2 axis binding | Each table uses the requested x-axis values and the shared 12.7x to 16.7x Exit Multiple y-axis. | Step sizes or centers drift from the prompt. |
| D3 IRR grid completeness | Each table has at least 25 IRR/formula cells near its title. | Agent writes labels only or a partial grid. |
| D4 delivery | Excel, PPTX, and PDF files all exist; PPTX has two slides with the four required topics and source text. | Excel-only completion or missing PDF export. |

## Trace Checks

- Did the agent inspect the existing `CAKE-US LBO` sheet and locate `J184`?
- Did it notice that one pre-existing sensitivity table is not enough?
- Did it preserve the base model while adding four sensitivity blocks?
- Did it create PPT/PDF deliverables, or stop after workbook edits?
