"""
compute_delta.py

Computes the change (2021 - 2019) in CPI and in party vote share for each
province + party pair, to answer Question 3 (economic change vs. political
change).

Reads:
  data/processed/cpi_summary.csv
  data/processed/provincial_vote_shares.csv

Writes:
  data/processed/economic_political_delta.csv
      One row per (province, party):
      cpi_2019, cpi_2021, cpi_delta,
      vote_share_2019, vote_share_2021, vote_share_delta

Run:
    python scripts/compute_delta.py
(Run preprocess_elections.py and preprocess_cpi.py first.)
"""

import os
import pandas as pd

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")


def main():
    cpi_path = os.path.join(PROCESSED_DIR, "cpi_summary.csv")
    shares_path = os.path.join(PROCESSED_DIR, "provincial_vote_shares.csv")

    for p in (cpi_path, shares_path):
        if not os.path.exists(p):
            raise FileNotFoundError(f"Missing {p}. Run the preprocess_* scripts first.")

    cpi = pd.read_csv(cpi_path)
    shares = pd.read_csv(shares_path)

    cpi_pivot = cpi.pivot(index="province", columns="election_year", values="average_cpi")
    cpi_pivot = cpi_pivot.rename(columns={2019: "cpi_2019", 2021: "cpi_2021"}).reset_index()
    cpi_pivot["cpi_delta"] = cpi_pivot["cpi_2021"] - cpi_pivot["cpi_2019"]

    shares_pivot = shares.pivot_table(
        index=["province", "party"], columns="election_year", values="vote_share"
    )
    shares_pivot = shares_pivot.rename(columns={2019: "vote_share_2019", 2021: "vote_share_2021"}).reset_index()
    shares_pivot["vote_share_delta"] = shares_pivot["vote_share_2021"] - shares_pivot["vote_share_2019"]

    merged = shares_pivot.merge(cpi_pivot, on="province", how="left")
    merged = merged[[
        "province", "party", "cpi_2019", "cpi_2021", "cpi_delta",
        "vote_share_2019", "vote_share_2021", "vote_share_delta",
    ]].round(2).sort_values(["province", "party"]).reset_index(drop=True)

    out_path = os.path.join(PROCESSED_DIR, "economic_political_delta.csv")
    merged.to_csv(out_path, index=False)
    print(f"Wrote {len(merged)} rows -> {out_path}")


if __name__ == "__main__":
    main()
