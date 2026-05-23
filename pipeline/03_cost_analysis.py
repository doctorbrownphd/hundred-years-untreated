#!/usr/bin/env python3
"""
03_cost_analysis.py — The Untreated · Cost Comparison
Cost per person across treatment and non-treatment systems.
Sources: SAMHSA, Vera Institute, TAC, NAMI, CBO.
Output: pipeline/output/cost_data.json
"""

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
OUTPUT = BASE / "output"
OUTPUT.mkdir(parents=True, exist_ok=True)


def main():
    systems = [
        {
            "name": "Outpatient Mental Health",
            "annual_cost": 4500,
            "category": "treatment",
            "color": "#4A90D9",
            "description": "Community-based outpatient care including therapy and medication management.",
            "effectiveness": "Most cost-effective for mild-to-moderate SMI",
        },
        {
            "name": "Supported Housing",
            "annual_cost": 18000,
            "category": "treatment",
            "color": "#5DADE2",
            "description": "Housing with wraparound mental health services.",
            "effectiveness": "Reduces hospitalization by 58%, incarceration by 40%",
        },
        {
            "name": "State Psychiatric Hospital",
            "annual_cost": 32000,
            "category": "treatment",
            "color": "#2E86C1",
            "description": "Inpatient psychiatric care in state-run facilities.",
            "effectiveness": "Necessary for acute and long-term severe cases",
        },
        {
            "name": "Nursing Home",
            "annual_cost": 52000,
            "category": "warehousing",
            "color": "#8E44AD",
            "description": "Long-term care facilities housing SMI patients, often inappropriately.",
            "effectiveness": "Not designed for psychiatric care; poor outcomes",
        },
        {
            "name": "County/City Jail",
            "annual_cost": 60000,
            "category": "incarceration",
            "color": "#E67E22",
            "description": "Local jails where 44% of inmates have diagnosed mental illness.",
            "effectiveness": "No therapeutic value; high recidivism",
        },
        {
            "name": "State Prison",
            "annual_cost": 85000,
            "category": "incarceration",
            "color": "#C0392B",
            "description": "State prisons where 37% of inmates have mental health conditions.",
            "effectiveness": "19x cost of outpatient treatment; minimal psychiatric care",
        },
        {
            "name": "ER Psychiatric Boarding",
            "annual_cost": 803000,
            "daily_cost": 2200,
            "category": "crisis",
            "color": "#E74C3C",
            "description": "Psychiatric patients held in ERs awaiting bed placement. Average stay: 8+ hours, some days.",
            "effectiveness": "Most expensive per-day option; no treatment value",
        },
    ]

    # Cost multipliers relative to outpatient
    for s in systems:
        s["multiplier_vs_outpatient"] = round(s["annual_cost"] / 4500, 1)

    # System-level spending estimates
    spending = {
        "criminal_justice_smi_annual": 15000000000,  # $15B
        "er_psychiatric_annual": 8400000000,          # $8.4B
        "medicaid_smi_annual": 68000000000,          # $68B
        "community_mh_federal": 5500000000,          # $5.5B
        "note": "Criminal justice costs for SMI exceed community mental health spending by ~3:1"
    }

    output = {
        "title": "The Cost",
        "subtitle": "What America pays per person, per system",
        "systems": systems,
        "spending_estimates": spending,
        "key_finding": "America spends 19x more to incarcerate a person with SMI than to treat them in the community.",
        "stats": {
            "outpatient_cost": 4500,
            "prison_cost": 85000,
            "cost_ratio": "19:1",
            "er_daily": 2200,
        }
    }

    path = OUTPUT / "cost_data.json"
    with open(path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"[cost] {len(systems)} systems compared")
    print(f"[cost] prison/outpatient ratio: 19:1")
    print(f"[cost] → {path}")


if __name__ == "__main__":
    main()
