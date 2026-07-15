#!/usr/bin/env python3
"""Extract timing/token metrics from the selected 4x15 traces and plot them."""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import OrderedDict
from datetime import datetime
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt


AGENTS = OrderedDict(
    [
        ("Original PG Agent", ("original-pg-agent", "pg")),
        ("RAG Agent", ("rag-agent", "pg")),
        ("Claude Code", ("claude-code", "claude")),
        ("Codex", ("codex", "codex")),
    ]
)

CASES = OrderedDict(
    [
        ("spider2lite_f1_overtake_audit_hard", "Spider2-Lite"),
        ("dci_browsecomp_architecture_firm_hard", "DCI / BrowseComp+"),
        ("docfinqa_oilgas_canada_pdf_hard", "DocFinQA"),
        ("docvqa_contract_effective_date_ocr_hard", "DocVQA"),
        ("longda_nscg_telework_hard", "LongDA"),
        ("multihiertt_global_products_atoi_share_hard", "MultiHiertt"),
        ("workspacebench_taobao_permissions_hard", "WorkspaceBench"),
        ("dvworld_dvevol_crime_association_network_hard", "DVWorld"),
        ("bankertoolbench_cake_lbo_sensitivity_hard", "BankerToolBench"),
        ("finlongdocqa_interest_expense_sensitivity_screen_hard", "FinLongDocQA"),
        ("dabstep_real_fees_1681", "DABstep"),
        ("prepbench_loyalty_tier_normalization_hard", "PrepBench"),
        ("spreadsheetbench_working_paper_transpose_hard", "SpreadsheetBench"),
        ("harveylab_reps_diligence_discrepancy_hard", "HarveyLab"),
        ("medagentbench_potassium_repletion_order_hard", "MedAgentBench"),
    ]
)

PASS_CASES = {
    "Original PG Agent": {
        "docfinqa_oilgas_canada_pdf_hard",
        "longda_nscg_telework_hard",
        "multihiertt_global_products_atoi_share_hard",
        "bankertoolbench_cake_lbo_sensitivity_hard",
        "dabstep_real_fees_1681",
    },
    "RAG Agent": {
        "spider2lite_f1_overtake_audit_hard",
        "docfinqa_oilgas_canada_pdf_hard",
        "longda_nscg_telework_hard",
        "multihiertt_global_products_atoi_share_hard",
        "bankertoolbench_cake_lbo_sensitivity_hard",
        "dabstep_real_fees_1681",
        "prepbench_loyalty_tier_normalization_hard",
        "spreadsheetbench_working_paper_transpose_hard",
        "harveylab_reps_diligence_discrepancy_hard",
        "medagentbench_potassium_repletion_order_hard",
    },
    "Claude Code": {
        "spider2lite_f1_overtake_audit_hard",
        "docfinqa_oilgas_canada_pdf_hard",
        "longda_nscg_telework_hard",
        "multihiertt_global_products_atoi_share_hard",
        "bankertoolbench_cake_lbo_sensitivity_hard",
        "dabstep_real_fees_1681",
        "prepbench_loyalty_tier_normalization_hard",
        "spreadsheetbench_working_paper_transpose_hard",
        "harveylab_reps_diligence_discrepancy_hard",
        "medagentbench_potassium_repletion_order_hard",
    },
    "Codex": {
        "spider2lite_f1_overtake_audit_hard",
        "docfinqa_oilgas_canada_pdf_hard",
        "longda_nscg_telework_hard",
        "multihiertt_global_products_atoi_share_hard",
        "dabstep_real_fees_1681",
        "prepbench_loyalty_tier_normalization_hard",
        "spreadsheetbench_working_paper_transpose_hard",
    },
}

# These are execution failures that do not measure a normal agent attempt.
OUTLIERS = {
    (
        "Original PG Agent",
        "dci_browsecomp_architecture_firm_hard",
    ): "terminated after a stalled command; elapsed time was 7h50m",
    (
        "Claude Code",
        "docvqa_contract_effective_date_ocr_hard",
    ): "401 runtime error with zero model tokens",
}

TRACE_STATUS = {
    ("Original PG Agent", "dci_browsecomp_architecture_firm_hard"): "terminated",
    (
        "Original PG Agent",
        "harveylab_reps_diligence_discrepancy_hard",
    ): "protocol_error_after_agent_run",
    ("Claude Code", "docvqa_contract_effective_date_ocr_hard"): "runtime_error",
}

