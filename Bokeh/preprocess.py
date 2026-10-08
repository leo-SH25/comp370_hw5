#!/usr/bin/env python3
"""Pre-compute monthly average response times (hours) per zipcode.

Reads the 311 CSV line by line and writes a small CSV the dashboard can load
instantly:   zipcode,month,avg_hours     (zipcode "ALL" = every incident)

Usage: python3 preprocess.py -i trimmed_2024.csv -o monthly_response.csv
"""

import argparse
import csv
from collections import defaultdict
from datetime import datetime

# Column positions in the 311 CSV (0-based) - same layout as borough_complaints.py
CREATED_COL = 1   # "Created Date"
CLOSED_COL = 2    # "Closed Date"
ZIP_COL = 8       # "Incident Zip"

DATE_FORMAT = "%m/%d/%Y %I:%M:%S %p"   # e.g. 01/15/2024 10:30:00 AM
YEAR = 2024


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-i", "--input", required=True, help="input 311 CSV file")
    parser.add_argument("-o", "--output", default="monthly_response.csv",
                        help="output CSV (default: monthly_response.csv)")
    args = parser.parse_args()

    # (zipcode, month) -> [sum of hours, number of incidents]
    totals = defaultdict(lambda: [0.0, 0])

    with open(args.input, newline="", encoding="utf-8") as f:
        for row in csv.reader(f):
            try:
                created = datetime.strptime(row[CREATED_COL], DATE_FORMAT)
                closed_text = row[CLOSED_COL]
                zipcode = row[ZIP_COL].strip()[:5]
            except (ValueError, IndexError):
                continue                      # header or malformed row
            if created.year != YEAR or not closed_text:
                continue                      # not 2024, or not closed yet
            try:
                closed = datetime.strptime(closed_text, DATE_FORMAT)
            except ValueError:
                continue
            hours = (closed - created).total_seconds() / 3600
            if hours < 0:
                continue                      # closed before created: bad row

            month = created.month             # bucket by creation month
            for key in (("ALL", month), (zipcode, month)):
                if key[0] == "ALL" or (len(key[0]) == 5 and key[0].isdigit()):
                    totals[key][0] += hours
                    totals[key][1] += 1

    with open(args.output, "w", newline="") as out:
        writer = csv.writer(out)
        writer.writerow(["zipcode", "month", "avg_hours"])
        for (zipcode, month), (hours_sum, n) in sorted(totals.items()):
            writer.writerow([zipcode, month, round(hours_sum / n, 2)])

    print(f"Wrote {len(totals)} rows to {args.output}")


if __name__ == "__main__":
    main()
