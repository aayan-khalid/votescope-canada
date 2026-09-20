"""
Votescope Canada — CLI entry point.

Analyzes Canadian federal election results (2019, 2021) alongside Statistics
Canada CPI data to explore relationships between economic conditions and
voting behaviour.

Usage:
    python main.py preprocess
        Runs the full preprocessing pipeline (election + CPI + merges).

    python main.py q1 --province Ontario [--year 2019|2021] [--party Liberal]
        Party vote share by province.

    python main.py q2 --year 2021 [--province Ontario]
        CPI vs. voter turnout.

    python main.py q3 --party Conservative [--province Alberta]
        CPI change vs. vote share change, 2019 -> 2021.
"""

import argparse
import subprocess
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from analysis import question1, question2, question3  # noqa: E402


def run_preprocess():
    scripts_dir = os.path.join(os.path.dirname(__file__), "scripts")
    pipeline = [
        "preprocess_elections.py",
        "preprocess_cpi.py",
        "merge_cpi_turnout.py",
        "compute_delta.py",
    ]
    for script in pipeline:
        print(f"\n--- Running {script} ---")
        subprocess.run([sys.executable, os.path.join(scripts_dir, script)], check=True)


def main():
    parser = argparse.ArgumentParser(description="Votescope Canada")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("preprocess", help="Run the full preprocessing pipeline")

    p1 = subparsers.add_parser("q1", help="Party vote share by province")
    p1.add_argument("--province", required=True)
    p1.add_argument("--year", required=False)
    p1.add_argument("--party", required=False)

    p2 = subparsers.add_parser("q2", help="CPI vs. voter turnout")
    p2.add_argument("--year", required=True)
    p2.add_argument("--province", required=False)

    p3 = subparsers.add_parser("q3", help="CPI change vs. vote share change")
    p3.add_argument("--party", required=True)
    p3.add_argument("--province", required=False)

    args = parser.parse_args()

    if args.command == "preprocess":
        run_preprocess()
    elif args.command == "q1":
        question1.run(province=args.province, year=args.year, party=args.party)
    elif args.command == "q2":
        question2.run(year=args.year, province=args.province)
    elif args.command == "q3":
        question3.run(party=args.party, province=args.province)


if __name__ == "__main__":
    main()
