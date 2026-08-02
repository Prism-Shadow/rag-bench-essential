from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


VALID_JUDGES = {"rule", "validator", "trace", "llm", "hybrid"}
VALID_DIMENSIONS = {
    "D1_answer",
    "D2_evidence_binding",
    "D3_key_intermediate",
    "D4_delivery",
    "D5_runtime_harness",
}
VALID_FAILURE_LAYERS = {
    "retrieval_miss",
    "evidence_binding",
    "program_semantics",
    "calculation",
    "completion_contract",
    "delivery_path",
    "runtime_harness",
}


class RubricError(ValueError):
    pass


def load_rubric(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RubricError(f"rubric not found: {path}") from exc
    except Exception as exc:
        raise RubricError(f"rubric unreadable: {path}: {exc}") from exc
    validate_rubric(data, source=str(path))
    return data


def validate_rubric(data: Any, source: str = "rubric") -> None:
    if not isinstance(data, dict):
        raise RubricError(f"{source}: rubric must be a mapping")
    if not data.get("case_id"):
        raise RubricError(f"{source}: missing case_id")
    points = data.get("points")
    if not isinstance(points, list) or not points:
        raise RubricError(f"{source}: missing non-empty points")

    seen: set[str] = set()
    total_weight = 0.0
    for idx, point in enumerate(points, start=1):
        if not isinstance(point, dict):
            raise RubricError(f"{source}: point {idx} must be a mapping")
        point_id = point.get("id")
        if not isinstance(point_id, str) or not point_id:
            raise RubricError(f"{source}: point {idx} missing id")
        if point_id in seen:
            raise RubricError(f"{source}: duplicate point id {point_id}")
        seen.add(point_id)

        weight = point.get("weight")
        if not isinstance(weight, (int, float)) or weight <= 0:
            raise RubricError(f"{source}: point {point_id} has non-positive weight")
        total_weight += float(weight)

        judge = point.get("judge")
        if judge not in VALID_JUDGES:
            raise RubricError(f"{source}: point {point_id} invalid judge {judge!r}")

        dimension = point.get("dimension")
        if dimension not in VALID_DIMENSIONS:
            raise RubricError(f"{source}: point {point_id} invalid dimension {dimension!r}")

        layers = point.get("failure_layers")
        if not isinstance(layers, list) or not layers:
            raise RubricError(f"{source}: point {point_id} must define failure_layers")
        invalid_layers = [layer for layer in layers if layer not in VALID_FAILURE_LAYERS]
        if invalid_layers:
            raise RubricError(f"{source}: point {point_id} invalid failure_layers {invalid_layers!r}")

        if judge in {"rule", "validator", "hybrid"}:
            checks = point.get("checks")
            if not isinstance(checks, list) or not checks:
                raise RubricError(f"{source}: point {point_id} needs non-empty checks")
            for check_idx, check in enumerate(checks, start=1):
                if not isinstance(check, dict) or not check.get("type"):
                    raise RubricError(f"{source}: point {point_id} check {check_idx} missing type")
        if judge == "llm":
            llm_judge = point.get("llm_judge")
            if not isinstance(llm_judge, dict) or not isinstance(llm_judge.get("config"), str):
                raise RubricError(f"{source}: point {point_id} needs llm_judge.config")

    scoring = data.get("scoring", {})
    if scoring:
        if not isinstance(scoring, dict):
            raise RubricError(f"{source}: scoring must be a mapping")
        max_score = scoring.get("max_score")
        if max_score is not None:
            if not isinstance(max_score, (int, float)):
                raise RubricError(f"{source}: scoring.max_score must be numeric")
            if abs(float(max_score) - total_weight) > 1e-9:
                raise RubricError(f"{source}: scoring.max_score must equal point weights")
        hard_pass_requires = scoring.get("hard_pass_requires", [])
        if not isinstance(hard_pass_requires, list):
            raise RubricError(f"{source}: scoring.hard_pass_requires must be a list")
        unknown = [point_id for point_id in hard_pass_requires if point_id not in seen]
        if unknown:
            raise RubricError(f"{source}: scoring.hard_pass_requires references unknown points {unknown!r}")
