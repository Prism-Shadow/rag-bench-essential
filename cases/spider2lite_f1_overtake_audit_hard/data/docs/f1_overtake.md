# Overtake Label Classification

This document defines how to label a valid overtake event after the event has
already been constructed from eligible race-position rows. Use the event
definition in `task.md` to decide which position reversals are valid events.

Apply the labels in this priority order:

1. `R`
2. `P`
3. `S`
4. `T`

The first matching rule wins.

## 1. R (Retirement) - Overtake during Retirement

Label a valid event as **R (Retirement)** if the `overtaken_driver` has a row in
`retirements` for the same `race_id` and event lap.

Retirement rows in `lap_positions` do not create overtake events by themselves.
They are status records. The `retirements` table is used only to label an event
that was already constructed from eligible race-position rows.

## 2. P (Pit) - Overtake related to Pit Stops

Label a valid event as **P (Pit)** under either of these scenarios:

- **Pit Entry**: the `overtaken_driver` has a row in `pit_stops` for the same
  `race_id` and event lap.
- **Pit Exit**: the `overtaken_driver` has a row in `pit_stops` for the same
  `race_id` and the lap immediately before the event lap.

Do not apply an additional time-gap or typical-pit-duration threshold.

## 3. S (Start) - Overtake at Race Start

Label a valid event as **S (Start)** if:

- the event lap is 1;
- both drivers have `results.grid` values for that race; and
- `abs(grid_overtaker - grid_overtaken) <= 2`.

## 4. T (Track) - Overtake under Normal Racing Conditions

Label a valid event as **T (Track)** if it does not match `R`, `P`, or `S`.
`T` is the fallback class for normal on-track passes under this table-based
definition.
