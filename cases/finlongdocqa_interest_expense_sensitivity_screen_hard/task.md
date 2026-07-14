# Interest Expense Sensitivity Screen

You are given a folder of real 10-K report markdown files and a manifest. Use only the report files in `data/reports/` and the manifest in `data/document_manifest.csv`.

Find the report file named `*_2024_10K.md` for each ticker in the manifest. For each such report, decide whether it discloses enough information to compute the company's annual interest expense sensitivity to a +100 basis point interest-rate shock on variable-rate or floating-rate debt:

```text
impact_per_1b_variable_debt_musd =
  standardized_interest_expense_impact_musd / variable_rate_debt_musd * 1000
```

Use these rules.

- A ticker is eligible only if its `*_2024_10K.md` report gives both:
  - an actual numeric amount of variable-rate, floating-rate, or similar rate-sensitive debt outstanding at the fiscal year-end or report-date balance sheet date; and
  - an actual numeric annual, future annual, or next-year interest expense impact from a stated hypothetical interest-rate change on that variable/floating debt.
- Standardize every eligible impact to a +100 basis point / +1.0 percentage point rate increase. If the report gives a +25 bp or +50 bp impact, scale it linearly to +100 bp. If the table gives both decrease and increase rows, use the increase row.
- Report all dollar amounts in millions of USD. Convert billions to millions where needed.
- Do not infer the variable/floating debt amount from the interest expense impact. The debt amount must be separately stated in the report.
- Do not include a ticker when it gives only a qualitative sensitivity statement or only says an impact was not significant.
- Commercial paper, short-term borrowings, or revolving-credit borrowings can count as variable/floating debt when the report identifies that borrowing family as rate-sensitive and gives the fiscal-year-end/report-date amount.
- Do not include fixed-rate debt fair value sensitivity, financial-liability fair value sensitivity, derivative fair value sensitivity, pension or postretirement discount-rate sensitivity, commodity sensitivity, foreign-exchange sensitivity, goodwill or asset impairment sensitivity, or future-debt pre-issuance hedge sensitivity.
- Do not use prior-year columns or prior-year files. Use only the `*_2024_10K.md` report file for each ticker.
- If a report gives both a fiscal-year-end variable/floating debt amount and an average-daily or during-the-year borrowing amount, use only the fiscal-year-end/report-date debt amount and the matching impact for that amount.
- Rank eligible tickers from highest `impact_per_1b_variable_debt_musd` to lowest.

Write `answers.json` in the current workspace with this shape:

```json
{
  "included_tickers": ["..."],
  "ranking_high_to_low": [
    {
      "ticker": "...",
      "rate_shock_bp": 100.0,
      "reported_interest_expense_impact_musd": 0.0,
      "standardized_interest_expense_impact_musd": 0.0,
      "variable_rate_debt_musd": 0.0,
      "impact_per_1b_variable_debt_musd": 0.0
    }
  ],
  "top_ticker": "...",
  "bottom_ticker": "...",
  "spread_per_1b_musd": 0.0,
  "excluded_tickers": [
    {"ticker": "...", "reason": "..."}
  ]
}
```

The ranking should include every eligible ticker, not only the top ticker. Keep enough precision in the amounts and ratios to reproduce the ranking.
