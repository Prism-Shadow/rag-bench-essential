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

# Latency and token validity are metric-specific. A stalled trace can have an
# unusable wall-clock span while still reporting real model tokens.
LATENCY_EXCLUSIONS = {
    (
        "Original PG Agent",
        "dci_browsecomp_architecture_firm_hard",
    ): "terminated after a stalled command; elapsed time was 7h50m",
    (
        "Claude Code",
        "docvqa_contract_effective_date_ocr_hard",
    ): "401 runtime error with zero model tokens",
}

TOKEN_EXCLUSIONS = {
    (
        "Claude Code",
        "docvqa_contract_effective_date_ocr_hard",
    ): "401 runtime error; no model invocation and zero reported model tokens",
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
UNCACHED_COLOR = "#2F6BFF"
CACHE_COLOR = "#14B8A6"
OUTPUT_COLOR = "#D97706"
TEXT_COLOR = "#172033"
MUTED_COLOR = "#667085"
GRID_COLOR = "#D0D5DD"

# DeepSeek V4 Pro public list prices, checked 2026-07-15.
# https://api-docs.deepseek.com/quick_start/pricing
PRICE_PER_MILLION = {
    "uncached_input_tokens": 0.435,
    "cache_read_tokens": 0.003625,
    "output_tokens": 0.87,
}


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


def pg_activity(rows: list[dict[str, Any]]) -> tuple[int, int]:
    model_calls = sum(
        row.get("type") == "event_msg"
        and row.get("payload", {}).get("type") == "token_usage"
        for row in rows
    )
    tool_calls = sum(
        row.get("type") == "model_msg"
        and row.get("payload", {}).get("type") == "tool_call"
        for row in rows
    )
    return model_calls, tool_calls


def claude_activity(rows: list[dict[str, Any]]) -> tuple[int, int]:
    model_ids = set()
    tool_ids = set()
    for row in rows:
        message = row.get("message")
        if row.get("type") != "assistant" or not isinstance(message, dict):
            continue
        if (
            message.get("id")
            and message.get("model") != "<synthetic>"
            and isinstance(message.get("usage"), dict)
        ):
            model_ids.add(message["id"])
        content = message.get("content", [])
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get("type") == "tool_use":
                    tool_ids.add(item.get("id"))
    tool_ids.discard(None)
    return len(model_ids), len(tool_ids)


def codex_activity(rows: list[dict[str, Any]]) -> tuple[int, int]:
    model_calls = sum(
        row.get("type") == "event_msg"
        and row.get("payload", {}).get("type") == "token_count"
        for row in rows
    )
    tool_ids = {
        row.get("payload", {}).get("call_id")
        for row in rows
        if row.get("type") == "response_item"
        and row.get("payload", {}).get("type")
        in {"function_call", "custom_tool_call"}
    }
    tool_ids.discard(None)
    return model_calls, len(tool_ids)


ACTIVITY_PARSERS = {
    "pg": pg_activity,
    "claude": claude_activity,
    "codex": codex_activity,
}


def estimate_costs(uncached: int, cached: int, output: int) -> dict[str, float]:
    components = {
        "uncached_input_cost_usd": uncached
        * PRICE_PER_MILLION["uncached_input_tokens"]
        / 1_000_000,
        "cache_read_cost_usd": cached
        * PRICE_PER_MILLION["cache_read_tokens"]
        / 1_000_000,
        "output_cost_usd": output
        * PRICE_PER_MILLION["output_tokens"]
        / 1_000_000,
    }
    components["estimated_cost_usd"] = sum(components.values())
    return {key: round(value, 6) for key, value in components.items()}


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
            model_calls, tool_calls = ACTIVITY_PARSERS[parser_name](rows)
            costs = estimate_costs(uncached, cached, output)
            key = (agent, case)
            latency_exclusion_reason = LATENCY_EXCLUSIONS.get(key, "")
            token_exclusion_reason = TOKEN_EXCLUSIONS.get(key, "")
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
                    "model_calls": model_calls,
                    "tool_calls": tool_calls,
                    **costs,
                    "excluded_from_latency": bool(latency_exclusion_reason),
                    "latency_exclusion_reason": latency_exclusion_reason,
                    "excluded_from_token": bool(token_exclusion_reason),
                    "token_exclusion_reason": token_exclusion_reason,
                }
            )
    return metrics


