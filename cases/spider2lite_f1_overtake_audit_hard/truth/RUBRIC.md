# Artifact Rubric

Only the three result CSVs are scored. The agent's method, trace, intermediate
values, source narrative, and any extra files do not affect the score.

| Part | Required artifact | Pass condition | Weight |
| --- | --- | --- | ---: |
| A | `answers/overtake_counts_all.csv` | The normalized `R/P/S/T` counts match the unified pit-data-race gold. | 1/3 |
| B | `answers/overtake_counts_first5.csv` | The normalized `R/P/S/T` counts match the unified all-race first-five-lap gold. | 1/3 |
| C | `answers/track_deficit_drivers.csv` | The normalized driver-name set matches the unified track-only gold. | 1/3 |

Row order, category aliases, capitalization, whitespace, quotation style, and
driver-name accents are normalized before comparison. Missing, extra, or wrong
semantic values fail that part. The continuous score is the fraction of parts
passed; official PASS requires all three parts.
