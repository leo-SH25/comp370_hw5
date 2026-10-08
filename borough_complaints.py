#!/usr/bin/env python3
"""Count NYC 311 complaint types per borough for a creation-date range."""

import argparse
import csv
import sys
from collections import Counter
from datetime import datetime

# Column positions in the 311 CSV (0-based). Check with:  head -2 your_file.csv
CREATED_COL = 1        # "Created Date"
COMPLAINT_COL = 5      # "Complaint Type"
BOROUGH_COL = 25       # "Borough"

CSV_DATE_FORMAT = "%m/%d/%Y %I:%M:%S %p"   # e.g. 01/15/2024 10:30:00 AM
ARG_DATE_FORMAT = "%Y-%m-%d"               # e.g. 2024-01-15


def parse_arg_date(text):
    try:
        return datetime.strptime(text, ARG_DATE_FORMAT).date()
    except ValueError:
        raise argparse.ArgumentTypeError(f"invalid date '{text}', expected YYYY-MM-DD")


def main():
    parser = argparse.ArgumentParser(
        description="Output the number of each complaint type per borough "
                    "for incidents created within a date range (inclusive).")
    parser.add_argument("-i", "--input", required=True,
                        help="input 311 CSV file")
    parser.add_argument("-s", "--start", required=True, type=parse_arg_date,
                        help="start date, YYYY-MM-DD (inclusive)")
    parser.add_argument("-e", "--end", required=True, type=parse_arg_date,
                        help="end date, YYYY-MM-DD (inclusive)")
    parser.add_argument("-o", "--output",
                        help="output CSV file (default: print to stdout)")
    args = parser.parse_args()

    if args.start > args.end:
        parser.error("start date must be on or before end date")

    counts = Counter()
    with open(args.input, newline="", encoding="utf-8") as f:
        for row in csv.reader(f):          # line by line: no pandas, low memory
            try:
                created = datetime.strptime(row[CREATED_COL], CSV_DATE_FORMAT).date()
            except (ValueError, IndexError):
                continue                   # header row or malformed line
            if args.start <= created <= args.end:
                counts[(row[COMPLAINT_COL], row[BOROUGH_COL])] += 1

    out = open(args.output, "w", newline="") if args.output else sys.stdout
    try:
        writer = csv.writer(out)
        writer.writerow(["complaint type", "borough", "count"])
        for (complaint, borough), n in sorted(counts.items()):
            writer.writerow([complaint, borough, n])
    finally:
        if args.output:
            out.close()


if __name__ == "__main__":
    main()