def summarize_settings(metrics: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summary = []
    for agent in AGENTS:
        rows = [row for row in metrics if row["agent"] == agent]
        valid_latency = [row for row in rows if not row["excluded_from_latency"]]
        valid_tokens = [row for row in rows if not row["excluded_from_token"]]
        summary.append(
            {
                "agent": agent,
                "trace_count": len(rows),
                "pass_count": sum(row["result"] == "PASS" for row in rows),
                "latency_excluded_trace_count": len(rows) - len(valid_latency),
                "latency_valid_trace_count": len(valid_latency),
                "token_excluded_trace_count": len(rows) - len(valid_tokens),
                "token_valid_trace_count": len(valid_tokens),
                "raw_total_duration_seconds": round(
                    sum(float(row["duration_seconds"]) for row in rows), 3
                ),
                "clean_total_duration_seconds": round(
                    sum(float(row["duration_seconds"]) for row in valid_latency), 3
                ),
                "mean_duration_seconds": round(
                    statistics.mean(
                        float(row["duration_seconds"]) for row in valid_latency
                    ),
                    3,
                ),
                "median_duration_seconds": round(
                    statistics.median(
                        float(row["duration_seconds"]) for row in valid_latency
                    ),
                    3,
                ),
                "reported_processed_tokens": sum(
                    int(row["processed_tokens"]) for row in rows
                ),
                "clean_uncached_input_tokens": sum(
                    int(row["uncached_input_tokens"]) for row in valid_tokens
                ),
                "clean_cache_read_tokens": sum(
                    int(row["cache_read_tokens"]) for row in valid_tokens
                ),
                "clean_output_tokens": sum(
                    int(row["output_tokens"]) for row in valid_tokens
                ),
                "clean_processed_tokens": sum(
                    int(row["processed_tokens"]) for row in valid_tokens
                ),
                "mean_uncached_input_tokens": round(
                    statistics.mean(
                        int(row["uncached_input_tokens"]) for row in valid_tokens
                    ),
                    1,
                ),
                "mean_cache_read_tokens": round(
                    statistics.mean(
                        int(row["cache_read_tokens"]) for row in valid_tokens
                    ),
                    1,
                ),
                "mean_output_tokens": round(
                    statistics.mean(int(row["output_tokens"]) for row in valid_tokens),
                    1,
                ),
                "mean_processed_tokens": round(
                    statistics.mean(
                        int(row["processed_tokens"]) for row in valid_tokens
                    ),
                    1,
                ),
                "median_output_tokens": round(
                    statistics.median(
                        int(row["output_tokens"]) for row in valid_tokens
                    ),
                    1,
                ),
                "mean_estimated_cost_usd": round(
                    statistics.mean(
                        float(row["estimated_cost_usd"]) for row in valid_tokens
                    ),
                    6,
                ),
                "median_estimated_cost_usd": round(
                    statistics.median(
                        float(row["estimated_cost_usd"]) for row in valid_tokens
                    ),
                    6,
                ),
                "model_calls": sum(int(row["model_calls"]) for row in rows),
                "tool_calls": sum(int(row["tool_calls"]) for row in rows),
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


def annotate_stacked_totals(
    axis: plt.Axes, y_values: list[int], totals: list[float], formatter: Any
) -> None:
    maximum = max(totals)
    offset = maximum * 0.025
    for y, total in zip(y_values, totals):
        axis.text(
            total + offset,
            y,
            formatter(total),
            va="center",
            ha="left",
            fontsize=8.2,
            color=TEXT_COLOR,
        )
    axis.set_xlim(0, maximum * 1.23)


def draw_figure(setting_summary: list[dict[str, Any]]) -> plt.Figure:
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

    figure = plt.figure(figsize=(16.2, 4.8), facecolor="white")
    grid = figure.add_gridspec(1, 3, wspace=0.48)
    setting_time = figure.add_subplot(grid[0, 0])
    setting_tokens = figure.add_subplot(grid[0, 1])
    setting_cost = figure.add_subplot(grid[0, 2])

    figure.suptitle(
        "Harness-Level Latency, Tokens, and Estimated Cost Across 15 Cases",
        x=0.055,
        y=0.97,
        ha="left",
        fontsize=15,
        fontweight="bold",
        color=TEXT_COLOR,
    )

    agent_labels = [row["agent"] for row in setting_summary]
    agent_y = list(range(len(agent_labels)))
    time_values = [row["mean_duration_seconds"] / 60 for row in setting_summary]
    token_components = {
        "Uncached input": [
            row["mean_uncached_input_tokens"] / 1_000_000
            for row in setting_summary
        ],
        "Cache read": [
            row["mean_cache_read_tokens"] / 1_000_000 for row in setting_summary
        ],
        "Output": [row["mean_output_tokens"] / 1_000_000 for row in setting_summary],
    }
    component_colors = [UNCACHED_COLOR, CACHE_COLOR, OUTPUT_COLOR]

    bars = setting_time.barh(agent_y, time_values, color=PASS_COLOR, height=0.54)
    setting_time.set_yticks(agent_y, agent_labels)
    setting_time.invert_yaxis()
    setting_time.set_xlabel("Mean minutes per trace")
    setting_time.set_title("a  Mean elapsed time", loc="left", fontweight="bold")
    style_axis(setting_time)
    annotate_bars(setting_time, bars, lambda value: f"{value:.1f}m")

    token_left = [0.0] * len(agent_labels)
    for (label, values), color in zip(token_components.items(), component_colors):
        setting_tokens.barh(
            agent_y,
            values,
            left=token_left,
            color=color,
            height=0.54,
            label=label,
        )
        token_left = [left + value for left, value in zip(token_left, values)]
    setting_tokens.set_yticks(agent_y, agent_labels)
    setting_tokens.invert_yaxis()
    setting_tokens.set_xlabel("Mean tokens per trace (millions)")
    setting_tokens.set_title("b  Mean total tokens", loc="left", fontweight="bold")
    style_axis(setting_tokens)
    annotate_stacked_totals(
        setting_tokens, agent_y, token_left, lambda value: f"{value:.2f}M"
    )
    setting_tokens.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, 1.18),
        ncol=3,
        frameon=False,
        fontsize=7.5,
        handlelength=1.2,
        columnspacing=0.9,
    )

    cost_components = {
        "Uncached input": [
            row["mean_uncached_input_tokens"]
            * PRICE_PER_MILLION["uncached_input_tokens"]
            / 1_000_000
            for row in setting_summary
        ],
        "Cache read": [
            row["mean_cache_read_tokens"]
            * PRICE_PER_MILLION["cache_read_tokens"]
            / 1_000_000
            for row in setting_summary
        ],
        "Output": [
            row["mean_output_tokens"]
            * PRICE_PER_MILLION["output_tokens"]
            / 1_000_000
            for row in setting_summary
        ],
    }
    cost_left = [0.0] * len(agent_labels)
    for values, color in zip(cost_components.values(), component_colors):
        setting_cost.barh(
            agent_y, values, left=cost_left, color=color, height=0.54
        )
        cost_left = [left + value for left, value in zip(cost_left, values)]
    setting_cost.set_yticks(agent_y, agent_labels)
    setting_cost.invert_yaxis()
    setting_cost.set_xlabel("Estimated USD per trace")
    setting_cost.set_title("c  Mean estimated cost", loc="left", fontweight="bold")
    style_axis(setting_cost)
    annotate_stacked_totals(
        setting_cost, agent_y, cost_left, lambda value: f"${value:.3f}"
    )

    figure.text(
        0.055,
        0.03,
        "Latency means exclude Original PG Agent on DCI and Claude Code on DocVQA; token means exclude only the zero-token DocVQA runtime failure.",
        ha="left",
        va="bottom",
        fontsize=8.5,
        color=MUTED_COLOR,
    )
    figure.text(
        0.055,
        0.01,
        "Cost uses DeepSeek V4 Pro list prices checked 2026-07-15: $0.435/M uncached input, $0.003625/M cache read, and $0.87/M output; actual provider bills may differ.",
        ha="left",
        va="bottom",
        fontsize=8.5,
        color=MUTED_COLOR,
    )
    figure.subplots_adjust(left=0.14, right=0.98, top=0.76, bottom=0.25)
    return figure


def main() -> None:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    metrics = collect_trace_metrics(repo_root)
    setting_summary = summarize_settings(metrics)

    results_dir = repo_root / "results"
    write_csv(results_dir / "trace_metrics.csv", metrics)
    write_csv(results_dir / "setting_summary.csv", setting_summary)

    figure = draw_figure(setting_summary)
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
    print(results_dir / "setting_summary.csv")
    print(figure_dir / "trace_efficiency.png")
    print(figure_dir / "trace_efficiency.pdf")


if __name__ == "__main__":
    main()
