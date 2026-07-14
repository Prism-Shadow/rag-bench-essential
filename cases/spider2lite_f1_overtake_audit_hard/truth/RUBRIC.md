# Per-Step Rubric

This case tests complex local-SQL event reconstruction over a many-table
Spider2-Lite SQLite database. Award partial credit even when one official
execution variant is missed.

| # | Step | Dimension | Expected | Silent failure |
| --- | --- | --- | --- | --- |
| 1 | Source discovery | D2 | Reads `f1.sqlite`, `data/README.md`, and `docs/f1_overtake.md` for Parts A/B | Treats the task as a simple table lookup |
| 2 | Schema navigation | D2/D3 | Identifies lap positions, pit-stop availability, pit stops, retirements, races, and drivers | Uses only `lap_times` or only `results` |
| 3 | Overtake event construction | D1/D3 | Counts pairwise reversals using only `lap_type = 'Race'` rows; lap 1 uses positive `results.grid` values; later laps use the previous Race lap | Uses retirement status rows as normal race positions; counts only per-driver deltas |
| 4 | Category assignment | D1/D2 | Applies `R`, `P`, `S`, `T` semantics with priority `R > P > S > T`; pit exit is previous-lap `pit_stops` with no time-gap threshold | Labels all reversals as track passes; adds an unsupported pit time-gap filter |
| 5 | Part A output | D1 | `answers/overtake_counts_all.csv` matches the unified pit-data-race gold | Uses all races instead of pit-data races; reuses old official local344 retirement semantics |
| 6 | Part B output | D1 | `answers/overtake_counts_first5.csv` matches the unified all-race first-five-lap gold | Reuses Part A filters or uses retirement `lap_positions` rows as event candidates |
| 7 | Part C direction | D1/D2 | Distinguishes overtook vs was overtaken and excludes pit/start/retirement events | Reverses direction or includes pit/start movements |
| 8 | Evidence binding | D2 | `evidence.json` binds tables, rules, direction, and exclusions | Correct CSVs with no auditable source trail |
| 9 | Delivery contract | D4 | Produces all three CSVs, `evidence.json`, and a non-trivial `report.md` | Missing one output or writes prose only |

All three parts are hard gates. The case uses one unified event definition with
`grid > 0` lap-1 semantics to remove the old disagreement between the upstream
Spider2 local344/local336/local356 variants while preserving the multi-table
event reconstruction difficulty.
