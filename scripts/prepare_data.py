"""Prepare the data behind the charts of "AI at the Doctor's".

Input : data/raw/fda_ai_devices_2026-06-29.csv
        FDA list of AI-enabled medical devices (snapshot of 29 June 2026),
        as published in Wang et al. (2026), "Clinical-function annotations for
        1524 US artificial intelligence medical-device authorizations", v1.3.0,
        CC BY 4.0 - https://github.com/wang177777/fda-ai-clinical-function-annotations
        data/raw/fda_ai_output_labels_v1.3.0.csv
        What each device produces (output labels of the same release, one row
        per device and label; a device can have several labels).

Output: data/chart-data.js  (window.CHART_DATA = {...}, loaded by js/charts.js)

Run from the repository root:
    python scripts/prepare_data.py
"""

import json
import math
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "fda_ai_devices_2026-06-29.csv"
LABELS = ROOT / "data" / "raw" / "fda_ai_output_labels_v1.3.0.csv"
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


# ---------- Section 2: time and distribution ----------

def decimal_year(dates):
    """Date -> year as a decimal number (2024-07-01 -> about 2024.5)."""
    start = pd.to_datetime(dates.dt.year.astype(str) + "-01-01")
    days = dates.dt.is_leap_year.map({True: 366, False: 365})
    return dates.dt.year + (dates - start).dt.days / days


def cumulative(df):
    """Line chart: cumulative authorizations per group, quarter by quarter."""
    order = MAIN_GROUPS + ["Other"]
    d = df.assign(q=df["date_of_final_decision"].dt.to_period("Q"))
    quarters = pd.period_range("2012Q1", d["q"].max(), freq="Q")
    series = []
    for g in order:
        sub = d[d["group"] == g]
        before = int((sub["q"] < quarters[0]).sum())
        counts = sub["q"].value_counts()
        total = before
        values = []
        for q in quarters:
            total += int(counts.get(q, 0))
            values.append(total)
        series.append({"group": g, "values": values})
    # Each point is placed at the end of its quarter.
    dates = [q.end_time.strftime("%Y-%m-%d") for q in quarters]
    return {"dates": dates, "series": series}


OUTPUT_NAMES = {
    "SEGMENTATION_OR_LOCALIZATION": "Segmentation or localization",
    "MEASUREMENT_OR_QUANTIFICATION": "Measurement or quantification",
    "DETECTION_OR_ALERT": "Detection or alert",
    "RECONSTRUCTION_OR_ENHANCEMENT": "Image reconstruction or enhancement",
    "CLASSIFICATION_OR_DIAGNOSIS": "Classification or diagnosis",
    "DOCUMENTATION_OR_SUMMARY": "Documentation or summary",
}


def functions(df):
    """Small multiple line charts: what devices produce, year by year."""
    labels = pd.read_csv(LABELS)
    years = list(range(2016, LAST_FULL_YEAR + 1))
    d = labels.merge(df[["submission_number", "year"]], on="submission_number")
    d = d[d["year"].isin(years)]
    annotated = d.groupby("year")["submission_number"].nunique()
    panels = []
    for code, name in OUTPUT_NAMES.items():
        counts = d[d["label"] == code].groupby("year").size()
        panels.append({
            "label": name,
            "values": [int(counts.get(y, 0)) for y in years],
            "total": int(counts.sum()),
        })
    panels.sort(key=lambda p: -p["total"])
    return {
        "years": years,
        "annotated": [int(annotated.get(y, 0)) for y in years],
        "devicesAnnotated": int(labels["submission_number"].nunique()),
        "panels": panels,
    }


