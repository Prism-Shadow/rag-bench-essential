#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def truth_dir() -> Path:
    env = os.environ.get("BENCH_TRUTH_DIR")
    return Path(env) if env else Path(__file__).resolve().parent


def load_json(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def first_float(value):
    if isinstance(value, (list, tuple)):
        value = value[0] if value else None
    try:
        return float(str(value).strip().rstrip("%"))
    except (TypeError, ValueError):
        return None


def rows_by_tier(answers: dict) -> dict:
    rows = answers.get("by_tier", {})
    if isinstance(rows, dict):
        return rows
    if isinstance(rows, list):
        out = {}
        for row in rows:
            if isinstance(row, dict) and row.get("tier"):
                out[str(row["tier"])] = row
        return out
    return {}


def close_number(got, expected, tol):
    gf = first_float(got)
    ef = first_float(expected)
    return gf is not None and ef is not None and abs(gf - ef) <= tol


def score_by_tier(answers: dict, expected: dict) -> bool:
    rows = rows_by_tier(answers)
    gold = expected["by_tier"]
    ok = True
    for tier, exp in gold.items():
        row = rows.get(tier)
        if not isinstance(row, dict):
            print(f"  [MISS] by_tier missing {tier}")
            ok = False
            continue
        for field, exp_value in exp.items():
            tol = 0.01 if isinstance(exp_value, float) else 0
            got_value = row.get(field)
            field_ok = (
                close_number(got_value, exp_value, tol)
                if isinstance(exp_value, float)
                else int(first_float(got_value) or -1) == int(exp_value)
            )
            print(
                f"  [{'OK ' if field_ok else 'MISS'}] {tier}.{field}: "
                f"expected={exp_value} got={got_value}"
            )
            ok = ok and field_ok
    return ok


def main() -> int:
    expected = load_json(truth_dir() / "expected.json")
    answers = load_json(Path("answers.json"))
    if answers is None:
        print(f"FAIL: missing or unreadable {Path('answers.json').resolve()}")
        return 2
    if expected is None:
        print("ERROR: expected.json missing or unreadable")
        return 2

    got = first_float(answers.get("answer"))
    exp = first_float(expected.get("answer"))
    tol = float(expected.get("tolerance", 0.000005))

    print("== D1 final answer ==")
    final_ok = got is not None and exp is not None and abs(got - exp) <= tol
    print(f"  [{'OK ' if final_ok else 'FAIL'}] Gold profit share: expected={exp} got={got} tol=±{tol}")

    print("== D3 key intermediates ==")
    by_tier_ok = score_by_tier(answers, expected)

    if final_ok and by_tier_ok:
        print("\nRESULT: PASS - tier normalization and profit share pass.")
        return 0

    for value, reason in expected.get("decoys", {}).items():
        vf = first_float(value)
        if got is not None and vf is not None and abs(got - vf) <= max(tol, 0.00001):
            print(f"HINT: decoy {value}: {reason}")
    print("\nRESULT: FAIL - see dimension diagnostics above.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
