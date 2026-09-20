"""
merge_cpi_turnout.py

Merges the CPI summary and the election turnout summary by province + year
to answer Question 2 (CPI vs. voter turnout).

Reads:
  data/processed/cpi_summary.csv
  data/processed/turnout_summary.csv

Writes:
  data/processed/cpi_turnout_analysis.csv
      One row per (province, election_year):
      average_cpi, total_valid_ballots, total_registered_electors, turnout

Run:
    python scripts/merge_cpi_turnout.py
(Run preprocess_elections.py and preprocess_cpi.py first.)
"""

import os
import pandas as pd

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")


def main():
    cpi_path = os.path.join(PROCESSED_DIR, "cpi_summary.csv")
    turnout_path = os.path.join(PROCESSED_DIR, "turnout_summary.csv")

    for p in (cpi_path, turnout_path):
        if not os.path.exists(p):
            raise FileNotFoundError(f"Missing {p}. Run the preprocess_* scripts first.")

    cpi = pd.read_csv(cpi_path)
    turnout = pd.read_csv(turnout_path)

    merged = turnout.merge(cpi, on=["province", "election_year"], how="inner")
    merged = merged[[
        "province", "election_year", "average_cpi",
        "total_valid_ballots", "total_registered_electors", "turnout",
    ]].sort_values(["election_year", "province"]).reset_index(drop=True)

    out_path = os.path.join(PROCESSED_DIR, "cpi_turnout_analysis.csv")
    merged.to_csv(out_path, index=False)
    print(f"Wrote {len(merged)} rows -> {out_path}")


if __name__ == "__main__":
    main()
