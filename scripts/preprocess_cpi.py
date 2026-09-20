"""
preprocess_cpi.py

Reads the raw Statistics Canada CPI file (Table 18-10-0004-11) and produces
an annual province-level summary for 2019 and 2021:

  data/processed/cpi_summary.csv
      One row per (province, year): average_cpi

Expected raw columns (data/raw/cpi.csv), matching StatCan's own export:
  REF_DATE (YYYY-MM), GEO (province), VALUE (CPI)

Run:
    python scripts/preprocess_cpi.py
"""

import os
import pandas as pd

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")

YEARS_OF_INTEREST = (2019, 2021)


def main():
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    raw_path = os.path.join(RAW_DIR, "cpi.csv")
    if not os.path.exists(raw_path):
        raise FileNotFoundError(
            f"Missing raw file: {raw_path}\n"
            "Run sample_data/generate_sample_data.py or download the real "
            "Statistics Canada CPI table (see README.md)."
        )

    df = pd.read_csv(raw_path)
    df["year"] = df["REF_DATE"].astype(str).str.slice(0, 4).astype(int)
    df = df[df["year"].isin(YEARS_OF_INTEREST)]

    summary = (
        df.groupby(["GEO", "year"], as_index=False)["VALUE"]
        .mean()
        .rename(columns={"GEO": "province", "VALUE": "average_cpi", "year": "election_year"})
    )
    summary["average_cpi"] = summary["average_cpi"].round(2)
    summary = summary.sort_values(["election_year", "province"]).reset_index(drop=True)

    out_path = os.path.join(PROCESSED_DIR, "cpi_summary.csv")
    summary.to_csv(out_path, index=False)
    print(f"Wrote {len(summary)} rows -> {out_path}")


if __name__ == "__main__":
    main()
