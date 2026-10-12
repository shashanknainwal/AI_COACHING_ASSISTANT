from datetime import datetime

TARGET_FIELDS = [
    {"name": "external_id", "required": True},
    {"name": "status", "required": True},
    {"name": "weight_kg", "required": True},
    {"name": "charge", "required": True},
    {"name": "customer_name", "required": False},
    {"name": "city", "required": False},
    {"name": "source_updated_at", "required": True},
]
TARGET_NAMES = [f["name"] for f in TARGET_FIELDS]
TRANSFORMS = ["none", "lookup", "lbs_to_kg", "cents_to_dollars", "to_float", "dmy_to_iso"]
PAGINATION_TYPES = ["cursor", "page"]
LBS_TO_KG = 0.45359237

NORTHWIND_CONFIG = {
    "name": "northwind",
    "pagination": {"type": "cursor", "param": "cursor", "items_field": "data", "next_field": "next_cursor"},
    "fields": {
        "external_id": {"path": "id"},
        "status": {"path": "status_code", "transform": "lookup",
                   "table": {"PU": "picked_up", "IT": "in_transit", "DL": "delivered", "EX": "exception"}},
        "weight_kg": {"path": "weight_lbs", "transform": "lbs_to_kg"},
        "charge": {"path": "charge_cents", "transform": "cents_to_dollars"},
        "customer_name": {"path": "consignee.name"},
        "city": {"path": "consignee.city"},
        "source_updated_at": {"path": "updated_at"},
    },
}

# TODO: describe Polar Express in the same shape as NORTHWIND_CONFIG.
POLAR_CONFIG = {
    "name": "polar_express",
    "pagination": {},
    "fields": {},
}


def get_path(record, path):
    """Follow a dotted path like 'consignee.name'; None if any step is missing."""
    # TODO
    pass


def apply_transform(value, spec):
    """Apply the spec's transform (default 'none') to a non-None value."""
    # TODO
    pass


def validate_config(config):
    """Problems that would make this config fail at runtime."""
    # TODO
    pass


def map_record(src, config):
    """One source record -> one target record, driven entirely by config."""
    # TODO
    pass


def fetch_all(fetch_page, config):
    """Every item from every page, using the config's pagination style."""
    # TODO
    pass


def run_connector(fetch_page, config):
    """Fetch and map everything; bad records go to errors, not exceptions."""
    # TODO
    pass


# --- Try it out (not graded) ---
for label, fetch, config in [("Northwind", northwind_fetch, NORTHWIND_CONFIG), ("Polar Express", polar_fetch, POLAR_CONFIG)]:
    print(label, "config problems:", validate_config(config))
    result = run_connector(fetch, config) if validate_config(config) == [] else None
    if result:
        for r in result["records"]:
            print("  ", r)
        print("   errors:", result["errors"])
