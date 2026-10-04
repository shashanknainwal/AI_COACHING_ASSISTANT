import json
import anthropic

client = anthropic.Anthropic()
MODEL = "claude-opus-5-5"

TARGET_FIELDS = [
    {"name": "external_id", "description": "Carrier's unique shipment ID", "required": True},
    {"name": "status", "description": "One of picked_up, in_transit, delivered, exception", "required": True},
    {"name": "weight_kg", "description": "Shipment weight in kilograms", "required": True},
    {"name": "charge", "description": "Shipping charge in US dollars, as a number", "required": True},
    {"name": "customer_name", "description": "Receiving customer's name", "required": False},
    {"name": "city", "description": "Destination city", "required": False},
    {"name": "source_updated_at", "description": "Last update time, ISO 8601 UTC", "required": True},
]
TARGET_NAMES = [f["name"] for f in TARGET_FIELDS]
TRANSFORMS = ["none", "lookup", "unit_conversion", "date_format", "type_cast"]

SYSTEM_PROMPT = """You map fields from a carrier's API onto a company's ERP schema.
- Only map a source field if the sample values clearly support it.
- Use the exact source field names from the samples. Never invent field names.
- Each target field should come from at most one source field.
- Confidence is your estimate from 0 to 1; be honest about uncertainty."""

POLAR_SAMPLES = [
    {"trk_no": "PX-88213", "state": "OUT_FOR_DELIVERY", "wt_kg": 12.5, "amt_usd": "48.20",
     "recipient": "Brightway Retail", "dest_city": "Austin", "last_event_ts": "10/03/2026 08:15", "svc_level": "GROUND"},
    {"trk_no": "PX-88214", "state": "DELIVERED", "wt_kg": 3.1, "amt_usd": "12.75",
     "recipient": "Brightway Outlet", "dest_city": "Reno", "last_event_ts": "10/03/2026 09:02", "svc_level": "EXPRESS"},
]


MAPPING_SCHEMA = {
    "type": "object",
    "properties": {
        "mappings": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "source": {"type": "string"},
                    "target": {"type": "string", "enum": TARGET_NAMES},
                    "transform": {"type": "string", "enum": TRANSFORMS},
                    "confidence": {"type": "number"},
                },
                "required": ["source", "target", "transform", "confidence"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["mappings"],
    "additionalProperties": False,
}


def build_prompt(samples):
    targets = "\n".join(f"- {f['name']}: {f['description']}" for f in TARGET_FIELDS)
    return (
        "Propose a field mapping from the carrier's records to our ERP schema.\n\n"
        f"Carrier sample records:\n{json.dumps(samples, indent=2)}\n\n"
        f"ERP target fields:\n{targets}"
    )


def suggest_mappings(client, samples):
    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_prompt(samples)}],
        output_config={"format": {"type": "json_schema", "schema": MAPPING_SCHEMA}},
    )
    if response.stop_reason == "max_tokens":
        raise ValueError("truncated")
    if response.stop_reason == "refusal":
        raise ValueError("refused")
    text = next(b.text for b in response.content if b.type == "text")
    return json.loads(text)


def review(suggestions, samples, threshold=0.8):
    source_fields = set().union(*(s.keys() for s in samples)) if samples else set()
    result = {"accepted": [], "needs_review": [], "rejected": [], "missing_required": []}
    used = set()
    for m in sorted(suggestions["mappings"], key=lambda m: -m["confidence"]):
        if m["source"] not in source_fields:
            result["rejected"].append((m, "unknown source field"))
        elif m["target"] in used:
            result["rejected"].append((m, "duplicate target"))
        else:
            used.add(m["target"])
            result["accepted" if m["confidence"] >= threshold else "needs_review"].append(m)
    result["missing_required"] = [f["name"] for f in TARGET_FIELDS if f["required"] and f["name"] not in used]
    return result


# --- Try it out (not graded) ---
suggestions = suggest_mappings(client, POLAR_SAMPLES)
result = review(suggestions, POLAR_SAMPLES) if suggestions else None
if result:
    for m in result["accepted"]:
        print(f"ACCEPT  {m['source']:<14} -> {m['target']:<18} ({m['transform']}, {m['confidence']})")
    for m in result["needs_review"]:
        print(f"REVIEW  {m['source']:<14} -> {m['target']:<18} ({m['transform']}, {m['confidence']})")
    for m, why in result["rejected"]:
        print(f"REJECT  {m['source']:<14} -> {m['target']:<18} {why}")
    print("Missing required targets:", result["missing_required"])
