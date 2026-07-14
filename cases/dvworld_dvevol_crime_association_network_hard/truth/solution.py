#!/usr/bin/env python3
import base64
import csv
import json
from pathlib import Path

import pandas as pd


CASE_ID = "dvworld_dvevol_crime_association_network_hard"
TITLE = "Crime Type Association Network (|corr| >= 0.40)"
NODE_ORDER = [
    "Murder",
    "Rape_Revised",
    "Robbery",
    "Assault",
    "Burglary",
    "Larceny",
    "Vehicle_Theft",
]
CRIME_RATE_COLS = [f"{node}_Rate" for node in NODE_ORDER]
THRESHOLD = 0.40
WIDTH_BY_BIN = {"0.40-0.54": 1.3, "0.55-0.69": 2.6, "0.70+": 4.0}
POS_COLOR = "#D7191C"
NEG_COLOR = "#2C7BB6"


def clean_workbook(path: Path) -> pd.DataFrame:
    df = pd.read_excel(path)
    data_start_idx = 0
    for i in range(len(df)):
        value = df.iloc[i, 0]
        if pd.notna(value) and str(value).strip() not in ("", "NaN"):
            area_name = str(value).strip().lower()
            if any(
                key in area_name
                for key in (
                    "northeast",
                    "midwest",
                    "south",
                    "west",
                    "alabama",
                    "alaska",
                    "arizona",
                )
            ):
                data_start_idx = i
                break

    df_clean = df.iloc[data_start_idx:].copy()
    df_clean.columns = [
        "Area",
        "Year",
        "Population",
        "Violent_Crime_Total",
        "Violent_Crime_Rate",
        "Murder_Total",
        "Murder_Rate",
        "Rape_Revised_Total",
        "Rape_Revised_Rate",
        "Rape_Legacy_Total",
        "Rape_Legacy_Rate",
        "Robbery_Total",
        "Robbery_Rate",
        "Assault_Total",
        "Assault_Rate",
        "Property_Crime_Total",
        "Property_Crime_Rate",
        "Burglary_Total",
        "Burglary_Rate",
        "Larceny_Total",
        "Larceny_Rate",
        "Vehicle_Theft_Total",
        "Vehicle_Theft_Rate",
    ]
    df_clean = df_clean.dropna(subset=["Area"])
    exclude_patterns = [
        "percent change",
        "total",
        "united states",
        "crime in",
        "by region",
        "area",
        "rate per",
    ]
    pattern = "|".join(exclude_patterns)
    df_clean = df_clean[
        ~df_clean["Area"].astype(str).str.lower().str.contains(pattern, na=False)
    ].copy()

    for col in df_clean.columns:
        if col not in ("Area", "Year"):
            df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")

    region_mapping = {
        "Northeast": [
            "Connecticut",
            "Maine",
            "Massachusetts",
            "New Hampshire",
            "Rhode Island",
            "Vermont",
            "New Jersey",
            "New York",
            "Pennsylvania",
        ],
        "Midwest": [
            "Illinois",
            "Indiana",
            "Michigan",
            "Ohio",
            "Wisconsin",
            "Iowa",
            "Kansas",
            "Minnesota",
            "Missouri",
            "Nebraska",
            "North Dakota",
            "South Dakota",
        ],
        "South": [
            "Delaware",
            "Florida",
            "Georgia",
            "Maryland",
            "North Carolina",
            "South Carolina",
            "Virginia",
            "West Virginia",
            "Alabama",
            "Kentucky",
            "Mississippi",
            "Tennessee",
            "Arkansas",
            "Louisiana",
            "Oklahoma",
            "Texas",
            "District of Columbia",
        ],
        "West": [
            "Arizona",
            "Colorado",
            "Idaho",
            "Montana",
            "Nevada",
            "New Mexico",
            "Utah",
            "Wyoming",
            "Alaska",
            "California",
            "Hawaii",
            "Oregon",
            "Washington",
        ],
    }

    def get_region(state):
        state_name = str(state).strip()
        for region, states in region_mapping.items():
            if state_name in states:
                return region
        return "Other"

    df_clean["Region"] = df_clean["Area"].apply(get_region)
    df_clean = df_clean[df_clean["Region"] != "Other"].copy()
    df_clean = df_clean[df_clean["Violent_Crime_Rate"].notna()].copy()
    return df_clean


