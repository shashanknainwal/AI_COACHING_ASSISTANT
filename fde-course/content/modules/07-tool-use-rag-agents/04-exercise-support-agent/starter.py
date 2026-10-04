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
    # TODO
    pass


def track_shipment(shipment_id):
    # TODO
    pass


def issue_store_credit(customer_id, amount, reason):
    # TODO
    pass


TOOL_FUNCTIONS = {"lookup_order": lookup_order, "track_shipment": track_shipment, "issue_store_credit": issue_store_credit}

# TODO: three strict tool definitions
TOOLS = []


def execute(block):
    """Run one tool_use block and return a tool_result dict."""
    # TODO
    pass


def run_agent(client, question, max_steps=6):
    """The agent loop. Returns {"answer", "steps", "trace"}."""
    # TODO
    pass


# --- Try it out (not graded) ---
result = run_agent(client, "My lamp order B-1001 is late. Can you check what's going on and make it right?")
if result:
    for i, t in enumerate(result["trace"], 1):
        print(f"step {i}: {t['tool']}({t['input']})" + ("  [error]" if t["is_error"] else ""))
    print(f"\n{result['steps']} API calls")
    print("Answer:", result["answer"])
    print("Maya's store credit now:", CUSTOMERS["C-100"]["store_credit"])
