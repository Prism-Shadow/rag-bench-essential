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


def normalize_date(value) -> str:
    parts = re.findall(r"\d+", str(value or ""))
    if len(parts) >= 3:
        return "-".join(str(int(p)) for p in parts[:3])
    return re.sub(r"\W+", "", str(value or "")).casefold()


def bbox_ok(bbox) -> bool:
    return (
        isinstance(bbox, list)
        and len(bbox) == 4
        and all(isinstance(x, (int, float)) for x in bbox)
        and bbox[2] > bbox[0]
        and bbox[3] > bbox[1]
    )


def main() -> int:
    workspace = workspace_dir()
    expected = load_json(truth_dir() / "expected.json")
    missing = [p for p in expected["required_outputs"] if not (workspace / p).exists()]
    if missing:
        print(f"FAIL: missing required output(s): {missing}")
        return 2

    answers = load_json(workspace / "answers.json")
    evidence = load_json(workspace / "evidence.json")
    failures: list[str] = []

    got = normalize_date(answers.get("contract_effective_date"))
    exp = normalize_date(expected["answer"]["contract_effective_date"])
    if got != exp:
        failures.append(f"contract_effective_date expected {expected['answer']['contract_effective_date']}, got {answers.get('contract_effective_date')!r}")

    sources = evidence.get("sources") if isinstance(evidence, dict) else None
    if not isinstance(sources, list) or not sources:
        failures.append("evidence.sources must be a non-empty list")
    else:
        src = sources[0]
        if src.get("image") != expected["evidence"]["required_image"]:
            failures.append(f"evidence image must be {expected['evidence']['required_image']}")
        if "contract effective date" not in str(src.get("field_label", "")).casefold():
            failures.append("evidence field_label must identify Contract Effective Date")
        if not bbox_ok(src.get("answer_region_bbox")):
            failures.append("evidence answer_region_bbox must be [x1, y1, x2, y2]")
        visual = str(src.get("visual_reading", ""))
        for token in expected["evidence"]["required_visual_tokens"]:
            if token not in visual and token not in str(answers.get("contract_effective_date", "")):
                failures.append(f"visual evidence missing token {token!r}")

    if len((workspace / "report.md").read_text(encoding="utf-8", errors="replace").strip()) < 60:
        failures.append("report.md is too short to audit")

    if failures:
        print("RESULT: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