# Large manufacturers appear under several legal names (one per subsidiary).
BRANDS = [
    (r"^SIEMENS", "Siemens Healthineers"),
    (r"^(GE |GE$|GENERAL ELECTRIC)", "GE HealthCare"),
    (r"PHILIPS", "Philips"),
    (r"^(CANON|TOSHIBA)", "Canon Medical"),
    (r"UNITED IMAGING", "United Imaging"),
    (r"^SAMSUNG", "Samsung"),
    (r"^FUJIFILM", "Fujifilm"),
    (r"^HOLOGIC", "Hologic"),
    (r"^AIDOC", "Aidoc"),
    (r"^VIZ\.AI", "Viz.ai"),
    (r"^QURE\.AI", "Qure.ai"),
    (r"^ISCHEMAVIEW", "iSchemaView (RapidAI)"),
    (r"^ICAD", "iCAD"),
    (r"^RAYSEARCH", "RaySearch Laboratories"),
    (r"^MIM SOFTWARE", "MIM Software"),
    (r"^EVER FORTUNE", "Ever Fortune.AI"),
    (r"^AVICENNA", "Avicenna.AI"),
    (r"^COSMO ARTIFICIAL INTELLIGENCE", "Cosmo AI"),
]
SUFFIXES = r"[,.]?\s+(INC|LLC|LTD|LIMITED|CORP|CORPORATION|CO|COMPANY|GMBH|AG|SA|SAS|BV|B\.V|AB|PLC|LTDA|S\.A|S\.P\.A|SRL|KK)\.?$"


def company_name(raw):
    name = " ".join(str(raw).upper().replace("\u00a0", " ").split())
    for pattern, brand in BRANDS:
        if re.search(pattern, name):
            return brand
    previous = None
    while previous != name:
        previous = name
        name = re.sub(SUFFIXES, "", name).strip(" ,.")
    return name.title()


def companies(df):
    """Box plot and jitter: number of AI devices per company, by group."""
    d = df.assign(company_clean=df["company"].map(company_name))
    rows = []
    for g in MAIN_GROUPS + ["Other"]:
        counts = d[d["group"] == g]["company_clean"].value_counts()
        for name, n in counts.items():
            rows.append([name, g, int(n)])
    total = d["company_clean"].value_counts()
    return {
        "rows": rows,
        "companyCount": int(total.size),
        "single": int((total == 1).sum()),
        "top": [[n, int(c)] for n, c in total.head(5).items()],
    }


def pathway_dates(df):
    """Jitter and box plot: decision dates within each regulatory pathway."""
    d = df.assign(t=decimal_year(df["date_of_final_decision"]))
    order = list(PATHWAYS.values())
    points = [[round(r.t, 3), order.index(r.pathway)] for r in d.itertuples()]
    return {"keys": order, "points": points}


def ridgeline(df):
    """Ridgeline: smoothed distribution of decision dates per specialty."""
    top = top_specialties(df, 7)
    d = df.assign(t=decimal_year(df["date_of_final_decision"]))
    d["row"] = d["medical_specialty"].where(d["medical_specialty"].isin(top), "Other")
    start, end, step, bandwidth = 2012.0, 2026.25, 0.125, 0.55
    grid = [round(start + i * step, 3) for i in range(int((end - start) / step) + 1)]
    rows = []
    for spec in top + ["Other"]:
        t = d.loc[d["row"] == spec, "t"].tolist()
        norm = 1 / (len(t) * bandwidth * math.sqrt(2 * math.pi))
        density = [
            norm * sum(math.exp(-0.5 * ((x - v) / bandwidth) ** 2) for v in t)
            for x in grid
        ]
        median = float(pd.Series(t).median())
        rows.append({
            "specialty": spec,
            "n": len(t),
            "median": round(median, 2),
            "density": [round(v, 4) for v in density],
        })
    return {"grid": grid, "rows": rows}


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
        "cumulative": cumulative(df),
        "functions": functions(df),
        "companies": companies(df),
        "pathwayDates": pathway_dates(df),
        "ridgeline": ridgeline(df),
    }
    js = "// Generated by scripts/prepare_data.py - do not edit by hand.\n"
    js += "window.CHART_DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n"
    OUT.write_text(js, encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)} ({len(df)} devices)")
    print(json.dumps(data["summary"], indent=2))


if __name__ == "__main__":
    main()
