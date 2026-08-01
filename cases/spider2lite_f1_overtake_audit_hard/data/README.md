# Data README

This case is adapted from the Spider2-Lite SQLite subset.

## Files

- `f1.sqlite`: local SQLite database for the Spider2-Lite `f1` database id.
- `docs/f1_overtake.md`: overtake category definitions used by the
  Spider2-Lite F1 overtake tasks.

## Source lineage

- Benchmark: Spider2-Lite
- Official repository: https://github.com/xlang-ai/Spider2
- Original source: Spider2-Lite F1 SQLite subset
- Original database id: `f1`

## Database scale

The SQLite database contains 29 user tables, 228 columns, and about 1.94 million
rows. Large lap-level tables include:

- `lap_positions`
- `lap_times`
- `lap_times_ext`
- `pit_stops`
- `retirements`
- `races_ext`
- `results`
- `drivers`

Use SQLite schema inspection (`sqlite_master`, `PRAGMA table_info`, sampling, and
small aggregate checks) to decide the exact query plan.

## Important caution

The task is event-oriented. Simple per-driver position deltas are not enough to
answer all parts reliably; the analysis must reconstruct pairwise events before
applying the requested categories and direction.
