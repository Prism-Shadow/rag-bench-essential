#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from pathlib import Path


MERCHANT = "Belles_cookbook_store"
YEAR = 2023
DAY_OF_YEAR = 10


def parse_bool(value: str) -> bool:
    return str(value).strip().lower() == "true"


def parse_amount(value: str) -> float:
    raw = str(value).strip().lower().replace(",", "").replace("%", "")
    multiplier = 1.0
    if raw.endswith("k"):
        multiplier = 1_000.0
        raw = raw[:-1]
    elif raw.endswith("m"):
        multiplier = 1_000_000.0
        raw = raw[:-1]
    return float(raw) * multiplier


def match_range(spec: str | None, value: float) -> bool:
    if spec is None:
        return True
    raw = str(spec).strip().lower()
    if "-" in raw:
        left, right = raw.split("-", 1)
        return parse_amount(left) <= value <= parse_amount(right)
    if raw.startswith(">"):
        return value > parse_amount(raw[1:])
    if raw.startswith("<"):
        return value < parse_amount(raw[1:])
    return abs(value - parse_amount(raw)) <= 1e-9


def match_capture_delay(spec: str | None, merchant_delay: str) -> bool:
    if spec is None:
        return True
    raw = str(spec).strip().lower()
    delay = str(merchant_delay).strip().lower()
    if raw == "manual":
        return delay == "manual"
    if raw == "immediate":
        return delay in {"immediate", "0"}
    try:
        days = float(delay)
    except ValueError:
        return False
    if "-" in raw:
        left, right = raw.split("-", 1)
        return float(left) <= days <= float(right)
    if raw.startswith(">"):
        return days > float(raw[1:])
    if raw.startswith("<"):
        return days < float(raw[1:])
    return delay == raw


def list_matches(options: list, value) -> bool:
    return not options or value in options


def load_rows(data_dir: Path) -> list[dict]:
    with (data_dir / "payments.csv").open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def fee_applies(rule: dict, row: dict, merchant: dict, monthly_volume: float, fraud_pct: float) -> bool:
    if rule["card_scheme"] != row["card_scheme"]:
        return False
    if not list_matches(rule["account_type"], merchant["account_type"]):
        return False
    if not match_capture_delay(rule["capture_delay"], merchant["capture_delay"]):
        return False
    if not match_range(rule["monthly_fraud_level"], fraud_pct):
        return False
    if not match_range(rule["monthly_volume"], monthly_volume):
        return False
    if not list_matches(rule["merchant_category_code"], int(merchant["merchant_category_code"])):
        return False
    if rule["is_credit"] is not None and bool(rule["is_credit"]) != parse_bool(row["is_credit"]):
        return False
    if not list_matches(rule["aci"], row["aci"]):
        return False
    if rule["intracountry"] is not None:
        intracountry = row["issuing_country"] == row["acquirer_country"]
        if bool(int(float(rule["intracountry"]))) != intracountry:
            return False
    return True


def main() -> int:
    data_dir = Path("data")
    merchants = json.loads((data_dir / "merchant_data.json").read_text(encoding="utf-8"))
    merchant = next(item for item in merchants if item["merchant"] == MERCHANT)
    fees = json.loads((data_dir / "fees.json").read_text(encoding="utf-8"))
    rows = [
        row for row in load_rows(data_dir)
        if row["merchant"] == MERCHANT and int(row["year"]) == YEAR
    ]

    # Day 10 is in January, so the natural month is day-of-year 1 through 31.
    month_rows = [row for row in rows if 1 <= int(row["day_of_year"]) <= 31]
    monthly_volume = sum(float(row["eur_amount"]) for row in month_rows)
    fraud_volume = sum(
        float(row["eur_amount"]) for row in month_rows
        if parse_bool(row["has_fraudulent_dispute"])
    )
    fraud_pct = fraud_volume / monthly_volume * 100.0 if monthly_volume else 0.0

    day_rows = [row for row in rows if int(row["day_of_year"]) == DAY_OF_YEAR]
    fee_ids = sorted({
        int(rule["ID"])
        for row in day_rows
        for rule in fees
        if fee_applies(rule, row, merchant, monthly_volume, fraud_pct)
    })

    answer = ", ".join(str(item) for item in fee_ids)
    Path("answers.json").write_text(
        json.dumps({"answer": [answer]}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"month_volume={monthly_volume:.2f} fraud_pct={fraud_pct:.6f} day_rows={len(day_rows)}")
    print(answer)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
