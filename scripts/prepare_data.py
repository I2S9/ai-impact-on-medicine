"""Prepare the data behind the charts of "AI at the Doctor's".

Input : data/raw/fda_ai_devices_2026-06-29.csv
        FDA list of AI-enabled medical devices (snapshot of 29 June 2026),
        as published in Wang et al. (2026), "Clinical-function annotations for
        1524 US artificial intelligence medical-device authorizations", v1.3.0,
        CC BY 4.0 - https://github.com/wang177777/fda-ai-clinical-function-annotations

Output: data/chart-data.js  (window.CHART_DATA = {...}, loaded by js/charts.js)

Run from the repository root:
    python scripts/prepare_data.py
"""

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "fda_ai_devices_2026-06-29.csv"
OUT = ROOT / "data" / "chart-data.js"

# The three largest FDA specialty panels get their own colour; the rest is "Other".
MAIN_GROUPS = ["Radiology", "Cardiovascular", "Neurology"]
PATHWAYS = {"510k": "510(k)", "de_novo": "De Novo", "pma": "PMA"}
LAST_FULL_YEAR = 2025


def load():
    df = pd.read_csv(RAW, parse_dates=["date_of_final_decision"])
    # Fix a spelling error present in the original FDA file.
    df["medical_specialty"] = df["medical_specialty"].replace(
        {"Clinical Toxcicology": "Clinical Toxicology"}
    )
    df["year"] = df["date_of_final_decision"].dt.year
    df["group"] = df["medical_specialty"].where(
        df["medical_specialty"].isin(MAIN_GROUPS), "Other"
    )
    df["pathway"] = df["regulatory_pathway"].map(PATHWAYS)
    return df


def per_year(df):
    """Bar chart: authorizations per year."""
    years = range(2012, int(df["year"].max()) + 1)
    counts = df["year"].value_counts()
    return [
        {"year": y, "count": int(counts.get(y, 0)), "partial": y > LAST_FULL_YEAR}
        for y in years
    ]


def top_specialties(df, n):
    return df["medical_specialty"].value_counts().head(n).index.tolist()


def grouped(df):
    """Grouped bar chart: top 5 specialties, last three full years."""
    years = [LAST_FULL_YEAR - 2, LAST_FULL_YEAR - 1, LAST_FULL_YEAR]
    rows = []
    for spec in top_specialties(df, 5):
        sub = df[df["medical_specialty"] == spec]
        for y in years:
            rows.append({"specialty": spec, "year": str(y), "count": int((sub["year"] == y).sum())})
    return {"years": [str(y) for y in years], "rows": rows}


def heatmap(df):
    """Heatmap: specialty x year (top 7 specialties + Other)."""
    years = list(range(2016, int(df["year"].max()) + 1))
    top = top_specialties(df, 7)
    d = df[df["year"].isin(years)].copy()
    d["row"] = d["medical_specialty"].where(d["medical_specialty"].isin(top), "Other")
    table = d.groupby(["row", "year"]).size()
    rows = top + ["Other"]
    cells = [
        {"specialty": r, "year": y, "count": int(table.get((r, y), 0))}
        for r in rows
        for y in years
    ]
    return {"rows": rows, "years": years, "cells": cells}


def pathway_share(df):
    """100% stacked bar chart: regulatory pathway within each specialty."""
    top = top_specialties(df, 6)
    d = df.copy()
    d["row"] = d["medical_specialty"].where(d["medical_specialty"].isin(top), "Other")
    rows = []
    for spec in top + ["Other"]:
        sub = d[d["row"] == spec]
        total = len(sub)
        counts = {p: int((sub["pathway"] == p).sum()) for p in PATHWAYS.values()}
        rows.append({"specialty": spec, "total": total, **counts})
    return {"keys": list(PATHWAYS.values()), "rows": rows}


def waffle(df):
    """Waffle chart: 100 squares split by specialty (largest-remainder rounding)."""
    shares = df["group"].value_counts(normalize=True) * 100
    order = MAIN_GROUPS + ["Other"]
    exact = {g: float(shares.get(g, 0)) for g in order}
    squares = {g: int(v) for g, v in exact.items()}
    left = 100 - sum(squares.values())
    for g in sorted(order, key=lambda g: exact[g] - squares[g], reverse=True)[:left]:
        squares[g] += 1
    counts = df["group"].value_counts()
    return [
        {"group": g, "squares": squares[g], "count": int(counts.get(g, 0)), "share": round(exact[g], 1)}
        for g in order
    ]


def devices(df):
    """Radial year clock: one record per device decided since 2016."""
    d = df[df["year"] >= 2016].sort_values("date_of_final_decision")
    return [
        [r.date_of_final_decision.strftime("%Y-%m-%d"), r.group, r.device_name, r.company, r.medical_specialty]
        for r in d.itertuples()
    ]


def summary(df):
    total = len(df)
    return {
        "total": total,
        "radiologyShare": round((df["medical_specialty"] == "Radiology").mean() * 100, 1),
        "pathway510kShare": round((df["pathway"] == "510(k)").mean() * 100, 1),
        "count2025": int((df["year"] == 2025).sum()),
        "count2020": int((df["year"] == 2020).sum()),
        "lastDecision": df["date_of_final_decision"].max().strftime("%Y-%m-%d"),
        "snapshot": "2026-06-29",
    }


def main():
    df = load()
    data = {
        "summary": summary(df),
        "perYear": per_year(df),
        "grouped": grouped(df),
        "heatmap": heatmap(df),
        "pathway": pathway_share(df),
        "waffle": waffle(df),
        "devices": devices(df),
    }
    js = "// Generated by scripts/prepare_data.py - do not edit by hand.\n"
    js += "window.CHART_DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n"
    OUT.write_text(js, encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)} ({len(df)} devices)")
    print(json.dumps(data["summary"], indent=2))


if __name__ == "__main__":
    main()