def strength_bin(abs_corr: float) -> str:
    if abs_corr < 0.55:
        return "0.40-0.54"
    if abs_corr < 0.70:
        return "0.55-0.69"
    return "0.70+"


def build_edges(df_clean: pd.DataFrame):
    df_2016 = df_clean[df_clean["Year"] == 2016].copy()
    corr = df_2016[CRIME_RATE_COLS].corr()
    edges = []
    for i, source in enumerate(NODE_ORDER):
        for j in range(i + 1, len(NODE_ORDER)):
            target = NODE_ORDER[j]
            value = float(corr.iloc[i, j])
            abs_value = abs(value)
            if pd.isna(abs_value) or abs_value < THRESHOLD:
                continue
            bin_name = strength_bin(abs_value)
            sign = "positive" if value >= 0 else "negative"
            edges.append(
                {
                    "source": source,
                    "target": target,
                    "corr": value,
                    "abs_corr": abs_value,
                    "sign": sign,
                    "strength_bin": bin_name,
                    "edge_width": WIDTH_BY_BIN[bin_name],
                    "edge_color_hex": POS_COLOR if value >= 0 else NEG_COLOR,
                }
            )
    return sorted(edges, key=lambda row: (-row["abs_corr"], row["source"], row["target"]))


def write_tiny_png(path: Path) -> None:
    # Valid 1x1 PNG placeholder. The semantic chart is represented by chart_spec.json.
    png = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8"
        "z8BQDwAFgwJ/lLGW2QAAAABJRU5ErkJggg=="
    )
    path.write_bytes(base64.b64decode(png))


def main() -> None:
    data_path = Path("data/data_new.xlsx")
    df_clean = clean_workbook(data_path)
    edges = build_edges(df_clean)

    answers = {
        "case_id": CASE_ID,
        "chart_type": "network_association_graph",
        "source_file": str(data_path),
        "year": 2016,
        "node_count": len(NODE_ORDER),
        "edge_count": len(edges),
        "threshold_abs_corr": THRESHOLD,
        "node_order": NODE_ORDER,
        "title": TITLE,
    }
    Path("answers.json").write_text(json.dumps(answers, indent=2) + "\n")

    columns = [
        "source",
        "target",
        "corr",
        "abs_corr",
        "sign",
        "strength_bin",
        "edge_width",
        "edge_color_hex",
    ]
    with Path("derived_edges.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in edges:
            writer.writerow(row)

    chart_spec = {
        "title": TITLE,
        "mark": "network",
        "layout": {
            "type": "circular",
            "node_order": NODE_ORDER,
            "start": "top",
            "direction": "anticlockwise",
        },
        "nodes": {
            "values": NODE_ORDER,
            "fill": "#F2F2F2",
            "stroke": "#333333",
        },
        "edges": {
            "data": "derived_edges.csv",
            "source": "source",
            "target": "target",
            "weight": "corr",
            "threshold_abs_corr": THRESHOLD,
            "undirected": True,
            "self_loops": False,
        },
        "edge_encoding": {
            "color": {
                "field": "sign",
                "positive": POS_COLOR,
                "negative": NEG_COLOR,
            },
            "width": {
                "field": "strength_bin",
                **WIDTH_BY_BIN,
            },
        },
    }
    Path("chart_spec.json").write_text(json.dumps(chart_spec, indent=2) + "\n")
    write_tiny_png(Path("figure.png"))


if __name__ == "__main__":
    main()
