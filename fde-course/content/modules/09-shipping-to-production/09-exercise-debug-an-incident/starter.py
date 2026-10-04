import json
from fde_datasets import incident

# Possible root causes the team is arguing about (given). Set ROOT_CAUSE to one key once the data convinces you.
CAUSES = {
    "anthropic_outage": "The Claude API was having an outage",
    "traffic_spike": "Ticket volume spiked and overwhelmed the service",
    "prompt_prefix_changes_every_request": "The system prompt changed on every request, so prompt caching stopped working",
    "bad_model_output": "The model started returning invalid output",
}


def parse_lines(lines):
    """(records sorted by ts, number of skipped lines). Skip lines that aren't JSON objects with "ts" and "event"."""
    # TODO
    pass


def request_timeline(records, request_id):
    """One readable line per event for a single request, in time order."""
    # TODO
    pass


def by_version(records):
    """Per-version stats from llm_call and llm_error events."""
    # TODO
    pass


def incident_summary(records):
    """The facts for the incident report."""
    # TODO
    pass


# TODO: once the numbers convince you, set this to one of the CAUSES keys.
ROOT_CAUSE = None


# --- Try it out (not graded) ---
parsed = parse_lines(incident.LOG_LINES)
if parsed:
    records, skipped = parsed
    print(f"{len(records)} records, {skipped} unparseable lines skipped")
    for r in records:
        if r["event"] == "deploy":
            print(f"   deploy {r['ts']} {r['version']}: {r['change']}")
    print("\nOne failed request:")
    for line in request_timeline(records, "req-1166") or []:
        print("  ", line)
    print("\nBy version:")
    for version, s in (by_version(records) or {}).items():
        print(f"   {version}: {s}")
    print("\nSummary:", incident_summary(records))
print("Root cause:", CAUSES.get(ROOT_CAUSE, "not chosen yet"))
