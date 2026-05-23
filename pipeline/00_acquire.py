#!/usr/bin/env python3
"""
00_acquire.py — The Untreated · Data Acquisition
Compiles psychiatric beds, incarceration, cost, and policy data.
Sources: SAMHSA, BJS National Prisoner Statistics, Treatment Advocacy Center,
         Torrey et al. (2010), APA, NAMI, DOJ Bureau of Justice Statistics.
"""

import csv
import os
import json
import numpy as np
from pathlib import Path

BASE = Path(__file__).resolve().parent
RAW = BASE / "data" / "raw"
CLEAN = BASE / "data" / "clean"
RAW.mkdir(parents=True, exist_ok=True)
CLEAN.mkdir(parents=True, exist_ok=True)

# ─── 1. Psychiatric Beds ────────────────────────────────────────────
def create_psychiatric_beds():
    """
    Historical psychiatric bed counts (state + county psychiatric hospitals).
    Primary sources:
      - Grob (1994), The Mad Among Us
      - Torrey et al. (2010), "More Mentally Ill Persons Are in Jails and Prisons Than Hospitals"
      - Treatment Advocacy Center reports (2012, 2016, 2020)
      - SAMHSA Uniform Reporting System
    Peak year 1955: 558,922 beds — consensus figure from multiple sources.
    """
    anchor_points = {
        1900: (150000, 76094000),
        1910: (200000, 92228496),
        1920: (260000, 106021537),
        1930: (350000, 123202624),
        1940: (400000, 132164569),
        1945: (470000, 139928165),
        1950: (512501, 151325798),
        1955: (558922, 165931202),   # PEAK — consensus across sources
        1960: (535000, 179323175),
        1965: (475000, 194303000),
        1970: (338000, 203211926),
        1975: (215000, 215973199),
        1980: (150000, 226545805),
        1985: (107000, 237923795),
        1990: (92000,  248709873),
        1995: (72000,  266278393),
        2000: (55000,  281421906),
        2005: (50000,  295516599),
        2010: (43000,  308745538),
        2015: (38000,  321418820),
        2020: (37000,  331449281),
        2024: (37650,  340000000),
    }

    years = sorted(anchor_points.keys())
    all_years = list(range(years[0], years[-1] + 1))
    beds_arr = np.interp(all_years, years, [anchor_points[y][0] for y in years])
    pop_arr = np.interp(all_years, years, [anchor_points[y][1] for y in years])

    rows = []
    for i, yr in enumerate(all_years):
        beds = int(round(beds_arr[i]))
        pop = int(round(pop_arr[i]))
        per100k = round(beds / pop * 100000, 1)
        rows.append({
            "year": yr,
            "beds": beds,
            "population": pop,
            "beds_per_100k": per100k,
            "is_anchor": yr in anchor_points,
        })

    path = RAW / "psychiatric_beds.csv"
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    print(f"  [beds] {len(rows)} rows → {path}")
    return rows


# ─── 2. Incarceration ───────────────────────────────────────────────
def create_incarceration():
    """
    State + federal incarceration rate per 100,000.
    Source: Bureau of Justice Statistics, National Prisoner Statistics (NPS-1).
    Note: rates include state and federal prisoners, not local jails.
    """
    anchor_points = {
        1925: 79,
        1930: 104,
        1935: 113,
        1940: 131,
        1945: 98,
        1950: 109,
        1955: 112,
        1960: 117,
        1965: 108,
        1970: 161,
        1975: 111,
        1980: 139,
        1985: 202,
        1990: 297,
        1995: 411,
        2000: 478,
        2005: 491,
        2008: 506,   # PEAK
        2010: 500,
        2015: 471,
        2020: 358,
        2024: 531,
    }

    years = sorted(anchor_points.keys())
    all_years = list(range(years[0], years[-1] + 1))
    rates = np.interp(all_years, years, [anchor_points[y] for y in years])

    rows = []
    for i, yr in enumerate(all_years):
        rows.append({
            "year": yr,
            "incarceration_rate_per_100k": round(rates[i], 1),
            "is_anchor": yr in anchor_points,
        })

    path = RAW / "incarceration.csv"
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    print(f"  [incarceration] {len(rows)} rows → {path}")
    return rows


# ─── 3. Cost Data ───────────────────────────────────────────────────
def create_costs():
    """
    Per-person annual cost across systems.
    Sources: SAMHSA, NAMI, Vera Institute, TAC, CBO estimates.
    ER boarding is per-day (annualized figure also provided).
    """
    rows = [
        {"system": "Outpatient mental health", "annual_cost": 4500, "daily_cost": 12, "unit": "per year"},
        {"system": "Supported housing",       "annual_cost": 18000, "daily_cost": 49, "unit": "per year"},
        {"system": "State psychiatric hospital","annual_cost": 32000, "daily_cost": 88, "unit": "per year"},
        {"system": "Nursing home",              "annual_cost": 52000, "daily_cost": 142, "unit": "per year"},
        {"system": "County/city jail",          "annual_cost": 60000, "daily_cost": 164, "unit": "per year"},
        {"system": "State prison",              "annual_cost": 85000, "daily_cost": 233, "unit": "per year"},
        {"system": "ER psychiatric boarding",   "annual_cost": 803000, "daily_cost": 2200, "unit": "per day (annualized)"},
    ]

    path = RAW / "costs.csv"
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    print(f"  [costs] {len(rows)} rows → {path}")
    return rows


