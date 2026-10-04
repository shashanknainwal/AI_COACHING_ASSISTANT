---
title: "Exercise: Measure a Baseline from Raw Data"
type: exercise
minutes: 25
hints:
  - "Parse a timestamp with `datetime.strptime(text, \"%Y-%m-%d %H:%M\")`. Subtracting two datetimes gives a timedelta; `.total_seconds() / 3600` converts it to hours."
  - "Use the full-precision hours for the statistics and only round the final results. Python's `statistics.median(values)` handles both odd and even counts."
  - "Nearest-rank percentile: sort the values, then take `values[math.ceil(p / 100 * len(values)) - 1]`."
  - "A record is open when `record[\"entered\"]` is `None`. Compute durations only for the completed ones."
  - "If there are no completed records, `baseline` should return `n` = 0, `median_hours` and `p90_hours` = None, and the open count."
  - "In `validate_metric`, treat a field as missing when it's absent, `None`, or an empty string: `metric.get(field) in (None, \"\")`."
---

Brightline Health's intake lead says referrals take "about two days" to get into the EHR. Before you promise a target, you need a real baseline. IT exported a month of referral records:

```python
{"id": "R-1042", "received": "2026-02-03 08:10", "entered": "2026-02-04 14:40"}
{"id": "R-1043", "received": "2026-02-03 08:55", "entered": None}   # still open
```

You'll write a baseline calculator, then a checker that catches incomplete metric definitions before they go into the engagement brief.

## Your task

**1. `hours_between(start, end)`** takes two timestamps in the format `"YYYY-MM-DD HH:MM"` and returns the hours between them as a float, rounded to 1 decimal.

**2. `baseline(records)`** returns a dictionary:

```python
{
    "n": 18,               # completed records (entered is not None)
    "open": 2,             # records still open
    "median_hours": 48.5,  # median duration of completed records, rounded to 1 decimal
    "p90_hours": 104.0,    # 90th percentile by nearest rank, rounded to 1 decimal
}
```

Compute durations at full precision and round only the final median and p90. If no records are completed, `median_hours` and `p90_hours` are `None`.

**3. `pct_within(records, hours)`** returns the share of **completed** records that took at most `hours`, as a float rounded to 2 decimals (`0.0` if none are completed). This is how you'll express a target like "80% of referrals entered within 24 hours."

**4. `validate_metric(metric)`** checks a metric definition and returns a list of problems (empty if it's fine):
- For each field in `REQUIRED_FIELDS`, in order, add `"missing <field>"` if it's absent, `None`, or `""`.
- If `direction` is present but isn't `"increase"` or `"decrease"`, add `"invalid direction"`.
- If direction is valid and both `baseline` and `target` are present, add `"target does not improve on baseline"` when the target isn't strictly better: lower for `"decrease"`, higher for `"increase"`.

Those are the real numbers for Brightline's export, so you can check your work. Press **Run**, then fill in `INTAKE_METRIC["baseline"]` with your median and run again: the metric problems list should become empty. Then **Submit**.

> **Notice what the data says:** the intake lead's "about two days" is close to the median, but the p90 shows that 1 in 10 referrals takes more than four days. That tail is where the lost referring practices come from, and it belongs in your engagement brief.