PASS_COLOR = "#2F6BFF"
TOKEN_COLOR = "#D97706"
TEXT_COLOR = "#172033"
MUTED_COLOR = "#667085"
GRID_COLOR = "#D0D5DD"


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=repo_root)
    parser.add_argument("--dpi", type=int, default=300)
    return parser.parse_args()


def parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def load_trace(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise ValueError(f"{path}:{line_number}: {error}") from error
    if not rows:
        raise ValueError(f"Empty trace: {path}")
    return rows


def duration_metrics(rows: list[dict[str, Any]]) -> tuple[str, str, float]:
    timestamps = []
    for row in rows:
        value = row.get("timestamp")
        if value:
            timestamps.append(parse_timestamp(value))
    if len(timestamps) < 2:
        raise ValueError("Trace has fewer than two timestamped events")
    start = min(timestamps)
    end = max(timestamps)
    return start.isoformat(), end.isoformat(), (end - start).total_seconds()


def pg_tokens(rows: list[dict[str, Any]]) -> tuple[int, int, int, int]:
    usages = [
        row["payload"]["session"]
        for row in rows
        if row.get("type") == "event_msg"
        and row.get("payload", {}).get("type") == "token_usage"
        and "session" in row.get("payload", {})
    ]
    if not usages:
        return 0, 0, 0, 0
    usage = usages[-1]
    uncached = int(usage.get("cache_write", 0))
    cached = int(usage.get("cache_read", 0))
    output = int(usage.get("output", 0))
    total = int(usage.get("total", uncached + cached + output))
    return uncached, cached, output, total


def claude_tokens(rows: list[dict[str, Any]]) -> tuple[int, int, int, int]:
    # A streamed assistant response can repeat the same API message id. Keep one
    # usage record per id to avoid double-counting the same model invocation.
    messages: dict[str, dict[str, Any]] = {}
    for row in rows:
        message = row.get("message")
        if row.get("type") != "assistant" or not isinstance(message, dict):
            continue
        message_id = message.get("id")
        usage = message.get("usage")
        if message_id and isinstance(usage, dict):
            messages[message_id] = usage

    uncached = sum(
        int(usage.get("input_tokens", 0))
        + int(usage.get("cache_creation_input_tokens", 0))
        for usage in messages.values()
    )
    cached = sum(
        int(usage.get("cache_read_input_tokens", 0)) for usage in messages.values()
    )
    output = sum(int(usage.get("output_tokens", 0)) for usage in messages.values())
    return uncached, cached, output, uncached + cached + output


def codex_tokens(rows: list[dict[str, Any]]) -> tuple[int, int, int, int]:
    usages = [
        row["payload"]["info"]["total_token_usage"]
        for row in rows
        if row.get("type") == "event_msg"
        and row.get("payload", {}).get("type") == "token_count"
        and row.get("payload", {}).get("info", {}).get("total_token_usage")
    ]
    if not usages:
        return 0, 0, 0, 0
    usage = usages[-1]
    input_tokens = int(usage.get("input_tokens", 0))
    cached = int(usage.get("cached_input_tokens", 0))
    uncached = max(input_tokens - cached, 0)
    output = int(usage.get("output_tokens", 0))
    total = int(usage.get("total_tokens", input_tokens + output))
    return uncached, cached, output, total


TOKEN_PARSERS = {"pg": pg_tokens, "claude": claude_tokens, "codex": codex_tokens}


def collect_trace_metrics(repo_root: Path) -> list[dict[str, Any]]:
    metrics = []
    expected_files = {f"{case}.jsonl" for case in CASES}
    for agent, (trace_dir, parser_name) in AGENTS.items():
        directory = repo_root / "traces" / trace_dir
        actual_files = {path.name for path in directory.glob("*.jsonl")}
        if actual_files != expected_files:
            missing = sorted(expected_files - actual_files)
            extra = sorted(actual_files - expected_files)
            raise ValueError(f"{agent}: missing={missing}, extra={extra}")

        for case, display_name in CASES.items():
            path = directory / f"{case}.jsonl"
            rows = load_trace(path)
            start, end, duration_seconds = duration_metrics(rows)
            uncached, cached, output, processed = TOKEN_PARSERS[parser_name](rows)
            key = (agent, case)
            exclusion_reason = OUTLIERS.get(key, "")
            metrics.append(
                {
                    "case": case,
                    "display_name": display_name,
                    "agent": agent,
                    "result": "PASS" if case in PASS_CASES[agent] else "FAIL",
                    "trace_path": path.relative_to(repo_root).as_posix(),
                    "trace_status": TRACE_STATUS.get(key, "completed"),
                    "start_time": start,
                    "end_time": end,
                    "duration_seconds": round(duration_seconds, 3),
                    "duration_minutes": round(duration_seconds / 60, 3),
                    "uncached_input_tokens": uncached,
                    "cache_read_tokens": cached,
                    "output_tokens": output,
                    "processed_tokens": processed,
                    "excluded_from_robust": bool(exclusion_reason),
                    "exclusion_reason": exclusion_reason,
                }
            )
    return metrics


def summarize_cases(metrics: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summary = []
    for case, display_name in CASES.items():
        rows = [row for row in metrics if row["case"] == case]
        valid = [row for row in rows if not row["excluded_from_robust"]]
        durations = [float(row["duration_seconds"]) for row in valid]
        outputs = [int(row["output_tokens"]) for row in valid]
        summary.append(
            {
                "case": case,
                "display_name": display_name,
                "trace_count": len(rows),
                "excluded_trace_count": len(rows) - len(valid),
                "valid_trace_count": len(valid),
                "mean_duration_seconds": round(statistics.mean(durations), 3),
                "mean_duration_minutes": round(statistics.mean(durations) / 60, 3),
                "median_duration_seconds": round(statistics.median(durations), 3),
                "median_duration_minutes": round(statistics.median(durations) / 60, 3),
                "min_duration_seconds": round(min(durations), 3),
                "max_duration_seconds": round(max(durations), 3),
                "mean_output_tokens": round(statistics.mean(outputs), 1),
                "median_output_tokens": round(statistics.median(outputs), 1),
                "min_output_tokens": min(outputs),
                "max_output_tokens": max(outputs),
            }
        )
    return summary


def summarize_settings(metrics: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summary = []
    for agent in AGENTS:
        rows = [row for row in metrics if row["agent"] == agent]
        valid = [row for row in rows if not row["excluded_from_robust"]]
        summary.append(
            {
                "agent": agent,
                "trace_count": len(rows),
                "pass_count": sum(row["result"] == "PASS" for row in rows),
                "excluded_trace_count": len(rows) - len(valid),
                "valid_trace_count": len(valid),
                "raw_total_duration_seconds": round(
                    sum(float(row["duration_seconds"]) for row in rows), 3
                ),
                "clean_total_duration_seconds": round(
                    sum(float(row["duration_seconds"]) for row in valid), 3
                ),
                "mean_duration_seconds": round(
                    statistics.mean(float(row["duration_seconds"]) for row in valid),
                    3,
                ),
                "median_duration_seconds": round(
                    statistics.median(float(row["duration_seconds"]) for row in valid),
                    3,
                ),
                "reported_processed_tokens": sum(
                    int(row["processed_tokens"]) for row in rows
                ),
                "clean_output_tokens": sum(int(row["output_tokens"]) for row in valid),
                "mean_output_tokens": round(
                    statistics.mean(int(row["output_tokens"]) for row in valid), 1
                ),
                "median_output_tokens": round(
                    statistics.median(int(row["output_tokens"]) for row in valid), 1
                ),
            }
        )
    return summary


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def style_axis(axis: plt.Axes) -> None:
    axis.grid(axis="x", color=GRID_COLOR, linewidth=0.7, alpha=0.65)
    axis.set_axisbelow(True)
    axis.tick_params(axis="both", length=0)
    for spine in axis.spines.values():
        spine.set_visible(False)


def annotate_bars(axis: plt.Axes, bars: Any, formatter: Any) -> None:
    maximum = max(bar.get_width() for bar in bars)
    offset = maximum * 0.025
    for bar in bars:
        axis.text(
            bar.get_width() + offset,
            bar.get_y() + bar.get_height() / 2,
            formatter(bar.get_width()),
            va="center",
            ha="left",
            fontsize=8.5,
            color=TEXT_COLOR,
        )
    axis.set_xlim(0, maximum * 1.22)


def draw_figure(
    case_summary: list[dict[str, Any]], setting_summary: list[dict[str, Any]]
) -> plt.Figure:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9.5,
            "axes.titlesize": 11,
            "axes.labelcolor": TEXT_COLOR,
            "text.color": TEXT_COLOR,
            "xtick.color": MUTED_COLOR,
            "ytick.color": TEXT_COLOR,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )

    figure = plt.figure(figsize=(14.2, 10.8), facecolor="white")
    grid = figure.add_gridspec(
        2, 2, height_ratios=(1.45, 4.6), hspace=0.34, wspace=0.38
    )
    setting_time = figure.add_subplot(grid[0, 0])
    setting_tokens = figure.add_subplot(grid[0, 1])
    case_time = figure.add_subplot(grid[1, 0])
    case_tokens = figure.add_subplot(grid[1, 1], sharey=case_time)

    figure.suptitle(
        "Time and Output Tokens Across the Selected 4×15 Traces",
        x=0.12,
        y=0.985,
        ha="left",
        fontsize=15,
        fontweight="bold",
        color=TEXT_COLOR,
    )

    agent_labels = [row["agent"] for row in setting_summary]
    agent_y = list(range(len(agent_labels)))
    time_values = [row["mean_duration_seconds"] / 60 for row in setting_summary]
    token_values = [row["mean_output_tokens"] / 1000 for row in setting_summary]

    bars = setting_time.barh(agent_y, time_values, color=PASS_COLOR, height=0.54)
    setting_time.set_yticks(agent_y, agent_labels)
    setting_time.invert_yaxis()
    setting_time.set_xlabel("Mean minutes per trace")
    setting_time.set_title("a  Setting-level elapsed time", loc="left", fontweight="bold")
    style_axis(setting_time)
    annotate_bars(setting_time, bars, lambda value: f"{value:.1f}m")

    bars = setting_tokens.barh(agent_y, token_values, color=TOKEN_COLOR, height=0.54)
    setting_tokens.set_yticks(agent_y, agent_labels)
    setting_tokens.invert_yaxis()
    setting_tokens.set_xlabel("Mean output tokens (thousands)")
    setting_tokens.set_title("b  Setting-level output", loc="left", fontweight="bold")
    style_axis(setting_tokens)
    annotate_bars(setting_tokens, bars, lambda value: f"{value:.1f}K")

    ordered_cases = sorted(
        case_summary, key=lambda row: row["mean_duration_seconds"], reverse=True
    )
    case_labels = [row["display_name"] for row in ordered_cases]
    case_y = list(range(len(case_labels)))
    time_values = [row["mean_duration_seconds"] / 60 for row in ordered_cases]
    token_values = [row["mean_output_tokens"] / 1000 for row in ordered_cases]

    bars = case_time.barh(case_y, time_values, color=PASS_COLOR, height=0.62)
    case_time.set_yticks(case_y, case_labels)
    case_time.invert_yaxis()
    case_time.set_xlabel("Mean minutes")
    case_time.set_title("c  Case-level elapsed time", loc="left", fontweight="bold")
    style_axis(case_time)
    annotate_bars(case_time, bars, lambda value: f"{value:.1f}")

    bars = case_tokens.barh(case_y, token_values, color=TOKEN_COLOR, height=0.62)
    case_tokens.tick_params(axis="y", labelleft=False)
    case_tokens.set_xlabel("Mean output tokens (thousands)")
    case_tokens.set_title("d  Case-level output", loc="left", fontweight="bold")
    style_axis(case_tokens)
    annotate_bars(case_tokens, bars, lambda value: f"{value:.1f}K")

    figure.text(
        0.12,
        0.017,
        "Means exclude two execution outliers: Original PG Agent on DCI (stalled/terminated) and Claude Code on DocVQA (401, zero model tokens).",
        ha="left",
        va="bottom",
        fontsize=8.5,
        color=MUTED_COLOR,
    )
    figure.text(
        0.12,
        0.002,
        "Elapsed time is the first-to-last timestamp span in each trace. Output tokens are used for cross-runtime comparison.",
        ha="left",
        va="bottom",
        fontsize=8.5,
        color=MUTED_COLOR,
    )
    figure.subplots_adjust(left=0.22, right=0.96, top=0.92, bottom=0.09)
    return figure


def main() -> None:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    metrics = collect_trace_metrics(repo_root)
    case_summary = summarize_cases(metrics)
    setting_summary = summarize_settings(metrics)

    results_dir = repo_root / "results"
    write_csv(results_dir / "trace_metrics.csv", metrics)
    write_csv(results_dir / "case_summary.csv", case_summary)
    write_csv(results_dir / "setting_summary.csv", setting_summary)

    figure = draw_figure(case_summary, setting_summary)
    figure_dir = repo_root / "figures"
    figure.savefig(
        figure_dir / "trace_efficiency.png",
        dpi=args.dpi,
        bbox_inches="tight",
        facecolor="white",
    )
    figure.savefig(
        figure_dir / "trace_efficiency.pdf", bbox_inches="tight", facecolor="white"
    )
    plt.close(figure)

    print(results_dir / "trace_metrics.csv")
    print(results_dir / "case_summary.csv")
    print(results_dir / "setting_summary.csv")
    print(figure_dir / "trace_efficiency.png")
    print(figure_dir / "trace_efficiency.pdf")


if __name__ == "__main__":
    main()
