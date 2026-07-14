#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


def page_text(page: int) -> str:
    return subprocess.check_output(
        ["pdftotext", "-layout", "-f", str(page), "-l", str(page), "data/annual_report.pdf", "-"],
        text=True,
    )


def main() -> int:
    workspace = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    old_cwd = Path.cwd()
    try:
        if workspace != Path.cwd():
            import os

            os.chdir(workspace)
        text = page_text(58)
        if "Oil, Gas and NGL Production" not in text or "Canada" not in text:
            raise RuntimeError("expected production table not found on page 58")

        canada_match = re.search(r"Canada\s+23\s+198\s+4\s+(\d+)", text)
        total_match = re.search(r"\bTotal\s+66\s+894\s+28\s+(\d+)", text)
        if not canada_match or not total_match:
            raise RuntimeError("could not parse Canada/Total MMBoe values")
        canada = int(canada_match.group(1))
        total = int(total_match.group(1))
        pct = canada / total * 100

        answers = {
            "answer": [f"{pct:.2f}%"],
            "calculation": {
                "canada_total_mmboe": canada,
                "company_total_mmboe": total,
                "percentage": round(pct, 2),
            },
        }
        quote = (
            "Oil, Gas and NGL Production table: Canada 23 oil, 198 gas, 4 NGLs, Total 60 MMBoe; "
            "Total 66 oil, 894 gas, 28 NGLs, Total 243 MMBoe."
        )
        evidence = {
            "sources": [
                {
                    "file": "data/annual_report.pdf",
                    "page": 58,
                    "supports": ["canada_total_mmboe", "company_total_mmboe"],
                    "quote": quote,
                }
            ]
        }
        report = (
            "# Report\n\n"
            "I used page-range PDF text extraction on the 116-page annual report and selected the "
            "`2008 Estimates` section's `Oil, Gas and NGL Production` table on PDF page 58. "
            "That table gives Canada total production of 60 MMBoe and company total production "
            "of 243 MMBoe. The calculation is 60 / 243 * 100 = 24.69%. I did not use the "
            "earlier operating-statistics or year-end-reserves table on page 27, because that "
            "table answers a different scope.\n"
        )

        Path("answers.json").write_text(json.dumps(answers, indent=2) + "\n", encoding="utf-8")
        Path("evidence.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
        Path("report.md").write_text(report, encoding="utf-8")
    finally:
        import os

        os.chdir(old_cwd)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
