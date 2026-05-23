"""
06_counterfactual_ensemble.py
Extension 02 — Counterfactual Ensemble for The Untreated

What if the 1963 Community Mental Health Centers Act had been fully funded?
Generates 500 plausible alternative trajectories for beds_per_100k and
incarceration_rate_per_100k, then outputs percentile bands.

Model:
  - Intervention year: 1963 (CMHC Act signed)
  - Replacement fraction: Normal(0.7, 0.1) — 70% of closed beds replaced
  - Community ramp-up: sigmoid from 1965, reaching target by 1980
  - Per-year noise: Normal(0, 5) beds_per_100k
  - Incarceration: Penrose's Law — each 10 beds/100k lost = ~10/100k more incarcerated
"""

import csv
import json
import math
import os
import numpy as np

# ─── Config ──────────────────────────────────────────────────────
N_TRAJECTORIES = 500
INTERVENTION_YEAR = 1963
RAMP_START = 1965
RAMP_END = 1980
REPLACEMENT_MEAN = 0.70
REPLACEMENT_STD = 0.10
NOISE_STD = 5.0
PENROSE_RATIO = 1.0  # 10 beds/100k lost → 10/100k more incarcerated

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(SCRIPT_DIR, "data", "clean", "untreated_combined.csv")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
SITE_DIR = os.path.join(SCRIPT_DIR, "..", "site")

np.random.seed(42)

# ─── Load actual data ────────────────────────────────────────────
rows = []
with open(DATA_PATH, "r") as f:
    reader = csv.DictReader(f)
    for r in reader:
        row = {
            "year": int(r["year"]),
            "beds_per_100k": float(r["beds_per_100k"]),
            "incarceration_rate_per_100k": float(r["incarceration_rate_per_100k"])
                if r["incarceration_rate_per_100k"] else None,
        }
        rows.append(row)

# Build lookup
actual = {r["year"]: r for r in rows}
years = sorted(actual.keys())
min_year = min(years)
max_year = max(years)

# Find the beds_per_100k at intervention year
beds_at_intervention = actual[INTERVENTION_YEAR]["beds_per_100k"]
print(f"Beds/100k at intervention ({INTERVENTION_YEAR}): {beds_at_intervention:.1f}")

# ─── Sigmoid ramp function ───────────────────────────────────────
def sigmoid_ramp(year):
    """Returns 0→1 sigmoid ramp from RAMP_START to RAMP_END."""
    if year <= RAMP_START:
        return 0.0
    if year >= RAMP_END:
        return 1.0
    midpoint = (RAMP_START + RAMP_END) / 2
    k = 8.0 / (RAMP_END - RAMP_START)  # steepness
    return 1.0 / (1.0 + math.exp(-k * (year - midpoint)))

# ─── Generate trajectories ───────────────────────────────────────
# Post-intervention years only
post_years = [y for y in years if y >= INTERVENTION_YEAR]
pre_years = [y for y in years if y < INTERVENTION_YEAR]

all_beds_trajectories = np.zeros((N_TRAJECTORIES, len(post_years)))
all_incar_trajectories = np.zeros((N_TRAJECTORIES, len(post_years)))

for i in range(N_TRAJECTORIES):
    # Sample replacement fraction for this trajectory
    repl_frac = np.clip(np.random.normal(REPLACEMENT_MEAN, REPLACEMENT_STD), 0.3, 0.95)

    for j, yr in enumerate(post_years):
        actual_beds = actual[yr]["beds_per_100k"]
        actual_incar = actual[yr]["incarceration_rate_per_100k"]

        if yr <= INTERVENTION_YEAR:
            # At or before intervention, counterfactual = actual
            cf_beds = actual_beds
        else:
            # How many beds were lost from intervention to now
            beds_lost = beds_at_intervention - actual_beds

            # Sigmoid ramp: how much community capacity has been built
            ramp = sigmoid_ramp(yr)

            # Community replacement beds
            community_beds = beds_lost * repl_frac * ramp

            # Counterfactual beds = actual + community replacement
            cf_beds = actual_beds + community_beds

            # Add per-year noise
            noise = np.random.normal(0, NOISE_STD)
            cf_beds = max(cf_beds + noise, actual_beds)  # never below actual

        all_beds_trajectories[i, j] = cf_beds

        # Incarceration counterfactual (Penrose's Law)
        if actual_incar is not None:
            beds_diff = cf_beds - actual_beds  # how many more beds in counterfactual
            incar_reduction = beds_diff * PENROSE_RATIO * 0.1  # per 10 beds = 10 incar
            # Actually: each 1 bed/100k more → 1/100k less incarcerated
            incar_reduction = beds_diff * PENROSE_RATIO
            cf_incar = max(actual_incar - incar_reduction, 50.0)  # floor at 50
            cf_incar += np.random.normal(0, NOISE_STD * 0.5)
            cf_incar = max(cf_incar, 50.0)
        else:
            cf_incar = None

        all_incar_trajectories[i, j] = cf_incar if cf_incar is not None else 0

# ─── Compute percentile bands ────────────────────────────────────
percentiles = [5, 25, 50, 75, 95]

beds_bands = {}
incar_bands = {}

for p in percentiles:
    beds_bands[f"p{p:02d}"] = np.percentile(all_beds_trajectories, p, axis=0).tolist()
    incar_bands[f"p{p:02d}"] = np.percentile(all_incar_trajectories, p, axis=0).tolist()

# ─── Build actual series for comparison ───────────────────────────
actual_beds_series = []
actual_incar_series = []
for yr in post_years:
    actual_beds_series.append(actual[yr]["beds_per_100k"])
    actual_incar_series.append(actual[yr]["incarceration_rate_per_100k"])