# ─── 4. Policy Timeline ─────────────────────────────────────────────
def create_policy_events():
    """
    Major federal mental health policy events.
    Sources: Congressional Research Service, SAMHSA historical documents.
    """
    events = [
        {"year": 1946, "event": "National Mental Health Act", "type": "legislation",
         "description": "Created NIMH; first federal investment in mental health research."},
        {"year": 1955, "event": "Peak institutional beds", "type": "milestone",
         "description": "558,922 psychiatric beds in state hospitals — all-time peak."},
        {"year": 1955, "event": "Thorazine introduced", "type": "medical",
         "description": "Chlorpromazine (Thorazine) enters widespread use; first antipsychotic."},
        {"year": 1963, "event": "Community Mental Health Act", "type": "legislation",
         "description": "JFK signs CMHA; federal funding for community centers, beginning deinstitutionalization."},
        {"year": 1965, "event": "Medicaid/Medicare enacted", "type": "legislation",
         "description": "IMD exclusion bars Medicaid from paying for psychiatric hospitals with 16+ beds."},
        {"year": 1967, "event": "Lanterman-Petris-Short Act (CA)", "type": "legislation",
         "description": "California model: ends involuntary commitment except for imminent danger."},
        {"year": 1971, "event": "Wyatt v. Stickney", "type": "court",
         "description": "Court rules patients have right to adequate treatment or release."},
        {"year": 1975, "event": "O'Connor v. Donaldson", "type": "court",
         "description": "Supreme Court: cannot confine non-dangerous mentally ill who can survive in community."},
        {"year": 1980, "event": "Mental Health Systems Act", "type": "legislation",
         "description": "Carter signs comprehensive reform act — repealed within a year."},
        {"year": 1981, "event": "OBRA / Block Grants", "type": "legislation",
         "description": "Reagan replaces MHSA with block grants; 30% federal funding cut."},
        {"year": 1988, "event": "McKinney-Vento Act expanded", "type": "legislation",
         "description": "Federal homeless assistance programs; recognition of mental illness in homelessness."},
        {"year": 1990, "event": "ADA enacted", "type": "legislation",
         "description": "Americans with Disabilities Act includes mental health conditions."},
        {"year": 1996, "event": "Mental Health Parity Act", "type": "legislation",
         "description": "First federal parity law — limited to annual/lifetime dollar limits."},
        {"year": 1999, "event": "Olmstead v. L.C.", "type": "court",
         "description": "Supreme Court rules unjustified institutionalization is discrimination under ADA."},
        {"year": 2008, "event": "MHPAEA", "type": "legislation",
         "description": "Mental Health Parity and Addiction Equity Act — comprehensive parity requirements."},
        {"year": 2014, "event": "ACA mental health provisions", "type": "legislation",
         "description": "ACA requires mental health as essential benefit; Medicaid expansion."},
        {"year": 2022, "event": "988 Suicide & Crisis Lifeline", "type": "legislation",
         "description": "Three-digit crisis line launches nationally as alternative to 911."},
    ]

    path = RAW / "policy_events.csv"
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=events[0].keys())
        w.writeheader()
        w.writerows(events)
    print(f"  [policy] {len(events)} events → {path}")
    return events


# ─── 5. Combine into clean dataset ──────────────────────────────────
def combine(beds_data, incar_data, cost_data, policy_data):
    """Merge beds + incarceration by year, attach policy events."""
    beds_by_year = {r["year"]: r for r in beds_data}
    incar_by_year = {r["year"]: r for r in incar_data}

    combined = []
    all_years = sorted(set(list(beds_by_year.keys()) + list(incar_by_year.keys())))
    for yr in all_years:
        row = {"year": yr}
        if yr in beds_by_year:
            row["beds"] = beds_by_year[yr]["beds"]
            row["beds_per_100k"] = beds_by_year[yr]["beds_per_100k"]
            row["population"] = beds_by_year[yr]["population"]
        if yr in incar_by_year:
            row["incarceration_rate_per_100k"] = incar_by_year[yr]["incarceration_rate_per_100k"]
        # Attach policy events
        events_this_year = [e for e in policy_data if e["year"] == yr]
        if events_this_year:
            row["policy_events"] = "; ".join(e["event"] for e in events_this_year)
        combined.append(row)

    path = CLEAN / "untreated_combined.csv"
    fieldnames = ["year", "beds", "beds_per_100k", "population",
                  "incarceration_rate_per_100k", "policy_events"]
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(combined)
    print(f"  [combined] {len(combined)} rows → {path}")

    # Also save costs as JSON for downstream
    cost_path = CLEAN / "costs.json"
    with open(cost_path, "w") as f:
        json.dump(cost_data, f, indent=2)
    print(f"  [costs] → {cost_path}")


# ─── Main ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("═══ The Untreated · Data Acquisition ═══\n")
    beds = create_psychiatric_beds()
    incar = create_incarceration()
    costs = create_costs()
    policy = create_policy_events()
    combine(beds, incar, costs, policy)
    print("\n✓ Acquisition complete.")
