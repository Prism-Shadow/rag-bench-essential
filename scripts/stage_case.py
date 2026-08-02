#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ALLOWED_ENTRIES = ("task.md", "data", "env.md")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create an evaluation-free case workspace.")
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--workspace", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = REPO_ROOT / "cases" / args.case_id
    workspace = args.workspace.resolve()
    if not source.is_dir():
        raise SystemExit(f"unknown case: {args.case_id}")
    if workspace.exists():
        raise SystemExit(f"workspace already exists: {workspace}")
    if not (source / "task.md").is_file():
        raise SystemExit(
            f"case payload is not materialized: {args.case_id}; see {source / 'README.md'}"
        )

    workspace.mkdir(parents=True)
    for name in ALLOWED_ENTRIES:
        item = source / name
        if not item.exists():
            continue
        target = workspace / name
        if item.is_dir():
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)

    forbidden = list(workspace.rglob("truth")) + list(workspace.rglob("evaluation"))
    if forbidden:
        raise SystemExit(f"evaluation material leaked into workspace: {forbidden}")
    print(workspace)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
