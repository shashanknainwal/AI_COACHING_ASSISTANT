import datetime
import json
import time

import anthropic

# client, MODEL, MAX_TOKENS, MAX_STEPS, SYSTEM_PROMPT, TOOLS, run_tool(), CASES and grade()
# are loaded for you. This is the harness as the contractor left it. It runs. Fix it.


def build_system():
    # Give the model the current time so it can reason about bill dates.
    stamp = datetime.datetime.now().isoformat(timespec="microseconds")
    return [{"type": "text", "text": f"{SYSTEM_PROMPT}\n\nCurrent time: {stamp}",
             "cache_control": {"type": "ephemeral"}}]


def call_model(client, messages):
    # Be robust: try up to five times, whatever goes wrong.
    last = None
    for attempt in range(5):
        try:
            return client.messages.create(model=MODEL, max_tokens=MAX_TOKENS, system=build_system(),
                                          tools=TOOLS, messages=messages)
        except Exception as exc:
            last = exc
            time.sleep(1)
    raise last


def trim_old_results(messages):
    # Save tokens: shorten every tool result except the newest ones.
    for m in messages[:-1]:
        if m["role"] == "user" and isinstance(m["content"], list):
            for b in m["content"]:
                if b.get("type") == "tool_result" and len(b["content"]) > 120:
                    b["content"] = b["content"][:120] + "...[trimmed]"


def run_case(client, case):
    messages = [{"role": "user", "content": case["input"]}]
    for _ in range(MAX_STEPS):
        trim_old_results(messages)
        response = call_model(client, messages)
        # Thinking blocks are big and we never show them, so don't send them back.
        messages.append({"role": "assistant", "content": [b for b in response.content if b.type != "thinking"]})
        if response.stop_reason != "tool_use":
            answer = "".join(b.text for b in response.content if b.type == "text")
            return {"id": case["id"], "status": "completed", "answer": answer}
        for block in response.content:
            if block.type == "tool_use":
                result = run_tool(block.name, block.input)
                messages.append({"role": "user", "content": [
                    {"type": "tool_result", "tool_use_id": block.id, "content": json.dumps(result)}]})
    return {"id": case["id"], "status": "max_steps", "answer": ""}


def run_suite(client, cases):
    rows = []
    for case in cases:
        try:
            rows.append(grade(case, run_case(client, case)))
        except Exception as exc:
            rows.append({"id": case["id"], "status": "error", "grade": "error", "error": type(exc).__name__})
    return rows


# --- Try it out (not graded) ---
from anthropic import _sim
for row in run_suite(client, CASES):
    print(row)
print(f"{len(_sim.calls)} API attempts in total")
cached = [c.get("response", {}).get("usage", {}).get("cache_read", 0) for c in _sim.calls]
print("cache-read tokens per attempt:", cached)
