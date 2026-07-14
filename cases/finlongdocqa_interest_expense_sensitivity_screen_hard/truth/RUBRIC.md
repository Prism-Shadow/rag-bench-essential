# Rubric

This case tests whether an agent can bind the correct market-risk disclosure family across many long 10-K reports.

Load-bearing checks:

- Use only files named `*_2024_10K.md`.
- Include only tickers with both a stated variable/floating debt amount and a stated interest expense sensitivity.
- Normalize +25 bp and +50 bp impacts to +100 bp.
- Rank by interest expense impact per $1 billion of variable/floating debt, not by absolute interest expense impact.

Common failure signatures:

- Including fixed-rate debt fair-value sensitivities such as RCL, STZ, or SJM.
- Including pension discount-rate sensitivity from GIS.
- Inferring CL's denominator from its $3 million impact instead of using the separately stated commercial paper amount.
- Using STZ's fixed-rate fair-value sensitivity instead of its short-term borrowings and variable-debt interest expense sensitivity.
- Using PWR's average daily commercial paper disclosure instead of fiscal-year-end variable-rate debt outstanding.
- Ranking by absolute impact, which puts ECL or RCL ahead of APTV.
