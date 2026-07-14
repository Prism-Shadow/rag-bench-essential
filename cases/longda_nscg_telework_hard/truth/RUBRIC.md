# RUBRIC — longda_nscg_telework_hard

Per-step audit. Each row names the **silent failure** that produces a wrong number.

| # | Step | What correct looks like | Silent failure if skipped/wrong |
| --- | --- | --- | --- |
| 1 | Telework column + code | `TELEC`; teleworker = code **4** ("allowed and did") | Includes code 3 (required) or others → every bucket inflated |
| 2 | Employer-size column | `EMSIZE`, codes 1-8 | Wrong column / wrong code order |
| 3 | Bucket merge | combine codes 7 (5000-24999) + 8 (25000+) → `size5000plus` | Returns 8 buckets → length mismatch / wrong last value |
| 4 | Weight | `WTSURVY` (final survey weight) | Counts rows (unweighted) → wrong magnitude |
| 5 | Units | divide summed weights by 1,000 (thousands) | Forgets /1000 → ~1000x too large |
| 6 | Deliver | `answers.json` = 7 numbers in bucket order | Wrong order / file → delivery fail |

**Gold provenance:** reproduced **exactly** from the microdata by `solution.py`
([3147, 1044, 1754, 3146, 1479, 3315, 9656]); the codebook (`Ppcg23.html`) also
prints the per-category weighted counts that cross-check codes 7+8 = 9656.

**Grading:** D1 (final answer) via `validate.py`, element-wise 5% relative
tolerance. D3 key intermediate = correct telework category + 7/8 bucket merge
(steps 1+3).
