#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


def main() -> int:
    answers = {"contract_effective_date": "7-1-99"}
    Path("answers.json").write_text(json.dumps(answers, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
