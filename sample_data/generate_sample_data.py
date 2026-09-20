"""
generate_sample_data.py

Generates SYNTHETIC sample data that mirrors the structure of:
  - Elections Canada official voting results (2019 / 2021)
  - Statistics Canada CPI Table 18-10-0004-11

This exists so the project can be cloned and run end-to-end without first
downloading the real government files. It is NOT real election or CPI data.

To use the real datasets instead, download them (see README.md > Data Sources)
and place them in data/raw/ with the same column names used here:

    data/raw/election_2019.csv
    data/raw/election_2021.csv
    data/raw/cpi.csv

Run:
    python sample_data/generate_sample_data.py
"""

import os
import random
import csv

random.seed(42)

PROVINCES = [
    "Ontario", "Quebec", "British Columbia", "Alberta", "Manitoba",
    "Saskatchewan", "Nova Scotia", "New Brunswick",
    "Newfoundland and Labrador", "Prince Edward Island",
]

PARTIES = ["Liberal", "Conservative", "NDP", "Green", "Bloc"]

# Ridings per province (roughly proportional, simplified for sample data)
RIDINGS_PER_PROVINCE = {
    "Ontario": 12, "Quebec": 10, "British Columbia": 8, "Alberta": 6,
    "Manitoba": 4, "Saskatchewan": 4, "Nova Scotia": 3, "New Brunswick": 3,
    "Newfoundland and Labrador": 2, "Prince Edward Island": 2,
}

# Base party strength per province (weights), tweaked slightly between years
# so the 2019 -> 2021 change tells a plausible story.
BASE_STRENGTH_2019 = {
    "Ontario":        {"Liberal": 40, "Conservative": 33, "NDP": 17, "Green": 6, "Bloc": 0},
    "Quebec":         {"Liberal": 30, "Conservative": 16, "NDP": 11, "Green": 4, "Bloc": 39},
    "British Columbia": {"Liberal": 26, "Conservative": 32, "NDP": 28, "Green": 12, "Bloc": 0},
    "Alberta":        {"Liberal": 14, "Conservative": 66, "NDP": 12, "Green": 4, "Bloc": 0},
    "Manitoba":       {"Liberal": 34, "Conservative": 42, "NDP": 19, "Green": 3, "Bloc": 0},
    "Saskatchewan":   {"Liberal": 12, "Conservative": 64, "NDP": 20, "Green": 3, "Bloc": 0},
    "Nova Scotia":    {"Liberal": 43, "Conservative": 32, "NDP": 20, "Green": 4, "Bloc": 0},
    "New Brunswick":  {"Liberal": 39, "Conservative": 32, "NDP": 8, "Green": 6, "Bloc": 0},
    "Newfoundland and Labrador": {"Liberal": 61, "Conservative": 20, "NDP": 12, "Green": 3, "Bloc": 0},
    "Prince Edward Island": {"Liberal": 44, "Conservative": 27, "NDP": 13, "Green": 15, "Bloc": 0},
}


def drift(weights, magnitude=6):
    """Apply a small random shift to a province's party weights for 2021."""
    new_weights = {}
    for party, w in weights.items():
        shift = random.uniform(-magnitude, magnitude)
        new_weights[party] = max(0.5, w + shift)
    total = sum(new_weights.values())
    return {p: (w / total) * 100 for p, w in new_weights.items()}


def make_election_csv(path, weights_by_province, year):
    rows = []
    for province in PROVINCES:
        n_ridings = RIDINGS_PER_PROVINCE[province]
        weights = weights_by_province[province]
        for riding_num in range(1, n_ridings + 1):
            district = f"{province} District {riding_num}"
            registered_electors = random.randint(55000, 95000)
            turnout_rate = random.uniform(0.60, 0.72)
            total_valid_votes = int(registered_electors * turnout_rate)

            # Split this riding's votes across parties using province weights
            # plus a little riding-level noise.
            riding_weights = {p: max(0.5, w + random.uniform(-5, 5)) for p, w in weights.items()}
            wsum = sum(riding_weights.values())

            remaining = total_valid_votes
            parties_list = list(riding_weights.items())
            for i, (party, w) in enumerate(parties_list):
                if i == len(parties_list) - 1:
                    votes = remaining
                else:
                    votes = int(total_valid_votes * (w / wsum))
                    remaining -= votes
                votes = max(0, votes)
                rows.append({
                    "province": province,
                    "electoral_district": district,
                    "party": party,
                    "votes": votes,
                    "total_valid_votes": total_valid_votes,
                    "registered_electors": registered_electors,
                    "election_year": year,
                })

    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "province", "electoral_district", "party", "votes",
            "total_valid_votes", "registered_electors", "election_year",
        ])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {path}")


def make_cpi_csv(path):
    rows = []
    # Rough starting index per province with a mild inflation trend.
    base_index = {
        "Ontario": 136.0, "Quebec": 134.5, "British Columbia": 137.5,
        "Alberta": 139.0, "Manitoba": 135.0, "Saskatchewan": 134.0,
        "Nova Scotia": 133.5, "New Brunswick": 132.5,
        "Newfoundland and Labrador": 133.0, "Prince Edward Island": 131.5,
    }
    for province in PROVINCES:
        idx = base_index[province]
        for year in (2019, 2021):
            monthly_growth = random.uniform(0.15, 0.45) if year == 2021 else random.uniform(0.05, 0.2)
            for month in range(1, 13):
                idx += random.uniform(0, monthly_growth)
                rows.append({
                    "REF_DATE": f"{year}-{month:02d}",
                    "GEO": province,
                    "VALUE": round(idx, 2),
                })

    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["REF_DATE", "GEO", "VALUE"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {path}")


def main():
    raw_dir = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
    os.makedirs(raw_dir, exist_ok=True)

    weights_2019 = BASE_STRENGTH_2019
    weights_2021 = {p: drift(w) for p, w in BASE_STRENGTH_2019.items()}

    make_election_csv(os.path.join(raw_dir, "election_2019.csv"), weights_2019, 2019)
    make_election_csv(os.path.join(raw_dir, "election_2021.csv"), weights_2021, 2021)
    make_cpi_csv(os.path.join(raw_dir, "cpi.csv"))


if __name__ == "__main__":
    main()
