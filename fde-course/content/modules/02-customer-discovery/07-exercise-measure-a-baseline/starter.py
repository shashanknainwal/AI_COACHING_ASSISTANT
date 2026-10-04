import math
import statistics
from datetime import datetime

FMT = "%Y-%m-%d %H:%M"
REQUIRED_FIELDS = ["name", "baseline", "target", "direction", "deadline", "owner"]

RECORDS = [
    {"id": "R-1040", "received": "2026-02-02 08:00", "entered": "2026-02-05 15:00"},
    {"id": "R-1041", "received": "2026-02-02 11:55", "entered": "2026-02-03 13:55"},
    {"id": "R-1042", "received": "2026-02-03 08:40", "entered": "2026-02-05 10:10"},
    {"id": "R-1043", "received": "2026-02-03 11:00", "entered": "2026-02-07 19:00"},
    {"id": "R-1044", "received": "2026-02-04 08:55", "entered": "2026-02-06 06:55"},
    {"id": "R-1090", "received": "2026-02-27 09:15", "entered": None},
    {"id": "R-1045", "received": "2026-02-04 11:00", "entered": "2026-02-06 07:00"},
    {"id": "R-1046", "received": "2026-02-05 08:10", "entered": "2026-02-07 15:10"},
    {"id": "R-1047", "received": "2026-02-05 11:55", "entered": "2026-02-06 17:55"},
    {"id": "R-1048", "received": "2026-02-06 08:00", "entered": "2026-02-09 07:00"},
    {"id": "R-1049", "received": "2026-02-06 11:55", "entered": "2026-02-08 05:25"},
    {"id": "R-1050", "received": "2026-02-07 08:55", "entered": "2026-02-11 11:25"},
    {"id": "R-1051", "received": "2026-02-07 11:40", "entered": "2026-02-09 11:10"},
    {"id": "R-1052", "received": "2026-02-08 08:00", "entered": "2026-02-09 06:30"},
    {"id": "R-1053", "received": "2026-02-08 11:10", "entered": "2026-02-08 17:40"},
    {"id": "R-1054", "received": "2026-02-09 08:00", "entered": "2026-02-15 05:00"},
    {"id": "R-1055", "received": "2026-02-09 11:55", "entered": "2026-02-11 23:55"},
    {"id": "R-1056", "received": "2026-02-10 08:10", "entered": "2026-02-11 22:10"},
    {"id": "R-1057", "received": "2026-02-10 11:25", "entered": "2026-02-12 15:25"},
    {"id": "R-1091", "received": "2026-02-27 16:30", "entered": None},
]

INTAKE_METRIC = {
    "name": "Median referral intake time (hours)",
    "baseline": None,          # fill in from your baseline() result
    "target": 8,
    "direction": "decrease",
    "deadline": "2026-06-30",
    "owner": "Priya Nair",
}


def hours_between(start, end):
    """Hours from start to end (both "YYYY-MM-DD HH:MM"), rounded to 1 decimal."""
    # TODO
    pass


def baseline(records):
    """Return {"n", "open", "median_hours", "p90_hours"} for the records."""
    # TODO
    pass


def pct_within(records, hours):
    """Share of completed records that took at most `hours`, rounded to 2 decimals."""
    # TODO
    pass


def validate_metric(metric):
    """Return a list of problems with a metric definition."""
    # TODO
    pass


# --- Try it out (not graded) ---
b = baseline(RECORDS)
print("Baseline:", b)
print("Share entered within 24h:", pct_within(RECORDS, 24))
print("Share entered within 48h:", pct_within(RECORDS, 48))
print("Metric problems:", validate_metric(INTAKE_METRIC))
