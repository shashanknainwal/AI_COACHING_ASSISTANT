def run_attack_set(defenses, tools):
    """Run every attack under one configuration.

    Returns {"success_rate": float, "successes": [ids], "utility_ok": bool}.
    Use run_agent(attack, defenses, tools), attack_succeeded(attack, result) and keeps_utility(result).
    """
    # TODO
    return {"success_rate": 1.0, "successes": [], "utility_ok": True}


def least_privilege_tools():
    """The smallest tool set the task needs."""
    # TODO
    return list(ALL_TOOLS)


BASELINE_DEFENSES = []
HARDENED_DEFENSES = []      # TODO: pick the defences
HARDENED_TOOLS = list(ALL_TOOLS)  # TODO: narrow this

DEFENSE_FOR = {
    # "A1": "tool_allowlist", ...
}


def baseline():
    return run_attack_set(BASELINE_DEFENSES, list(ALL_TOOLS))


def hardened():
    return run_attack_set(HARDENED_DEFENSES, HARDENED_TOOLS)


# --- Try it out (not graded) ---
b, h = baseline(), hardened()
print(f"Baseline attack success rate: {b['success_rate']:.0%}  (got through: {b['successes']})")
print(f"Hardened attack success rate: {h['success_rate']:.0%}  utility kept: {h['utility_ok']}")
