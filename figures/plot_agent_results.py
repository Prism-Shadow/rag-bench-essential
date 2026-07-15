#!/usr/bin/env python3
"""Plot aggregate and case-level results for the selected 4x15 traces."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Rectangle


AGENTS = ["Original PG Agent\n(empty AGENTS.md)", "RAG Agent", "Claude Code", "Codex"]

# Rows are deliberately ordered by outcome pattern so the result structure is
# visible at a glance rather than hidden by benchmark naming order.
ROWS = [
    ("DocFinQA", (1, 1, 1, 1)),
    ("DABstep", (1, 1, 1, 1)),
    ("LongDA", (1, 1, 1, 1)),
    ("MultiHiertt", (1, 1, 1, 1)),
    ("Spider2-Lite", (0, 1, 1, 1)),
    ("PrepBench", (0, 1, 1, 1)),
    ("SpreadsheetBench", (0, 1, 1, 1)),
    ("BankerToolBench", (1, 1, 1, 0)),
    ("HarveyLab", (0, 1, 1, 0)),
    ("MedAgentBench", (0, 1, 1, 0)),
    ("DCI / BrowseComp+", (0, 0, 0, 0)),
    ("DocVQA", (0, 0, 0, 0)),
    ("WorkspaceBench", (0, 0, 0, 0)),
    ("DVWorld", (0, 0, 0, 0)),
    ("FinLongDocQA", (0, 0, 0, 0)),
]

GROUPS = [
    (0, 3, "Passed by all", "4 cases"),
    (4, 6, "RAG Agent + CC + Codex", "3 cases"),
    (7, 7, "Original PG + RAG + CC", "1 case"),
    (8, 9, "RAG Agent + Claude Code", "2 cases"),
    (10, 14, "Failed by all", "5 cases"),
]

PASS_COLOR = "#2F6BFF"
FAIL_COLOR = "#E5E7EB"
TEXT_COLOR = "#172033"
MUTED_COLOR = "#667085"
GRID_COLOR = "#D0D5DD"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="Directory for generated PNG and PDF files.",
    )
    parser.add_argument(
        "--stem",
        default="agent_results",
        help="Output filename stem (default: agent_results).",
    )
    parser.add_argument("--dpi", type=int, default=300, help="PNG resolution.")
    return parser.parse_args()


def validate_data() -> list[int]:
    if len(ROWS) != 15:
        raise ValueError(f"Expected 15 cases, found {len(ROWS)}")
    if any(len(outcomes) != len(AGENTS) for _, outcomes in ROWS):
        raise ValueError("Every case must have one result per agent")

    scores = [sum(outcomes[i] for _, outcomes in ROWS) for i in range(len(AGENTS))]
    if scores != [5, 10, 10, 7]:
        raise ValueError(f"Expected aggregate scores [5, 10, 10, 7], found {scores}")
    return scores


def draw_figure() -> plt.Figure:
    scores = validate_data()
    total = len(ROWS)

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.titlesize": 11,
            "axes.labelcolor": TEXT_COLOR,
            "text.color": TEXT_COLOR,
            "xtick.color": MUTED_COLOR,
            "ytick.color": TEXT_COLOR,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )

    figure = plt.figure(figsize=(12.2, 9.3), facecolor="white")
    grid = figure.add_gridspec(2, 1, height_ratios=(1.75, 5.2), hspace=0.3)
    bars = figure.add_subplot(grid[0])
    matrix = figure.add_subplot(grid[1])

    figure.suptitle(
        "Selected Results Across 15 Benchmark Cases",
        x=0.12,
        y=0.985,
        ha="left",
        fontsize=15,
        fontweight="bold",
        color=TEXT_COLOR,
    )

    # Panel A: denominator-aware horizontal bars.
    y_positions = list(range(len(AGENTS)))
    bars.barh(y_positions, [total] * len(AGENTS), color=FAIL_COLOR, height=0.52)
    bars.barh(y_positions, scores, color=PASS_COLOR, height=0.52)
    bars.set_yticks(y_positions, AGENTS)
    bars.invert_yaxis()
    bars.set_xlim(0, total + 1.2)
    bars.set_xticks([0, 5, 10, 15])
    bars.set_xlabel("Cases passed", labelpad=4)
    bars.grid(axis="x", color=GRID_COLOR, linewidth=0.7, alpha=0.65)
    bars.set_axisbelow(True)
    bars.tick_params(axis="y", length=0, pad=8)
    bars.tick_params(axis="x", length=0)
    for spine in bars.spines.values():
        spine.set_visible(False)
    for y, score in zip(y_positions, scores):
        bars.text(
            score + 0.22,
            y,
            f"{score}/{total}  ({score / total:.1%})",
            va="center",
            ha="left",
            fontsize=10,
            fontweight="bold",
        )
    bars.text(
        -0.11,
        1.08,
        "a  Overall result",
        transform=bars.transAxes,
        ha="left",
        va="bottom",
        fontsize=11,
        fontweight="bold",
    )

    # Panel B: compact binary matrix with outcome-pattern grouping.
    matrix.set_xlim(-0.65, 5.7)
    matrix.set_ylim(len(ROWS) - 0.5, -0.5)
    matrix.set_xticks(range(len(AGENTS)), AGENTS)
    matrix.xaxis.tick_top()
    matrix.tick_params(axis="x", length=0, pad=9)
    matrix.set_yticks(range(len(ROWS)), [label for label, _ in ROWS])
    matrix.tick_params(axis="y", length=0, pad=8)

    for row_index, (_, outcomes) in enumerate(ROWS):
        for column_index, passed in enumerate(outcomes):
            color = PASS_COLOR if passed else FAIL_COLOR
            matrix.add_patch(
                Rectangle(
                    (column_index - 0.39, row_index - 0.34),
                    0.78,
                    0.68,
                    facecolor=color,
                    edgecolor="none",
                )
            )
            matrix.text(
                column_index,
                row_index,
                "✓" if passed else "–",
                ha="center",
                va="center",
                color="white" if passed else MUTED_COLOR,
                fontsize=11,
                fontweight="bold",
            )

    for separator in (3.5, 6.5, 7.5, 9.5):
        matrix.axhline(separator, color=GRID_COLOR, linewidth=0.9)

    for start, end, label, count in GROUPS:
        center = (start + end) / 2
        x = 3.82
        matrix.plot(
            [x + 0.12, x, x, x + 0.12],
            [start - 0.34, start - 0.34, end + 0.34, end + 0.34],
            color=GRID_COLOR,
            linewidth=1.0,
            clip_on=False,
        )
        matrix.text(
            x + 0.22,
            center - 0.12,
            label,
            ha="left",
            va="center",
            fontsize=9.5,
            fontweight="bold",
        )
        matrix.text(
            x + 0.22,
            center + 0.38,
            count,
            ha="left",
            va="center",
            fontsize=9,
            color=MUTED_COLOR,
        )

    matrix.legend(
        handles=[
            Patch(facecolor=PASS_COLOR, edgecolor="none", label="PASS"),
            Patch(facecolor=FAIL_COLOR, edgecolor="none", label="FAIL"),
        ],
        loc="lower right",
        frameon=False,
        ncol=2,
        bbox_to_anchor=(1.0, -0.08),
        handlelength=1.2,
        columnspacing=1.3,
    )
    for spine in matrix.spines.values():
        spine.set_visible(False)
    matrix.text(
        -0.11,
        1.14,
        "b  Case-level result",
        transform=matrix.transAxes,
        ha="left",
        va="bottom",
        fontsize=11,
        fontweight="bold",
    )

    figure.text(
        0.12,
        0.012,
        "Each cell represents one selected trace. Original PG uses a near-empty AGENTS.md; changed tasks were rerun.",
        ha="left",
        va="bottom",
        fontsize=8.5,
        color=MUTED_COLOR,
    )
    figure.subplots_adjust(left=0.25, right=0.96, top=0.92, bottom=0.09)
    return figure


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    figure = draw_figure()
    png_path = args.output_dir / f"{args.stem}.png"
    pdf_path = args.output_dir / f"{args.stem}.pdf"
    figure.savefig(png_path, dpi=args.dpi, bbox_inches="tight", facecolor="white")
    figure.savefig(pdf_path, bbox_inches="tight", facecolor="white")
    plt.close(figure)
    print(png_path)
    print(pdf_path)


if __name__ == "__main__":
    main()
