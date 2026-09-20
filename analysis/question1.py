"""
question1.py

Q1: How did party vote shares vary by province in the 2019 and 2021 federal
    elections?

Filters data/processed/provincial_vote_shares.csv by province (required),
election year (optional), and party (optional), then draws a grouped bar
chart comparing 2019 vs. 2021 vote share for each party.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")


def run(province, year=None, party=None):
    path = os.path.join(PROCESSED_DIR, "provincial_vote_shares.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing {path}. Run scripts/preprocess_elections.py first.")

    df = pd.read_csv(path)
    df = df[df["province"].str.lower() == province.lower()]
    if party:
        df = df[df["party"].str.lower() == party.lower()]
    if year:
        df = df[df["election_year"] == int(year)]

    if df.empty:
        print("No data found for the given filters.")
        return

    pivot = df.pivot(index="party", columns="election_year", values="vote_share").fillna(0)
    print(pivot)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    ax = pivot.plot(kind="bar", figsize=(8, 5))
    ax.set_ylabel("Vote Share (%)")
    ax.set_xlabel("Party")
    title = f"Vote Share by Party — {province}"
    if party:
        title += f" ({party})"
    ax.set_title(title)
    plt.xticks(rotation=0)
    plt.tight_layout()

    out_file = os.path.join(OUTPUT_DIR, f"q1_{province.replace(' ', '_')}.png")
    plt.savefig(out_file, dpi=150)
    plt.close()
    print(f"Saved chart -> {out_file}")
