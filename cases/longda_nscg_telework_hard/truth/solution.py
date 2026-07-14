#!/usr/bin/env python3
"""Reference solution — NSCG 2023 telework counts by employer size.

Teleworkers = TELEC == 4 ("allowed to telework/work remotely and did"). Weighted
counts (WTSURVY) in thousands, by employer size (EMSIZE), with the two largest
size codes (7: 5000-24999, 8: 25000+) merged into size5000plus.

Run from the case dir (reads ../data) or set BENCH_DATA_DIR to the data folder.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import pandas as pd


def data_dir() -> Path:
    env = os.environ.get("BENCH_DATA_DIR")
    if env:
        return Path(env)
    here = Path(__file__).resolve().parent
    for cand in (here.parent / "data", Path("data")):
        if (cand / "epcg23.csv").exists():
            return cand
    raise SystemExit("cannot locate data/ (set BENCH_DATA_DIR)")


# EMSIZE code -> output bucket
BUCKET = {"1": "size10", "2": "size11_24", "3": "size25_99", "4": "size100_499",
          "5": "size500_999", "6": "size1000_4999", "7": "size5000plus",
          "8": "size5000plus"}
ORDER = ["size10", "size11_24", "size25_99", "size100_499", "size500_999",
         "size1000_4999", "size5000plus"]


def main() -> None:
    f = data_dir() / "epcg23.csv"
    df = pd.read_csv(f, usecols=["EMSIZE", "TELEC", "WTSURVY"], dtype={"EMSIZE": str, "TELEC": str})
    tw = df[df["TELEC"] == "4"].copy()
    tw["bucket"] = tw["EMSIZE"].map(BUCKET)
    counts = (tw.groupby("bucket")["WTSURVY"].sum() / 1000.0).round().astype(int)
    out = [int(counts.get(b, 0)) for b in ORDER]
    result = {"answer": [str(x) for x in out]}
    Path("answers.json").write_text(
        json.dumps(result, indent=2) + "\n",
        encoding="utf-8",
    )
    print(dict(zip(ORDER, out)))
    print("answer:", result["answer"])


if __name__ == "__main__":
    main()
