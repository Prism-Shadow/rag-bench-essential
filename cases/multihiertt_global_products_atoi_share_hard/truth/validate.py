#!/usr/bin/env python3
"""MultiHiertt-derived hard case validator.

Physical isolation: this script and expected.json live in truth/ and should not
be copied into the agent workspace. Run with cwd=workspace and point
BENCH_TRUTH_DIR at this truth directory.

Exit codes: 0 pass; 1 answer mismatch; 2 missing/unreadable output.
"""
from __future__ import annotations

import json
import math
import os
import re
import sys
from pathlib import Path


def truth_path() -> Path:
    env = os.environ.get("BENCH_TRUTH_DIR")
    base = Path(env) if env else Path(__file__).resolve().parent
    return base / "expected.json"


def to_number(value):
    if isinstance(value, (list, tuple)):
        value = value[0] if value else None
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", "")
    match = re.search(r"[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?", text)
    return float(match.group(0)) if match else None


def main() -> int:
    answers_path = Path("answers.json")
    if not answers_path.exists():
        print(f"FAIL: answers.json not found at {answers_path.resolve()}")
        return 2

    try:
        answers = json.loads(answers_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"FAIL: cannot parse answers.json: {exc}")
        return 2

    expected = json.loads(truth_path().read_text(encoding="utf-8"))
    got = to_number(answers.get("answer"))
    gold = float(expected["gold_numeric"])
    tol = float(expected.get("abs_tolerance", 0.00002))

    ok = got is not None and math.isfinite(got) and abs(got - gold) <= tol
    print(f"[{'OK  ' if ok else 'FAIL'}] expected={gold:.12g} got={got!r} abs_tol={tol}")

    if ok:
        print("RESULT: PASS")
        return 0

    for value, why in expected.get("decoys", {}).items():
        decoy = to_number(value)
        if got is not None and decoy is not None and abs(got - decoy) <= max(tol, abs(decoy) * 1e-6):
            print(f"HINT: matched decoy {value} -- {why}")
            break

    print("RESULT: FAIL")
    return 1


if __name__ == "__main__":
    sys.exit(main())
