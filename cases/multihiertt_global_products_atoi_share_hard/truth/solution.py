#!/usr/bin/env python3
"""Reference solution for the MultiHiertt ATOI share-change case."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path


TOTAL_RE = re.compile(
    r"ATOI for all reportable segments totaled \$(\d[\d,]*) in 2016, "
    r"\$(\d[\d,]*) in 2015, and \$(\d[\d,]*) in 2014\."
)
SEG_RE = re.compile(r"ATOI of (201[456]) is \$(\d[\d,]*)")


def data_dir() -> Path:
    env = os.environ.get("BENCH_DATA_DIR")
    if env:
        return Path(env)
    here = Path(__file__).resolve().parent
    for candidate in (here.parent / "data", Path("data")):
        if (candidate / "corpus.jsonl").exists():
            return candidate
    raise SystemExit("cannot locate data/corpus.jsonl; set BENCH_DATA_DIR")


def amount(raw: str) -> int:
    return int(raw.replace(",", ""))


def load_docs(path: Path):
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            yield json.loads(line)


def main() -> None:
    candidates = []
    for doc in load_docs(data_dir() / "corpus.jsonl"):
        total_values = None
        for para in doc.get("paragraphs", []):
            match = TOTAL_RE.search(para)
            if match:
                total_values = {
                    2016: amount(match.group(1)),
                    2015: amount(match.group(2)),
                    2014: amount(match.group(3)),
                }
                break
        if not total_values:
            continue
        if not any("Global Rolled Products" in para for para in doc.get("paragraphs", [])):
            continue

        segment_values = {}
        for desc in doc.get("table_descriptions", {}).values():
            match = SEG_RE.search(desc)
            if match:
                segment_values[int(match.group(1))] = amount(match.group(2))

        if 2015 in segment_values and 2014 in segment_values:
            candidates.append((doc["doc_key"], total_values, segment_values))

    if len(candidates) != 1:
        raise SystemExit(f"expected exactly one candidate document, found {len(candidates)}")

    doc_key, total, segment = candidates[0]
    answer = (segment[2015] / total[2015]) - (segment[2014] / total[2014])
    calculation = f"({segment[2015]} / {total[2015]}) - ({segment[2014]} / {total[2014]})"
    result = {
        "answer": f"{answer:.5f}",
        "doc_key": doc_key,
        "calculation": calculation,
    }
    Path("answers.json").write_text(
        json.dumps(result, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"doc_key: {doc_key}")
    print(f"calculation: {calculation}")
    print(f"answer_exact: {answer:.15f}")
    print(f"answer_for_benchmark: {answer:.5f}")


if __name__ == "__main__":
    main()
