# Trace Audit Rubric - DocFinQA Devon Annual Report PDF

| Dimension | Full credit | Common failure |
| --- | --- | --- |
| PDF navigation | Uses PDF-aware extraction/rendering on `data/annual_report.pdf` and searches beyond the opening pages. | Reads only the first pages or relies on memory/metadata. |
| Scope binding | Uses the `2008 Estimates` / `Oil, Gas and NGL Production` table on PDF page 58. | Uses the page 27 operating-statistics or year-end-reserves table. |
| Calculation | Computes `60 / 243 * 100 = 24.69%` and rounds to two decimals. | Computes `58 / 224`, `734 / 2496`, or another near-duplicate table ratio. |
| Evidence binding | `evidence.json` cites `data/annual_report.pdf`, page 58, and includes the Canada 60 and Total 243 table evidence. | Provides only a generic annual-report citation or cites a wrong table page. |
| Delivery | Writes `answers.json`, `evidence.json`, and `report.md` in the workspace root. | Gives a conversational answer but omits required artifacts. |
