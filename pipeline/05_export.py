#!/usr/bin/env python3
"""
05_export.py — The Untreated · Meta Export
Combines all pipeline outputs into a single meta.json for the site.
Output: pipeline/output/meta.json + site/meta.json
"""

import json
import shutil
from pathlib import Path

BASE = Path(__file__).resolve().parent
OUTPUT = BASE / "output"
SITE = BASE.parent / "site"


def main():
    beds = json.load(open(OUTPUT / "beds_data.json"))
    transfer = json.load(open(OUTPUT / "transfer_data.json"))
    cost = json.load(open(OUTPUT / "cost_data.json"))
    encounter = json.load(open(OUTPUT / "encounter_data.json"))

    meta = {
        "project": "The Untreated",
        "series": "One Hundred Years",
        "report_number": "06 / 10",
        "window": "1900 — 2024",
        "generated": "2026-05-21",
        "tabs": [
            {"id": "beds", "file": "index.html", "label": "The Beds"},
            {"id": "transfer", "file": "transfer.html", "label": "Transfer"},
            {"id": "geography", "file": "geography.html", "label": "Geography"},
            {"id": "cost", "file": "cost.html", "label": "The Cost"},
            {"id": "encounter", "file": "encounter.html", "label": "Encounter"},
            {"id": "pipeline", "file": "pipeline.html", "label": "Pipeline"},
            {"id": "method", "file": "method.html", "label": "Method"},
        ],
        "headline_stats": {
            "peak_beds": 558922,
            "peak_year": 1955,
            "current_beds": 37650,
            "current_year": 2024,
            "decline_pct": beds["stats"]["decline_percent"],
            "incarcerated_smi": 383000,
            "smi_adults": 14200000,
            "untreated_smi": 5000000,
            "treatment_gap_years": 11,
            "sixteen_x": 16,
            "cost_ratio": "19:1",
        },
        "data": {
            "beds": beds,
            "transfer": transfer,
            "cost": cost,
            "encounter": encounter,
        },
        "confidence": {
            "beds_1955_peak": {"level": "high", "note": "Multiple corroborating sources"},
            "incarceration_rates": {"level": "high", "note": "BJS official statistics"},
            "smi_in_jails": {"level": "high", "note": "DOJ surveys + TAC analysis"},
            "cost_figures": {"level": "candidate", "note": "Ranges vary by state; national averages"},
            "16x_encounter": {"level": "candidate", "note": "TAC 2015 study; methodology debated"},
            "homelessness_smi": {"level": "candidate", "note": "PIT counts undercount; definitions vary"},
        }
    }

    # Write to pipeline/output
    path = OUTPUT / "meta.json"
    with open(path, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"[export] → {path}")

    # Copy to site/
    SITE.mkdir(parents=True, exist_ok=True)
    site_path = SITE / "meta.json"
    shutil.copy2(path, site_path)
    print(f"[export] → {site_path}")
    print(f"[export] {len(meta['tabs'])} tabs, {len(meta['headline_stats'])} headline stats")


if __name__ == "__main__":
    main()
