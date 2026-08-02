#!/usr/bin/env python3
"""Truth-side reference output materializer for the unified F1 overtake case.

Run from a case workspace containing ``data/f1.sqlite``. The script writes the
three required answer CSVs using the clean-engine semantics described in
task.md.
"""
from __future__ import annotations

import csv
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path


DB_PATH = Path("data/f1.sqlite")
ANSWERS_DIR = Path("answers")
CATEGORIES = ["R", "P", "S", "T"]


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def load_state(conn: sqlite3.Connection) -> dict[str, object]:
    pit_data_races = {
        row["race_id"]
        for row in conn.execute(
            "SELECT race_id FROM races_ext WHERE is_pit_data_available = 1"
        )
    }

    grids: dict[int, dict[int, int]] = defaultdict(dict)
    for row in conn.execute(
        "SELECT race_id, driver_id, grid FROM results WHERE grid IS NOT NULL AND grid > 0"
    ):
        grids[row["race_id"]][row["driver_id"]] = row["grid"]

    retirements = {
        (row["race_id"], row["driver_id"], int(row["lap"]))
        for row in conn.execute("SELECT race_id, driver_id, lap FROM retirements")
    }

    pit_stops = {
        (row["race_id"], row["driver_id"], int(row["lap"]))
        for row in conn.execute("SELECT race_id, driver_id, lap FROM pit_stops")
    }

    race_positions: dict[int, dict[int, dict[int, int]]] = defaultdict(lambda: defaultdict(dict))
    for row in conn.execute(
        """
        SELECT race_id, driver_id, lap, position
        FROM lap_positions
        WHERE lap_type = 'Race'
        """
    ):
        race_positions[row["race_id"]][int(row["lap"])][row["driver_id"]] = row["position"]

    driver_names = {
        row["driver_id"]: row["full_name"]
        for row in conn.execute(
            "SELECT driver_id, forename || ' ' || surname AS full_name FROM drivers"
        )
    }

    return {
        "pit_data_races": pit_data_races,
        "grids": grids,
        "retirements": retirements,
        "pit_stops": pit_stops,
        "race_positions": race_positions,
        "driver_names": driver_names,
    }


def iter_events(
    state: dict[str, object],
    *,
    scope_races: set[int] | None = None,
    lap_min: int = 1,
    lap_max: int | None = None,
) -> list[dict[str, int]]:
    race_positions = state["race_positions"]
    grids = state["grids"]
    events: list[dict[str, int]] = []

    for race_id, laps in race_positions.items():
        if scope_races is not None and race_id not in scope_races:
            continue

        for curr_lap in sorted(laps):
            if curr_lap < lap_min:
                continue
            if lap_max is not None and curr_lap > lap_max:
                continue

            curr_pos = laps[curr_lap]
            if curr_lap == 1:
                prev_pos = grids.get(race_id, {})
            else:
                prev_pos = laps.get(curr_lap - 1)
                if prev_pos is None:
                    continue

            common_drivers = sorted(set(prev_pos) & set(curr_pos))
            for overtaker in common_drivers:
                for overtaken in common_drivers:
                    if overtaker == overtaken:
                        continue
                    if (
                        prev_pos[overtaker] > prev_pos[overtaken]
                        and curr_pos[overtaker] < curr_pos[overtaken]
                    ):
                        events.append(
                            {
                                "race_id": race_id,
                                "lap": curr_lap,
                                "overtaker_id": overtaker,
                                "overtaken_id": overtaken,
                                "grid_overtaker": grids.get(race_id, {}).get(overtaker),
                                "grid_overtaken": grids.get(race_id, {}).get(overtaken),
                            }
                        )

    return events


def classify_event(state: dict[str, object], event: dict[str, int]) -> str:
    race_id = event["race_id"]
    lap = event["lap"]
    overtaken = event["overtaken_id"]
    retirements = state["retirements"]
    pit_stops = state["pit_stops"]

    if (race_id, overtaken, lap) in retirements:
        return "R"
    if (race_id, overtaken, lap) in pit_stops or (race_id, overtaken, lap - 1) in pit_stops:
        return "P"
    if lap == 1:
        grid_overtaker = event.get("grid_overtaker")
        grid_overtaken = event.get("grid_overtaken")
        if (
            grid_overtaker is not None
            and grid_overtaken is not None
            and abs(grid_overtaker - grid_overtaken) <= 2
        ):
            return "S"
    return "T"


def count_categories(state: dict[str, object], events: list[dict[str, int]]) -> dict[str, int]:
    counts = Counter(classify_event(state, event) for event in events)
    return {category: counts.get(category, 0) for category in CATEGORIES}


def write_counts(path: Path, counts: dict[str, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["overtake_type", "num_overtakes"])
        for category in CATEGORIES:
            writer.writerow([category, counts[category]])


def write_drivers(path: Path, names: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["full_name"])
        for name in names:
            writer.writerow([name])


def main() -> None:
    state = load_state(connect())
    pit_data_races = state["pit_data_races"]
    driver_names = state["driver_names"]

    part_a_events = iter_events(state, scope_races=pit_data_races)
    part_b_events = iter_events(state, lap_min=1, lap_max=5)
    part_c_events = iter_events(state)

    part_a_counts = count_categories(state, part_a_events)
    part_b_counts = count_categories(state, part_b_events)

    overtook = Counter()
    was_overtaken = Counter()
    for event in part_c_events:
        if classify_event(state, event) == "T":
            overtook[event["overtaker_id"]] += 1
            was_overtaken[event["overtaken_id"]] += 1

    deficit_names = sorted(
        driver_names[driver_id]
        for driver_id in set(overtook) | set(was_overtaken)
        if was_overtaken[driver_id] > overtook[driver_id]
    )

    write_counts(ANSWERS_DIR / "overtake_counts_all.csv", part_a_counts)
    write_counts(ANSWERS_DIR / "overtake_counts_first5.csv", part_b_counts)
    write_drivers(ANSWERS_DIR / "track_deficit_drivers.csv", deficit_names)

if __name__ == "__main__":
    main()
