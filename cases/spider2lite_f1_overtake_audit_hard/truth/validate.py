#!/usr/bin/env python3
"""External validator for the Spider2-Lite F1 overtake audit case.

Physical isolation: this script stays in truth/ and is not copied into an agent
workspace. Run it with cwd set to the workspace. Truth files are resolved from
BENCH_TRUTH_DIR, or from this script's directory by default.

Scoring dimensions:
  D1 answer correctness:
     - Part A must match the unified clean-engine gold counts.
     - Part B must match the unified clean-engine gold counts.
     - Part C must match the unified clean-engine track-only driver list.

Only these three result artifacts are scored. Reasoning traces, evidence files,
reports, and intermediate calculations are outside the grading contract.

Exit codes:
  0: pass.
  1: answer/evidence/delivery mismatch.
  2: missing or unreadable required output.
"""
from __future__ import annotations

import csv
import os
import re
import sys
import unicodedata
from pathlib import Path


PARTS = {
    "part_a": {
        "output": Path("answers/overtake_counts_all.csv"),
        "variant_dir": "local344",
        "kind": "counts",
    },
    "part_b": {
        "output": Path("answers/overtake_counts_first5.csv"),
        "variant_dir": "local336",
        "kind": "counts",
    },
    "part_c": {
        "output": Path("answers/track_deficit_drivers.csv"),
        "variant_dir": "local356",
        "kind": "drivers",
    },
}


def truth_dir() -> Path:
    env = os.environ.get("BENCH_TRUTH_DIR")
    return Path(env) if env else Path(__file__).resolve().parent


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    try:
        with path.open(newline="", encoding="utf-8-sig") as f:
            return list(csv.DictReader(f))
    except Exception as exc:
        raise ValueError(f"cannot read CSV {path}: {exc}") from exc


def normalize_category(value: object) -> str | None:
    raw = str(value or "").strip().strip('"').strip("'")
    key = re.sub(r"[^a-z0-9]+", " ", raw.lower()).strip()
    aliases = {
        "r": "R",
        "retirement": "R",
        "retirements": "R",
        "retirement related": "R",
        "p": "P",
        "pit": "P",
        "pit stop": "P",
        "pit stops": "P",
        "pit related": "P",
        "s": "S",
        "start": "S",
        "start related": "S",
        "t": "T",
        "track": "T",
        "on track": "T",
        "normal track": "T",
        "normal on track passes": "T",
        "standard on track passes": "T",
    }
    return aliases.get(key)


def parse_number(value: object) -> int | None:
    text = str(value or "").strip().replace(",", "")
    try:
        return int(round(float(text)))
    except ValueError:
        return None


def parse_counts(path: Path) -> dict[str, int]:
    rows = read_csv_rows(path)
    out: dict[str, int] = {}
    for row in rows:
        if not row:
            continue
        keys = list(row.keys())
        cat_value = row.get("overtake_type") or row.get("OVERTAKE_TYPE") or row.get("category") or row.get("Category") or row.get(keys[0])
        count_value = (
            row.get("num_overtakes")
            or row.get("OVERTAKE_COUNT")
            or row.get("overtake_count")
            or row.get("overtakes")
            or row.get("count")
            or row.get(keys[1] if len(keys) > 1 else keys[0])
        )
        cat = normalize_category(cat_value)
        count = parse_number(count_value)
        if cat is None or count is None:
            raise ValueError(f"cannot parse count row in {path}: {row}")
        out[cat] = count
    return out


def normalize_name(value: object) -> str:
    """Fold accents, case, quote style, and whitespace for driver-name matching.

    Part C is a hard gate, so a semantically correct answer must not fail on
    cosmetic name formatting (e.g. "Gutiérrez" vs "Gutierrez", curly vs straight
    apostrophe, double spaces). Both gold and agent answers pass through here.
    """
    text = str(value or "").strip().strip('"').strip("'")
    # unify common unicode apostrophe/quote variants to a straight apostrophe
    text = text.replace("’", "'").replace("ʼ", "'").replace("`", "'")
    # decompose and drop combining marks (accent folding)
    text = "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))
    # collapse internal whitespace and casefold
    text = re.sub(r"\s+", " ", text).strip().casefold()
    return text


def parse_driver_set(path: Path) -> set[str]:
    rows = read_csv_rows(path)
    names: set[str] = set()
    for row in rows:
        if not row:
            continue
        keys = list(row.keys())
        value = row.get("full_name") or row.get("FULL_NAME") or row.get(keys[0])
        name = normalize_name(value)
        if name:
            names.add(name)
    return names


def expected_variants(part: str, kind: str) -> list[object]:
    base = truth_dir() / "expected_variants" / PARTS[part]["variant_dir"]
    files = sorted(base.glob("*.csv"))
    if not files:
        raise ValueError(f"no expected variants found under {base}")
    if kind == "counts":
        return [parse_counts(p) for p in files]
    return [parse_driver_set(p) for p in files]


def compare_part(part: str) -> tuple[bool, str]:
    cfg = PARTS[part]
    path = cfg["output"]
    if not path.exists():
        raise FileNotFoundError(f"missing {path}")
    kind = cfg["kind"]
    got = parse_counts(path) if kind == "counts" else parse_driver_set(path)
    variants = expected_variants(part, kind)
    for idx, expected in enumerate(variants, start=1):
        if got == expected:
            if kind == "drivers":
                return True, f"matched variant {idx}; driver_count={len(got)}"
            return True, f"matched variant {idx}; counts={got}"
    if kind == "drivers":
        sizes = [len(v) for v in variants]
        return False, f"no variant match; got_driver_count={len(got)} expected_variant_sizes={sizes}"
    return False, f"no variant match; got={got} expected_variants={variants}"


def main() -> int:
    print("== Result artifacts ==")
    statuses: dict[str, bool] = {}
    missing = False
    for part in ["part_a", "part_b", "part_c"]:
        try:
            ok, msg = compare_part(part)
        except FileNotFoundError as exc:
            print(f"  [MISS] {part}: {exc}")
            statuses[part] = False
            missing = True
            continue
        except Exception as exc:
            print(f"  [FAIL] {part}: {exc}")
            statuses[part] = False
            continue
        statuses[part] = ok
        print(f"  [{'OK ' if ok else 'WARN'}] {part}: {msg}")

    if missing:
        print("\nRESULT: FAIL - missing required output files.")
        return 2

    answers_ok = all(statuses.get(part, False) for part in ["part_a", "part_b", "part_c"])

    if answers_ok:
        print("\nRESULT: PASS - all three parts match unified clean-engine gold.")
        return 0

    print("\nRESULT: FAIL - one or more answer files did not match unified clean-engine gold.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
