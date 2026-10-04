import json
import anthropic
from fde_datasets import brightway

client = anthropic.Anthropic()
MODEL = "claude-opus-5-5"
AUTO_APPROVE_LIMIT = 50     # agents may issue up to $50 on their own (KB-04)
HARD_LIMIT = 200            # nobody can issue more than this through the assistant
CREDIT_REASONS = ["late_delivery", "damaged_item", "goodwill"]
DECLINED_MESSAGE = "Declined by a human reviewer. Do not retry; tell the customer a teammate will follow up."
SYSTEM_PROMPT = """You are Brightway Retail's customer-service agent.
Use tools to check real order and shipment data before answering. Never guess.
Late-delivery policy: standard customers get $20 store credit, gold members get $25, when a shipment is delayed."""

CUSTOMERS, ORDERS, SHIPMENTS = brightway.fresh()


def reset_data():
    """Restore fresh copies of the Brightway data."""
    global CUSTOMERS, ORDERS, SHIPMENTS
    CUSTOMERS, ORDERS, SHIPMENTS = brightway.fresh()


# ---- Tools from the previous exercise (given) ----

def lookup_order(order_id):
    oid = order_id.strip().upper()
    if oid not in ORDERS:
        raise KeyError(f"No order found with ID {oid}.")
    o = ORDERS[oid]
    return {"order_id": oid, "customer_id": o["customer_id"], "status": o["status"],
            "shipment_id": o["shipment_id"], "total": o["total"]}


def track_shipment(shipment_id):
    sid = shipment_id.strip().upper()
    if sid not in SHIPMENTS:
        raise KeyError(f"No shipment found with ID {sid}.")
    s = SHIPMENTS[sid]
    return {"shipment_id": sid, "status": s["status"], "eta": s["eta"], "last_event": s["last_event"]}


def issue_store_credit(customer_id, amount, reason):
    if not 0 < amount <= HARD_LIMIT:
        raise ValueError(f"amount must be between 0 and {HARD_LIMIT}")
    if customer_id not in CUSTOMERS:
        raise KeyError(f"No customer found with ID {customer_id}.")
    CUSTOMERS[customer_id]["store_credit"] += amount
    return {"customer_id": customer_id, "new_balance": CUSTOMERS[customer_id]["store_credit"]}


TOOL_FUNCTIONS = {"lookup_order": lookup_order, "track_shipment": track_shipment, "issue_store_credit": issue_store_credit}
READ_TOOLS = {"lookup_order", "track_shipment"}
WRITE_TOOLS = {"issue_store_credit"}


def _tool(name, description, properties):
    return {"name": name, "description": description, "strict": True,
            "input_schema": {"type": "object", "properties": properties, "required": list(properties), "additionalProperties": False}}


TOOLS = [
    _tool("lookup_order", "Look up an order by ID (format B-1234). Call this whenever the customer mentions an order.",
          {"order_id": {"type": "string", "description": "Order ID such as B-1001"}}),
    _tool("track_shipment", "Get carrier status for a shipment ID (format SHP-1234). Call this when you need delivery status.",
          {"shipment_id": {"type": "string", "description": "Shipment ID such as SHP-1003"}}),
    _tool("issue_store_credit", "Add store credit to a customer's account. Amounts over $50 go to a human for approval. "
          "Call this only when policy allows compensation.",
          {"customer_id": {"type": "string", "description": "Customer ID such as C-100"},
           "amount": {"type": "number", "description": "Dollars of credit"},
           "reason": {"type": "string", "enum": CREDIT_REASONS}}),
]


def execute(block):
    result = {"type": "tool_result", "tool_use_id": block.id}
    fn = TOOL_FUNCTIONS.get(block.name)
    if fn is None:
        return dict(result, content=f"Unknown tool: {block.name}", is_error=True)
    try:
        return dict(result, content=json.dumps(fn(**block.input)))
    except (KeyError, ValueError) as e:
        return dict(result, content=e.args[0], is_error=True)


# ---- Your code ----

def needs_approval(name, tool_input):
    return name == "issue_store_credit" and tool_input.get("amount", 0) > AUTO_APPROVE_LIMIT


def describe_action(name, tool_input):
    if name == "issue_store_credit":
        cid, amount, reason = tool_input["customer_id"], tool_input["amount"], tool_input["reason"]
        customer = CUSTOMERS.get(cid)
        if customer is None:
            return f"Issue ${amount:.2f} store credit to unknown customer {cid} for {reason}."
        return (f"Issue ${amount:.2f} store credit to {customer['name']} ({cid}, {customer['tier']}) for {reason}. "
                f"Current balance: ${customer['store_credit']:.2f}.")
    return f"Run {name} with {json.dumps(tool_input, sort_keys=True)}"


def guarded_execute(block, approver, audit):
    if needs_approval(block.name, block.input):
        request = {"tool": block.name, "input": block.input, "summary": describe_action(block.name, block.input)}
        try:
            approved = approver(request) is True
        except Exception:
            approved = False
        if not approved:
            audit.append({"tool": block.name, "input": block.input, "approval": "declined", "is_error": True})
            return {"type": "tool_result", "tool_use_id": block.id, "content": DECLINED_MESSAGE, "is_error": True}
        approval = "approved"
    elif block.name in WRITE_TOOLS:
        approval = "auto"
    else:
        approval = "not_required"
    result = execute(block)
    audit.append({"tool": block.name, "input": block.input, "approval": approval, "is_error": result.get("is_error", False)})
    return result


# ---- The agent loop (given) ----

def run_agent(client, question, approver, max_steps=6):
    messages = [{"role": "user", "content": question}]
    audit = []
    for step in range(1, max_steps + 1):
        response = client.messages.create(model=MODEL, max_tokens=16000, system=SYSTEM_PROMPT, tools=TOOLS, messages=messages)
        messages.append({"role": "assistant", "content": response.content})
        if response.stop_reason != "tool_use":
            answer = "".join(b.text for b in response.content if b.type == "text")
            return {"answer": answer, "steps": step, "audit": audit}
        results = [guarded_execute(b, approver, audit) for b in response.content if b.type == "tool_use"]
        messages.append({"role": "user", "content": results})
    raise RuntimeError("agent did not finish within max_steps")


# --- Try it out (not graded) ---
def approve_all(request):
    print("   REVIEWER SEES:", request["summary"], "-> approve")
    return True


def decline_all(request):
    print("   REVIEWER SEES:", request["summary"], "-> decline")
    return False


for label, question, approver in [
    ("Late order, $25 (auto)", "My order B-1001 is late. Can you make it right?", decline_all),
    ("Damaged rug, $75, approved", "My rug B-1004 arrived damaged. I'd like $75 in store credit.", approve_all),
    ("Damaged rug, $75, declined", "My rug B-1004 arrived damaged. I'd like $75 in store credit.", decline_all),
]:
    reset_data()
    print(label)
    result = run_agent(client, question, approver)
    for entry in result["audit"]:
        print("   audit:", entry)
    print("   answer:", result["answer"])
    print()
