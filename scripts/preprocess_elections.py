"""
preprocess_elections.py

Reads the raw riding-level 2019 and 2021 federal election CSVs and produces
two province-level summary files used by the demo:

  data/processed/provincial_vote_shares.csv
      One row per (province, party, election_year):
      total_raw_votes, total_valid_ballots, vote_share (%)

  data/processed/turnout_summary.csv
      One row per (province, election_year):
      total_valid_ballots, total_registered_electors, turnout (%)

Expected raw columns (data/raw/election_2019.csv, election_2021.csv):
  province, electoral_district, party, votes, total_valid_votes,
  registered_electors, election_year

Run:
    python scripts/preprocess_elections.py
"""

import os
import pandas as pd

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")


def load_election_files():
    files = [
        os.path.join(RAW_DIR, "election_2019.csv"),
        os.path.join(RAW_DIR, "election_2021.csv"),
    ]
    frames = []
    for f in files:
        if not os.path.exists(f):
            raise FileNotFoundError(
                f"Missing raw file: {f}\n"
                "Run sample_data/generate_sample_data.py or download the real "
                "Elections Canada files (see README.md)."
            )
        frames.append(pd.read_csv(f))
    return pd.concat(frames, ignore_index=True)


def build_vote_shares(df):
    # Sum votes per province + party + year
    party_votes = (
        df.groupby(["province", "party", "election_year"], as_index=False)["votes"]
        .sum()
        .rename(columns={"votes": "total_raw_votes"})
    )

    # Total valid ballots per province + year (denominator for vote share)
    # total_valid_votes is per-riding, so take the first riding value per
    # riding and sum, not the value duplicated across parties.
    riding_totals = (
        df.drop_duplicates(subset=["province", "electoral_district", "election_year"])
        .groupby(["province", "election_year"], as_index=False)["total_valid_votes"]
        .sum()
        .rename(columns={"total_valid_votes": "total_valid_ballots"})
    )

    merged = party_votes.merge(riding_totals, on=["province", "election_year"], how="left")
    merged["vote_share"] = (merged["total_raw_votes"] / merged["total_valid_ballots"]) * 100
    return merged.sort_values(["election_year", "province", "party"]).reset_index(drop=True)


def build_turnout_summary(df):
    riding_level = df.drop_duplicates(subset=["province", "electoral_district", "election_year"])
    turnout = (
        riding_level.groupby(["province", "election_year"], as_index=False)
        .agg(
            total_valid_ballots=("total_valid_votes", "sum"),
            total_registered_electors=("registered_electors", "sum"),
        )
    )
    turnout["turnout"] = (turnout["total_valid_ballots"] / turnout["total_registered_electors"]) * 100
    return turnout.sort_values(["election_year", "province"]).reset_index(drop=True)


def main():
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    df = load_election_files()

    vote_shares = build_vote_shares(df)
    vote_shares_path = os.path.join(PROCESSED_DIR, "provincial_vote_shares.csv")
    vote_shares.to_csv(vote_shares_path, index=False)
    print(f"Wrote {len(vote_shares)} rows -> {vote_shares_path}")

    turnout = build_turnout_summary(df)
    turnout_path = os.path.join(PROCESSED_DIR, "turnout_summary.csv")
    turnout.to_csv(turnout_path, index=False)
    print(f"Wrote {len(turnout)} rows -> {turnout_path}")


if __name__ == "__main__":
    main()
