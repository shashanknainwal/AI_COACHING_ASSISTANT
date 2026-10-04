import anthropic

client = anthropic.Anthropic()
MODEL = "claude-opus-5-5"

NOTES = """Customer: Brightline Health
Date: 2026-03-02
Attendees: Dana Ruiz (VP Operations, sponsor), Sam Okafor (IT Director),
Priya Nair (Intake Lead, champion), Leo Park (Intake Specialist)
Goals: cut referral intake from 3 days to same-day; reduce manual data entry errors
Risks: EHR vendor API access needs ~6 weeks of approval
Actions: Sam shares sandbox credentials by Friday; FDE profiles one month of fax referrals
"""

SYSTEM_PROMPT = (
    "You write briefings for a busy executive sponsor of a software deployment. "
    "Summarize meeting notes in under 120 words: one sentence on the goal, then "
    "3 bullets covering owners, risks and next steps. Plain language, no jargon, "
    "and never invent facts that aren't in the notes."
)


def summarize_for_exec(client, notes):
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": f"Summarize these kickoff notes for the executive sponsor:\n\n{notes}"}
        ],
    )
    if response.stop_reason == "refusal":
        return None
    return "".join(b.text for b in response.content if b.type == "text").strip()


def estimate_cost(usage, input_price=4.0, output_price=20.0):
    cost = usage.input_tokens / 1_000_000 * input_price + usage.output_tokens / 1_000_000 * output_price
    return round(cost, 6)


summary = summarize_for_exec(client, NOTES)
print(summary)
