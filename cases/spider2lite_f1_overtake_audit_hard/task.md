# Spider2-Lite F1 Overtake Audit

This is a hard-tier Spider2-Lite SQLite case. The workspace contains a local
Formula 1 SQLite database and one rules document. The answer requires combining
lap-level race data with the overtake taxonomy. The task is intentionally
event-oriented: there is no precomputed overtake table.

## Data

Read `data/README.md`, inspect `data/f1.sqlite`, and use
`data/docs/f1_overtake.md` where it applies.

## Questions

Produce answers for all three parts.

## Event definition

Use this definition for every part.

An overtake event is a pairwise position reversal between two drivers. Lower
position numbers are better race positions.

Eligible position rows:

- Use `lap_positions` rows with `lap_type = 'Race'` to construct race-lap
  overtake events.
- Do not use `lap_positions` rows whose `lap_type` begins with `Retirement` to
  construct overtake events. Retirement rows are status records, not normal race
  positions.
- `lap = 0` rows are starting-position records, not race laps. Do not compare
  `lap = 0` directly to `lap = 1` for this task.
- For lap 1 events, use positive `results.grid` values (`grid > 0`) as the
  previous state and lap 1 `lap_type = 'Race'` positions as the current state.
  Treat `grid = 0` as a non-normal grid marker rather than a race position.
- For lap 2 and later events, use the previous lap's `lap_type = 'Race'`
  positions as the previous state and the current lap's `lap_type = 'Race'`
  positions as the current state. If either driver does not have an eligible
  previous or current state, no event is formed for that pair and lap.

Direction:

- If driver A was ahead of driver B in the previous state, and driver A is
  behind driver B in the current state, then driver B overtook driver A.
- The event lap is the current lap.
- Driver B is the `overtaking_driver`; driver A is the `overtaken_driver`.

Classify each valid event with the rules in `data/docs/f1_overtake.md`. The
classification priority is `R`, then `P`, then `S`, then `T`; the first matching
rule wins.

### Part A: all pit-data races

Considering all races where pit-stop data is available, how many valid overtake
events occurred in each overtake category?

Use `races_ext.is_pit_data_available = 1` to identify the race scope. Count
events across all eligible race laps in those races.

### Part B: first five laps

Considering all races, how many valid overtake events occurred on event laps 1
through 5 in each category: retirement-related, pit-related, start-related, and
normal on-track passes?

Do not inherit the Part A pit-data race filter for Part B.

### Part C: track-only driver direction audit

Provide the full names of drivers who were overtaken on track more times than
they overtook others on track during race laps.

Use all races and all eligible race laps. Count only events classified as `T`
after applying the same `R`, `P`, `S`, `T` priority rules. For each `T` event,
add 1 to the `overtaking_driver`'s overtook count and 1 to the
`overtaken_driver`'s was-overtaken count. Output drivers where
`was_overtaken > overtook`.

## Working rules

- Work only from `task.md` and `data/`.
- Do not use outside Formula 1 facts.
- You may write helper scripts inside the current workspace.
- Decide the database tables, joins, filters, and event logic from the sources.

## Output contract

Produce the three result files below.

1. `answers/overtake_counts_all.csv`

   A two-column CSV with one row per category. Use category codes `R`, `P`, `S`,
   and `T`, where those codes mean retirement, pit, start, and track.

   ```csv
   overtake_type,num_overtakes
   R,<count>
   P,<count>
   S,<count>
   T,<count>
   ```

2. `answers/overtake_counts_first5.csv`

   Same two-column shape and category codes as Part A.

3. `answers/track_deficit_drivers.csv`

   A one-column CSV:

   ```csv
   full_name
   <driver full name>
   ```

After writing the files, report the three output file paths.
