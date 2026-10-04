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
    """Per-day volume, automation rate, handling time, ops hours and API cost per exception from the pilot."""
    # TODO
    pass


def impact(baseline, pm, assumptions):
    """Monthly hours saved, savings, API cost, net savings and payback."""
    # TODO
    pass


def headlines(baseline, pilot, pm, imp):
    """The five headline sentences for the readout."""
    # TODO
    pass


NUMBER = re.compile(r"\$?\d[\d,]*(?:\.\d+)?%?")


def numbers_in(text):
    """Every number in text, normalized: "$14,797" -> "14797", "8.2%" -> "8.2%"."""
    # TODO
    pass


def draft_summary(client, lines):
    """Ask Claude for a summary of the headlines, then flag numbers that aren't in them."""
    # TODO
    pass


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
