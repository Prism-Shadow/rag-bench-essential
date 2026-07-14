#!/usr/bin/env python3
import csv
import json
import math
import os
import sys
from pathlib import Path


def truth_dir() -> Path:
    return Path(os.environ.get("BENCH_TRUTH_DIR", Path(__file__).resolve().parent))


def read_json(path: Path):
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        print(f"MISSING: {path}")
        sys.exit(2)
    except Exception as exc:
        print(f"UNREADABLE: {path}: {exc}")
        sys.exit(2)


def fail(messages):
    for msg in messages:
        print(f"FAIL: {msg}")
    sys.exit(1)


def check_close(actual, expected, tol, label, errors):
    try:
        actual_value = float(actual)
    except Exception:
        errors.append(f"{label}: not numeric: {actual!r}")
        return
    if math.isnan(actual_value) or abs(actual_value - float(expected)) > tol:
        errors.append(f"{label}: expected {expected}, got {actual_value}")


def check_png(path: Path, errors):
    try:
        signature = path.read_bytes()[:8]
    except FileNotFoundError:
        print(f"MISSING: {path}")
        sys.exit(2)
    except Exception as exc:
        print(f"UNREADABLE: {path}: {exc}")
        sys.exit(2)
    if signature != b"\x89PNG\r\n\x1a\n":
        errors.append("figure.png is not a valid PNG file")


def main() -> None:
    expected = read_json(truth_dir() / "expected.json")
    errors = []

    for required in expected["required_outputs"]:
        if not Path(required).exists():
            print(f"MISSING: {required}")
            sys.exit(2)

    answers = read_json(Path("answers.json"))
    chart = expected["chart"]
    intermediates = expected["key_intermediates"]
    required_answer_fields = {
        "case_id": expected["case_id"],
        "chart_type": chart["chart_type"],
        "source_file": intermediates["source_file"],
        "year": intermediates["year"],
        "node_count": chart["node_count"],
        "edge_count": chart["edge_count"],
        "threshold_abs_corr": intermediates["threshold_abs_corr"],
        "node_order": intermediates["node_order"],
        "title": chart["title"],
    }
    for key, value in required_answer_fields.items():
        if answers.get(key) != value:
            errors.append(f"answers.json field {key}: expected {value!r}, got {answers.get(key)!r}")

    try:
        with Path("derived_edges.csv").open(newline="") as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)
            if reader.fieldnames != expected["csv_columns"]:
                errors.append(
                    f"derived_edges.csv columns: expected {expected['csv_columns']}, got {reader.fieldnames}"
                )
    except Exception as exc:
        print(f"UNREADABLE: derived_edges.csv: {exc}")
        sys.exit(2)

    gold_rows = expected["derived_edges"]
    if len(rows) != len(gold_rows):
        errors.append(f"derived_edges.csv row count: expected {len(gold_rows)}, got {len(rows)}")
    tol = expected["tolerances"]["float_abs"]
    for idx, gold in enumerate(gold_rows[: len(rows)]):
        row = rows[idx]
        for key in ("source", "target", "sign", "strength_bin", "edge_color_hex"):
            if row.get(key) != gold[key]:
                errors.append(
                    f"row {idx + 1} {key}: expected {gold[key]!r}, got {row.get(key)!r}"
                )
        for key in ("corr", "abs_corr", "edge_width"):
            check_close(row.get(key), gold[key], tol, f"row {idx + 1} {key}", errors)

    spec = read_json(Path("chart_spec.json"))
    if spec.get("title") != chart["title"]:
        errors.append("chart_spec.json title mismatch")
    if spec.get("mark") != "network":
        errors.append("chart_spec.json mark must be network")
    layout = spec.get("layout", {})
    for key, value in chart["layout"].items():
        if layout.get(key) != value:
            errors.append(f"chart_spec.json layout.{key}: expected {value!r}, got {layout.get(key)!r}")
    if layout.get("node_order") != intermediates["node_order"]:
        errors.append("chart_spec.json layout.node_order mismatch")
    nodes = spec.get("nodes", {})
    if nodes.get("values") != intermediates["node_order"]:
        errors.append("chart_spec.json nodes.values mismatch")
    if nodes.get("fill") != chart["node_fill"] or nodes.get("stroke") != chart["node_stroke"]:
        errors.append("chart_spec.json node styling mismatch")
    edges = spec.get("edges", {})
    edge_expect = {
        "data": "derived_edges.csv",
        "source": "source",
        "target": "target",
        "weight": "corr",
        "threshold_abs_corr": intermediates["threshold_abs_corr"],
        "undirected": True,
        "self_loops": False,
    }
    for key, value in edge_expect.items():
        if edges.get(key) != value:
            errors.append(f"chart_spec.json edges.{key}: expected {value!r}, got {edges.get(key)!r}")
    enc = spec.get("edge_encoding", {})
    color = enc.get("color", {})
    if color.get("positive") != chart["edge_color_positive"]:
        errors.append("chart_spec.json positive edge color mismatch")
    if color.get("negative") != chart["edge_color_negative"]:
        errors.append("chart_spec.json negative edge color mismatch")
    width = enc.get("width", {})
    for bin_name, width_value in chart["width_by_bin"].items():
        check_close(width.get(bin_name), width_value, tol, f"chart_spec width {bin_name}", errors)

    check_png(Path("figure.png"), errors)

    if errors:
        fail(errors)
    print("PASS: DV-World crime association network outputs match expected semantics")


if __name__ == "__main__":
    main()
