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

# TODO: write a system prompt for an executive-summary assistant
SYSTEM_PROMPT = ""


def summarize_for_exec(client, notes):
    """Ask Claude for an executive summary of the notes and return the text (or None on refusal)."""
    # TODO
    pass


def estimate_cost(usage, input_price=4.0, output_price=20.0):
    """Return the cost in USD of a call, given its usage and per-million-token prices."""
    # TODO
    pass


# --- Try it out (not graded) ---
summary = summarize_for_exec(client, NOTES)
print(summary)
