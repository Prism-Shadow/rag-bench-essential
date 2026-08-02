#!/usr/bin/env python3
"""External validator for the interest expense sensitivity screen case.

Run with cwd=workspace and BENCH_TRUTH_DIR pointing at this truth directory.
Exit codes: 0 pass; 1 answer mismatch; 2 missing/unreadable output.
"""
from __future__ import annotations

import json
import math
import os
import re
import sys
from pathlib import Path


def truth_dir() -> Path:
    env = os.environ.get("BENCH_TRUTH_DIR")
    return Path(env) if env else Path(__file__).resolve().parent


def load_expected() -> dict:
    return json.loads((truth_dir() / "expected.json").read_text(encoding="utf-8"))


def fail2(message: str) -> int:
    print(f"FAIL: {message}")
    return 2


def norm_ticker(value) -> str:
    return str(value or "").strip().upper()


def to_number(value):
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).replace(",", "").strip()
    match = re.search(r"[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?", text)
    return float(match.group(0)) if match else None


def ticker_list(value) -> list[str]:
    if not isinstance(value, list):
        return []
    result = []
    for item in value:
        if isinstance(item, dict):
            result.append(norm_ticker(item.get("ticker")))
        else:
            result.append(norm_ticker(item))
    return [ticker for ticker in result if ticker]


def ranking_rows(answers: dict) -> list[dict]:
    raw = answers.get("ranking_high_to_low")
    if not isinstance(raw, list):
        return []
    rows = []
    for item in raw:
        if isinstance(item, dict):
            ticker = norm_ticker(item.get("ticker"))
            if ticker:
                rows.append({"ticker": ticker, **item})
        else:
            ticker = norm_ticker(item)
            if ticker:
                rows.append({"ticker": ticker})
    return rows


def row_value(row: dict, *keys: str):
    for key in keys:
        if key in row:
            return row.get(key)
    return None


def check_close(label: str, expected: float, got, tol: float) -> bool:
    num = to_number(got)
    ok = num is not None and math.isfinite(num) and abs(num - expected) <= tol
    print(f"  [{'OK ' if ok else 'FAIL'}] {label}: expected={expected:.6f} got={num!r} tol=+/-{tol}")
    return ok


def main() -> int:
    path = Path("answers.json")
    if not path.exists():
        return fail2(f"answers.json not found at {path.resolve()}")
    try:
        answers = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return fail2(f"cannot parse answers.json: {exc}")

    expected = load_expected()
    amount_tol = float(expected["tolerances"]["amount_abs_musd"])
    shock_tol = float(expected["tolerances"]["rate_shock_abs_bp"])
    ratio_tol = float(expected["tolerances"]["ratio_abs_musd_per_1b"])
    spread_tol = float(expected["tolerances"]["spread_abs_musd_per_1b"])

    rows = ranking_rows(answers)
    rows_by_ticker = {row["ticker"]: row for row in rows}
    ok = True

    print("== D1 eligible universe ==")
    exp_included = sorted(expected["included_tickers"])
    got_included = sorted(ticker_list(answers.get("included_tickers")) or [row["ticker"] for row in rows])
    included_ok = got_included == exp_included
    print(f"  [{'OK ' if included_ok else 'FAIL'}] included_tickers: expected={exp_included} got={got_included}")
    ok = included_ok and ok

    exp_excluded = sorted(expected["excluded_tickers"])
    got_excluded = sorted(ticker_list(answers.get("excluded_tickers")))
    if got_excluded:
        excluded_ok = got_excluded == exp_excluded
        print(f"  [{'OK ' if excluded_ok else 'FAIL'}] excluded_tickers: expected={exp_excluded} got={got_excluded}")
        ok = excluded_ok and ok
    else:
        print("  [WARN] excluded_tickers missing or empty; not used for pass/fail")

    print("== D2 ranking and spread ==")
    got_ranking = [row["ticker"] for row in rows]
    exp_ranking = expected["ranking_high_to_low"]
    ranking_ok = got_ranking == exp_ranking
    print(f"  [{'OK ' if ranking_ok else 'FAIL'}] ranking_high_to_low: expected={exp_ranking} got={got_ranking}")
    ok = ranking_ok and ok

    top_ok = norm_ticker(answers.get("top_ticker")) == expected["top_ticker"]
    bottom_ok = norm_ticker(answers.get("bottom_ticker")) == expected["bottom_ticker"]
    print(f"  [{'OK ' if top_ok else 'FAIL'}] top_ticker: expected={expected['top_ticker']} got={answers.get('top_ticker')!r}")
    print(f"  [{'OK ' if bottom_ok else 'FAIL'}] bottom_ticker: expected={expected['bottom_ticker']} got={answers.get('bottom_ticker')!r}")
    ok = top_ok and bottom_ok and ok
    ok = check_close("spread_per_1b_musd", float(expected["spread_per_1b_musd"]), answers.get("spread_per_1b_musd"), spread_tol) and ok

    print("== D3 load-bearing figures ==")
    for ticker in expected["ranking_high_to_low"]:
        row = rows_by_ticker.get(ticker)
        if not row:
            print(f"  [FAIL] {ticker}: missing ranking row")
            ok = False
            continue
        exp = expected["figures"][ticker]
        ok = check_close(
            f"{ticker}.rate_shock_bp",
            float(exp["rate_shock_bp"]),
            row_value(row, "rate_shock_bp", "reported_rate_shock_bp", "shock_bp"),
            shock_tol,
        ) and ok
        ok = check_close(
            f"{ticker}.reported_interest_expense_impact_musd",
            float(exp["reported_interest_expense_impact_musd"]),
            row_value(row, "reported_interest_expense_impact_musd", "reported_impact_musd", "interest_expense_impact_musd"),
            amount_tol,
        ) and ok
        ok = check_close(
            f"{ticker}.standardized_interest_expense_impact_musd",
            float(exp["standardized_interest_expense_impact_musd"]),
            row_value(row, "standardized_interest_expense_impact_musd", "standardized_impact_musd", "impact_100bp_musd"),
            amount_tol,
        ) and ok
        ok = check_close(
            f"{ticker}.variable_rate_debt_musd",
            float(exp["variable_rate_debt_musd"]),
            row_value(row, "variable_rate_debt_musd", "floating_rate_debt_musd", "variable_debt_musd"),
            amount_tol,
        ) and ok
        ok = check_close(
            f"{ticker}.impact_per_1b_variable_debt_musd",
            float(exp["impact_per_1b_variable_debt_musd"]),
            row_value(row, "impact_per_1b_variable_debt_musd", "impact_per_1b_musd", "sensitivity_per_1b_musd"),
            ratio_tol,
        ) and ok

    print()
    if ok:
        print("RESULT: PASS - interest expense sensitivity screen passes.")
        return 0

    print("RESULT: FAIL - eligible universe, ranking, spread, or load-bearing figures mismatch.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
