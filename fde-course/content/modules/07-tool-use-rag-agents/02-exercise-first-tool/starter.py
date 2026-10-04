import json
import anthropic
from fde_datasets.brightway import ORDERS

client = anthropic.Anthropic()
MODEL = "claude-opus-5-5"
SYSTEM_PROMPT = "You are Brightway Retail's customer-service assistant. Use tools to look up real order data; never guess."


# TODO: a strict tool definition named "lookup_order"
LOOKUP_ORDER_TOOL = {}


def lookup_order(order_id):
    """Order summary dict, or KeyError for unknown IDs."""
    # TODO
    pass


def run_tool(block):
    """Run one tool_use block and return a tool_result dict."""
    # TODO
    pass


def answer(client, question):
    """Question -> (tool call ->) final answer text."""
    # TODO
    pass


# --- Try it out (not graded) ---
for q in ["Where is my order B-1001?", "What's happening with order b-9999?", "Hi, I need help"]:
    print("Customer: ", q)
    print("Assistant:", answer(client, q))
    print()
