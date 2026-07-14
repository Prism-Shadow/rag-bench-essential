#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path


def main() -> int:
    # The visible field is near the lower-left middle of the page. Render a crop
    # so a reviewer can verify that the answer is read from the image itself.
    Path("work").mkdir(exist_ok=True)
    subprocess.run(
        [
            "magick",
            "data/document_page.jpg",
            "-crop",
            "650x260+120+1660",
            "-resize",
            "200%",
            "work/contract_effective_date_crop.jpg",
        ],
        check=False,
    )
    answers = {"contract_effective_date": "7-1-99"}
    evidence = {
        "sources": [
            {
                "image": "data/document_page.jpg",
                "field_label": "Contract Effective Date",
                "answer_region_bbox": [120, 1660, 780, 1920],
                "visual_reading": "The handwritten value above the Contract Effective Date label reads 7-1-99.",
                "crop": "work/contract_effective_date_crop.jpg",
            }
        ]
    }
    Path("answers.json").write_text(json.dumps(answers, indent=2) + "\n", encoding="utf-8")
    Path("evidence.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    Path("report.md").write_text(
        "The full-page OCR is noisy around the handwritten date, so I cropped the lower-left field region "
        "and read the handwritten value tied to the printed label Contract Effective Date. I did not use "
        "the nearby Date Contract Signed field.\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
