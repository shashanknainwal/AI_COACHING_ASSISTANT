import json

import anthropic

# client, MODEL, MAX_TOKENS, MAX_STEPS, SYSTEM_PROMPT, TOOLS, run_tool(), CASES and grade()
# are loaded for you.

# Bug 1 fixed: the system prompt is byte-identical on every request, so the cached
# prefix (tools + system) is reused. If the model needs today's date, put the date
# (not a timestamp) in the first user message instead.
SYSTEM = [{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}]


def call_model(client, messages):
    # Bug 4 fixed: the SDK already retries 429, 5xx and connection errors with backoff
    # (max_retries=2 by default). A second retry loop on top multiplies attempts, and
    # retrying a 400 can never succeed. One call; let errors surface.
    return client.messages.create(model=MODEL, max_tokens=MAX_TOKENS, system=SYSTEM,
                                  tools=TOOLS, messages=messages)


def run_case(client, case):
    messages = [{"role": "user", "content": case["input"]}]
    for _ in range(MAX_STEPS):
        response = call_model(client, messages)
        # Bug 3 fixed: append exactly what came back, thinking blocks included, and
        # never edit earlier turns. The history is append-only.
        messages.append({"role": "assistant", "content": response.content})
        if response.stop_reason != "tool_use":
            answer = "".join(b.text for b in response.content if b.type == "text")
            return {"id": case["id"], "status": "completed", "answer": answer}
        # Bug 2 fixed: every tool_result for this turn goes in ONE user message.
        results = [{"type": "tool_result", "tool_use_id": b.id, "content": json.dumps(run_tool(b.name, b.input))}
                   for b in response.content if b.type == "tool_use"]
        messages.append({"role": "user", "content": results})
    return {"id": case["id"], "status": "max_steps", "answer": ""}


def run_suite(client, cases):
    rows = []
    for case in cases:
        try:
            rows.append(grade(case, run_case(client, case)))
        except anthropic.APIError as exc:
            rows.append({"id": case["id"], "status": "error", "grade": "error", "error": type(exc).__name__})
    return rows


# --- Try it out (not graded) ---
from anthropic import _sim
for row in run_suite(client, CASES):
    print(row)
print(f"{len(_sim.calls)} API attempts in total")
cached = [c.get("response", {}).get("usage", {}).get("cache_read", 0) for c in _sim.calls]
print("cache-read tokens per attempt:", cached)
