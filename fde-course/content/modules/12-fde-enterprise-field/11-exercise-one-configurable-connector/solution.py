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

POLAR_CONFIG = {
    "name": "polar_express",
    "pagination": {"type": "page", "param": "page", "items_field": "shipments", "has_more_field": "has_more"},
    "fields": {
        "external_id": {"path": "trk_no"},
        "status": {"path": "state", "transform": "lookup",
                   "table": {"PICKED_UP": "picked_up", "IN_TRANSIT": "in_transit", "OUT_FOR_DELIVERY": "in_transit",
                             "DELIVERED": "delivered", "EXCEPTION": "exception"}},
        "weight_kg": {"path": "wt_kg"},
        "charge": {"path": "amt_usd", "transform": "to_float"},
        "customer_name": {"path": "recipient"},
        "city": {"path": "dest_city"},
        "source_updated_at": {"path": "last_event_ts", "transform": "dmy_to_iso"},
    },
}


def get_path(record, path):
    """Follow a dotted path like 'consignee.name'; None if any step is missing."""
    value = record
    for key in path.split("."):
        if not isinstance(value, dict) or value.get(key) is None:
            return None
        value = value[key]
    return value


def apply_transform(value, spec):
    """Apply the spec's transform (default 'none') to a non-None value."""
    name = spec.get("transform", "none")
    if name == "none":
        return value
    if name == "lookup":
        table = spec.get("table") or {}
        if value not in table:
            raise ValueError(f"unknown value {value}")
        return table[value]
    if name == "lbs_to_kg":
        return round(value * LBS_TO_KG, 1)
    if name == "cents_to_dollars":
        return round(value / 100, 2)
    if name == "to_float":
        return round(float(value), 2)
    if name == "dmy_to_iso":
        return datetime.strptime(value, "%d/%m/%Y %H:%M").strftime("%Y-%m-%dT%H:%M:%SZ")
    raise ValueError(f"unknown transform {name}")


def validate_config(config):
    """Problems that would make this config fail at runtime."""
    problems = []
    ptype = config.get("pagination", {}).get("type")
    if ptype not in PAGINATION_TYPES:
        problems.append(f"unknown pagination type: {ptype}")
    fields = config.get("fields", {})
    for target, spec in fields.items():
        if target not in TARGET_NAMES:
            problems.append(f"unknown target field: {target}")
        transform = spec.get("transform", "none")
        if transform not in TRANSFORMS:
            problems.append(f"{target}: unknown transform {transform}")
        elif transform == "lookup" and not spec.get("table"):
            problems.append(f"{target}: lookup needs a table")
    for f in TARGET_FIELDS:
        if f["required"] and f["name"] not in fields:
            problems.append(f"missing required field: {f['name']}")
    return problems


def map_record(src, config):
    """One source record -> one target record, driven entirely by config."""
    out = {}
    for f in TARGET_FIELDS:
        name = f["name"]
        spec = config["fields"].get(name)
        value = get_path(src, spec["path"]) if spec else None
        if value is None:
            if f["required"]:
                raise ValueError(f"missing {name}")
            out[name] = None
        else:
            out[name] = apply_transform(value, spec)
    return out


def fetch_all(fetch_page, config):
    """Every item from every page, using the config's pagination style."""
    p = config["pagination"]
    items = []
    if p["type"] == "cursor":
        params = {}
        while True:
            resp = fetch_page(params)
            items.extend(resp[p["items_field"]])
            nxt = resp.get(p["next_field"])
            if not nxt:
                return items
            params = {p["param"]: nxt}
    page = 1
    while True:
        resp = fetch_page({p["param"]: page})
        items.extend(resp[p["items_field"]])
        if not resp.get(p["has_more_field"]):
            return items
        page += 1


def run_connector(fetch_page, config):
    """Fetch and map everything; bad records go to errors, not exceptions."""
    problems = validate_config(config)
    if problems:
        raise ValueError("invalid config: " + "; ".join(problems))
    records, errors = [], []
    id_path = config["fields"]["external_id"]["path"]
    for raw in fetch_all(fetch_page, config):
        try:
            records.append(map_record(raw, config))
        except ValueError as exc:
            errors.append((get_path(raw, id_path), str(exc)))
    return {"records": records, "errors": errors}


# --- Try it out (not graded) ---
for label, fetch, config in [("Northwind", northwind_fetch, NORTHWIND_CONFIG), ("Polar Express", polar_fetch, POLAR_CONFIG)]:
    print(label, "config problems:", validate_config(config))
    result = run_connector(fetch, config) if validate_config(config) == [] else None
    if result:
        for r in result["records"]:
            print("  ", r)
        print("   errors:", result["errors"])
