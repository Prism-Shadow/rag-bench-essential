#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

import yaml

from sync_results import check_readmes, load_results, validate_results


REPO_ROOT = Path(__file__).resolve().parents[1]
CASES_DIR = REPO_ROOT / "cases"
REQUIRED_EVALUATION_FILES = {
    "RUBRIC.md",
    "expected.json",
    "rubric.yaml",
    "solution.py",
    "validate.py",
}
FORBIDDEN_PUBLIC_NAMES = {
    "truth",
    "RUBRIC.md",
    "rubric.yaml",
    "expected.json",
    "solution.py",
    "validate.py",
    "vision_judge.yaml",
    "vision_judge_prompt.md",
}


def main() -> int:
    errors: list[str] = []
    case_ids = {path.name for path in CASES_DIR.iterdir() if path.is_dir()}
    if len(case_ids) != 15:
        errors.append(f"expected 15 cases, found {len(case_ids)}")

    for case_id in sorted(case_ids):
        case_dir = CASES_DIR / case_id
        directory = case_dir / "truth"
        for path in case_dir.iterdir():
            if path.name == "truth":
                continue
            if path.name in FORBIDDEN_PUBLIC_NAMES:
                errors.append(f"evaluation material outside truth/: {path.relative_to(REPO_ROOT)}")
        missing = sorted(name for name in REQUIRED_EVALUATION_FILES if not (directory / name).is_file())
        if missing:
            errors.append(f"{case_id}: missing evaluation files {missing}")
            continue
        rubric = yaml.safe_load((directory / "rubric.yaml").read_text(encoding="utf-8"))
        if rubric.get("case_id") != case_id:
            errors.append(f"{case_id}: rubric case_id={rubric.get('case_id')!r}")
        for point in rubric.get("points", []):
            config = point.get("llm_judge", {}).get("config")
            if not config:
                continue
            config_path = directory / config
            if not config_path.is_file():
                errors.append(f"{case_id}: missing LLM judge config {config}")
                continue
            judge_config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
            prompt = judge_config.get("prompt_file")
            if not prompt or not (directory / prompt).is_file():
                errors.append(f"{case_id}: missing LLM judge prompt {prompt!r}")

    cache_files = list(CASES_DIR.rglob("truth/__pycache__")) + list(CASES_DIR.rglob("truth/**/*.pyc"))
    if cache_files:
        errors.append(f"generated Python cache files present: {cache_files}")

    results = load_results()
    errors.extend(validate_results(results))
    errors.extend(check_readmes(results))

    if errors:
        print("repository verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"repository verification passed: {len(case_ids)} cases with evaluation packages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
