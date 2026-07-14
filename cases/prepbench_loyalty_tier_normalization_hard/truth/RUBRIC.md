# Per-Step Rubric

Use this rubric for trace audit. The final answer alone is not enough; the
important behavior is whether the agent profiles and normalizes the loyalty tier
field before filtering or grouping.

| # | Step | Dimension | Expected | Silent failure |
| --- | --- | --- | --- | --- |
| 1 | Read public data | Trace audit | Reads `data/README.md`, then inspects all three CSVs | Uses only the loyalty table or only the transaction table |
| 2 | Profile raw tiers | Trace audit / D3 | Observes raw values including `Goald`, `Bronz`, `Sliver`, lowercase variants | Exact-match grouping treats spelling variants as null |
| 3 | Normalize tier variants | Trace audit / D3 | Maps obvious variants to canonical `Gold`, `Silver`, `Bronze` | Gold transaction count drops to 2,596 instead of 3,255 |
| 4 | Join identifiers | D3 | Normalizes loyalty ids such as `1004721.0` before joining | Large unmatched-loyalty loss |
| 5 | Product join | D3 | Splits `Product_ID`, restores scent spaces, uses `Product_Size`/`Pack_Size` consistently | Quantity/profit missing or systematically wrong |
| 6 | Missing discount semantics | D3 | Leaves `Sales_After_Discount`/`Profit` null when `Loyalty_Discount` is missing; counts those rows/customers but excludes null monetary values from sums | Treats missing discount as 0%, yielding `0.091295` |
| 7 | Profit formula | D1 | Uses `Sales_After_Discount - Unit_Cost * Quantity` | Reports Gold sales share `0.119419` instead of profit share |
| 8 | Final denominator | D1 | Denominator is total non-null profit across canonical Gold/Silver/Bronze rows | Reports transaction share `0.127557` |
| 9 | Trace evidence | Trace audit | The trace shows raw profiling before tier grouping/filtering | Final answer is correct but trace cannot show how variants were found |
| 10 | Delivery | D4 | Writes `answers.json` in the requested schema | Correct reasoning but missing `answers.json` |

Gold answer: `0.094106`.
