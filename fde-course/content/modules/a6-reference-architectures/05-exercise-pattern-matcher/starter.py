PATTERNS = ["support_automation", "document_processing", "knowledge_assistant", "coding_assistant"]

# What each reference architecture is built for.
FIT = {
    "support_automation": {"job": "resolve_customer_requests", "users": {"customers"},
                           "inputs": {"chat", "email", "phone_transcripts", "web_form"}},
    "document_processing": {"job": "extract_from_documents", "users": {"back_office"},
                            "inputs": {"pdf", "scans", "email_attachments", "forms"}},
    "knowledge_assistant": {"job": "answer_employee_questions", "users": {"employees"},
                            "inputs": {"wiki", "shared_drives", "policies", "ticket_archive"}},
    "coding_assistant": {"job": "assist_developers", "users": {"developers"},
                         "inputs": {"repos", "pull_requests", "issues", "ci_logs"}},
}

# What each pattern assumes about the deployment.
ASSUMES = {
    "support_automation": {"latency": {"interactive"}, "write_actions_ok": True},
    "document_processing": {"latency": {"minutes", "overnight"}, "write_actions_ok": True},
    "knowledge_assistant": {"latency": {"interactive"}, "write_actions_ok": False},
    "coding_assistant": {"latency": {"interactive", "minutes"}, "write_actions_ok": True},
}

JOB_POINTS, USER_POINTS, INPUT_POINTS = 5, 2, 1
MIN_FIT = 5                  # below this, no pattern fits: the job itself doesn't match
CLOSE_MARGIN = 2             # best minus runner-up at or below this is a "close" call
AUTO_APPROVE_LIMIT_USD = 100
MIN_GOLDEN_SET = 100
DEFAULT_REVIEW_RATE = 0.15
# Message Batches is listed for the Claude API and Claude Platform on AWS only
# (Anthropic's platform availability table, checked 2026-10-08).
NO_BATCH_PLATFORMS = {"bedrock", "vertex", "foundry"}
# Structured outputs on Bedrock split by integration (checked 2026-10-10): the newer
# Messages-API endpoint lists them as not supported; the legacy InvokeModel
# integration supports them for some models. Flag it so someone confirms which.
STRUCTURED_OUTPUT_CHECK_PLATFORMS = {"bedrock"}
SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def fit_scores(brief):
    """{pattern: score} for every pattern in PATTERNS."""
    # TODO: JOB_POINTS if the job matches, USER_POINTS if the users match,
    # INPUT_POINTS for each input the brief shares with FIT[pattern]["inputs"].
    pass


def flags_for(brief, pattern):
    """Mismatches and risks for running `brief` on `pattern` (pattern may be None).

    Returns a list of {"code", "severity", "reason"} dicts sorted by severity
    (high, medium, low) and then by code.
    """
    # TODO
    pass


def recommend(brief):
    """Pick a reference architecture for a customer brief and explain the risks."""
    # TODO: return {"customer", "pattern", "runner_up", "confidence", "scores", "flags", "go"}
    pass


# --- Try it out (not graded) ---
for b in BRIEFS:
    r = recommend(b)
    if not r:
        print(b["customer"], "-> (not implemented yet)")
        continue
    print(f"{r['customer']}: {r['pattern']} ({r['confidence']}), go={r['go']}")
    for f in r["flags"]:
        print(f"   [{f['severity']}] {f['code']}: {f['reason']}")
