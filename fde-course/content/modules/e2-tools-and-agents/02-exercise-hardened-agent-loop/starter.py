import json
import anthropic

client = anthropic.Anthropic()
MODEL = "claude-opus-5-5"
MAX_TOKENS = 16000
SYSTEM_PROMPT = """You are Fernway Travel's trip-support agent.
Always check bookings and flight data with your tools before answering. Never guess a flight status.
When several lookups are independent, call the tools in parallel."""
HANDOFF_MESSAGE = "I'm handing this to a Fernway agent who will follow up shortly."
REFUSAL_MESSAGE = "I can't help with that request here. A Fernway agent will follow up."

# ---- Given: Fernway's systems (sample data) ---------------------------------

BOOKINGS = {
    "FW7Q2K": {"traveler": "Ana Souza", "flight": "FW 212", "date": "2026-11-02", "route": "LIS-BOS", "fare_class": "flex"},
    "HX3M8P": {"traveler": "Dev Mehta", "flight": "FW 88", "date": "2026-11-03", "route": "JFK-SFO", "fare_class": "basic"},
    "RT5V1C": {"traveler": "Lena Park", "flight": "FW 404", "date": "2026-11-04", "route": "ORD-DEN", "fare_class": "flex"},
}
FLIGHTS = {
    ("FW 212", "2026-11-02"): {"status": "cancelled", "delay_minutes": 0, "gate": None},
    ("FW 88", "2026-11-03"): {"status": "delayed", "delay_minutes": 95, "gate": "B12"},
}
ALTERNATIVES = {
    ("FW 212", "2026-11-02"): [
        {"flight": "FW 214", "departs": "2026-11-02T18:40", "seats": 4},
        {"flight": "FW 216", "departs": "2026-11-03T07:15", "seats": 12},
    ],
}


class ToolError(Exception):
    """A failure the model should hear about (bad ID, no such flight)."""


def get_booking(booking_ref):
    ref = booking_ref.strip().upper()
    if ref not in BOOKINGS:
        raise ToolError(f"No booking found with reference {ref}. References look like FW7Q2K.")
    return dict(BOOKINGS[ref], booking_ref=ref)


def get_flight_status(flight, date):
    if flight == "FW 404":
        # The flight-ops database is flaky. This message is internal: never show it to the model.
        raise ConnectionError("timeout talking to ops-db 10.0.3.7:5432")
    if (flight, date) not in FLIGHTS:
        raise ToolError(f"No flight {flight} on {date}.")
    return dict(FLIGHTS[(flight, date)], flight=flight, date=date)


def find_alternatives(flight, date):
    options = ALTERNATIVES.get((flight, date), [])
    return {"flight": flight, "date": date, "options": options[:3]}


TOOL_FUNCTIONS = {"get_booking": get_booking, "get_flight_status": get_flight_status, "find_alternatives": find_alternatives}


def _tool(name, description, properties):
    return {
        "name": name,
        "description": description,
        "strict": True,
        "input_schema": {"type": "object", "properties": properties, "required": list(properties), "additionalProperties": False},
    }


TOOLS = [
    _tool("get_booking", "Look up a booking by its 6-character reference. Call this first whenever the traveler gives a booking reference.",
          {"booking_ref": {"type": "string", "description": "Booking reference such as FW7Q2K"}}),
    _tool("get_flight_status", "Get live status for one flight on one date. Call this when the traveler asks whether a flight is on time, delayed or cancelled.",
          {"flight": {"type": "string", "description": "Flight number such as FW 212"},
           "date": {"type": "string", "format": "date", "description": "Departure date, YYYY-MM-DD"}}),
    _tool("find_alternatives", "List up to 3 other flights on the same route. Call this when a flight is cancelled or the traveler wants to rebook.",
          {"flight": {"type": "string", "description": "The original flight number"},
           "date": {"type": "string", "format": "date", "description": "The original departure date, YYYY-MM-DD"}}),
]

# ---- Your code ----------------------------------------------------------------


def execute_tool(block):
    """Run one tool_use block and return a tool_result dict. Never raises."""
    # TODO: look the tool up in TOOL_FUNCTIONS, call it with **block.input,
    # and turn ToolError / unknown tools / any other exception into is_error results.
    pass


def run_agent(client, question, max_iterations=6):
    """The hardened loop. Returns {"status", "answer", "iterations", "tool_calls", "usage"}."""
    # TODO
    pass


# --- Try it out (not graded) ---
for question in ["Booking FW7Q2K: I just got a cancellation email. What are my options?",
                 "Is my flight on booking RT5V1C on time?"]:
    result = run_agent(client, question)
    if result:
        print(f"Q: {question}")
        for call in result["tool_calls"]:
            print(f"   {call['name']}({call['input']})" + ("  [error]" if call["is_error"] else ""))
        print(f"   status={result['status']}  calls={result['iterations']}  tokens={result['usage']}")
        print(f"   A: {result['answer']}\n")
print("Open the Trace tab to see each call, its tool_use blocks and the results you sent back.")
