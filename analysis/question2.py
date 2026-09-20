"""
question2.py

Q2: What relationship is there between CPI and voter turnout across each
    province in those federal elections?

Filters data/processed/cpi_turnout_analysis.csv by election year (required)
and optionally province, then draws a scatter plot of CPI vs. turnout and
reports the correlation coefficient.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")


def run(year, province=None):
    path = os.path.join(PROCESSED_DIR, "cpi_turnout_analysis.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing {path}. Run scripts/merge_cpi_turnout.py first.")

    df = pd.read_csv(path)
    df = df[df["election_year"] == int(year)]
    if province:
        df = df[df["province"].str.lower() == province.lower()]

    if df.empty:
        print("No data found for the given filters.")
        return

    print(df[["province", "average_cpi", "turnout"]].to_string(index=False))

    if len(df) > 1:
        corr = df["average_cpi"].corr(df["turnout"])
        direction = "positive" if corr > 0 else "negative"
        print(f"\nCorrelation (CPI vs turnout): {corr:.3f} ({direction})")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(df["average_cpi"], df["turnout"])
    for _, row in df.iterrows():
        ax.annotate(row["province"], (row["average_cpi"], row["turnout"]), fontsize=8,
                    xytext=(4, 4), textcoords="offset points")
    ax.set_xlabel("Average CPI")
    ax.set_ylabel("Voter Turnout (%)")
    ax.set_title(f"CPI vs. Voter Turnout by Province — {year}")
    plt.tight_layout()

    suffix = f"_{province.replace(' ', '_')}" if province else ""
    out_file = os.path.join(OUTPUT_DIR, f"q2_{year}{suffix}.png")
    plt.savefig(out_file, dpi=150)
    plt.close()
    print(f"Saved chart -> {out_file}")
