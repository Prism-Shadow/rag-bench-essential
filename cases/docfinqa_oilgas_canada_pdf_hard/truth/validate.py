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


def norm_text(value) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip().casefold()


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


def get_path(obj, *keys):
    cur = obj
    for key in keys:
        if not isinstance(cur, dict) or key not in cur:
            return None
        cur = cur[key]
    return cur


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

    exp = expected["answer"]
    got_pct = number(first_answer_value(answers))
    if got_pct is None or abs(got_pct - number(exp["answer"])) > 0.02:
        failures.append(f"answer must be {exp['answer']}, got {first_answer_value(answers)!r}")

    calc_canada = number(get_path(answers, "calculation", "canada_total_mmboe"))
    calc_total = number(get_path(answers, "calculation", "company_total_mmboe"))
    if calc_canada is not None and abs(calc_canada - exp["canada_total_mmboe"]) > 0.01:
        failures.append(f"calculation.canada_total_mmboe expected {exp['canada_total_mmboe']}, got {calc_canada}")
    if calc_total is not None and abs(calc_total - exp["company_total_mmboe"]) > 0.01:
        failures.append(f"calculation.company_total_mmboe expected {exp['company_total_mmboe']}, got {calc_total}")

    sources = evidence.get("sources") if isinstance(evidence, dict) else None
    if not isinstance(sources, list) or not sources:
        failures.append("evidence.sources must be a non-empty list")
    else:
        required_file = expected["evidence"]["required_file"]
        if not any(isinstance(src, dict) and src.get("file") == required_file for src in sources):
            failures.append(f"evidence must cite {required_file}")
        if not any(
            isinstance(src, dict) and int(src.get("page", -1)) in expected["evidence"]["required_pages"]
            for src in sources
        ):
            failures.append(f"evidence must cite page(s) {expected['evidence']['required_pages']}")
        combined = norm_text(" ".join(str(src.get("quote", "")) for src in sources if isinstance(src, dict)))
        for snippet in expected["evidence"]["required_snippets"]:
            if norm_text(snippet) not in combined:
                failures.append(f"evidence quote missing snippet: {snippet}")

    report_text = (workspace / "report.md").read_text(encoding="utf-8", errors="replace")
    if len(report_text.strip()) < 80:
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
