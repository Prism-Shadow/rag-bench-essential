#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RESULTS_PATH = REPO_ROOT / "site" / "results.json"
START_MARKER = "<!-- RESULTS_TABLE_START -->"
END_MARKER = "<!-- RESULTS_TABLE_END -->"
SITE_START_MARKER = "<!-- RESULTS_DATA_START -->"
SITE_END_MARKER = "<!-- RESULTS_DATA_END -->"


def load_results() -> dict:
    return json.loads(RESULTS_PATH.read_text(encoding="utf-8"))


def validate_results(payload: dict) -> list[str]:
    errors: list[str] = []
    suite = payload.get("suite", {})
    results = payload.get("results", [])
    if suite.get("cases") != 15:
        errors.append(f"results suite must contain 15 cases, found {suite.get('cases')!r}")
    if len(results) != 8:
        errors.append(f"expected 8 published settings, found {len(results)}")

    ids = [row.get("id") for row in results]
    if len(set(ids)) != len(ids):
        errors.append("result ids must be unique")

    required = {
        "id",
        "framework",
        "version",
        "setting",
        "setting_zh",
        "configuration",
        "configuration_zh",
        "configuration_detail",
        "configuration_detail_zh",
        "model",
        "accuracy_passes",
        "accuracy_total",
        "time_seconds_per_run",
        "tokens_per_run",
        "recorded_cost_usd_per_run",
        "result_basis",
    }
    for row in results:
        missing = sorted(required - row.keys())
        if missing:
            errors.append(f"{row.get('id', '<unknown>')}: missing fields {missing}")
            continue
        if row["accuracy_total"] != suite.get("cases"):
            errors.append(f"{row['id']}: accuracy_total does not match suite size")
        if not 0 <= row["accuracy_passes"] <= row["accuracy_total"]:
            errors.append(f"{row['id']}: invalid accuracy")
        if row["result_basis"] not in {"current-evaluator", "historical-evaluator"}:
            errors.append(f"{row['id']}: invalid result_basis={row['result_basis']!r}")
        if row.get("vision_tool") and row.get("vision_tool_cost_included") is not False:
            errors.append(f"{row['id']}: auxiliary vision cost scope must be explicit")
    return errors


def format_cost(value: float) -> str:
    return f"{value:.4f}" if value < 1 else f"{value:.2f}"


def results_table(payload: dict, locale: str) -> str:
    if locale == "zh":
        header = (
            "| Setting | 版本与配置 | Accuracy | 平均单题耗时（分钟） | "
            "Token 用量（百万） | 成本（美元） | 结果口径 |"
        )
        basis_labels = {
            "current-evaluator": "当前 evaluator",
            "historical-evaluator": "历史 evaluator",
        }
    else:
        header = (
            "| Setting | Version and configuration | Accuracy | Avg. time / case (min) | "
            "Token usage (M) | Cost (USD) | Result basis |"
        )
        basis_labels = {
            "current-evaluator": "Current evaluator",
            "historical-evaluator": "Historical evaluator",
        }

    lines = [header, "| --- | --- | ---: | ---: | ---: | ---: | --- |"]
    for row in payload["results"]:
        setting = row["setting_zh"] if locale == "zh" else row["setting"]
        configuration = row["configuration_detail_zh"] if locale == "zh" else row["configuration_detail"]
        percentage = row["accuracy_passes"] / row["accuracy_total"] * 100
        lines.append(
            f"| {setting} | {configuration} | "
            f"{row['accuracy_passes']}/{row['accuracy_total']} ({percentage:.1f}%) | "
            f"{row['time_seconds_per_run'] / 60 / row['accuracy_total']:.2f} | "
            f"{row['tokens_per_run'] / 1_000_000:.2f} | "
            f"${format_cost(row['recorded_cost_usd_per_run'])} | "
            f"{basis_labels[row['result_basis']]} |"
        )
    return "\n".join(lines)


def replace_results_block(content: str, table: str) -> str:
    if START_MARKER not in content or END_MARKER not in content:
        raise ValueError("README is missing results table markers")
    before, remainder = content.split(START_MARKER, 1)
    _, after = remainder.split(END_MARKER, 1)
    return f"{before}{START_MARKER}\n{table}\n{END_MARKER}{after}"


def readme_updates(payload: dict) -> dict[Path, str]:
    updates: dict[Path, str] = {}
    for filename, locale in (("README.md", "en"), ("README.zh.md", "zh")):
        path = REPO_ROOT / filename
        content = path.read_text(encoding="utf-8")
        updates[path] = replace_results_block(content, results_table(payload, locale))
    return updates


def site_update(payload: dict) -> tuple[Path, str]:
    path = REPO_ROOT / "site" / "index.html"
    content = path.read_text(encoding="utf-8")
    if SITE_START_MARKER not in content or SITE_END_MARKER not in content:
        raise ValueError("site/index.html is missing embedded results markers")
    before, remainder = content.split(SITE_START_MARKER, 1)
    _, after = remainder.split(SITE_END_MARKER, 1)
    embedded = json.dumps(payload, ensure_ascii=False, indent=2)
    block = f'{SITE_START_MARKER}\n    <script id="results-data" type="application/json">\n{embedded}\n    </script>\n    {SITE_END_MARKER}'
    return path, f"{before}{block}{after}"


def published_updates(payload: dict) -> dict[Path, str]:
    updates = readme_updates(payload)
    path, content = site_update(payload)
    updates[path] = content
    return updates


def check_readmes(payload: dict) -> list[str]:
    errors: list[str] = []
    try:
        updates = published_updates(payload)
    except (OSError, ValueError) as exc:
        return [str(exc)]
    for path, expected in updates.items():
        if path.read_text(encoding="utf-8") != expected:
            errors.append(f"{path.relative_to(REPO_ROOT)} is out of sync; run scripts/sync_results.py")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Keep README result tables aligned with site/results.json")
    parser.add_argument("--check", action="store_true", help="check without modifying files")
    args = parser.parse_args()

    payload = load_results()
    errors = validate_results(payload)
    if errors:
        for error in errors:
            print(f"- {error}")
        return 1

    if args.check:
        errors = check_readmes(payload)
        if errors:
            for error in errors:
                print(f"- {error}")
            return 1
        print("published results and README tables are in sync")
        return 0

    for path, content in published_updates(payload).items():
        path.write_text(content, encoding="utf-8")
        print(f"updated {path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
