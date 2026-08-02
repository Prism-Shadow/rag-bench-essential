#!/usr/bin/env python3
"""DABstep 官方 task 1681 校验脚本（隔离真值版）。

DABstep 的列表型答案按**无序集合**判定。把 answers.json 的 answer 与 gold
（expected.json）都解析成 fee ID 集合后比较。物理隔离：本脚本与 expected.json
放在 truth/，不进 workspace；判分时 cwd=workspace（读 answers.json），真值从
BENCH_TRUTH_DIR（缺省本脚本同级）读。退出码：0 正确；1 不匹配；2 缺文件。
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path


def as_id_set(value) -> set[str]:
    """把 'A, B, C' / 列表 / 'Not Applicable' / '' 解析成规范化 token 集合。"""
    if value is None:
        return set()
    if isinstance(value, (list, tuple)):
        value = ", ".join(str(v) for v in value)
    s = str(value).strip()
    if s == "" or s.lower() in ("not applicable", "n/a", "none"):
        return set()
    return {tok.strip() for tok in re.split(r"[,\s]+", s) if tok.strip()}


def truth_path() -> Path:
    env = os.environ.get("BENCH_TRUTH_DIR")
    if env:
        return Path(env) / "expected.json"
    return Path(__file__).resolve().parent / "expected.json"


def main() -> int:
    answers_path = Path("answers.json")
    if not answers_path.exists():
        print(f"FAIL: 找不到 {answers_path.resolve()}（Agent 未产出答案文件）")
        return 2

    answers = json.loads(answers_path.read_text(encoding="utf-8"))
    expected = json.loads(truth_path().read_text(encoding="utf-8"))

    exp = as_id_set(expected.get("answer"))
    got = as_id_set(answers.get("answer"))
    ok = got == exp

    print(f"[{'OK  ' if ok else 'FAIL'}] {len(got)} ids given, {len(exp)} expected")
    if not ok:
        missing = sorted(exp - got, key=lambda x: (len(x), x))
        extra = sorted(got - exp, key=lambda x: (len(x), x))
        if missing:
            print(f"  missing (in gold, not answered): {', '.join(missing)}")
        if extra:
            print(f"  extra (answered, not in gold):   {', '.join(extra)}")
        print("\nRESULT: FAIL — fee ID 集合与 gold 不一致。")
        return 1
    print("\nRESULT: PASS — fee ID 集合完全匹配 gold。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
