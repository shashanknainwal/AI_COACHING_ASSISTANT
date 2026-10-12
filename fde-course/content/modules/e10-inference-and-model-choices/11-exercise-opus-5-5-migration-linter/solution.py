"""A linter that flags request bodies that will fail (or misbehave) after moving to Claude Opus 5.5."""
import json

TARGET = "claude-opus-5-5"
SAMPLING = ("temperature", "top_p", "top_k")
MIN_MAX_TOKENS = 4_000   # Lumenfold's own rule: leave room for thinking


def finding(rule, severity, path, fix):
    return {"rule": rule, "severity": severity, "path": path, "fix": fix}


def lint(body, platform="anthropic"):
    """Return findings for one Messages API request body, in rule order.
    platform: "anthropic", "vertex" or "bedrock"."""
    out = []
    thinking = body.get("thinking") or {}
    if thinking.get("type") == "disabled":
        out.append(finding("THINKING_DISABLED", "error", "thinking.type",
                           "omit thinking and lower output_config.effort instead"))
    if thinking.get("type") == "enabled" or "budget_tokens" in thinking:
        out.append(finding("THINKING_BUDGET", "error", "thinking.budget_tokens",
                           "omit thinking and set output_config.effort"))
    tc = body.get("tool_choice") or {}
    if tc.get("type") in ("any", "tool"):
        out.append(finding("FORCED_TOOL_CHOICE", "error", "tool_choice.type",
                           "use auto + strict tools + a prompt instruction, and check a tool_use came back"))
    msgs = body.get("messages") or []
    if msgs and msgs[-1].get("role") == "assistant":
        content = msgs[-1].get("content")
        blocks = content if isinstance(content, list) else []
        if not any(isinstance(b, dict) and b.get("type") == "server_tool_use" for b in blocks):
            out.append(finding("PREFILL", "error", f"messages.{len(msgs) - 1}",
                               "end with a user turn; use output_config.format for structure"))
    for p in SAMPLING:
        if p in body:
            out.append(finding("SAMPLING_PARAM", "error", p, "remove it; steer with the prompt"))
    for i, tool in enumerate(body.get("tools") or []):
        if tool.get("type") == "computer_20251124":
            if platform == "bedrock":
                out.append(finding("COMPUTER_TOOL", "warning", f"tools.{i}.type",
                                   "still accepted on Bedrock; plan the move to computer_toolset_20260801"))
            else:
                out.append(finding("COMPUTER_TOOL", "error", f"tools.{i}.type",
                                   "declare {type: computer_toolset_20260801} and update the agent loop"))
    if "output_format" in body:
        out.append(finding("OUTPUT_FORMAT", "warning", "output_format", "move it to output_config.format"))
    if "effort" not in (body.get("output_config") or {}):
        out.append(finding("EFFORT_UNSET", "warning", "output_config.effort",
                           "set effort explicitly: the default on Opus 5.5 is medium"))
    if body.get("max_tokens", 0) < MIN_MAX_TOKENS:
        out.append(finding("MAX_TOKENS_LOW", "warning", "max_tokens",
                           "thinking counts toward max_tokens; leave room for it"))
    return out


def check_history(previous, current):
    """Compare the previous request with the next one in the same conversation.
    Returns a HISTORY_EDITED error finding (or None) when earlier turns carrying thinking blocks were changed."""
    prev_msgs = previous.get("messages") or []
    has_thinking = any(
        m.get("role") == "assistant" and isinstance(m.get("content"), list)
        and any(isinstance(b, dict) and b.get("type") in ("thinking", "redacted_thinking") for b in m["content"])
        for m in prev_msgs)
    if not has_thinking:
        return None
    for field in ("system", "tools"):
        if previous.get(field) != current.get(field):
            return finding("HISTORY_EDITED", "error", field,
                           "keep it byte-identical; append a role: system message or declare all tools up front")
    cur_msgs = current.get("messages") or []
    for i, m in enumerate(prev_msgs):
        if i >= len(cur_msgs) or json.dumps(cur_msgs[i], sort_keys=True) != json.dumps(m, sort_keys=True):
            return finding("HISTORY_EDITED", "error", f"messages.{i}",
                           "history must be append-only; use server-side compaction or context editing")
    return None


def will_400(body, platform="anthropic"):
    return any(f["severity"] == "error" for f in lint(body, platform))


def report(bodies, platform="anthropic"):
    """{rule: count} over many request bodies, plus "blocked": how many would 400."""
    counts = {"blocked": 0}
    for b in bodies:
        fs = lint(b, platform)
        for f in fs:
            counts[f["rule"]] = counts.get(f["rule"], 0) + 1
        if any(f["severity"] == "error" for f in fs):
            counts["blocked"] += 1
    return counts


# --- Try it out (not graded) ---
LOGGED_BODIES = [
    {"model": TARGET, "max_tokens": 1024, "temperature": 0,
     "tools": [{"name": "tag_article", "input_schema": {"type": "object"}}],
     "tool_choice": {"type": "tool", "name": "tag_article"},
     "messages": [{"role": "user", "content": "Tag this article: ..."}]},
    {"model": TARGET, "max_tokens": 8000, "thinking": {"type": "disabled"},
     "messages": [{"role": "user", "content": "Extract the byline as JSON."},
                  {"role": "assistant", "content": "{\"byline\": \""}]},
    {"model": TARGET, "max_tokens": 16000, "output_config": {"effort": "low"},
     "messages": [{"role": "user", "content": "Suggest five headlines."}]},
]
for body in LOGGED_BODIES:
    findings = lint(body)
    if findings is None:
        break
    print("will 400:", will_400(body))
    for f in findings:
        print("   ", f["severity"], f["rule"], "at", f["path"], "->", f["fix"])
print(report(LOGGED_BODIES))
