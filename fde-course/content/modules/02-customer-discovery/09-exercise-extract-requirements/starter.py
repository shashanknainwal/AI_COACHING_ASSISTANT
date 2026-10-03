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

# TODO: describe the shape from the instructions as a JSON Schema
REQUIREMENTS_SCHEMA = {}


def extract_requirements(client, notes):
    """Call Claude with structured outputs and return the parsed dict."""
    # TODO
    pass


def prioritized(result):
    """Return requirement titles ordered must -> should -> could, without duplicates."""
    # TODO
    pass


# --- Try it out (not graded) ---
result = extract_requirements(client, NOTES)
print(json.dumps(result, indent=2)[:1200])
print()
print("Prioritized:")
for i, title in enumerate(prioritized(result) or [], 1):
    print(f"  {i}. {title}")
