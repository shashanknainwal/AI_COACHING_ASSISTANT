import json
import re
import anthropic
from fde_datasets import northstar

client = anthropic.Anthropic()
MODEL = "claude-opus-5-5"
SHIPMENTS, LATEST, CUSTOMERS = northstar.clean_data()
ACTIONS = ["notify_only", "notify_and_ticket", "open_claim", "escalate_customs", "request_address", "reroute", "escalate", "no_action"]
BANNED_WORDS = ["refund", "credit", "compensation", "discount", "guarantee"]
MAX_MESSAGE_CHARS = 600
WRITE_TOOLS_NEEDING_APPROVAL = {"reroute_shipment"}
DECLINED = "Declined by a NorthStar coordinator. Do not retry; open an ops ticket instead."
SYSTEM_PROMPT = """You triage shipment exceptions for NorthStar Logistics.
1. Always start with get_shipment.
2. Priority: P1 for platinum customers; P2 for gold customers or any damage or customs hold; otherwise P3.
3. Tell the customer what happened and what happens next with notify_customer. Never promise refunds, credits or compensation.
4. Open an ops ticket for platinum delays, damage and customs holds.
5. For a missed pickup, propose a backup carrier with reroute_shipment (a coordinator approves it).
6. Finish by calling record_decision exactly once."""

# ---- Tools that read or write NorthStar's systems (given) ----
_TICKETS = []


def get_shipment(shipment_id):
    sid = shipment_id.strip().upper()
    if sid not in SHIPMENTS:
        raise KeyError(f"No shipment found with ID {sid}.")
    s, e = SHIPMENTS[sid], LATEST.get(sid, {"code": "UNKNOWN", "detail": ""})
    c = CUSTOMERS[s["customer_id"]]
    return {"shipment_id": sid, "customer_id": s["customer_id"], "customer": c["name"], "tier": c["tier"],
            "sla_hours": c["sla_hours"], "carrier": s["carrier"], "value_usd": s["value_usd"],
            "promised_date": s["promised_date"], "event_code": e["code"], "event_detail": e["detail"]}


def create_ops_ticket(shipment_id, priority, summary):
    _TICKETS.append({"shipment_id": shipment_id, "priority": priority, "summary": summary})
    return {"ticket_id": f"OPS-{500 + len(_TICKETS)}"}


def reroute_shipment(shipment_id, carrier):
    s = SHIPMENTS.get(shipment_id)
    if s is None:
        raise KeyError(f"No shipment found with ID {shipment_id}.")
    if carrier not in northstar.CARRIERS or carrier == s["carrier"]:
        raise ValueError(f"carrier must be one of {northstar.CARRIERS} and differ from {s['carrier']}")
    return {"status": "rerouted", "carrier": carrier}


def record_decision(action, priority, reason):
    return {"recorded": True}


def _tool(name, description, properties):
    return {"name": name, "description": description, "strict": True,
            "input_schema": {"type": "object", "properties": properties, "required": list(properties), "additionalProperties": False}}


_ID = {"type": "string", "description": "Shipment ID such as NS-2001"}
_PRIORITY = {"type": "string", "enum": ["P1", "P2", "P3"]}
TOOLS = [
    _tool("get_shipment", "Get a shipment with its customer, SLA tier and latest carrier event. Call this first.", {"shipment_id": _ID}),
    _tool("notify_customer", "Email the customer about their shipment. Call this to explain what happened and what happens next.",
          {"shipment_id": _ID, "message": {"type": "string", "description": "Plain-text message, at most 600 characters"}}),
    _tool("create_ops_ticket", "Open a ticket for NorthStar's ops coordinators. Call this when a person must act.",
          {"shipment_id": _ID, "priority": _PRIORITY, "summary": {"type": "string"}}),
    _tool("reroute_shipment", "Book a backup carrier. Call this when a pickup was missed. A coordinator must approve.",
          {"shipment_id": _ID, "carrier": {"type": "string", "enum": northstar.CARRIERS}}),
    _tool("record_decision", "Record the final triage decision. Call this exactly once, last.",
          {"action": {"type": "string", "enum": ACTIONS}, "priority": _PRIORITY, "reason": {"type": "string"}}),
]


# ---- Your code ----

def notify_customer(shipment_id, message):
    s = SHIPMENTS.get(shipment_id)
    if s is None:
        raise KeyError(f"No shipment found with ID {shipment_id}.")
    if len(message) > MAX_MESSAGE_CHARS:
        raise ValueError(f"message is {len(message)} characters; the limit is {MAX_MESSAGE_CHARS}")
    lowered = message.lower()
    for word in BANNED_WORDS:
        if re.search(rf"\b{word}", lowered):
            raise ValueError(f"message must not promise compensation (found '{word}')")
    return {"status": "queued", "to": CUSTOMERS[s["customer_id"]]["contact"]}


TOOL_FUNCTIONS = {"get_shipment": get_shipment, "notify_customer": notify_customer, "create_ops_ticket": create_ops_ticket,
                  "reroute_shipment": reroute_shipment, "record_decision": record_decision}


def guarded_execute(block, approver, audit):
    result = {"type": "tool_result", "tool_use_id": block.id}
    fn = TOOL_FUNCTIONS.get(block.name)
    if fn is None:
        audit.append({"tool": block.name, "input": block.input, "approval": "not_required", "is_error": True})
        return dict(result, content=f"Unknown tool: {block.name}", is_error=True)
    approval = "not_required"
    if block.name in WRITE_TOOLS_NEEDING_APPROVAL:
        try:
            approved = approver({"tool": block.name, "input": block.input}) is True
        except Exception:
            approved = False
        if not approved:
            audit.append({"tool": block.name, "input": block.input, "approval": "declined", "is_error": True})
            return dict(result, content=DECLINED, is_error=True)
        approval = "approved"
    try:
        out = dict(result, content=json.dumps(fn(**block.input)))
    except (KeyError, ValueError) as e:
        out = dict(result, content=e.args[0], is_error=True)
    audit.append({"tool": block.name, "input": block.input, "approval": approval, "is_error": out.get("is_error", False)})
    return out


def run_triage(client, shipment_id, approver, max_steps=8):
    messages = [{"role": "user", "content": f"Triage the exception for shipment {shipment_id}."}]
    audit = []
    for step in range(1, max_steps + 1):
        response = client.messages.create(model=MODEL, max_tokens=16000, system=SYSTEM_PROMPT, tools=TOOLS, messages=messages)
        messages.append({"role": "assistant", "content": response.content})
        if response.stop_reason != "tool_use":
            decisions = [a["input"] for a in audit if a["tool"] == "record_decision" and not a["is_error"]]
            return {"decision": decisions[-1] if decisions else None, "steps": step, "audit": audit}
        results = [guarded_execute(b, approver, audit) for b in response.content if b.type == "tool_use"]
        messages.append({"role": "user", "content": results})
    raise RuntimeError("triage did not finish within max_steps")


# --- Try it out (not graded) ---
def coordinator(request):
    print(f"   COORDINATOR asked to approve {request['tool']} {request['input']} -> approve")
    return True


for sid in ["NS-2001", "NS-2005", "NS-2006", "NS-2002"]:
    print(f"\n{sid}")
    result = run_triage(client, sid, coordinator)
    if result:
        for entry in result["audit"]:
            flag = "  [blocked]" if entry["is_error"] else ""
            print(f"   {entry['tool']}({', '.join(f'{k}={v!r}' for k, v in entry['input'].items())}){flag}")
        print("   decision:", result["decision"], f"({result['steps']} API calls)")
