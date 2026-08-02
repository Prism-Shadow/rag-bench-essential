from __future__ import annotations

import base64
import hashlib
import json
import mimetypes
import os
import shutil
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import yaml

from .rule_checks import CheckResult


class VisionJudgeError(RuntimeError):
    pass


def _read_config(path: Path) -> dict[str, Any]:
    try:
        config = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise VisionJudgeError(f"vision judge config unreadable: {path}: {exc}") from exc
    if not isinstance(config, dict):
        raise VisionJudgeError(f"vision judge config must be a mapping: {path}")
    required = ("judge_id", "prompt_version", "prompt_file", "input", "required_boolean_gates")
    missing = [key for key in required if not config.get(key)]
    if missing:
        raise VisionJudgeError(f"vision judge config missing fields {missing}: {path}")
    gates = config["required_boolean_gates"]
    if not isinstance(gates, list) or not gates or any(not isinstance(gate, str) for gate in gates):
        raise VisionJudgeError(f"required_boolean_gates must be a non-empty string list: {path}")
    return config


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _codex_request(workspace: Path, config_path: Path) -> tuple[dict[str, Any], Path, Path]:
    config = _read_config(config_path)
    prompt_path = config_path.parent / str(config["prompt_file"])
    input_spec = config["input"]
    if not isinstance(input_spec, dict):
        raise VisionJudgeError("vision judge input must be a mapping")
    artifact_path = workspace / str(input_spec.get("path", ""))
    artifact = {
        "path": str(artifact_path),
        "sha256": _sha256(artifact_path) if artifact_path.is_file() else None,
        "exists": artifact_path.is_file(),
        "input_spec": input_spec,
    }
    request = {
        "schema_version": 1,
        "judge_type": "codex_visual",
        "judge_id": config["judge_id"],
        "prompt_version": config["prompt_version"],
        "prompt": prompt_path.read_text(encoding="utf-8"),
        "prompt_sha256": _sha256(prompt_path),
        "required_boolean_gates": list(config["required_boolean_gates"]),
        "artifact": artifact,
    }
    judges_dir = workspace.parent / "judges"
    judges_dir.mkdir(parents=True, exist_ok=True)
    request_path = judges_dir / f"{config['judge_id']}.request.json"
    verdict_path = judges_dir / f"{config['judge_id']}.verdict.json"
    canonical = json.dumps(request, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    request["request_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    request_path.write_text(
        json.dumps(request, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return request, request_path, verdict_path


def run_codex_visual_judge(workspace: Path, config_path: Path) -> CheckResult:
    """Use a Codex-authored, artifact-bound verdict when present; otherwise queue review."""
    started = time.monotonic()
    try:
        request, request_path, verdict_path = _codex_request(workspace, config_path)
        pending_details = {
            "judge_id": request["judge_id"],
            "prompt_version": request["prompt_version"],
            "prompt_sha256": request["prompt_sha256"],
            "request_sha256": request["request_sha256"],
            "request_path": str(request_path),
            "verdict_path": str(verdict_path),
            "judge_runtime": "codex",
            "status": "pending",
            "duration_seconds": round(time.monotonic() - started, 6),
        }
        if not verdict_path.is_file():
            return CheckResult(False, "pending Codex visual review", pending_details)
        try:
            verdict = json.loads(verdict_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            return CheckResult(False, f"invalid Codex verdict: {exc}", pending_details)
        if not isinstance(verdict, dict):
            return CheckResult(False, "invalid Codex verdict: expected object", pending_details)
        identity_errors = []
        for field in ("judge_id", "prompt_version", "request_sha256"):
            if verdict.get(field) != request.get(field):
                identity_errors.append(field)
        gates = verdict.get("gates")
        required_gates = list(request["required_boolean_gates"])
        if not isinstance(gates, dict):
            identity_errors.append("gates")
            gates = {}
        invalid_gates = [gate for gate in required_gates if not isinstance(gates.get(gate), bool)]
        if invalid_gates:
            identity_errors.append("gate_values:" + ",".join(invalid_gates))
        if identity_errors:
            return CheckResult(
                False,
                "Codex verdict does not match current request: " + ", ".join(identity_errors),
                pending_details,
            )
        failed = [gate for gate in required_gates if gates[gate] is not True]
        details = {
            **pending_details,
            "status": "completed",
            "model": str(verdict.get("model", "codex")),
            "gates": {gate: gates[gate] for gate in required_gates},
            "failed_gates": failed,
            "blocking_defects": verdict.get("blocking_defects", []),
            "notes": verdict.get("notes", ""),
            "judged_at": verdict.get("judged_at"),
            "duration_seconds": round(time.monotonic() - started, 6),
        }
        return CheckResult(
            not failed,
            "Codex visual judge gates pass" if not failed else "Codex visual judge gates failed",
            details,
        )
    except Exception as exc:
        return CheckResult(
            False,
            f"Codex visual judge request failed: {exc}",
            {"judge_runtime": "codex", "status": "pending"},
        )


def _data_url(path: Path) -> str:
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise VisionJudgeError(f"judge image unreadable: {path}: {exc}") from exc
    if not data:
        raise VisionJudgeError(f"judge image is empty: {path}")
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    return f"data:{mime};base64,{base64.b64encode(data).decode('ascii')}"


def _render_pdf_pages(workspace: Path, input_spec: dict[str, Any], temp_dir: Path) -> list[Path]:
    renderer = str(input_spec.get("renderer", "pdftoppm"))
    executable = shutil.which(renderer)
    if executable is None:
        raise VisionJudgeError(f"required PDF renderer not found on PATH: {renderer}")
    pdf_path = workspace / str(input_spec.get("path", ""))
    if not pdf_path.exists():
        raise VisionJudgeError(f"judge PDF missing: {pdf_path}")
    pages = input_spec.get("pages", [])
    if not isinstance(pages, list) or not pages or any(not isinstance(page, int) or page < 1 for page in pages):
        raise VisionJudgeError("pdf_pages input requires positive integer pages")
    dpi = int(input_spec.get("dpi", 150))
    prefix = temp_dir / "page"
    proc = subprocess.run(
        [
            executable,
            "-png",
            "-r",
            str(dpi),
            "-f",
            str(min(pages)),
            "-l",
            str(max(pages)),
            str(pdf_path),
            str(prefix),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=120,
        check=False,
    )
    if proc.returncode != 0:
        raise VisionJudgeError(f"PDF rendering failed ({proc.returncode}): {proc.stderr.strip()[:1000]}")
    rendered = sorted(temp_dir.glob("page-*.png"))
    by_page: dict[int, Path] = {}
    for path in rendered:
        suffix = path.stem.rsplit("-", 1)[-1]
        try:
            by_page[int(suffix)] = path
        except ValueError:
            continue
    missing = [page for page in pages if page not in by_page]
    if missing:
        raise VisionJudgeError(f"PDF renderer did not produce requested pages: {missing}")
    return [by_page[page] for page in pages]


def _prepare_images(workspace: Path, config: dict[str, Any], temp_dir: Path) -> list[Path]:
    input_spec = config["input"]
    if not isinstance(input_spec, dict):
        raise VisionJudgeError("vision judge input must be a mapping")
    input_type = input_spec.get("type")
    if input_type == "image":
        path = workspace / str(input_spec.get("path", ""))
        if not path.exists():
            raise VisionJudgeError(f"judge image missing: {path}")
        return [path]
    if input_type == "pdf_pages":
        return _render_pdf_pages(workspace, input_spec, temp_dir)
    raise VisionJudgeError(f"unsupported vision judge input type: {input_type!r}")


def _extract_json(content: Any) -> dict[str, Any]:
    if isinstance(content, list):
        text_parts = [str(item.get("text", "")) for item in content if isinstance(item, dict)]
        content = "\n".join(text_parts)
    if not isinstance(content, str):
        raise VisionJudgeError("judge response content is not text")
    text = content.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise VisionJudgeError(f"judge returned invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise VisionJudgeError("judge response JSON must be an object")
    return value


def _usage(response: dict[str, Any]) -> dict[str, Any]:
    usage = response.get("usage") if isinstance(response.get("usage"), dict) else {}
    prompt_details = usage.get("prompt_tokens_details") if isinstance(usage.get("prompt_tokens_details"), dict) else {}
    completion_details = usage.get("completion_tokens_details") if isinstance(usage.get("completion_tokens_details"), dict) else {}
    return {
        "input_tokens": usage.get("prompt_tokens"),
        "output_tokens": usage.get("completion_tokens"),
        "total_tokens": usage.get("total_tokens"),
        "cached_input_tokens": prompt_details.get("cached_tokens"),
        "reasoning_tokens": completion_details.get("reasoning_tokens"),
    }


def _call_openai_compatible(
    *,
    base_url: str,
    api_key: str,
    model: str,
    prompt: str,
    images: list[Path],
    temperature: float,
    max_output_tokens: int,
    timeout_seconds: int,
) -> dict[str, Any]:
    content: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
    content.extend(
        {"type": "image_url", "image_url": {"url": _data_url(path), "detail": "high"}}
        for path in images
    )
    body = {
        "model": model,
        "messages": [{"role": "user", "content": content}],
        "temperature": temperature,
        "max_tokens": max_output_tokens,
        "response_format": {"type": "json_object"},
    }
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:1000]
        raise VisionJudgeError(f"judge API HTTP {exc.code}: {detail}") from exc
    except Exception as exc:
        raise VisionJudgeError(f"judge API request failed: {exc}") from exc
    if not isinstance(payload, dict):
        raise VisionJudgeError("judge API response must be an object")
    return payload


def run_vision_judge(workspace: Path, config_path: Path) -> CheckResult:
    started = time.monotonic()
    try:
        config = _read_config(config_path)
        prompt_path = config_path.parent / str(config["prompt_file"])
        prompt = prompt_path.read_text(encoding="utf-8")
        model_env = str(config.get("model_env", "BENCH_VISION_JUDGE_MODEL"))
        api_key_env = str(config.get("api_key_env", "BENCH_VISION_JUDGE_API_KEY"))
        base_url_env = str(config.get("base_url_env", "BENCH_VISION_JUDGE_BASE_URL"))
        model = os.environ.get(model_env, "").strip()
        api_key = os.environ.get(api_key_env, "").strip()
        base_url = os.environ.get(base_url_env, str(config.get("base_url_default", ""))).strip()
        missing = [name for name, value in ((model_env, model), (api_key_env, api_key), (base_url_env, base_url)) if not value]
        if missing:
            raise VisionJudgeError(f"vision judge is not configured; missing environment values: {missing}")

        prompt_sha256 = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        config_sha256 = hashlib.sha256(config_path.read_bytes()).hexdigest()
        attempts = int(config.get("max_attempts", 2))
        last_error: Exception | None = None
        with tempfile.TemporaryDirectory(prefix="bench-vision-judge-") as temp_name:
            images = _prepare_images(workspace, config, Path(temp_name))
            for attempt in range(1, attempts + 1):
                try:
                    response = _call_openai_compatible(
                        base_url=base_url,
                        api_key=api_key,
                        model=model,
                        prompt=prompt,
                        images=images,
                        temperature=float(config.get("temperature", 0)),
                        max_output_tokens=int(config.get("max_output_tokens", 600)),
                        timeout_seconds=int(config.get("timeout_seconds", 180)),
                    )
                    choices = response.get("choices")
                    if not isinstance(choices, list) or not choices:
                        raise VisionJudgeError("judge API response has no choices")
                    message = choices[0].get("message", {}) if isinstance(choices[0], dict) else {}
                    verdict = _extract_json(message.get("content"))
                    gates = list(config["required_boolean_gates"])
                    invalid = [gate for gate in gates if not isinstance(verdict.get(gate), bool)]
                    if invalid:
                        raise VisionJudgeError(f"judge response missing boolean gates: {invalid}")
                    failed = [gate for gate in gates if verdict[gate] is not True]
                    details = {
                        "judge_id": config["judge_id"],
                        "prompt_version": config["prompt_version"],
                        "prompt_sha256": prompt_sha256,
                        "config_sha256": config_sha256,
                        "model": response.get("model") or model,
                        "attempt": attempt,
                        "input_artifacts": [str(path.relative_to(workspace)) if path.is_relative_to(workspace) else path.name for path in images],
                        "gates": {gate: verdict[gate] for gate in gates},
                        "failed_gates": failed,
                        "blocking_defects": verdict.get("blocking_defects", []),
                        "token_usage": _usage(response),
                        "duration_seconds": round(time.monotonic() - started, 6),
                    }
                    return CheckResult(
                        not failed,
                        "vision judge gates pass" if not failed else "vision judge gates failed",
                        details,
                    )
                except Exception as exc:  # retry malformed or transient judge responses
                    last_error = exc
        raise VisionJudgeError(f"vision judge failed after {attempts} attempts: {last_error}")
    except Exception as exc:
        return CheckResult(
            False,
            str(exc),
            {"judge_config": str(config_path), "duration_seconds": round(time.monotonic() - started, 6)},
        )
