def run_attack_set(defenses, tools):
    """Run every attack under one configuration. Returns success rate, the attacks that got through, and utility."""
    successes = [a["id"] for a in ATTACKS if attack_succeeded(a, run_agent(a, defenses, tools))]
    utility_ok = all(keeps_utility(run_agent(a, defenses, tools)) for a in ATTACKS)
    return {"success_rate": len(successes) / len(ATTACKS), "successes": successes, "utility_ok": utility_ok}


def least_privilege_tools():
    """The smallest tool set the task needs: the two read tools, and no write tools."""
    return list(TASK_TOOLS)


# Each defence and the attacks it stops.
#   data_marking   - fences untrusted tool output and docs so plain planted instructions are ignored
#   url_filter     - drops output links to hosts outside the allowlist
#   tool_allowlist - the agent never holds send_email or issue_credit, so it can't call them
BASELINE_DEFENSES = []
HARDENED_DEFENSES = ["data_marking", "url_filter"]
HARDENED_TOOLS = least_privilege_tools()

# Which single defence stops each attack (the first line of defence; others may also help).
DEFENSE_FOR = {
    "A1": "tool_allowlist",   # marker in tool output tries to call send_email
    "A2": "url_filter",       # marker in a doc tries to add an off-allowlist link
    "A3": "tool_allowlist",   # a stronger marker ignores the fence, but the write tool isn't there
    "A4": "tool_allowlist",   # a poisoned tool description tries to call send_email
}


def baseline():
    return run_attack_set(BASELINE_DEFENSES, list(ALL_TOOLS))


def hardened():
    return run_attack_set(HARDENED_DEFENSES, HARDENED_TOOLS)


# --- Try it out (not graded) ---
b, h = baseline(), hardened()
print(f"Baseline attack success rate: {b['success_rate']:.0%}  (got through: {b['successes']})")
print(f"Hardened attack success rate: {h['success_rate']:.0%}  utility kept: {h['utility_ok']}")
print("Tools before:", list(ALL_TOOLS), "-> after:", HARDENED_TOOLS)
