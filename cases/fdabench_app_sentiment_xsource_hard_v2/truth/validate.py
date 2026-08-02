#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def to_float(value):
    if isinstance(value, (list, tuple)):
        value = value[0] if value else None
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return None


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def main() -> int:
    answers = load_json(Path("answers.json"))
    if answers is None:
        print(f"FAIL: missing or unreadable {Path('answers.json').resolve()}")
        return 2

    truth_dir = Path(os.environ.get("BENCH_TRUTH_DIR", Path(__file__).resolve().parent))
    expected = load_json(truth_dir / "expected.json")
    if expected is None:
        print("ERROR: expected.json missing or unreadable")
        return 2

    got = to_float(answers.get("answer"))
    gold = to_float(expected.get("answer"))
    tolerance = float(expected.get("tolerance", 0.005))
    passed = got is not None and gold is not None and abs(got - gold) <= tolerance
    print(f"[{'OK ' if passed else 'FAIL'}] answer: expected={gold} got={got} tol=±{tolerance}")
    if passed:
        print("RESULT: PASS - final scalar matches.")
        return 0

    for value, reason in expected.get("decoys", {}).items():
        decoy = to_float(value)
        if decoy is not None and got is not None and abs(got - decoy) <= tolerance:
            print(f"HINT: decoy {value}: {reason}")
    print("RESULT: FAIL - final scalar is outside tolerance.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
