import csv
import io
import re
from datetime import datetime
from fde_datasets import northstar

DATE_FORMATS = ["%Y-%m-%d", "%m/%d/%Y", "%b %d %Y"]
CARRIER_KEYS = {  # normalized key -> canonical carrier name (given)
    "fastfreight": "FastFreight",
    "bluelineexpress": "BlueLine Express",
    "northpeakcarriers": "NorthPeak Carriers",
    "northpeak": "NorthPeak Carriers",
}
COMPANY_SUFFIXES = {"inc", "llc", "co", "corp"}


def parse_date(raw):
    """Any of DATE_FORMATS -> "YYYY-MM-DD"; None if it matches none of them."""
    # TODO
    pass


def normalize_id(raw):
    """Remove all whitespace and uppercase: " ns - 2001 " -> "NS-2001"."""
    # TODO
    pass


def normalize_carrier(raw):
    """Map any spelling of a carrier to its canonical name, or None if unknown."""
    # TODO
    pass


def parse_money(raw):
    """ "$1,200.00" -> 1200.0 """
    # TODO
    pass


def clean_shipments(csv_text):
    """(shipments keyed by ID, data-quality issues)."""
    # TODO
    pass


def latest_events(events):
    """{shipment_id: {"code", "ts", "detail"}} keeping each shipment's most recent event."""
    # TODO
    pass


def build_queue(shipments, latest, customers):
    """(exception queue sorted most urgent first, sorted IDs of events with no matching shipment)."""
    # TODO
    pass


# --- Try it out (not graded) ---
cleaned = clean_shipments(northstar.SHIPMENTS_CSV)
if cleaned:
    shipments, issues = cleaned
    print(f"{len(shipments)} clean shipments; data-quality issues: {issues}")
    latest = latest_events(northstar.CARRIER_EVENTS)
    built = build_queue(shipments, latest, northstar.CUSTOMERS) if latest else None
    if built:
        queue, orphans = built
        print(f"\nException queue ({len(queue)}), most urgent first:")
        for q in queue:
            print(f"   {q['shipment_id']} {q['tier']:<9} {q['code']:<14} ${q['value_usd']:>9,.2f}  {q['customer']}")
        print("Events for unknown shipments:", orphans)
