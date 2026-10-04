import json
import anthropic
from fde_datasets.brightway import ORDERS

client = anthropic.Anthropic()
MODEL = "claude-opus-5-5"
SYSTEM_PROMPT = "You are Brightway Retail's customer-service assistant. Use tools to look up real order data; never guess."


LOOKUP_ORDER_TOOL = {
    "name": "lookup_order",
    "description": (
        "Look up a Brightway order by its order ID (format B-1234). Returns status, total, item names and "
        "shipment ID. Call this whenever the customer mentions an order number or asks about an order."
    ),
    "input_schema": {
        "type": "object",
        "properties": {"order_id": {"type": "string", "description": "Order ID such as B-1001"}},
        "required": ["order_id"],
        "additionalProperties": False,
    },
    "strict": True,
}


def lookup_order(order_id):
    oid = order_id.strip().upper()
    if oid not in ORDERS:
        raise KeyError(f"No order found with ID {oid}.")
    o = ORDERS[oid]
    return {"order_id": oid, "status": o["status"], "total": o["total"],
            "items": [i["name"] for i in o["items"]], "shipment_id": o["shipment_id"]}


def run_tool(block):
    result = {"type": "tool_result", "tool_use_id": block.id}
    if block.name != "lookup_order":
        return dict(result, content=f"Unknown tool: {block.name}", is_error=True)
    try:
        return dict(result, content=json.dumps(lookup_order(block.input["order_id"])))
    except KeyError as e:
        return dict(result, content=e.args[0], is_error=True)


def _text(response):
    return "".join(b.text for b in response.content if b.type == "text")


def answer(client, question):
    messages = [{"role": "user", "content": question}]
    params = dict(model=MODEL, max_tokens=16000, system=SYSTEM_PROMPT, tools=[LOOKUP_ORDER_TOOL])
    response = client.messages.create(messages=messages, **params)
    if response.stop_reason != "tool_use":
        return _text(response)
    results = [run_tool(b) for b in response.content if b.type == "tool_use"]
    messages += [{"role": "assistant", "content": response.content}, {"role": "user", "content": results}]
    return _text(client.messages.create(messages=messages, **params))


# --- Try it out (not graded) ---
for q in ["Where is my order B-1001?", "What's happening with order b-9999?", "Hi, I need help"]:
    print("Customer: ", q)
    print("Assistant:", answer(client, q))
    print()
