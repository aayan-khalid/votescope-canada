# Votescope Canada

Votescope Canada analyzes Canadian federal election results (2019 and 2021)
alongside Statistics Canada Consumer Price Index (CPI) data to explore
whether — and how — economic conditions relate to voting behaviour across
provinces.

I built this as a course data-analysis project: designing the research
questions, sourcing the datasets, building the preprocessing pipeline, and
writing the CLI + visualization layer used to answer each question.

## What it answers

1. **How did party vote shares vary by province in the 2019 and 2021 federal
   elections?**
2. **What relationship is there between CPI and voter turnout across each
   province in those elections?**
3. **How did changes in CPI relate to changes in vote share for the major
   parties between 2019 and 2021?**

## How it works

Raw data is riding-level (thousands of rows) and CPI data is monthly, which
is too granular and too slow to query live. So the project separates raw
inputs from a fast preprocessing pipeline that produces small, province-level
summary files, which the CLI then filters and plots on demand.

```
data/raw/            <- source CSVs (election + CPI)
data/processed/       <- generated summary CSVs (not committed, see below)
scripts/               <- preprocessing pipeline
analysis/               <- one module per research question
output/                  <- generated charts (.png)
main.py                   <- CLI entry point
```

### Pipeline

| Script | Input | Output |
|---|---|---|
| `scripts/preprocess_elections.py` | `election_2019.csv`, `election_2021.csv` | `provincial_vote_shares.csv`, `turnout_summary.csv` |
| `scripts/preprocess_cpi.py` | `cpi.csv` | `cpi_summary.csv` |
| `scripts/merge_cpi_turnout.py` | `cpi_summary.csv` + `turnout_summary.csv` | `cpi_turnout_analysis.csv` |
| `scripts/compute_delta.py` | `cpi_summary.csv` + `provincial_vote_shares.csv` | `economic_political_delta.csv` |

Each processed file is what the demo actually queries at runtime, so no raw
file is re-read or re-merged during a live demo — only the small summary
CSVs.

## Data sources

| Dataset | Source | Update frequency |
|---|---|---|
| 2019 Federal Election Results (43rd General Election) | [Elections Canada / open.canada.ca](https://open.canada.ca/data/en/dataset/199e5070-2fd5-49d3-aa21-aece08964d18) | Finalized historical record, not updated once certified |
| 2021 Federal Election Results (44th General Election) | [Elections Canada / open.canada.ca](https://open.canada.ca/data/en/dataset/199e5070-2fd5-49d3-aa21-aece08964d18) | Finalized historical record, not updated once certified |
| Consumer Price Index, Table 18-10-0004-11 | [Statistics Canada](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810000411) | Updated monthly |

Because the CPI dataset is updated monthly while the election datasets are
fixed historical records, the system separates raw and processed files: if a
source dataset is updated (e.g. a monthly CPI refresh, or a rare Elections
Canada correction), you re-run the relevant `preprocess_*` script to
regenerate the summary file the demo reads from — no other code changes
needed.

## Quickstart

This repo ships with a **synthetic sample dataset generator** so it runs
immediately without downloading anything. The generated data mimics the
real files' structure but the numbers are fabricated — swap in the real CSVs
(see below) for actual analysis.

```bash
git clone <this-repo-url>
cd votescope-canada
pip install -r requirements.txt

# 1. Generate sample data (or drop real files into data/raw/ instead)
python sample_data/generate_sample_data.py

# 2. Run the full preprocessing pipeline
python main.py preprocess

# 3. Ask the questions
python main.py q1 --province Ontario
python main.py q1 --province Ontario --party Liberal

python main.py q2 --year 2021
python main.py q2 --year 2019 --province Quebec

python main.py q3 --party Conservative --province Alberta
python main.py q3 --party Liberal
```

Charts are saved to `output/*.png`.

### Using the real data instead

Download the three source files linked above and save them as:

```
data/raw/election_2019.csv
data/raw/election_2021.csv
data/raw/cpi.csv
```

with columns matching what `sample_data/generate_sample_data.py` produces
(`province, electoral_district, party, votes, total_valid_votes,
registered_electors, election_year` for elections; `REF_DATE, GEO, VALUE`
for CPI — StatCan's own export format). Then run `python main.py preprocess`
as above. You may need a small mapping step if the real files use different
column headers.

## CLI reference

```
python main.py preprocess
    Runs the full preprocessing pipeline (election + CPI + merges).

python main.py q1 --province <name> [--year 2019|2021] [--party <name>]
    Party vote share by province. Draws a grouped bar chart.

python main.py q2 --year <2019|2021> [--province <name>]
    CPI vs. voter turnout across provinces. Draws a scatter plot and
    prints the correlation coefficient.

python main.py q3 --party <name> [--province <name>]
    CPI change vs. vote share change, 2019 -> 2021. Draws a bar chart
    (vote share change by province) and a scatter plot (CPI change vs.
    vote share change) when multiple provinces are in scope.
```

## Tech stack

- Python 3
- pandas — data aggregation and merging
- matplotlib — bar charts and scatter plots
- argparse — CLI

## Project structure

```
votescope-canada/
├── main.py
├── requirements.txt
├── sample_data/
│   └── generate_sample_data.py
├── scripts/
│   ├── preprocess_elections.py
│   ├── preprocess_cpi.py
│   ├── merge_cpi_turnout.py
│   └── compute_delta.py
├── analysis/
│   ├── question1.py
│   ├── question2.py
│   └── question3.py
├── data/
│   ├── raw/         (gitignored contents; source CSVs go here)
│   └── processed/   (gitignored contents; generated by the pipeline)
└── output/            (gitignored contents; generated charts)
```

## Notes

- `data/processed/*.csv` and `output/*.png` are gitignored since they're
  generated artifacts — run the pipeline to regenerate them locally.
- The sample data generator uses a fixed random seed, so results are
  reproducible across runs until you replace it with real data.
