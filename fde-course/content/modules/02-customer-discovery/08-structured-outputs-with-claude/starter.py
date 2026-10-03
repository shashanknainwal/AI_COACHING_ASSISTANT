import json
import anthropic

client = anthropic.Anthropic()

notes = """Lumen Insurance kickoff. Claims arrive by email, ~900/week.
Adjusters re-key everything into ClaimsPro. 18% rework from keying errors.
Joan (VP Claims) needs regulator complaints under 5 per quarter."""

schema = {
    "type": "object",
    "properties": {
        "customer": {"type": "string"},
        "pain_points": {"type": "array", "items": {"type": "string"}},
        "sponsor": {"type": ["string", "null"]},
    },
    "required": ["customer", "pain_points", "sponsor"],
    "additionalProperties": False,
}

response = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=4096,
    system="Extract information from discovery notes. Only use facts stated in the notes.",
    messages=[{"role": "user", "content": notes}],
    output_config={"format": {"type": "json_schema", "schema": schema}},
)

print("stop_reason:", response.stop_reason)
text = next(b.text for b in response.content if b.type == "text")
data = json.loads(text)
print(json.dumps(data, indent=2))

# The simulator fills in placeholder values that match your schema.
# Try removing "additionalProperties": False above and run again to see the API error.
