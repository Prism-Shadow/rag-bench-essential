#!/usr/bin/env python3
"""Reference solver for fdabench_app_sentiment_xsource_hard_v2.

Computes the gold Multi-Genre Excess Subjectivity (MGES) and the audit
checkpoints from the real BIRD app_store sources. Not copied into a workspace.

Usage:
    python3 solution.py [DATA_DIR]      # DATA_DIR defaults to ./data
"""
from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

B0 = 0.42  # MGES single-genre control (methodology_review.md, breadth branch)


def subj(x):
    """Parse Sentiment_Subjectivity; return None for blank/nan/garbage."""
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(v) else v


def main() -> int:
    data = Path(sys.argv[1] if len(sys.argv) > 1 else "data")
    playstore = list(csv.DictReader((data / "playstore.csv").open(encoding="utf-8")))
    reviews = list(csv.DictReader((data / "user_reviews.csv").open(encoding="utf-8")))

    # Multi-genre apps: the Genres field lists 2+ genres joined by ';'.
    multi = {r["App"] for r in playstore if ";" in (r.get("Genres") or "")}

    # MGES = sum over multi-genre reviews with a *defined* subjectivity of (s - b0).
    valid = [subj(r["Sentiment_Subjectivity"]) for r in reviews if r["App"] in multi]
    valid = [v for v in valid if v is not None]
    n = len(valid)
    raw_sum = sum(valid)
    mges = raw_sum - B0 * n

    print(f"multi_genre_app_count          = {len(multi)}")
    print(f"valid_multi_genre_review_count = {n}")
    print(f"raw_subjectivity_sum           = {raw_sum:.5f}")
    print(f"baseline_used                  = {B0}")
    print(f"MGES                           = {mges:.5f}  -> {round(mges, 2)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
