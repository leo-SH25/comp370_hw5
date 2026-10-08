"""Bokeh dashboard: monthly average 311 response time, all NYC vs two zipcodes.

Run with:
  bokeh serve dashboard.py --port 6002 --allow-websocket-origin=YOUR_IP:6002
Needs monthly_response.csv from preprocess.py in the same folder.
"""

import csv
from collections import defaultdict

from bokeh.io import curdoc
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Select
from bokeh.plotting import figure

DATA_FILE = "monthly_response.csv"
MONTHS = list(range(1, 13))
MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Load the small pre-computed file once: averages[zip][month] = hours
averages = defaultdict(dict)
with open(DATA_FILE, newline="") as f:
    for row in csv.DictReader(f):
        averages[row["zipcode"]][int(row["month"])] = float(row["avg_hours"])

zipcodes = sorted(z for z in averages if z != "ALL")


def series(zipcode):
    """12 monthly values for a zipcode; NaN leaves a gap for missing months."""
    return [averages[zipcode].get(m, float("nan")) for m in MONTHS]


zip1 = Select(title="Zipcode 1", value=zipcodes[0], options=zipcodes)
zip2 = Select(title="Zipcode 2", value=zipcodes[1], options=zipcodes)

source = ColumnDataSource(data=dict(
    month=MONTHS,
    all=series("ALL"),
    zip1=series(zip1.value),
    zip2=series(zip2.value),
))

plot = figure(title="Monthly average 311 response time (2024)",
              x_axis_label="Month (2024)",
              y_axis_label="Average create-to-closed time (hours)",
              width=800, height=450)
plot.line("month", "all", source=source, line_width=3,
          color="black", legend_label="All NYC")
line1 = plot.line("month", "zip1", source=source, line_width=2,
                  color="#1f77b4", legend_label=f"Zipcode {zip1.value}")
line2 = plot.line("month", "zip2", source=source, line_width=2,
                  color="#ff7f0e", legend_label=f"Zipcode {zip2.value}")
plot.xaxis.ticker = MONTHS
plot.xaxis.major_label_overrides = {m: name for m, name in zip(MONTHS, MONTH_NAMES)}
plot.legend.location = "top_left"


def update(attr, old, new):
    # Only swaps in already-computed numbers, so updates are instant.
    source.data = dict(month=MONTHS, all=series("ALL"),
                       zip1=series(zip1.value), zip2=series(zip2.value))
    plot.legend.items[1].label = {"value": f"Zipcode {zip1.value}"}
    plot.legend.items[2].label = {"value": f"Zipcode {zip2.value}"}


zip1.on_change("value", update)
zip2.on_change("value", update)

curdoc().add_root(column(zip1, zip2, plot))
curdoc().title = "NYC 311 Response Times"
