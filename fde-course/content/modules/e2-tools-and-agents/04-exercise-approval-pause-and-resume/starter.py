import json
import anthropic

client = anthropic.Anthropic()
MODEL = "claude-opus-5-5"
MAX_TOKENS = 16000
MAX_ITERATIONS = 8
AUTO_REFUND_LIMIT = 200          # refunds above this need a human
SYSTEM_PROMPT = """You are Fernway Travel's trip-support agent.
Check the booking before any refund or cancellation. Refund only amounts the traveler actually paid.
Some actions need a supervisor's approval; if one is declined, tell the traveler a teammate will follow up."""
DECLINED_MESSAGE = "A supervisor declined this action. Do not retry it; tell the traveler a teammate will follow up."

# ---- Given: Fernway's systems (sample data) ---------------------------------

BOOKINGS = {}
REFUNDS = []                     # the payment provider's ledger


def reset_data():
    """Restore the sample bookings and empty the refund ledger."""
    BOOKINGS.clear()
    BOOKINGS.update({
        "FW7Q2K": {"traveler": "Ana Souza", "route": "LIS-BOS", "date": "2026-11-02", "fare_paid": 612.0, "status": "confirmed"},
        "HX3M8P": {"traveler": "Dev Mehta", "route": "JFK-SFO", "date": "2026-11-03", "fare_paid": 489.0, "status": "confirmed"},
        "RT5V1C": {"traveler": "Lena Park", "route": "ORD-DEN", "date": "2026-11-04", "fare_paid": 236.0, "status": "confirmed"},
    })
    REFUNDS.clear()


reset_data()


class ToolError(Exception):
    """A failure the model should hear about."""


def get_booking(booking_ref):
    if booking_ref not in BOOKINGS:
        raise ToolError(f"No booking found with reference {booking_ref}.")
    return dict(BOOKINGS[booking_ref], booking_ref=booking_ref)


def issue_refund(booking_ref, amount, reason, idempotency_key):
    """Refund money. The provider dedupes on idempotency_key, like real payment APIs."""
    for r in REFUNDS:
        if r["idempotency_key"] == idempotency_key:
            return {"refund_id": r["refund_id"], "amount": r["amount"], "duplicate": True}
    booking = BOOKINGS.get(booking_ref)
    if booking is None:
        raise ToolError(f"No booking found with reference {booking_ref}.")
    if not 0 < amount <= booking["fare_paid"]:
        raise ToolError(f"Refund must be between 0 and the fare paid ({booking['fare_paid']:.2f}).")
    refund = {"refund_id": f"rf_{len(REFUNDS) + 1:03d}", "booking_ref": booking_ref, "amount": amount,
              "reason": reason, "idempotency_key": idempotency_key}
    REFUNDS.append(refund)
    return {"refund_id": refund["refund_id"], "amount": amount, "duplicate": False}


def cancel_booking(booking_ref):
    booking = BOOKINGS.get(booking_ref)
    if booking is None:
        raise ToolError(f"No booking found with reference {booking_ref}.")
    booking["status"] = "cancelled"
    return {"booking_ref": booking_ref, "status": "cancelled"}


TOOL_FUNCTIONS = {"get_booking": get_booking, "issue_refund": issue_refund, "cancel_booking": cancel_booking}


def _tool(name, description, properties):
    return {"name": name, "description": description, "strict": True,
            "input_schema": {"type": "object", "properties": properties, "required": list(properties), "additionalProperties": False}}


TOOLS = [
    _tool("get_booking", "Look up a booking by reference. Call this before any refund or cancellation.",
          {"booking_ref": {"type": "string", "description": "Booking reference such as FW7Q2K"}}),
    _tool("issue_refund", "Refund money to the traveler's card. Call this only after get_booking, for an amount they paid.",
          {"booking_ref": {"type": "string"}, "amount": {"type": "number", "description": "Dollars to refund"},
           "reason": {"type": "string", "enum": ["schedule_change", "airline_cancellation", "upgrade_not_provided", "goodwill"]}}),
    _tool("cancel_booking", "Cancel a whole booking. Irreversible. Call this only when the traveler explicitly asks to cancel.",
          {"booking_ref": {"type": "string"}}),
]


def execute(block):
    """Run one tool_use block. Refunds use the tool_use id as the idempotency key."""
    result = {"type": "tool_result", "tool_use_id": block.id}
    fn = TOOL_FUNCTIONS.get(block.name)
    if fn is None:
        return dict(result, content=f"Unknown tool: {block.name}", is_error=True)
    args = dict(block.input)
    if block.name == "issue_refund":
        args["idempotency_key"] = block.id
    try:
        return dict(result, content=json.dumps(fn(**args)))
    except ToolError as exc:
        return dict(result, content=str(exc), is_error=True)


def describe(name, tool_input):
    """The one line a reviewer sees."""
    b = BOOKINGS.get(tool_input.get("booking_ref"), {})
    who = f"{b['traveler']} ({tool_input['booking_ref']}, fare paid ${b['fare_paid']:.2f})" if b else f"unknown booking {tool_input.get('booking_ref')}"
    if name == "issue_refund":
        return f"Refund ${tool_input['amount']:.2f} to {who} for {tool_input['reason']}."
    if name == "cancel_booking":
        return f"Cancel the booking of {who}. This cannot be undone."
    return f"Run {name} with {json.dumps(tool_input, sort_keys=True)}"


# ---- Your code ----------------------------------------------------------------


def requires_approval(name, tool_input):
    """True if a human must approve this call before it runs."""
    # TODO: cancellations always; refunds over AUTO_REFUND_LIMIT
    return False


def run_agent(client, state, audit):
    """Drive the loop from `state` until Claude finishes or a call needs approval.

    Returns {"status": "completed" | "awaiting_approval" | "max_iterations", "answer": ..., "pending": [...]}.
    """
    # TODO
    return {"status": "completed", "answer": None, "pending": []}


def start(client, question, audit):
    """Begin a conversation. Returns (outcome, state)."""
    state = {"messages": [{"role": "user", "content": question}], "iterations": 0, "pending": []}
    return run_agent(client, state, audit), state


def resume(client, state, decisions, audit):
    """Apply human decisions to the pending calls, send every result back, and continue."""
    # TODO
    return {"status": "completed", "answer": None, "pending": []}


# --- Try it out (not graded) ---
audit = []
outcome, state = start(client, "Booking FW7Q2K: the airline cancelled my flight. Please refund the full fare.", audit)
if outcome:
    print("status:", outcome["status"])
    for p in outcome["pending"]:
        print("  needs approval:", p["summary"])
    if outcome["status"] == "awaiting_approval":
        decisions = {p["id"]: {"approved": True, "approver": "maria.chen"} for p in outcome["pending"]}
        outcome = resume(client, state, decisions, audit)
        print("after approval:", outcome["status"], "-", outcome["answer"])
    print("\nAudit log:")
    for entry in audit:
        print(" ", entry)
    print("Refund ledger:", REFUNDS)
