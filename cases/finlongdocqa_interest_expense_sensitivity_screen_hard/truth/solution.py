#!/usr/bin/env python3
"""Reference solution for the interest expense sensitivity screen case."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path


CASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = CASE_DIR / "data"


def require(pattern: str, text: str, label: str, flags: int = re.IGNORECASE | re.DOTALL) -> re.Match:
    match = re.search(pattern, text, flags)
    if not match:
        raise RuntimeError(f"missing expected disclosure: {label}")
    return match


def clean_number(value: str) -> float:
    return float(value.replace(",", ""))


def load_manifest_tickers() -> list[str]:
    with (DATA_DIR / "document_manifest.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    tickers = sorted({row["ticker"].strip().upper() for row in rows if row.get("ticker")})
    return tickers


def text_for(ticker: str) -> str:
    return (DATA_DIR / "reports" / f"{ticker}_2024_10K.md").read_text(encoding="utf-8", errors="ignore")


def compute() -> dict:
    # These extraction patterns are deliberately tied to the public filings, not to
    # an external answer table. They assert the disclosures that make each ticker
    # eligible and leave ineligible tickers out because at least one required field
    # is missing or belongs to a decoy sensitivity family.
    rows = []

    anss = text_for("ANSS")
    debt = clean_number(require(r"term loan borrowings of \$([0-9,.]+) million", anss, "ANSS debt").group(1))
    impact = clean_number(require(r"100 basis points.*?increase in interest expense of \$([0-9,.]+) million", anss, "ANSS impact").group(1))
    rows.append(row("ANSS", 100.0, impact, impact, debt))

    aptv = text_for("APTV")
    debt = clean_number(require(r"approximately S([0-9,.]+) million of floating rate debt", aptv, "APTV debt").group(1))
    impact = clean_number(require(r"\| 25 bp increase\s+\| \+ \$([0-9,.]+)", aptv, "APTV impact").group(1))
    rows.append(row("APTV", 25.0, impact, impact * 4, debt))

    cl = text_for("CL")
    debt = clean_number(require(r"commercial paper outstanding was S([0-9,.]+)", cl, "CL debt").group(1))
    impact = clean_number(require(r"1% increase in interest rates would have increased Interest expense by S([0-9,.]+)", cl, "CL impact").group(1))
    rows.append(row("CL", 100.0, impact, impact, debt))

    ecl = text_for("ECL")
    debt_bil = clean_number(require(r"approximately \$([0-9,.]+) billion in the form of floating rate debt", ecl, "ECL debt").group(1))
    impact = clean_number(require(r"one percentage point.*?increase future interest expense by approximately \$([0-9,.]+) million", ecl, "ECL impact").group(1))
    rows.append(row("ECL", 100.0, impact, impact, debt_bil * 1000))

    pwr = text_for("PWR")
    debt = clean_number(require(r"variable-rate debt consisted of \$([0-9,.]+) million outstanding under our senior credit facility", pwr, "PWR debt").group(1))
    impact = clean_number(require(r"50 basis point increase or decrease.*?impact annual interest expense by approximately \$([0-9,.]+) million", pwr, "PWR impact").group(1))
    rows.append(row("PWR", 50.0, impact, impact * 2, debt))

    rcl = text_for("RCL")
    debt_bil = clean_number(require(r"approximately \$([0-9,.]+) billion of indebtedness that bears interest at variable rates", rcl, "RCL debt").group(1))
    impact = clean_number(require(r"1% increase in prevailing interest rates would increase.*?interest expense by approximately \$([0-9,.]+) million", rcl, "RCL impact").group(1))
    rows.append(row("RCL", 100.0, impact, impact, debt_bil * 1000))

    stz = text_for("STZ")
    debt = clean_number(require(r"Short-term borrowings\s+\| \$ ([0-9,.]+)", stz, "STZ short-term borrowings").group(1))
    impact = clean_number(require(r"1% hypothetical change.*?increased interest expense on our variable interest rate debt by \$([0-9,.]+) million", stz, "STZ impact").group(1))
    rows.append(row("STZ", 100.0, impact, impact, debt))

    rows.sort(key=lambda item: item["impact_per_1b_variable_debt_musd"], reverse=True)
    included = [item["ticker"] for item in rows]
    all_tickers = load_manifest_tickers()
    excluded = [{"ticker": ticker, "reason": "No eligible year-end variable/floating debt amount and matching interest expense sensitivity disclosure."} for ticker in all_tickers if ticker not in included]
    spread = rows[0]["impact_per_1b_variable_debt_musd"] - rows[-1]["impact_per_1b_variable_debt_musd"]
    return {
        "included_tickers": sorted(included),
        "ranking_high_to_low": rows,
        "top_ticker": rows[0]["ticker"],
        "bottom_ticker": rows[-1]["ticker"],
        "spread_per_1b_musd": spread,
        "excluded_tickers": excluded,
    }


def row(ticker: str, shock_bp: float, reported_impact: float, standardized_impact: float, debt: float) -> dict:
    return {
        "ticker": ticker,
        "rate_shock_bp": shock_bp,
        "reported_interest_expense_impact_musd": reported_impact,
        "standardized_interest_expense_impact_musd": standardized_impact,
        "variable_rate_debt_musd": debt,
        "impact_per_1b_variable_debt_musd": standardized_impact / debt * 1000,
    }


def main() -> None:
    print(json.dumps(compute(), indent=2, sort_keys=False))


if __name__ == "__main__":
    main()
