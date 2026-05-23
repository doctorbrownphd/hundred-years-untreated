#!/usr/bin/env python3
"""
01_beds_analysis.py — The Untreated · Beds/Incarceration Crossover
Produces the scissors chart data: beds declining, incarceration rising.
Identifies the crossover year and annotates policy events.
Output: pipeline/output/beds_data.json
"""

import csv
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
CLEAN = BASE / "data" / "clean"
RAW = BASE / "data" / "raw"
OUTPUT = BASE / "output"
OUTPUT.mkdir(parents=True, exist_ok=True)


def load_combined():
    rows = []
    with open(CLEAN / "untreated_combined.csv") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows


def load_policy():
    events = []
    with open(RAW / "policy_events.csv") as f:
        for r in csv.DictReader(f):
            r["year"] = int(r["year"])
            events.append(r)
    return events


def find_crossover(data):
    """Find year where incarceration rate exceeds beds per 100k."""
    for row in data:
        beds = row.get("beds_per_100k")
        incar = row.get("incarceration_rate_per_100k")
        if beds and incar and float(incar) >= float(beds):
            return int(row["year"])
    return None


def main():
    combined = load_combined()
    policy = load_policy()

    # Build time series for chart
    series_beds = []
    series_incar = []
    for row in combined:
        yr = int(row["year"])
        if row.get("beds_per_100k"):
            series_beds.append({"year": yr, "value": float(row["beds_per_100k"])})
        if row.get("incarceration_rate_per_100k"):
            series_incar.append({"year": yr, "value": float(row["incarceration_rate_per_100k"])})

    crossover_year = find_crossover(combined)

    # Key statistics
    peak_beds = max(series_beds, key=lambda x: x["value"])
    current_beds = series_beds[-1]
    decline_pct = round((1 - current_beds["value"] / peak_beds["value"]) * 100, 1)

    peak_incar = max(series_incar, key=lambda x: x["value"])

    output = {
        "title": "The Beds",
        "subtitle": "Psychiatric beds vs. incarceration rate, 1900-2024",
        "series": {
            "beds_per_100k": series_beds,
            "incarceration_per_100k": series_incar,
        },
        "crossover_year": crossover_year,
        "annotations": {
            "peak_beds": {
                "year": peak_beds["year"],
                "value": peak_beds["value"],
                "label": f"Peak: {peak_beds['value']}/100k ({peak_beds['year']})"
            },
            "current_beds": {
                "year": current_beds["year"],
                "value": current_beds["value"],
                "label": f"Today: {current_beds['value']}/100k"
            },
            "decline": f"{decline_pct}% decline",
            "peak_incarceration": {
                "year": peak_incar["year"],
                "value": peak_incar["value"],
                "label": f"Peak: {peak_incar['value']}/100k ({peak_incar['year']})"
            },
        },
        "policy_events": policy,
        "stats": {
            "peak_beds_total": 558922,
            "peak_beds_year": 1955,
            "current_beds_total": 37650,
            "current_beds_year": 2024,
            "decline_percent": decline_pct,
            "beds_per_100k_1955": 337,
            "beds_per_100k_2024": 11,
        }
    }

    path = OUTPUT / "beds_data.json"
    with open(path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"[beds_analysis] crossover year: {crossover_year}")
    print(f"[beds_analysis] decline: {decline_pct}%")
    print(f"[beds_analysis] → {path}")


if __name__ == "__main__":
    main()
