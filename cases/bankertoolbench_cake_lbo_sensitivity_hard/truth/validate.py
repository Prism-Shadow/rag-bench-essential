#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from scoring.rule_checks import check_banker_workbook


def truth_dir() -> Path:
    return Path(os.environ.get("BENCH_TRUTH_DIR", Path(__file__).resolve().parent))


def load_expected() -> dict:
    return json.loads((truth_dir() / "expected.json").read_text(encoding="utf-8"))


def score_workbook(expected: dict) -> bool:
    result = check_banker_workbook(Path(expected["required_outputs"][0]), expected)
    details = result.details or {}
    base_ok = bool(details.get("base_irr_present"))
    print(f"  [{'OK ' if base_ok else 'MISS'}] base IRR cell {expected['base_irr_cell']} present")
    for table in details.get("tables", []):
        candidate = table.get("candidate") or {}
        print(f"  [{'OK ' if table['x_axis_found'] else 'MISS'}] {table['id']} x-axis values")
        print(f"  [{'OK ' if table['y_axis_found'] else 'MISS'}] {table['id']} y-axis values")
        print(
            f"  [{'OK ' if table['passed'] else 'MISS'}] {table['id']} has a 5x5 IRR/formula grid "
            f"(found {candidate.get('irr_count', 0)} cells)"
        )
    if not details:
        print(f"  [MISS] {result.message}")
    return result.passed


def pptx_text(path: Path) -> tuple[list[str], int]:
    with zipfile.ZipFile(path) as zf:
        slide_names = sorted(name for name in zf.namelist() if re.match(r"ppt/slides/slide\d+\.xml", name))
        texts: list[str] = []
        for name in slide_names:
            root = ET.fromstring(zf.read(name))
            for node in root.iter():
                if node.tag.endswith("}t") and node.text:
                    texts.append(node.text)
    return texts, len(slide_names)


def score_ppt(expected: dict) -> bool:
    path = Path(expected["required_outputs"][1])
    try:
        texts, slide_count = pptx_text(path)
    except Exception as exc:
        print(f"  [MISS] pptx unreadable: {exc}")
        return False
    blob = "\n".join(texts).lower()
    slide_ok = slide_count == int(expected["ppt_required_slide_count"])
    print(f"  [{'OK ' if slide_ok else 'MISS'}] slide count={slide_count}")
    tokens_ok = True
    for token in expected["ppt_required_tokens"]:
        hit = token.lower() in blob
        print(f"  [{'OK ' if hit else 'MISS'}] PPT token: {token}")
        tokens_ok = tokens_ok and hit
    return slide_ok and tokens_ok


def score_pdf(expected: dict) -> bool:
    path = Path(expected["required_outputs"][2])
    try:
        data = path.read_bytes()
    except Exception as exc:
        print(f"  [MISS] PDF unreadable: {exc}")
        return False
    ok = data.startswith(b"%PDF") and len(data) >= 1000
    print(f"  [{'OK ' if ok else 'MISS'}] PDF exists, has PDF header, and is non-trivial")
    return ok


def main() -> int:
    expected = load_expected()
    missing = [name for name in expected["required_outputs"] if not Path(name).exists()]
    if missing:
        print("FAIL: required output files missing:")
        for name in missing:
            print(f"  - {name}")
        return 2
    print("== D1/D3 Excel sensitivity tables ==")
    workbook_ok = score_workbook(expected)
    print("== D4 PowerPoint deck ==")
    ppt_ok = score_ppt(expected)
    print("== D4 PDF export ==")
    pdf_ok = score_pdf(expected)
    if workbook_ok and ppt_ok and pdf_ok:
        print("\nRESULT: PASS - Excel/PPT/PDF sensitivity deliverables satisfy the deterministic gates.")
        return 0
    print("\nRESULT: FAIL - sensitivity table structure or deliverables are incomplete.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
