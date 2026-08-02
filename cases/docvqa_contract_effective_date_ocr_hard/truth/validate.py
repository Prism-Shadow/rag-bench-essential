#!/usr/bin/env python3
"""Artifact-only validator for the DocVQA contract effective date."""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any


DATE_FORMATS = (
    "%m-%d-%y",
    "%m/%d/%y",
    "%m.%d.%y",
    "%m-%d-%Y",
    "%m/%d/%Y",
    "%m.%d.%Y",
    "%Y-%m-%d",
    "%Y/%m/%d",
    "%B %d %Y",
    "%b %d %Y",
    "%d %B %Y",
    "%d %b %Y",
)


def truth_dir() -> Path:
    return Path(os.environ.get("BENCH_TRUTH_DIR", Path(__file__).resolve().parent))


def parse_date(value: Any) -> date | None:
    text = str(value or "").strip()
    text = re.sub(r"(?<=\d)(st|nd|rd|th)\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"[,\s]+", " ", text).strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def main() -> int:
    answers_path = Path("answers.json")
    if not answers_path.exists():
        print("RESULT: FAIL - missing answers.json.")
        return 2
    try:
        answers = json.loads(answers_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"RESULT: FAIL - unreadable answers.json: {exc}")
        return 2

    expected = json.loads((truth_dir() / "expected.json").read_text(encoding="utf-8"))
    got_raw = answers.get("contract_effective_date") if isinstance(answers, dict) else None
    expected_date = parse_date(expected["answer"]["contract_effective_date"])
    got_date = parse_date(got_raw)

    print("== Final answer artifact ==")
    if got_date is not None and got_date == expected_date:
        print(f"  [OK ] contract_effective_date={got_raw!r} -> {got_date.isoformat()}")
        print("RESULT: PASS - contract effective date matches.")
        return 0

    print(f"  [MISS] expected={expected_date} got={got_raw!r} parsed={got_date}")
    print("RESULT: FAIL - contract effective date does not match.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
