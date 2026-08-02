#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path


def truth_dir() -> Path:
    return Path(os.environ.get("BENCH_TRUTH_DIR", Path(__file__).resolve().parent))


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"MISSING: {path}")
        raise SystemExit(2)
    except Exception as exc:
        print(f"UNREADABLE: {path}: {exc}")
        raise SystemExit(2)


def close(actual, expected, tolerance: float) -> bool:
    try:
        value = float(actual)
    except (TypeError, ValueError):
        return False
    return math.isfinite(value) and abs(value - float(expected)) <= tolerance


def main() -> int:
    expected = read_json(truth_dir() / "expected.json")
    missing = [name for name in expected["required_outputs"] if not Path(name).exists()]
    if missing:
        print("FAIL: required final chart artifacts missing:")
        for name in missing:
            print(f"  - {name}")
        return 2

    spec = read_json(Path("chart_spec.json"))
    chart = expected["chart"]
    inter = expected["key_intermediates"]
    tolerance = float(expected["tolerances"]["float_abs"])
    errors: list[str] = []

    scalar_fields = {
        "source_file": inter["source_file"],
        "year": inter["year"],
        "title": chart["title"],
        "mark": "network",
    }
    for key, value in scalar_fields.items():
        if spec.get(key) != value:
            errors.append(f"{key}: expected {value!r}, got {spec.get(key)!r}")

    layout = spec.get("layout", {})
    for key, value in {**chart["layout"], "node_order": inter["node_order"]}.items():
        if layout.get(key) != value:
            errors.append(f"layout.{key}: expected {value!r}, got {layout.get(key)!r}")

    nodes = spec.get("nodes", {})
    node_fields = {
        "values": inter["node_order"],
        "fill": chart["node_fill"],
        "stroke": chart["node_stroke"],
    }
    for key, value in node_fields.items():
        if nodes.get(key) != value:
            errors.append(f"nodes.{key}: expected {value!r}, got {nodes.get(key)!r}")

    edges = spec.get("edges", {})
    edge_fields = {
        "source": "source",
        "target": "target",
        "weight": "corr",
        "threshold_abs_corr": inter["threshold_abs_corr"],
        "undirected": True,
        "self_loops": False,
    }
    for key, value in edge_fields.items():
        if edges.get(key) != value:
            errors.append(f"edges.{key}: expected {value!r}, got {edges.get(key)!r}")

    rows = edges.get("values")
    if not isinstance(rows, list):
        errors.append("edges.values must be a list")
        rows = []
    gold_rows = expected["edges"]
    if len(rows) != len(gold_rows):
        errors.append(f"edges.values count: expected {len(gold_rows)}, got {len(rows)}")
    for idx, gold in enumerate(gold_rows[: len(rows)]):
        row = rows[idx]
        if not isinstance(row, dict):
            errors.append(f"edges.values[{idx}] must be an object")
            continue
        for key in ("source", "target", "sign", "strength_bin", "edge_color_hex"):
            if row.get(key) != gold[key]:
                errors.append(f"edges.values[{idx}].{key}: expected {gold[key]!r}, got {row.get(key)!r}")
        for key in ("corr", "abs_corr", "edge_width"):
            if not close(row.get(key), gold[key], tolerance):
                errors.append(f"edges.values[{idx}].{key}: expected {gold[key]!r}, got {row.get(key)!r}")

    encoding = spec.get("edge_encoding", {})
    color = encoding.get("color", {})
    color_fields = {
        "field": "sign",
        "positive": chart["edge_color_positive"],
        "negative": chart["edge_color_negative"],
    }
    for key, value in color_fields.items():
        if color.get(key) != value:
            errors.append(f"edge_encoding.color.{key}: expected {value!r}, got {color.get(key)!r}")
    width = encoding.get("width", {})
    if width.get("field") != "strength_bin":
        errors.append("edge_encoding.width.field must be strength_bin")
    for key, value in chart["width_by_bin"].items():
        if not close(width.get(key), value, tolerance):
            errors.append(f"edge_encoding.width.{key}: expected {value!r}, got {width.get(key)!r}")

    try:
        png = Path("figure.png").read_bytes()
    except OSError as exc:
        print(f"UNREADABLE: figure.png: {exc}")
        return 2
    if not png.startswith(b"\x89PNG\r\n\x1a\n"):
        errors.append("figure.png is not a valid PNG")

    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("PASS: final chart specification matches expected network semantics; visual usability is scored separately")
    return 0


if __name__ == "__main__":
    sys.exit(main())
