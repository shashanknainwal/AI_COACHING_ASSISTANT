import json
import anthropic
from fde_datasets import brightway

client = anthropic.Anthropic()
MODEL = "claude-opus-5-5"
CREDIT_LIMIT = 50
CREDIT_REASONS = ["late_delivery", "damaged_item", "goodwill"]
SYSTEM_PROMPT = """You are Brightway Retail's customer-service agent.
Use tools to check real order and shipment data before answering. Never guess.
Late-delivery policy: standard customers get $20 store credit, gold members get $25, when a shipment is delayed."""

CUSTOMERS, ORDERS, SHIPMENTS = brightway.fresh()


def reset_data():
    """Restore fresh copies of the Brightway data."""
    global CUSTOMERS, ORDERS, SHIPMENTS
    CUSTOMERS, ORDERS, SHIPMENTS = brightway.fresh()


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
    if not 0 < amount <= CREDIT_LIMIT:
        raise ValueError(f"amount must be between 0 and {CREDIT_LIMIT}")
    if customer_id not in CUSTOMERS:
        raise KeyError(f"No customer found with ID {customer_id}.")
    CUSTOMERS[customer_id]["store_credit"] += amount
    return {"customer_id": customer_id, "new_balance": CUSTOMERS[customer_id]["store_credit"]}


TOOL_FUNCTIONS = {"lookup_order": lookup_order, "track_shipment": track_shipment, "issue_store_credit": issue_store_credit}


def _tool(name, description, properties):
    return {
        "name": name,
        "description": description,
        "input_schema": {"type": "object", "properties": properties, "required": list(properties), "additionalProperties": False},
        "strict": True,
    }


TOOLS = [
    _tool("lookup_order", "Look up an order by ID (format B-1234). Call this whenever the customer mentions an order.",
          {"order_id": {"type": "string", "description": "Order ID such as B-1001"}}),
    _tool("track_shipment", "Get carrier status for a shipment ID (format SHP-1234). Call this when you need delivery status.",
          {"shipment_id": {"type": "string", "description": "Shipment ID such as SHP-1003"}}),
    _tool("issue_store_credit", "Add store credit (max $50) to a customer's account. Call this only when policy allows compensation.",
          {"customer_id": {"type": "string", "description": "Customer ID such as C-100"},
           "amount": {"type": "number", "description": "Dollars of credit, up to 50"},
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


def run_agent(client, question, max_steps=6):
    messages = [{"role": "user", "content": question}]
    trace = []
    for step in range(1, max_steps + 1):
        response = client.messages.create(model=MODEL, max_tokens=16000, system=SYSTEM_PROMPT, tools=TOOLS, messages=messages)
        messages.append({"role": "assistant", "content": response.content})
        if response.stop_reason != "tool_use":
            answer = "".join(b.text for b in response.content if b.type == "text")
            return {"answer": answer, "steps": step, "trace": trace}
        results = []
        for block in response.content:
            if block.type == "tool_use":
                result = execute(block)
                trace.append({"tool": block.name, "input": block.input, "is_error": result.get("is_error", False)})
                results.append(result)
        messages.append({"role": "user", "content": results})
    raise RuntimeError("agent did not finish within max_steps")


# --- Try it out (not graded) ---
result = run_agent(client, "My lamp order B-1001 is late. Can you check what's going on and make it right?")
if result:
    for i, t in enumerate(result["trace"], 1):
        print(f"step {i}: {t['tool']}({t['input']})" + ("  [error]" if t["is_error"] else ""))
    print(f"\n{result['steps']} API calls")
    print("Answer:", result["answer"])
    print("Maya's store credit now:", CUSTOMERS["C-100"]["store_credit"])
