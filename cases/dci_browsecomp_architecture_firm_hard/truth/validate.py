#!/usr/bin/env python3
"""Artifact-only validator for the BrowseComp-Plus architecture-firm case."""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(value: Any) -> str:
    if isinstance(value, list):
        value = " ".join(str(item) for item in value)
    text = str(value or "").strip().lower()
    text = re.sub(r"[\s_\\-]+", " ", text)
    text = re.sub(r"[^a-z0-9 ]+", "", text)
    return re.sub(r"\s+", " ", text).strip()


def main() -> int:
    workspace = Path.cwd()
    truth_dir = Path(os.environ.get("BENCH_TRUTH_DIR", Path(__file__).resolve().parent))
    answers_path = workspace / "answers.json"

    if not answers_path.exists():
        print("RESULT: FAIL - missing answers.json.")
        return 2
    try:
        answers = load_json(answers_path)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"RESULT: FAIL - unreadable answers.json: {exc}")
        return 2

    expected = load_json(truth_dir / "expected.json")
    answer_value = answers.get("answer") if isinstance(answers, dict) else answers
    aliases = [expected["answer"]["exact"], *expected["answer"].get("aliases", [])]
    answer_ok = normalize(answer_value) in {normalize(alias) for alias in aliases}

    print("== Final answer artifact ==")
    if answer_ok:
        print(f"  [OK ] answer={answer_value!r}")
        print("RESULT: PASS - architecture firm matches the accepted answer.")
        return 0

    print(f"  [MISS] expected={expected['answer']['exact']!r} got={answer_value!r}")
    print("RESULT: FAIL - architecture firm does not match the accepted answer.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
