#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scoring.report import score_workspace


REPO_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score one RAG Bench Essential workspace.")
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument(
        "--truth-dir",
        type=Path,
        help="Truth directory; defaults to cases/<case-id>/truth in this repository.",
    )
    parser.add_argument("--rubric", type=Path)
    parser.add_argument("--runtime")
    parser.add_argument("--batch-id")
    parser.add_argument("--run-issue", default="ok")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--api-vision-judges", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    truth_dir = args.truth_dir or REPO_ROOT / "cases" / args.case_id / "truth"
    rubric = args.rubric or truth_dir / "rubric.yaml"
    report = score_workspace(
        case_id=args.case_id,
        workspace=args.workspace.resolve(),
        truth_dir=truth_dir.resolve(),
        rubric_path=rubric.resolve(),
        run_issue=args.run_issue,
        runtime=args.runtime,
        batch_id=args.batch_id,
        run_llm_judges=args.api_vision_judges,
    )
    output = args.output or args.workspace.parent / "score.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report["hard_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
