# Illustrative snapshot of the platform availability table (October 2026).
# Statuses: "yes", "beta", "partial" (only some deployments), "no".
# A real port re-checks every row against the current platform docs.
PLATFORM_FEATURES = {
    "claude_api": {
        "messages": "yes", "prompt_caching": "yes", "structured_outputs": "yes",
        "batches": "yes", "mcp_connector": "beta", "agent_skills": "yes",
        "code_execution": "yes", "files_api": "yes", "server_fallbacks": "beta",
        "inference_geo": "yes",
    },
    "claude_platform_aws": {
        "messages": "yes", "prompt_caching": "yes", "structured_outputs": "yes",
        "batches": "yes", "mcp_connector": "beta", "agent_skills": "yes",
        "code_execution": "yes", "files_api": "yes", "server_fallbacks": "beta",
        "inference_geo": "yes",
    },
    "bedrock": {
        "messages": "yes", "prompt_caching": "yes", "structured_outputs": "yes",
        "batches": "no", "mcp_connector": "no", "agent_skills": "no",
        "code_execution": "no", "files_api": "no", "server_fallbacks": "no",
        "inference_geo": "no",
    },
    "vertex": {
        "messages": "yes", "prompt_caching": "yes", "structured_outputs": "yes",
        "batches": "no", "mcp_connector": "no", "agent_skills": "no",
        "code_execution": "no", "files_api": "no", "server_fallbacks": "no",
        "inference_geo": "no",
    },
    "foundry": {
        "messages": "yes", "prompt_caching": "yes", "structured_outputs": "yes",
        "batches": "no", "mcp_connector": "beta", "agent_skills": "partial",
        "code_execution": "partial", "files_api": "partial", "server_fallbacks": "no",
        "inference_geo": "no",
    },
}

WORKAROUNDS = {
    "batches": "Run the backlog through a rate-limited worker pool on the Messages API (no 50% discount), or use the cloud's own batch service on its terms.",
    "mcp_connector": "Connect to the MCP server from your own code with an MCP client and pass its tools as ordinary tool definitions.",
    "agent_skills": "Load the skill's instructions into the system prompt and run its scripts in your own sandbox.",
    "code_execution": "Run generated code in your own sandboxed container.",
    "files_api": "Send documents inline as base64 content blocks on each request.",
    "server_fallbacks": "Catch stop_reason 'refusal' in your code and retry on an allowed fallback model yourself.",
}

VERDICT_ORDER = ["ready", "ready_with_beta", "confirm", "rework", "blocked"]

QUARRYBANK_PROTOTYPE = [
    {"file": "triage/classify.py", "feature": "messages"},
    {"file": "triage/classify.py", "feature": "structured_outputs"},
    {"file": "triage/classify.py", "feature": "prompt_caching"},
    {"file": "jobs/nightly_backfill.py", "feature": "batches"},
    {"file": "jobs/retry_failed.py", "feature": "batches"},
    {"file": "agent/tools.py", "feature": "mcp_connector"},
    {"file": "agent/runner.py", "feature": "server_fallbacks"},
    {"file": "reports/charts.py", "feature": "code_execution"},
]


def features_used(call_sites):
    """Sorted list of distinct features the code uses."""
    return sorted({site["feature"] for site in call_sites})


def files_using(call_sites, feature):
    """Sorted list of distinct files that use one feature."""
    return sorted({site["file"] for site in call_sites if site["feature"] == feature})


def audit_platform(name, matrix, call_sites, requirements, workarounds):
    """What breaks, and where, if this code moves to one platform."""
    features = matrix[name]
    allow_beta = bool(requirements.get("allow_beta"))
    blockers, beta, open_items = [], [], []

    for feature in features_used(call_sites):
        status = features.get(feature, "unknown")
        if status == "yes":
            continue
        if status == "beta" and allow_beta:
            beta.append(feature)
        elif status in ("no", "beta"):
            blockers.append({
                "feature": feature,
                "files": files_using(call_sites, feature),
                "workaround": workarounds.get(feature),
            })
        elif status == "partial":
            open_items.append(f"{feature}: only on some {name} deployments; confirm theirs")
        else:
            open_items.append(f"{feature}: not in the matrix; check the {name} docs")

    residency = None
    if requirements.get("residency"):
        if features.get("inference_geo") == "yes":
            residency = "inference_geo"
        else:
            residency = "confirm"
            open_items.append(
                f"residency: {requirements['residency']} is set by region or deployment on {name}; confirm the model is offered there"
            )

    if any(b["workaround"] is None for b in blockers):
        verdict = "blocked"
    elif blockers:
        verdict = "rework"
    elif open_items:
        verdict = "confirm"
    elif beta:
        verdict = "ready_with_beta"
    else:
        verdict = "ready"

    rework_files = sorted({f for b in blockers for f in b["files"]})
    return {
        "platform": name,
        "verdict": verdict,
        "blockers": blockers,
        "beta": beta,
        "open_items": open_items,
        "residency": residency,
        "rework_files": rework_files,
    }


def port_report(matrix, call_sites, requirements, workarounds):
    """Audit every platform, best first."""
    audits = [audit_platform(name, matrix, call_sites, requirements, workarounds) for name in matrix]
    return sorted(audits, key=lambda a: (VERDICT_ORDER.index(a["verdict"]), len(a["rework_files"]), a["platform"]))


# --- Try it out (not graded) ---
for req in ({"residency": "us", "allow_beta": False}, {"residency": "us", "allow_beta": True}):
    print("Requirements:", req)
    for audit in port_report(PLATFORM_FEATURES, QUARRYBANK_PROTOTYPE, req, WORKAROUNDS) or []:
        print(f"  {audit['platform']:<20} {audit['verdict']:<16} rework: {', '.join(audit['rework_files']) or '-'}")
        for item in audit["open_items"]:
            print("      open:", item)
