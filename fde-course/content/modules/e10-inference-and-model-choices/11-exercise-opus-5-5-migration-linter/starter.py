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
    # TODO
    pass


def check_history(previous, current):
    """Compare the previous request with the next one in the same conversation.
    Returns a HISTORY_EDITED error finding (or None) when earlier turns carrying thinking blocks were changed."""
    # TODO
    pass


def will_400(body, platform="anthropic"):
    """True if lint() finds any error."""
    # TODO
    pass


def report(bodies, platform="anthropic"):
    """{rule: count} over many request bodies, plus "blocked": how many would 400."""
    # TODO
    pass


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
