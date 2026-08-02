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

    final_ok = got is not None and exp is not None and abs(got - exp) <= tol
    print(f"[{'OK ' if final_ok else 'FAIL'}] Gold profit share: expected={exp} got={got} tol=±{tol}")

    if final_ok:
        print("RESULT: PASS - final Gold profit share matches.")
        return 0

    for value, reason in expected.get("decoys", {}).items():
        vf = first_float(value)
        if got is not None and vf is not None and abs(got - vf) <= max(tol, 0.00001):
            print(f"HINT: decoy {value}: {reason}")
    print("RESULT: FAIL - final Gold profit share is outside tolerance.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
