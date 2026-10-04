---
title: "Exercise: The Numbers for the Readout"
type: exercise
minutes: 35
hints:
  - "`pilot_metrics`: total minutes = `auto_handled × avg_minutes_auto + assisted × avg_minutes_assisted`; divide by exceptions for the average, and by days × 60 for hours per day."
  - "`impact`: baseline minutes per exception = `ops_hours_per_day × 60 / per_day`. Monthly volume = baseline `per_day × working_days_per_month`. Round only the final values, not the intermediate ones."
  - "`headlines`: format with `{x:.0%}`, `{x:.1%}` and `{x:,.0f}`. The payback number is used as is (`2.6`)."
  - "`numbers_in`: `NUMBER.findall(text)`, then remove `$` and `,` and strip a trailing `.` from each match."
  - "`draft_summary`: collect every number from the headlines into a set, then list the summary's numbers that aren't in it, in order."
---

The engagement ends with a readout to Dana and NorthStar's CEO. After fixing the failures your eval found, the team ran a two-week pilot in Chicago (`PILOT`). You'll turn the pilot data into the handful of numbers executives remember. Then you'll let Claude draft the summary and **fact-check it**, because a confident, wrong number in front of a CEO costs more trust than any bug.

`BASELINE` (from your scoping exercise), `PILOT`, `ASSUMPTIONS` (agreed with NorthStar's finance team) and `SUMMARY_SCHEMA` are given.

## Your task

**1. `pilot_metrics(pilot)`** returns:

```python
{"per_day": 40.2,              # exceptions / days, 1 decimal
 "automation_rate": 0.45,      # auto_handled / exceptions, 3 decimals
 "avg_handle_minutes": 8.6,    # (auto × avg_minutes_auto + assisted × avg_minutes_assisted) / exceptions, 1 decimal
 "ops_hours_per_day": 5.8,     # those total minutes / days / 60, 1 decimal
 "cost_per_exception": 0.0185} # api_cost_usd / exceptions, 4 decimals
```

**2. `impact(baseline, pm, assumptions)`** projects the pilot onto NorthStar's normal volume:
- `baseline_avg_minutes` = `ops_hours_per_day × 60 / per_day` from the baseline (1 decimal).
- Monthly volume = baseline `per_day × working_days_per_month`.
- `hours_saved_per_month` = (baseline minutes − pilot `avg_handle_minutes`) × monthly volume / 60 (1 decimal).
- `labor_savings_per_month` = hours saved × `loaded_cost_per_hour`.
- `api_cost_per_month` = `cost_per_exception` × monthly volume.
- `net_savings_per_month` = labor savings − API cost. These three dollar values are rounded to 2 decimals.
- `payback_months` = `engagement_fee_usd / net_savings_per_month` (1 decimal).

Use the unrounded baseline minutes in the calculation.

**3. `headlines(baseline, pilot, pm, imp)`** returns exactly these five strings, filled with the real values:

```
45% of exceptions were handled end to end
309 coordinator hours saved per month
SLA breaches fell from 20.7% to 8.2%
Platinum breaches fell from 39% to 5%
$14,797 net savings per month, paying back the engagement in 2.6 months
```

**4. `numbers_in(text)`** returns every number in `text`, in order, using the given `NUMBER` pattern. Remove `$` and `,` and drop a trailing period: `"$14,797"` → `"14797"`, `"8.2%"` → `"8.2%"`.

**5. `draft_summary(client, lines)`** asks Claude for a three-sentence summary:
- One user message listing each headline as `- <line>` between `<headlines>` tags, with an instruction to use only those facts.
- `model=MODEL`, `max_tokens` ≥ 1024, and `output_config` with `effort: "medium"` and the `SUMMARY_SCHEMA` format.
- Return `{"summary": ..., "unsupported_numbers": [...]}`, where `unsupported_numbers` lists the summary's numbers that appear in none of the headlines.

Press **Run**. Claude's draft reads well, so find the number nobody gave it. Then **Submit**.
