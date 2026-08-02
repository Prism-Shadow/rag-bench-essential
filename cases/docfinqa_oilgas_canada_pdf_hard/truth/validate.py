#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path


def truth_dir() -> Path:
    return Path(os.environ.get("BENCH_TRUTH_DIR", Path(__file__).resolve().parent))


def workspace_dir() -> Path:
    return Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError(f"cannot read JSON {path}: {exc}") from exc


def number(value):
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value or "").replace(",", "")
    match = re.search(r"-?\d+(?:\.\d+)?", text)
    return float(match.group()) if match else None


def first_answer_value(answers):
    if isinstance(answers, dict):
        raw = answers.get("answer")
        if isinstance(raw, list) and raw:
            return raw[0]
        return raw
    return None


def main() -> int:
    workspace = workspace_dir()
    expected = load_json(truth_dir() / "expected.json")
    missing = [p for p in expected["required_outputs"] if not (workspace / p).exists()]
    if missing:
        print(f"FAIL: missing required output(s): {missing}")
        return 2

    answers = load_json(workspace / "answers.json")
    failures: list[str] = []

    exp = expected["answer"]
    got_pct = number(first_answer_value(answers))
    if got_pct is None or abs(got_pct - number(exp["answer"])) > 0.02:
        failures.append(f"answer must be {exp['answer']}, got {first_answer_value(answers)!r}")

    if failures:
        print("RESULT: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
