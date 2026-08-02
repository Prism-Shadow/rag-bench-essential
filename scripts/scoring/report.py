from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .rubric import load_rubric
from .rule_checks import ScoreContext, run_check
from .vision_judge import run_codex_visual_judge, run_vision_judge


def load_expected(truth_dir: Path) -> dict[str, Any]:
    return json.loads((truth_dir / "expected.json").read_text(encoding="utf-8"))


def run_validator(workspace: Path, truth_dir: Path) -> dict[str, Any]:
    validator = truth_dir / "validate.py"
    if not validator.exists():
        return {"exit_code": None, "stdout": "", "stderr": f"missing validator: {validator}"}
    env = os.environ.copy()
    env["BENCH_TRUTH_DIR"] = str(truth_dir.resolve())
    proc = subprocess.run(
        ["python3", str(validator.resolve())],
        cwd=workspace,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=300,
        check=False,
    )
    return {"exit_code": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}


def score_workspace(
    case_id: str,
    workspace: Path,
    truth_dir: Path,
    rubric_path: Path | None = None,
    run_issue: str | None = None,
    runtime: str | None = None,
    batch_id: str | None = None,
    run_llm_judges: bool = True,
    validator_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rubric_path = rubric_path or truth_dir / "rubric.yaml"
    rubric = load_rubric(rubric_path)
    expected = load_expected(truth_dir)
    validator = validator_result if validator_result is not None else run_validator(workspace, truth_dir)
    ctx = ScoreContext(
        workspace=workspace,
        truth_dir=truth_dir,
        expected=expected,
        validator_exit=validator["exit_code"],
    )

    point_results = []
    total_weight = 0.0
    earned_weight = 0.0
    rule_total = 0.0
    rule_earned = 0.0
    llm_total = 0.0
    llm_earned = 0.0
    hard_failures = []
    failure_layers: set[str] = set()

    for point in rubric["points"]:
        weight = float(point["weight"])
        total_weight += weight
        judge = point["judge"]
        status = "failed"
        checks = []
        passed = False

        if judge == "llm":
            llm_total += weight
            if validator["exit_code"] != 0:
                status = "not_run"
                message = "LLM judge skipped because deterministic validator did not pass"
            else:
                config_path = truth_dir / point["llm_judge"]["config"]
                codex_result = run_codex_visual_judge(workspace, config_path)
                codex_completed = (
                    isinstance(codex_result.details, dict)
                    and codex_result.details.get("status") == "completed"
                )
                if codex_completed:
                    result = codex_result
                elif run_llm_judges:
                    result = run_vision_judge(workspace, config_path)
                else:
                    result = codex_result
                checks = [
                    {
                        "passed": result.passed,
                        "message": result.message,
                        "details": result.details or {},
                    }
                ]
                pending_codex = (
                    isinstance(result.details, dict)
                    and result.details.get("judge_runtime") == "codex"
                    and result.details.get("status") == "pending"
                )
                passed = result.passed
                status = "not_run" if pending_codex else "passed" if passed else "failed"
                message = result.message
        elif judge == "trace":
            status = "not_run"
            message = f"{judge} judge not run"
        else:
            check_results = [run_check(check, ctx) for check in point.get("checks", [])]
            checks = [
                {
                    "passed": result.passed,
                    "message": result.message,
                    "details": result.details or {},
                }
                for result in check_results
            ]
            passed = all(result.passed for result in check_results)
            status = "passed" if passed else "failed"
            message = "all checks passed" if passed else "one or more checks failed"

        score = weight if status == "passed" else 0.0
        if judge in {"rule", "validator", "hybrid"}:
            rule_total += weight
            rule_earned += score
        if judge == "llm":
            llm_earned += score
        earned_weight += score

        if status != "passed":
            failure_layers.update(point["failure_layers"])
            if point.get("hard_gate"):
                hard_failures.append(point["id"])

        point_results.append(
            {
                "id": point["id"],
                "goal": point.get("goal", ""),
                "dimension": point["dimension"],
                "judge": judge,
                "hard_gate": bool(point.get("hard_gate")),
                "weight": weight,
                "score": score,
                "status": status,
                "message": message,
                "failure_layers": point["failure_layers"],
                "checks": checks,
            }
        )

    run_issue_value = run_issue or "unknown"
    run_issue_clean = run_issue_value == "ok"
    hard_pass = not hard_failures and validator["exit_code"] == 0 and run_issue_clean
    normalized_score = earned_weight / total_weight if total_weight else 0.0
    rule_score = rule_earned / rule_total if rule_total else None
    llm_score = llm_earned / llm_total if llm_total else None
    llm_details = [
        check["details"]
        for point in point_results
        if point["judge"] == "llm"
        for check in point["checks"]
        if isinstance(check.get("details"), dict)
    ]
    token_fields = ("input_tokens", "output_tokens", "total_tokens", "cached_input_tokens", "reasoning_tokens")
    token_usage = {
        field: sum(
            int(details.get("token_usage", {}).get(field) or 0)
            for details in llm_details
            if isinstance(details.get("token_usage"), dict)
        )
        for field in token_fields
    }
    llm_judge_metrics = {
        "configured_points": sum(1 for point in point_results if point["judge"] == "llm"),
        "completed_calls": sum(1 for details in llm_details if details.get("model")),
        "duration_seconds": round(sum(float(details.get("duration_seconds") or 0) for details in llm_details), 6),
        "token_usage": token_usage,
    }

    return {
        "schema_version": 1,
        "case_id": case_id,
        "runtime": runtime,
        "batch_id": batch_id,
        "workspace": str(workspace),
        "truth_dir": str(truth_dir),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "run_issue": run_issue_value,
        "run_issue_clean": run_issue_clean,
        "validator": validator,
        "hard_pass": hard_pass,
        "normalized_score": round(normalized_score, 6),
        "rule_score": round(rule_score, 6) if rule_score is not None else None,
        "llm_score": round(llm_score, 6) if llm_score is not None else None,
        "llm_judge_metrics": llm_judge_metrics,
        "earned_weight": earned_weight,
        "total_weight": total_weight,
        "hard_failures": hard_failures,
        "failure_layers": sorted(failure_layers),
        "points": point_results,
    }
