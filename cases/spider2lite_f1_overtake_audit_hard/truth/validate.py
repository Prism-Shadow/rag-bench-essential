#!/usr/bin/env python3
"""External validator for the Spider2-Lite F1 overtake audit case.

Physical isolation: this script stays in truth/ and is not copied into an agent
workspace. Run it with cwd set to the workspace. Truth files are resolved from
BENCH_TRUTH_DIR, or from this script's directory by default.

Scoring dimensions:
  D1 answer correctness:
     - Part A must match the unified clean-engine gold counts.
     - Part B must match the unified clean-engine gold counts.
     - Part C must match the unified clean-engine track-only driver list.
  D2 evidence binding: evidence.json must bind tables, taxonomy, direction, and
     exclusions to sources, including the Race-row event eligibility rule.
  D4 delivery: all CSV outputs, evidence.json, and report.md must exist.

Exit codes:
  0: pass.
  1: answer/evidence/delivery mismatch.
  2: missing or unreadable required output.
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys
import unicodedata
from pathlib import Path


PARTS = {
    "part_a": {
        "output": Path("answers/overtake_counts_all.csv"),
        "variant_dir": "local344",
        "kind": "counts",
    },
    "part_b": {
        "output": Path("answers/overtake_counts_first5.csv"),
        "variant_dir": "local336",
        "kind": "counts",
    },
    "part_c": {
        "output": Path("answers/track_deficit_drivers.csv"),
        "variant_dir": "local356",
        "kind": "drivers",
    },
}


def truth_dir() -> Path:
    env = os.environ.get("BENCH_TRUTH_DIR")
    return Path(env) if env else Path(__file__).resolve().parent


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    try:
        with path.open(newline="", encoding="utf-8-sig") as f:
            return list(csv.DictReader(f))
    except Exception as exc:
        raise ValueError(f"cannot read CSV {path}: {exc}") from exc


def normalize_category(value: object) -> str | None:
    raw = str(value or "").strip().strip('"').strip("'")
    key = re.sub(r"[^a-z0-9]+", " ", raw.lower()).strip()
    aliases = {
        "r": "R",
        "retirement": "R",
        "retirements": "R",
        "retirement related": "R",
        "p": "P",
        "pit": "P",
        "pit stop": "P",
        "pit stops": "P",
        "pit related": "P",
        "s": "S",
        "start": "S",
        "start related": "S",
        "t": "T",
        "track": "T",
        "on track": "T",
        "normal track": "T",
        "normal on track passes": "T",
        "standard on track passes": "T",
    }
    return aliases.get(key)


def parse_number(value: object) -> int | None:
    text = str(value or "").strip().replace(",", "")
    try:
        return int(round(float(text)))
    except ValueError:
        return None


def parse_counts(path: Path) -> dict[str, int]:
    rows = read_csv_rows(path)
    out: dict[str, int] = {}
    for row in rows:
        if not row:
            continue
        keys = list(row.keys())
        cat_value = row.get("overtake_type") or row.get("OVERTAKE_TYPE") or row.get("category") or row.get("Category") or row.get(keys[0])
        count_value = (
            row.get("num_overtakes")
            or row.get("OVERTAKE_COUNT")
            or row.get("overtake_count")
            or row.get("overtakes")
            or row.get("count")
            or row.get(keys[1] if len(keys) > 1 else keys[0])
        )
        cat = normalize_category(cat_value)
        count = parse_number(count_value)
        if cat is None or count is None:
            raise ValueError(f"cannot parse count row in {path}: {row}")
        out[cat] = count
    return out


def normalize_name(value: object) -> str:
    """Fold accents, case, quote style, and whitespace for driver-name matching.

    Part C is a hard gate, so a semantically correct answer must not fail on
    cosmetic name formatting (e.g. "Gutiérrez" vs "Gutierrez", curly vs straight
    apostrophe, double spaces). Both gold and agent answers pass through here.
    """
    text = str(value or "").strip().strip('"').strip("'")
    # unify common unicode apostrophe/quote variants to a straight apostrophe
    text = text.replace("’", "'").replace("ʼ", "'").replace("`", "'")
    # decompose and drop combining marks (accent folding)
    text = "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))
    # collapse internal whitespace and casefold
    text = re.sub(r"\s+", " ", text).strip().casefold()
    return text


def parse_driver_set(path: Path) -> set[str]:
    rows = read_csv_rows(path)
    names: set[str] = set()
    for row in rows:
        if not row:
            continue
        keys = list(row.keys())
        value = row.get("full_name") or row.get("FULL_NAME") or row.get(keys[0])
        name = normalize_name(value)
        if name:
            names.add(name)
    return names


def expected_variants(part: str, kind: str) -> list[object]:
    base = truth_dir() / "expected_variants" / PARTS[part]["variant_dir"]
    files = sorted(base.glob("*.csv"))
    if not files:
        raise ValueError(f"no expected variants found under {base}")
    if kind == "counts":
        return [parse_counts(p) for p in files]
    return [parse_driver_set(p) for p in files]


def compare_part(part: str) -> tuple[bool, str]:
    cfg = PARTS[part]
    path = cfg["output"]
    if not path.exists():
        raise FileNotFoundError(f"missing {path}")
    kind = cfg["kind"]
    got = parse_counts(path) if kind == "counts" else parse_driver_set(path)
    variants = expected_variants(part, kind)
    for idx, expected in enumerate(variants, start=1):
        if got == expected:
            if kind == "drivers":
                return True, f"matched variant {idx}; driver_count={len(got)}"
            return True, f"matched variant {idx}; counts={got}"
    if kind == "drivers":
        sizes = [len(v) for v in variants]
        return False, f"no variant match; got_driver_count={len(got)} expected_variant_sizes={sizes}"
    return False, f"no variant match; got={got} expected_variants={variants}"


def load_json(path: Path) -> object | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def evidence_checks() -> bool:
    ev = load_json(Path("evidence.json"))
    if ev is None:
        print("  [MISS] evidence.json missing or invalid")
        return False
    blob = json.dumps(ev, ensure_ascii=False).lower()

    table_terms = ["lap_positions", "pit_stops", "retirements", "races_ext", "results", "drivers"]
    table_hits = [term for term in table_terms if term in blob]
    taxonomy_terms = ["retirement", "pit", "start", "track"]
    taxonomy_ok = all(term in blob for term in taxonomy_terms)
    doc_ok = "f1_overtake" in blob or taxonomy_ok
    event_ok = "lap_type" in blob and "race" in blob and "grid" in blob
    priority_ok = "priority" in blob and all(code.lower() in blob for code in ["r", "p", "s", "t"])
    pit_exit_ok = (
        "pit exit" in blob
        or "p_exit" in blob
        or "previous lap (exit)" in blob
        or "lap immediately before" in blob
    ) and ("previous lap" in blob or "lap - 1" in blob or "lap-1" in blob or "lap immediately before" in blob)
    direction_ok = (
        ("overtook" in blob and "overtaken" in blob)
        or ("behind" in blob and "direction" in blob)
        or ("pairwise" in blob and "driver" in blob)
    )
    exclusion_ok = all(term in blob for term in ["pit", "retirement", "start"]) and ("first lap" in blob or "lap 1" in blob)

    table_ok = len(table_hits) >= 5
    evidence_ok = table_ok and taxonomy_ok and doc_ok and event_ok and priority_ok and pit_exit_ok and direction_ok and exclusion_ok

    print(f"  [{'OK ' if table_ok else 'MISS'}] table binding hits={table_hits}")
    print(f"  [{'OK ' if taxonomy_ok else 'MISS'}] R/P/S/T taxonomy terms present")
    print(f"  [{'OK ' if event_ok else 'MISS'}] Race-row event eligibility and grid start state documented")
    print(f"  [{'OK ' if priority_ok else 'MISS'}] R/P/S/T priority documented")
    print(f"  [{'OK ' if pit_exit_ok else 'MISS'}] pit exit previous-lap rule documented")
    print(f"  [{'OK ' if direction_ok else 'MISS'}] overtook/overtaken direction documented")
    print(f"  [{'OK ' if exclusion_ok else 'MISS'}] Part C exclusions documented")
    return evidence_ok


def delivery_ok() -> bool:
    ok = True
    for cfg in PARTS.values():
        path = cfg["output"]
        present = path.exists() and path.stat().st_size > 0
        ok = ok and present
        print(f"  [{'OK ' if present else 'MISS'}] {path}")
    ev_present = Path("evidence.json").exists()
    report = Path("report.md")
    report_ok = report.exists() and len(report.read_text(encoding="utf-8", errors="replace").strip()) >= 120
    print(f"  [{'OK ' if ev_present else 'MISS'}] evidence.json")
    print(f"  [{'OK ' if report_ok else 'MISS'}] report.md non-trivial")
    return ok and ev_present and report_ok


def main() -> int:
    print("== D1 official execution outputs ==")
    statuses: dict[str, bool] = {}
    missing = False
    for part in ["part_a", "part_b", "part_c"]:
        try:
            ok, msg = compare_part(part)
        except FileNotFoundError as exc:
            print(f"  [MISS] {part}: {exc}")
            statuses[part] = False
            missing = True
            continue
        except Exception as exc:
            print(f"  [FAIL] {part}: {exc}")
            statuses[part] = False
            continue
        statuses[part] = ok
        print(f"  [{'OK ' if ok else 'WARN'}] {part}: {msg}")

    if missing:
        print("\nRESULT: FAIL - missing required output files.")
        return 2

    print("== D2 evidence binding ==")
    evidence_ok = evidence_checks()
    print("== D4 delivery ==")
    deliver_ok = delivery_ok()

    answers_ok = all(statuses.get(part, False) for part in ["part_a", "part_b", "part_c"])

    if answers_ok and evidence_ok and deliver_ok:
        print("\nRESULT: PASS - all three parts match unified clean-engine gold.")
        return 0

    if not answers_ok:
        print("\nRESULT: FAIL - one or more answer files did not match unified clean-engine gold.")
    else:
        print("\nRESULT: FAIL - answers match, but evidence or delivery checks failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
