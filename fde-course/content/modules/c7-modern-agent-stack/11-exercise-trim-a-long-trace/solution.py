import copy
import json


def audit_append_only(prev, new):
    """List every way `new` breaks the append-only rule relative to `prev`. Empty list = safe."""
    problems = []
    if json.dumps(prev.get("system"), sort_keys=True) != json.dumps(new.get("system"), sort_keys=True):
        problems.append("system changed")
    if json.dumps(prev.get("tools"), sort_keys=True) != json.dumps(new.get("tools"), sort_keys=True):
        problems.append("tools changed")
    old, cur = prev.get("messages", []), new.get("messages", [])
    if len(cur) < len(old):
        problems.append("messages removed")
    for i, m in enumerate(old[:len(cur)]):
        if json.dumps(m, sort_keys=True) != json.dumps(cur[i], sort_keys=True):
            problems.append(f"message {i} changed")
            break
    return problems


def next_request(prev, last_response_content, user_text, new_rule):
    """Request 41: append-only, with the new rule as a system message and server-side clearing."""
    req = copy.deepcopy(prev)
    req["messages"] = copy.deepcopy(prev["messages"]) + [
        {"role": "assistant", "content": copy.deepcopy(last_response_content)},
        {"role": "user", "content": user_text},
        {"role": "system", "content": new_rule},
    ]
    req["betas"] = ["context-management-2025-06-27"]
    req["context_management"] = {"edits": [{"type": "clear_tool_uses_20250919"}]}
    return req


EDIT_CHOICES = {
    "delete_old_tool_results_client_side": "avoid",
    "server_side_tool_result_clearing": "use",
    "rewrite_system_prompt_with_new_rule": "avoid",
    "append_role_system_message": "use",
    "keep_tail_compaction_replaying_thinking": "avoid",
    "server_side_compaction": "use",
    "strip_all_thinking_every_request": "avoid",
    "remove_issue_credit_from_tools_array": "avoid",
}


# --- Try it out (not graded) ---
req = next_request(PREV_REQUEST, LAST_RESPONSE_CONTENT, NEW_USER_TEXT, NEW_RULE)
before, after = seen_tokens(naive_next_request()), seen_tokens(req)
print("Append-only problems:", audit_append_only(PREV_REQUEST, req) or "none")
print(f"Tokens the model reads: {before:,} -> {after:,} ({1 - after / before:.0%} less)")
broken = copy.deepcopy(req)
broken["system"] += " Escalate shipments over EUR 50,000."
print("Editing the system prompt instead:", audit_append_only(PREV_REQUEST, broken))
