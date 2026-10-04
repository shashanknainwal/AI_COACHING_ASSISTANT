import json
import re
import anthropic

client = anthropic.Anthropic()
MODEL = "claude-opus-5-5"

# From your scoping exercise (given).
BASELINE = {"per_day": 39.8, "ops_hours_per_day": 20.4, "breach_rate": 0.207, "platinum_breach_rate": 0.39}
# Two-week pilot in Chicago after fixing the eval failures (given).
PILOT = {"days": 10, "exceptions": 402, "auto_handled": 181, "assisted": 221, "avg_minutes_auto": 2.0,
         "avg_minutes_assisted": 14.0, "breach_rate": 0.082, "platinum_breach_rate": 0.05, "api_cost_usd": 7.42}
# Agreed with NorthStar's finance team (given).
ASSUMPTIONS = {"loaded_cost_per_hour": 48.0, "working_days_per_month": 21, "engagement_fee_usd": 38000}
SUMMARY_SCHEMA = {"type": "object", "properties": {"summary": {"type": "string"}}, "required": ["summary"],
                  "additionalProperties": False}


def pilot_metrics(pilot):
    n = pilot["exceptions"]
    minutes = pilot["auto_handled"] * pilot["avg_minutes_auto"] + pilot["assisted"] * pilot["avg_minutes_assisted"]
    return {
        "per_day": round(n / pilot["days"], 1),
        "automation_rate": round(pilot["auto_handled"] / n, 3),
        "avg_handle_minutes": round(minutes / n, 1),
        "ops_hours_per_day": round(minutes / pilot["days"] / 60, 1),
        "cost_per_exception": round(pilot["api_cost_usd"] / n, 4),
    }


def impact(baseline, pm, assumptions):
    baseline_minutes = baseline["ops_hours_per_day"] * 60 / baseline["per_day"]
    monthly_volume = baseline["per_day"] * assumptions["working_days_per_month"]
    hours_saved = round((baseline_minutes - pm["avg_handle_minutes"]) * monthly_volume / 60, 1)
    labor = round(hours_saved * assumptions["loaded_cost_per_hour"], 2)
    api = round(pm["cost_per_exception"] * monthly_volume, 2)
    net = round(labor - api, 2)
    return {
        "baseline_avg_minutes": round(baseline_minutes, 1),
        "hours_saved_per_month": hours_saved,
        "labor_savings_per_month": labor,
        "api_cost_per_month": api,
        "net_savings_per_month": net,
        "payback_months": round(assumptions["engagement_fee_usd"] / net, 1),
    }


def headlines(baseline, pilot, pm, imp):
    return [
        f"{pm['automation_rate']:.0%} of exceptions were handled end to end",
        f"{imp['hours_saved_per_month']:,.0f} coordinator hours saved per month",
        f"SLA breaches fell from {baseline['breach_rate']:.1%} to {pilot['breach_rate']:.1%}",
        f"Platinum breaches fell from {baseline['platinum_breach_rate']:.0%} to {pilot['platinum_breach_rate']:.0%}",
        f"${imp['net_savings_per_month']:,.0f} net savings per month, paying back the engagement in "
        f"{imp['payback_months']} months",
    ]


NUMBER = re.compile(r"\$?\d[\d,]*(?:\.\d+)?%?")


def numbers_in(text):
    found = []
    for token in NUMBER.findall(text):
        token = token.replace("$", "").replace(",", "").rstrip(".")
        if token:
            found.append(token)
    return found


def draft_summary(client, lines):
    prompt = ("Write a three-sentence executive summary of the pilot for NorthStar's CEO. "
              "Use only the facts and numbers below.\n\n<headlines>\n" + "\n".join(f"- {l}" for l in lines) + "\n</headlines>")
    response = client.messages.create(
        model=MODEL, max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
        output_config={"effort": "medium", "format": {"type": "json_schema", "schema": SUMMARY_SCHEMA}},
    )
    summary = json.loads(next(b.text for b in response.content if b.type == "text"))["summary"]
    allowed = set()
    for line in lines:
        allowed.update(numbers_in(line))
    unsupported = [n for n in numbers_in(summary) if n not in allowed]
    return {"summary": summary, "unsupported_numbers": unsupported}


# --- Try it out (not graded) ---
pm = pilot_metrics(PILOT)
if pm:
    print("Pilot:", pm)
    imp = impact(BASELINE, pm, ASSUMPTIONS)
    if imp:
        print("Impact:", imp)
        lines = headlines(BASELINE, PILOT, pm, imp)
        if lines:
            print("\nHeadlines:")
            for line in lines:
                print("  -", line)
            draft = draft_summary(client, lines)
            if draft:
                print("\nClaude's draft:", draft["summary"])
                print("Numbers not in the facts:", draft["unsupported_numbers"] or "none")
