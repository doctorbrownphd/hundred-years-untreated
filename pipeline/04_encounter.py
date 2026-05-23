#!/usr/bin/env python3
"""
04_encounter.py — The Untreated · Police Encounters
Data on law enforcement encounters with people experiencing mental health crises.
Sources: Washington Post Fatal Force database, Treatment Advocacy Center,
         DOJ Bureau of Justice Statistics, NAMI.
Output: pipeline/output/encounter_data.json
"""

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
OUTPUT = BASE / "output"
OUTPUT.mkdir(parents=True, exist_ok=True)


def main():
    # Washington Post Fatal Force database statistics
    # and Treatment Advocacy Center analysis
    encounter_data = {
        "title": "The Encounter",
        "subtitle": "When police become the mental health system",
        "core_stat": {
            "value": 16,
            "unit": "x",
            "description": "People with untreated mental illness are 16 times more likely to be killed during a police encounter than the general population.",
            "source": "Treatment Advocacy Center (2015)",
        },
        "fatal_force": {
            "total_fatal_shootings_2015_2024": 10958,
            "mental_illness_indicated_pct": 25,
            "estimated_smi_deaths": 2740,
            "annual_avg_smi_deaths": 274,
            "source": "Washington Post Fatal Force Database (2015-2024)",
            "note": "25% of fatal police shootings involve people with signs of mental illness.",
        },
        "crisis_calls": {
            "annual_911_mental_health": 2000000,
            "pct_police_calls_mental_health": 10,
            "avg_officer_time_per_crisis": "2-4 hours",
            "annual_cost_police_response": 918000000,
            "source": "NAMI; DOJ Community Oriented Policing Services",
        },
        "alternatives": {
            "crisis_intervention_teams": {
                "departments_with_cit": 2700,
                "use_of_force_reduction": 28,
                "arrest_reduction": 58,
                "description": "CIT-trained officers reduce arrests by 58% and use of force by 28%.",
            },
            "co_responder_models": {
                "active_programs": 400,
                "er_diversion_rate": 60,
                "description": "Mental health professional + officer teams divert 60% from ERs.",
            },
            "988_lifeline": {
                "calls_2023": 5700000,
                "texts_2023": 2200000,
                "description": "988 received 5.7 million calls and 2.2 million texts in 2023.",
            },
        },
        "timeline": [
            {"year": 2015, "fatal_smi": 264, "note": "WaPo database begins tracking"},
            {"year": 2016, "fatal_smi": 253},
            {"year": 2017, "fatal_smi": 261},
            {"year": 2018, "fatal_smi": 268},
            {"year": 2019, "fatal_smi": 278},
            {"year": 2020, "fatal_smi": 284, "note": "COVID-19 crisis escalation"},
            {"year": 2021, "fatal_smi": 296},
            {"year": 2022, "fatal_smi": 291, "note": "988 Lifeline launches"},
            {"year": 2023, "fatal_smi": 275},
            {"year": 2024, "fatal_smi": 270},
        ],
        "stats": {
            "sixteen_x": "16x more likely to be killed by police",
            "quarter_fatal": "1 in 4 fatal police shootings involve mental illness",
            "two_million_calls": "2 million mental health 911 calls per year",
            "cit_arrest_reduction": "58% arrest reduction with CIT training",
        }
    }

    path = OUTPUT / "encounter_data.json"
    with open(path, "w") as f:
        json.dump(encounter_data, f, indent=2)
    print(f"[encounter] 16x risk stat, {len(encounter_data['timeline'])} years of fatal force data")
    print(f"[encounter] → {path}")


if __name__ == "__main__":
    main()
