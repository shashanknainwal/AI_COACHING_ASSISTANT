import json
import anthropic

client = anthropic.Anthropic()
MODEL = "claude-opus-5-5"

REQUIREMENT_TYPES = ["functional", "data", "integration", "security", "non-functional"]
PRIORITY_ORDER = ["must", "should", "could"]

SYSTEM_PROMPT = """You extract software requirements from customer discovery notes.
- Only include requirements the notes state or clearly imply. Never invent.
- For each requirement, quote the shortest phrase from the notes that supports it as evidence.
- Use "must" only for things the customer called essential or blocking.
- Put anything ambiguous or contradictory in open_questions instead of guessing."""

NOTES = """Lumen Insurance discovery, calls 1-3 (Mar 3-5)
Marcus: Claims come in by email, about 900 a week. Adjusters read each one and key it
into ClaimsPro by hand. 18% of claims get sent back because a field was keyed wrong.
Joan: late payouts drive regulator complaints (14 last quarter, target under 5).
Board cares about that and cost per claim.
Ravi (CISO): wants data to stay in our tenant. No customer data in third-party logs.
Unclear: does ClaimsPro have an API? Which claim types first?"""

REQUIREMENT_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "type": {"type": "string", "enum": REQUIREMENT_TYPES},
        "priority": {"type": "string", "enum": PRIORITY_ORDER},
        "evidence": {"type": "string"},
    },
    "required": ["title", "type", "priority", "evidence"],
    "additionalProperties": False,
}

REQUIREMENTS_SCHEMA = {
    "type": "object",
    "properties": {
        "requirements": {"type": "array", "items": REQUIREMENT_SCHEMA},
        "open_questions": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["requirements", "open_questions"],
    "additionalProperties": False,
}


def extract_requirements(client, notes):
    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"Discovery notes:\n\n{notes}"}],
        output_config={"format": {"type": "json_schema", "schema": REQUIREMENTS_SCHEMA}},
    )
    if response.stop_reason == "max_tokens":
        raise ValueError("truncated")
    if response.stop_reason == "refusal":
        raise ValueError("refused")
    text = next(b.text for b in response.content if b.type == "text")
    return json.loads(text)


def prioritized(result):
    ordered = sorted(result["requirements"], key=lambda r: PRIORITY_ORDER.index(r["priority"]))
    seen = set()
    titles = []
    for r in ordered:
        key = r["title"].strip().lower()
        if key in seen:
            continue
        seen.add(key)
        titles.append(r["title"])
    return titles


# --- Try it out (not graded) ---
result = extract_requirements(client, NOTES)
print(json.dumps(result, indent=2)[:1200])
print()
print("Prioritized:")
for i, title in enumerate(prioritized(result) or [], 1):
    print(f"  {i}. {title}")
