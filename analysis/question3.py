"""
question3.py

Q3: How did changes in CPI relate to changes in vote share for the major
    political parties between 2019 and 2021?

Filters data/processed/economic_political_delta.csv by party (required) and
optionally province, then draws:
  - a bar chart of vote share change by province
  - a scatter plot of CPI change vs. vote share change
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")


def run(party, province=None):
    path = os.path.join(PROCESSED_DIR, "economic_political_delta.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing {path}. Run scripts/compute_delta.py first.")

    df = pd.read_csv(path)
    df = df[df["party"].str.lower() == party.lower()]
    if province:
        df = df[df["province"].str.lower() == province.lower()]

    if df.empty:
        print("No data found for the given filters.")
        return

    print(df[["province", "cpi_delta", "vote_share_delta"]].to_string(index=False))

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    suffix = f"_{province.replace(' ', '_')}" if province else ""

    # Bar chart: vote share change by province
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(df["province"], df["vote_share_delta"])
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_ylabel("Vote Share Change, pp (2021 - 2019)")
    ax.set_title(f"Vote Share Change by Province — {party}")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    bar_file = os.path.join(OUTPUT_DIR, f"q3_bar_{party}{suffix}.png")
    plt.savefig(bar_file, dpi=150)
    plt.close()
    print(f"Saved chart -> {bar_file}")

    # Scatter plot: CPI change vs vote share change
    if len(df) > 1:
        fig, ax = plt.subplots(figsize=(7, 6))
        ax.scatter(df["cpi_delta"], df["vote_share_delta"])
        for _, row in df.iterrows():
            ax.annotate(row["province"], (row["cpi_delta"], row["vote_share_delta"]), fontsize=8,
                        xytext=(4, 4), textcoords="offset points")
        ax.axhline(0, color="grey", linewidth=0.6)
        ax.set_xlabel("CPI Change (2021 - 2019)")
        ax.set_ylabel("Vote Share Change, pp (2021 - 2019)")
        ax.set_title(f"CPI Change vs. Vote Share Change — {party}")
        plt.tight_layout()
        scatter_file = os.path.join(OUTPUT_DIR, f"q3_scatter_{party}{suffix}.png")
        plt.savefig(scatter_file, dpi=150)
        plt.close()
        print(f"Saved chart -> {scatter_file}")
