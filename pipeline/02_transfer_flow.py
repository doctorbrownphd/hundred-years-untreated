#!/usr/bin/env python3
"""
02_transfer_flow.py — The Untreated · Transfer Flow
Models where the deinstitutionalized population went.
Five receiving systems: jails/prisons, homelessness, nursing homes, ERs, community (unsupported).
Sources: TAC, SAMHSA, HUD PIT counts, DOJ, NAMI.
Output: pipeline/output/transfer_data.json
"""

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
OUTPUT = BASE / "output"
OUTPUT.mkdir(parents=True, exist_ok=True)


def main():
    # The ~521,000 "missing" beds represent people who would have been
    # institutionalized under 1955 ratios but are now in other systems.
    missing_beds = 558922 - 37650  # 521,272

    systems = [
        {
            "id": "jails_prisons",
            "name": "Jails & Prisons",
            "icon": "bars",
            "estimated_smi": 383000,
            "share_pct": 35,
            "description": "An estimated 383,000 people with serious mental illness are incarcerated — roughly 10x the number in state psychiatric hospitals.",
            "key_stat": "10x more SMI in jails than hospitals",
            "source": "Treatment Advocacy Center (2014); DOJ Bureau of Justice Statistics",
            "color": "#C0392B",
            "details": {
                "state_prisons_smi_pct": 37,
                "local_jails_smi_pct": 44,
                "median_wait_competency": "114 days",
            }
        },
        {
            "id": "homelessness",
            "name": "Homelessness",
            "icon": "tent",
            "estimated_smi": 172000,
            "share_pct": 20,
            "description": "Roughly one-third of the 653,000 people experiencing homelessness on any given night have a serious mental illness.",
            "key_stat": "1 in 3 homeless have SMI",
            "source": "HUD 2024 Annual Homeless Assessment; SAMHSA",
            "color": "#E67E22",
            "details": {
                "total_homeless_2024": 653104,
                "smi_share": 0.33,
                "unsheltered_smi_pct": 39,
            }
        },
        {
            "id": "nursing_homes",
            "name": "Nursing Homes",
            "icon": "building",
            "estimated_smi": 200000,
            "share_pct": 15,
            "description": "IMD exclusion pushed patients into nursing homes. An estimated 200,000 nursing home residents have SMI as a primary diagnosis.",
            "key_stat": "200,000 SMI in nursing homes",
            "source": "CMS Minimum Data Set; Mechanic & Rochefort (1990)",
            "color": "#8E44AD",
            "details": {
                "total_nursing_home_residents": 1300000,
                "smi_primary_pct": 15,
            }
        },
        {
            "id": "emergency_rooms",
            "name": "Emergency Rooms",
            "icon": "hospital",
            "estimated_annual_visits": 12000000,
            "share_pct": 15,
            "description": "12 million psychiatric ER visits per year. Average boarding time: 8+ hours. ERs have become de facto psychiatric holding facilities.",
            "key_stat": "12M psychiatric ER visits/year",
            "source": "ACEP; Owens et al. (2017); SAMHSA",
            "color": "#E74C3C",
            "details": {
                "avg_boarding_hours": 8,
                "pct_er_visits_psychiatric": 5,
                "repeat_visit_rate": 0.40,
            }
        },
        {
            "id": "community_unsupported",
            "name": "Community (Unsupported)",
            "icon": "home",
            "estimated_smi": 5000000,
            "share_pct": 15,
            "description": "~5 million adults with SMI receive no treatment. Many cycle through ERs, jails, and shelters. The 'treatment gap' averages 11 years.",
            "key_stat": "11-year average treatment gap",
            "source": "NAMI; SAMHSA National Survey on Drug Use and Health",
            "color": "#95A5A6",
            "details": {
                "smi_no_treatment_pct": 40,
                "avg_treatment_gap_years": 11,
                "total_smi_adults": 14200000,
            }
        },
    ]

    output = {
        "title": "The Transfer",
        "subtitle": "Where did the deinstitutionalized go?",
        "beds_lost": missing_beds,
        "peak_year": 1955,
        "peak_beds": 558922,
        "current_beds": 37650,
        "systems": systems,
        "summary_stats": {
            "smi_in_jails_vs_hospitals": "10:1",
            "total_smi_adults": 14200000,
            "receiving_no_treatment": 5000000,
            "treatment_gap_years": 11,
        }
    }

    path = OUTPUT / "transfer_data.json"
    with open(path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"[transfer] 5 receiving systems modeled")
    print(f"[transfer] → {path}")


if __name__ == "__main__":
    main()
