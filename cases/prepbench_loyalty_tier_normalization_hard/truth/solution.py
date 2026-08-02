#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd


CANONICAL_TIERS = ["Bronze", "Gold", "Silver"]


def normalize_identifier(value):
    if pd.isna(value):
        return pd.NA
    text = str(value).strip()
    if not text:
        return pd.NA
    if text.endswith(".0") and text.replace(".", "", 1).isdigit():
        text = text.split(".", 1)[0]
    return text


def normalize_tier(value):
    if pd.isna(value):
        return pd.NA
    token = str(value).strip().lower()
    if not token:
        return pd.NA
    if "gold" in token or "goald" in token:
        return "Gold"
    if "silv" in token or "sliv" in token:
        return "Silver"
    if "bron" in token:
        return "Bronze"
    return pd.NA


def solve(data_dir: Path) -> dict:
    transactions = pd.read_csv(data_dir / "transactions.csv")
    products = pd.read_csv(data_dir / "products.csv")
    loyalty = pd.read_csv(data_dir / "loyalty_customers.csv")

    transactions["Transaction_Date"] = pd.to_datetime(
        transactions["Transaction_Date"], format="%a, %B %d, %Y", errors="coerce"
    ).fillna(pd.to_datetime(transactions["Transaction_Date"], errors="coerce"))
    transactions = transactions[
        transactions["Transaction_Date"].dt.year.isin([2023, 2024])
    ].copy()
    transactions["Loyalty_Number"] = transactions["Loyalty_Number"].apply(
        normalize_identifier
    )
    transactions["Sales_Before_Discount"] = pd.to_numeric(
        transactions["Sales_Before_Discount"], errors="coerce"
    )

    product_parts = transactions["Product_ID"].astype("string").str.split(
        "-", n=2, expand=True
    )
    transactions["Product_Type"] = product_parts[0].str.strip()
    transactions["Product_Scent"] = (
        product_parts[1].str.replace("_", " ", regex=False).str.strip()
    )
    transactions["Product_Size"] = product_parts[2].str.strip()

    products = products.copy()
    products["Product_Size"] = (
        products["Product_Size"]
        .replace("", pd.NA)
        .fillna(products["Pack_Size"].replace("", pd.NA))
        .astype("string")
        .str.strip()
    )
    products["Product_Type"] = products["Product_Type"].astype("string").str.strip()
    products["Product_Scent"] = products["Product_Scent"].astype("string").str.strip()
    products["Unit_Cost"] = pd.to_numeric(products["Unit_Cost"], errors="coerce")
    products["Selling_Price"] = pd.to_numeric(
        products["Selling_Price"], errors="coerce"
    )

    transactions = transactions.merge(
        products[
            [
                "Product_Type",
                "Product_Scent",
                "Product_Size",
                "Unit_Cost",
                "Selling_Price",
            ]
        ],
        how="left",
        on=["Product_Type", "Product_Scent", "Product_Size"],
    )
    quantity = (transactions["Sales_Before_Discount"] / transactions["Selling_Price"]).map(
        lambda value: math.floor(value) if pd.notna(value) else pd.NA
    )
    quantity = quantity.where(
        transactions["Selling_Price"].notna() & transactions["Selling_Price"].ne(0)
    )
    transactions["Quantity"] = pd.to_numeric(quantity, errors="coerce")

    loyalty = loyalty.copy()
    raw_tier_profile = {
        str(k): int(v)
        for k, v in loyalty["Loyalty_Tier"].value_counts(dropna=True).to_dict().items()
    }
    loyalty["Loyalty_Number"] = loyalty["Loyalty_Number"].apply(normalize_identifier)
    loyalty["Canonical_Tier"] = loyalty["Loyalty_Tier"].apply(normalize_tier)
    loyalty["Loyalty_Discount"] = (
        loyalty["Loyalty_Discount"]
        .astype(str)
        .str.replace(r"[^\d.]", "", regex=True)
    )
    loyalty["Loyalty_Discount"] = (
        pd.to_numeric(loyalty["Loyalty_Discount"], errors="coerce") / 100
    )

    transactions = transactions.merge(
        loyalty[
            [
                "Loyalty_Number",
                "Loyalty_Tier",
                "Canonical_Tier",
                "Loyalty_Discount",
            ]
        ],
        on="Loyalty_Number",
        how="left",
    )

    discount_mask = (
        transactions["Loyalty_Number"].notna()
        & transactions["Loyalty_Discount"].notna()
        & transactions["Sales_Before_Discount"].notna()
    )
    transactions["Sales_After_Discount"] = float("nan")
    transactions.loc[discount_mask, "Sales_After_Discount"] = (
        transactions.loc[discount_mask, "Sales_Before_Discount"]
        * (1 - transactions.loc[discount_mask, "Loyalty_Discount"])
    )

    profit_mask = (
        transactions["Sales_After_Discount"].notna()
        & transactions["Unit_Cost"].notna()
        & transactions["Quantity"].notna()
    )
    transactions["Profit"] = float("nan")
    transactions.loc[profit_mask, "Profit"] = (
        transactions.loc[profit_mask, "Sales_After_Discount"]
        - transactions.loc[profit_mask, "Unit_Cost"]
        * transactions.loc[profit_mask, "Quantity"]
    )

    canonical = transactions[transactions["Canonical_Tier"].isin(CANONICAL_TIERS)]
    by_tier_df = (
        canonical.groupby("Canonical_Tier", as_index=False)
        .agg(
            transaction_rows=("Transaction_Date", "size"),
            loyalty_customers=("Loyalty_Number", "nunique"),
            sales_after_discount=("Sales_After_Discount", "sum"),
            profit=("Profit", "sum"),
        )
        .rename(columns={"Canonical_Tier": "tier"})
        .sort_values("tier")
    )
    by_tier_df["sales_after_discount"] = by_tier_df["sales_after_discount"].round(2)
    by_tier_df["profit"] = by_tier_df["profit"].round(2)

    by_tier = {}
    for row in by_tier_df.to_dict(orient="records"):
        by_tier[row["tier"]] = {
            "transaction_rows": int(row["transaction_rows"]),
            "loyalty_customers": int(row["loyalty_customers"]),
            "sales_after_discount": float(row["sales_after_discount"]),
            "profit": float(row["profit"]),
        }

    total_profit = sum(row["profit"] for row in by_tier.values())
    gold_share = by_tier["Gold"]["profit"] / total_profit
    answer = f"{gold_share:.6f}"

    return {
        "answer": [answer],
        "by_tier": [
            {"tier": tier, **by_tier[tier]}
            for tier in ["Bronze", "Gold", "Silver"]
        ],
        "checkpoints": {
            "raw_loyalty_tier_values": raw_tier_profile,
            "canonical_transaction_rows": {
                tier: by_tier[tier]["transaction_rows"]
                for tier in ["Bronze", "Gold", "Silver"]
            },
        },
    }


def main() -> None:
    data_dir = Path(__file__).resolve().parents[1] / "data"
    print(json.dumps(solve(data_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