# ─── Summary statistics ──────────────────────────────────────────
# At 2024: people who would be in treatment instead of prison
idx_2024 = post_years.index(2024)
pop_2024 = 340_000_000

beds_diff_median = beds_bands["p50"][idx_2024] - actual[2024]["beds_per_100k"]
beds_diff_lo = beds_bands["p05"][idx_2024] - actual[2024]["beds_per_100k"]
beds_diff_hi = beds_bands["p95"][idx_2024] - actual[2024]["beds_per_100k"]

# Convert per-100k difference to absolute people
people_treated_median = int(beds_diff_median * pop_2024 / 100_000)
people_treated_lo = int(beds_diff_lo * pop_2024 / 100_000)
people_treated_hi = int(beds_diff_hi * pop_2024 / 100_000)

incar_diff_median = actual[2024]["incarceration_rate_per_100k"] - incar_bands["p50"][idx_2024]
incar_diff_lo = actual[2024]["incarceration_rate_per_100k"] - incar_bands["p95"][idx_2024]
incar_diff_hi = actual[2024]["incarceration_rate_per_100k"] - incar_bands["p05"][idx_2024]

people_not_incarcerated_median = int(incar_diff_median * pop_2024 / 100_000)
people_not_incarcerated_lo = int(incar_diff_lo * pop_2024 / 100_000)
people_not_incarcerated_hi = int(incar_diff_hi * pop_2024 / 100_000)

summary = {
    "counterfactual_beds_2024": {
        "median": round(beds_bands["p50"][idx_2024], 1),
        "p05": round(beds_bands["p05"][idx_2024], 1),
        "p95": round(beds_bands["p95"][idx_2024], 1),
        "actual": actual[2024]["beds_per_100k"],
    },
    "counterfactual_incar_2024": {
        "median": round(incar_bands["p50"][idx_2024], 1),
        "p05": round(incar_bands["p05"][idx_2024], 1),
        "p95": round(incar_bands["p95"][idx_2024], 1),
        "actual": actual[2024]["incarceration_rate_per_100k"],
    },
    "additional_people_in_treatment": {
        "median": people_treated_median,
        "ci90": [people_treated_lo, people_treated_hi],
    },
    "fewer_people_incarcerated": {
        "median": people_not_incarcerated_median,
        "ci90": [people_not_incarcerated_lo, people_not_incarcerated_hi],
    },
    "intervention_year": INTERVENTION_YEAR,
    "n_trajectories": N_TRAJECTORIES,
    "replacement_fraction": {"mean": REPLACEMENT_MEAN, "std": REPLACEMENT_STD},
}

# ─── Build output ────────────────────────────────────────────────
output = {
    "meta": {
        "generated": "2026-05-23",
        "n_trajectories": N_TRAJECTORIES,
        "intervention_year": INTERVENTION_YEAR,
        "model": "sigmoid community ramp-up with stochastic replacement fraction",
        "noise_std": NOISE_STD,
        "replacement_fraction": {"mean": REPLACEMENT_MEAN, "std": REPLACEMENT_STD},
        "penrose_ratio": PENROSE_RATIO,
    },
    "years": post_years,
    "actual": {
        "beds_per_100k": actual_beds_series,
        "incarceration_rate_per_100k": actual_incar_series,
    },
    "counterfactual_beds": beds_bands,
    "counterfactual_incarceration": incar_bands,
    "summary": summary,
}

# ─── Save JSON ────────────────────────────────────────────────────
os.makedirs(OUTPUT_DIR, exist_ok=True)
output_path = os.path.join(OUTPUT_DIR, "counterfactual_ensemble.json")
with open(output_path, "w") as f:
    json.dump(output, f, indent=2)
print(f"Saved: {output_path}")

# ─── Generate site/counterfactual-data.js ─────────────────────────
js_path = os.path.join(SITE_DIR, "counterfactual-data.js")
with open(js_path, "w") as f:
    f.write("// Counterfactual ensemble data — auto-generated by 06_counterfactual_ensemble.py\n")
    f.write("// Do not edit manually.\n")
    f.write("window.COUNTERFACTUAL = ")
    json.dump(output, f, indent=2)
    f.write(";\n")
print(f"Saved: {js_path}")

# ─── Print summary ───────────────────────────────────────────────
print("\n=== Counterfactual Ensemble Summary ===")
print(f"Trajectories: {N_TRAJECTORIES}")
print(f"Intervention: {INTERVENTION_YEAR} (CMHC Act)")
print(f"\nBeds/100k in 2024:")
print(f"  Actual:        {actual[2024]['beds_per_100k']}")
print(f"  Counterfactual: {summary['counterfactual_beds_2024']['median']} "
      f"[{summary['counterfactual_beds_2024']['p05']}, {summary['counterfactual_beds_2024']['p95']}]")
print(f"\nIncarceration/100k in 2024:")
print(f"  Actual:        {actual[2024]['incarceration_rate_per_100k']}")
print(f"  Counterfactual: {summary['counterfactual_incar_2024']['median']} "
      f"[{summary['counterfactual_incar_2024']['p05']}, {summary['counterfactual_incar_2024']['p95']}]")
print(f"\nAdditional people in treatment (not prison): {people_treated_median:,} "
      f"[{people_treated_lo:,}, {people_treated_hi:,}]")
print(f"Fewer people incarcerated: {people_not_incarcerated_median:,} "
      f"[{people_not_incarcerated_lo:,}, {people_not_incarcerated_hi:,}]")
