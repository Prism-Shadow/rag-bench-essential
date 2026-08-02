#!/usr/bin/env python3
"""LongDA case validator (isolated-truth, numeric tolerance).

LongDA answers are a single number or an ordered list of numbers. The agent
writes answers.json: {"answer": [...]} (a list, even for a single value).
We parse both predicted and gold into numeric vectors and compare element-wise
with an absolute tolerance in the reported thousand-person unit.

Physical isolation: this script + expected.json live in truth/ and are never
staged into the workspace. At grading time cwd = workspace (reads answers.json),
gold is read from BENCH_TRUTH_DIR (default: this script's dir).

Exit codes: 0 pass; 1 mismatch; 2 missing/unreadable required output.
"""
from __future__ import annotations
import json, os, re, sys
from pathlib import Path


def to_vec(value):
    """Normalize an answer into a list of floats."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return [float(value)]
    if isinstance(value, str):
        nums = re.findall(r"-?\d+(?:\.\d+)?", value.replace(",", ""))
        return [float(x) for x in nums] if nums else None
    if isinstance(value, (list, tuple)):
        out = []
        for v in value:
            sub = to_vec(v)
            if sub is None:
                return None
            out.extend(sub)
        return out
    return None


def truth_dir() -> Path:
    env = os.environ.get("BENCH_TRUTH_DIR")
    return Path(env) if env else Path(__file__).resolve().parent


def main() -> int:
    ans_path = Path("answers.json")
    if not ans_path.exists():
        print(f"FAIL: answers.json not found at {ans_path.resolve()} (agent produced no answer)")
        return 2
    try:
        answers = json.loads(ans_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"FAIL: answers.json unreadable ({e})")
        return 2

    expected = json.loads((truth_dir() / "expected.json").read_text(encoding="utf-8"))
    abs_tolerance = float(expected.get("abs_tolerance", 1.0))

    got = to_vec(answers.get("answer"))
    exp = to_vec(expected.get("answer"))

    if exp is None:
        print("FAIL: gold answer missing in expected.json"); return 2
    if got is None:
        print("FAIL: could not parse a numeric answer from answers.json"); return 1
    if len(got) != len(exp):
        print(f"FAIL: expected {len(exp)} value(s) {exp}, got {len(got)} value(s) {got}")
        return 1

    bad = []
    for i, (g, e) in enumerate(zip(got, exp)):
        if abs(g - e) > abs_tolerance:
            bad.append((i, e, g))
    ok = not bad
    print(f"[{'OK  ' if ok else 'FAIL'}] expected={exp} got={got} (abs_tol={abs_tolerance})")
    if bad:
        for i, e, g in bad:
            print(f"   idx {i}: expected {e}, got {g} (absolute difference {abs(g-e)})")
        print("\nRESULT: FAIL — value(s) outside tolerance.")
        return 1
    print("\nRESULT: PASS — all values within tolerance.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
