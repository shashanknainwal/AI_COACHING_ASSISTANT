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
    # TODO
    pass


def files_using(call_sites, feature):
    """Sorted list of distinct files that use one feature."""
    # TODO
    pass


def audit_platform(name, matrix, call_sites, requirements, workarounds):
    """What breaks, and where, if this code moves to one platform."""
    # TODO
    pass


def port_report(matrix, call_sites, requirements, workarounds):
    """Audit every platform, best first."""
    # TODO
    pass


# --- Try it out (not graded) ---
for req in ({"residency": "us", "allow_beta": False}, {"residency": "us", "allow_beta": True}):
    print("Requirements:", req)
    for audit in port_report(PLATFORM_FEATURES, QUARRYBANK_PROTOTYPE, req, WORKAROUNDS) or []:
        print(f"  {audit['platform']:<20} {audit['verdict']:<16} rework: {', '.join(audit['rework_files']) or '-'}")
        for item in audit["open_items"]:
            print("      open:", item)
