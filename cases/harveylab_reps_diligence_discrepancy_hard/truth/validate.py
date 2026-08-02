#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


OUTPUT = Path("reps-vs-diligence-memo.docx")


def truth_dir() -> Path:
    return Path(os.environ.get("BENCH_TRUTH_DIR", Path(__file__).resolve().parent))


def load_expected() -> dict:
    return json.loads((truth_dir() / "expected.json").read_text(encoding="utf-8"))


def docx_text(path: Path) -> str:
    try:
        with zipfile.ZipFile(path) as zf:
            xml = zf.read("word/document.xml")
    except Exception as exc:
        raise ValueError(f"cannot read docx document.xml: {exc}") from exc
    root = ET.fromstring(xml)
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    chunks: list[str] = []
    for node in root.findall(".//w:t", ns):
        if node.text:
            chunks.append(node.text)
    return "\n".join(chunks)


def norm(value: str) -> str:
    value = value.casefold()
    value = value.replace("\u2013", "-").replace("\u2014", "-").replace("\u00a0", " ")
    value = re.sub(r"[\s_]+", " ", value)
    return value


def contains(text: str, needle: str) -> bool:
    n = norm(needle)
    if n in text:
        return True
    compact_text = text.replace(",", "")
    compact_needle = n.replace(",", "")
    return compact_needle in compact_text


def group_hit(text: str, group) -> bool:
    if isinstance(group, str):
        return contains(text, group)
    return any(contains(text, item) for item in group)


def count_token_hits(text: str, tokens: list[str]) -> int:
    return sum(1 for token in tokens if contains(text, token))


def count_severity_mentions(text: str, tokens: list[str]) -> int:
    return sum(len(re.findall(rf"\b{re.escape(norm(token))}\b", text)) for token in tokens)


def main() -> int:
    expected = load_expected()
    if not OUTPUT.exists():
        print(f"FAIL: required output missing: {OUTPUT}")
        return 2
    try:
        text_raw = docx_text(OUTPUT)
    except ValueError as exc:
        print(f"FAIL: {exc}")
        return 2

    text = norm(text_raw)
    delivery_ok = len(text.strip()) >= 2500
    print("== D4 delivery ==")
    print(f"  [{'OK ' if delivery_ok else 'MISS'}] readable non-trivial docx text length={len(text.strip())}")

    print("== D1 discrepancy coverage ==")
    hits: list[str] = []
    for issue in expected["issues"]:
        ok = all(group_hit(text, group) for group in issue["groups"])
        if ok:
            hits.append(issue["id"])
        print(f"  [{'OK ' if ok else 'MISS'}] {issue['id']}: {issue['label']}")
    coverage_ok = len(hits) >= int(expected["minimum_issue_hits"])
    print(f"  issue coverage: {len(hits)}/{len(expected['issues'])} hit; required >= {expected['minimum_issue_hits']}")

    print("== D2 source and section binding ==")
    source_hits = count_token_hits(text, expected["source_tokens"])
    section_hits = count_token_hits(text, expected["section_tokens"])
    source_ok = source_hits >= int(expected["minimum_source_mentions"])
    section_ok = section_hits >= int(expected["minimum_section_mentions"])
    print(f"  [{'OK ' if source_ok else 'MISS'}] source families mentioned {source_hits}; required >= {expected['minimum_source_mentions']}")
    print(f"  [{'OK ' if section_ok else 'MISS'}] SPA section/schedule markers mentioned {section_hits}; required >= {expected['minimum_section_mentions']}")

    print("== D3 memo controls ==")
    severity_mentions = count_severity_mentions(text, expected["severity_tokens"])
    recommendation_hits = count_token_hits(text, expected["recommendation_tokens"])
    severity_ok = severity_mentions >= int(expected["minimum_severity_mentions"])
    recommendation_ok = recommendation_hits >= int(expected["minimum_recommendation_mentions"])
    print(f"  [{'OK ' if severity_ok else 'MISS'}] severity labels count={severity_mentions}; required >= {expected['minimum_severity_mentions']}")
    print(f"  [{'OK ' if recommendation_ok else 'MISS'}] recommendation action families hit={recommendation_hits}; required >= {expected['minimum_recommendation_mentions']}")

    if delivery_ok and coverage_ok and source_ok and section_ok and severity_ok and recommendation_ok:
        print("\nRESULT: PASS - memo identifies enough material discrepancies with source binding and deal-team controls.")
        return 0

    print("\nRESULT: FAIL - memo coverage, binding, or delivery is incomplete.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
