"""Hidden setup: a 40-request trace from Cindervale's (fictional) disruption agent on Opus 5.5."""
import copy
import json

MODEL = "claude-opus-5-5"

SYSTEM = (
    "You are Cindervale Freight's disruption agent. You look up shipments, carrier status and depot "
    "capacity, and you propose reroutes for a human to approve. Be concise. Cite shipment IDs."
)

TOOLS = [
    {"name": n, "description": d, "input_schema": {"type": "object", "properties": {"id": {"type": "string"}}, "required": ["id"]}}
    for n, d in [
        ("get_shipment", "Get one shipment. Call this when you need a shipment's status or route."),
        ("carrier_status", "Get a carrier's live status board. Call this when a carrier may be disrupted."),
        ("depot_capacity", "Get a depot's capacity for the next 72 hours. Call this before proposing a reroute."),
        ("weather_alerts", "Get weather alerts for a region. Call this when weather may cause delays."),
        ("propose_reroute", "Record a reroute proposal for human approval. Call this only after checking capacity."),
        ("issue_credit", "Issue a customer credit. Call this only when a human has approved it."),
    ]
]

_TOOL_CYCLE = ["get_shipment", "carrier_status", "depot_capacity", "weather_alerts"]


def _tool_output(i):
    # Long, mostly stale status dumps: the kind of output that fills a long agent's context.
    rows = [f"row {r}: lane RTM-LYS slot {r % 12} status {'ok' if (i + r) % 5 else 'delayed'} eta +{(i * r) % 9}h"
            for r in range(90)]
    return f"[{_TOOL_CYCLE[i % 4]} result #{i}]\n" + "\n".join(rows)


_messages = [{"role": "user", "content": "A strike has closed the Rotterdam depot until Friday. Check every Lyon-bound shipment and propose reroutes."}]
for _i in range(1, 40):
    _tid = f"toolu_{_i:03d}"
    _messages.append({"role": "assistant", "content": [
        {"type": "thinking", "thinking": "", "signature": f"sig_{_i:03d}_bound_to_prefix"},
        {"type": "tool_use", "id": _tid, "name": _TOOL_CYCLE[_i % 4], "input": {"id": f"CV-{1000 + _i}"}},
    ]})
    _messages.append({"role": "user", "content": [{"type": "tool_result", "tool_use_id": _tid, "content": _tool_output(_i)}]})

# The body sent on request 40 (39 tool rounds so far). Treat it as read-only.
PREV_REQUEST = {"model": MODEL, "max_tokens": 16000, "system": SYSTEM, "tools": TOOLS,
                "output_config": {"effort": "medium"}, "messages": _messages}

# The response to request 40: a thinking block, then a progress summary.
LAST_RESPONSE_CONTENT = [
    {"type": "thinking", "thinking": "", "signature": "sig_040_bound_to_prefix"},
    {"type": "text", "text": "Checked 39 items. 6 Lyon-bound shipments need reroutes; Antwerp and Le Havre have capacity. Proposals drafted for CV-1004, CV-1011, CV-1018."},
]

NEW_USER_TEXT = "Good. Draft the remaining three proposals, then stop."
NEW_RULE = "From now on, flag any shipment worth more than EUR 50,000 for a human before proposing a reroute."


def seen_tokens(request):
    """Simulated server view: roughly how many input tokens the model reads for this request.

    It applies the server-side strategies this course covers, the way the API applies them
    before the model sees the conversation (the check for edited history looks at what you
    sent, not at this edited copy):
      - clear_tool_uses_20250919 (beta context-management-2025-06-27): replaces the content of
        every tool result except the three most recent with a short placeholder. In the real API,
        when it triggers and how many results it keeps are configurable; see the context-editing docs.
      - clear_thinking_20251015 (same beta): removes thinking blocks except in the latest assistant turn.
    """
    req = copy.deepcopy(request)
    betas = req.get("betas") or []
    edits = [e.get("type") for e in (req.get("context_management") or {}).get("edits", [])]
    on = "context-management-2025-06-27" in betas
    msgs = req.get("messages", [])
    if on and "clear_tool_uses_20250919" in edits:
        results = [b for m in msgs if isinstance(m.get("content"), list) for b in m["content"]
                   if isinstance(b, dict) and b.get("type") == "tool_result"]
        for b in results[:-3]:
            b["content"] = "[tool result cleared]"
    if on and "clear_thinking_20251015" in edits:
        last_assistant = max((i for i, m in enumerate(msgs) if m.get("role") == "assistant"), default=-1)
        for i, m in enumerate(msgs):
            if m.get("role") == "assistant" and i != last_assistant and isinstance(m.get("content"), list):
                m["content"] = [b for b in m["content"] if b.get("type") != "thinking"]
    raw = json.dumps([req.get("system"), req.get("tools"), msgs])
    return len(raw) // 4


def naive_next_request():
    """Append-only, with no context management: the baseline your request must beat."""
    req = copy.deepcopy(PREV_REQUEST)
    req["messages"] += [{"role": "assistant", "content": copy.deepcopy(LAST_RESPONSE_CONTENT)},
                        {"role": "user", "content": NEW_USER_TEXT}]
    return req

# Edits the team proposed in the incident channel. Decide "use" or "avoid" for each.
CANDIDATE_EDITS = {
    "delete_old_tool_results_client_side": "Remove the content of old tool_result blocks from messages before sending.",
    "server_side_tool_result_clearing": "Send context_management with clear_tool_uses_20250919 and let the API clear old results.",
    "rewrite_system_prompt_with_new_rule": "Add the EUR 50,000 rule to the top-level system prompt.",
    "append_role_system_message": "Append the EUR 50,000 rule as a role 'system' message after the new user turn.",
    "keep_tail_compaction_replaying_thinking": "Summarise turns 1-30 client-side, keep turns 31-40 verbatim with their thinking blocks.",
    "server_side_compaction": "Turn on the API's server-side compaction and append response.content every turn.",
    "strip_all_thinking_every_request": "Remove every thinking block from the history on every request to save tokens.",
    "remove_issue_credit_from_tools_array": "Delete issue_credit from tools mid-session so the agent can't call it.",
}
