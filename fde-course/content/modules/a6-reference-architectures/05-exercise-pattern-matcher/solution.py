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
SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def fit_scores(brief):
    """{pattern: score} for every pattern in PATTERNS."""
    inputs = set(brief.get("inputs", []))
    scores = {}
    for p in PATTERNS:
        f = FIT[p]
        s = 0
        if brief.get("job") == f["job"]:
            s += JOB_POINTS
        if brief.get("users") in f["users"]:
            s += USER_POINTS
        s += INPUT_POINTS * len(inputs & f["inputs"])
        scores[p] = s
    return scores


def _flag(code, severity, reason):
    return {"code": code, "severity": severity, "reason": reason}


def flags_for(brief, pattern):
    """Mismatches and risks for running `brief` on `pattern` (pattern may be None)."""
    flags = []
    actions = brief.get("write_actions", [])

    if pattern is not None:
        a = ASSUMES[pattern]
        if brief.get("latency") not in a["latency"]:
            flags.append(_flag("latency_mismatch", "medium",
                               f"{pattern} assumes {sorted(a['latency'])} latency, brief needs {brief.get('latency')}"))
        if actions and not a["write_actions_ok"]:
            names = ", ".join(x["name"] for x in actions)
            flags.append(_flag("read_only_pattern", "high",
                               f"{pattern} is read-only but the brief needs write actions: {names}"))
        if brief.get("users") not in FIT[pattern]["users"]:
            flags.append(_flag("users_mismatch", "low",
                               f"{pattern} is built for {sorted(FIT[pattern]['users'])}, brief serves {brief.get('users')}"))

    for x in actions:
        if x.get("human_approval"):
            continue
        if not x.get("reversible", True):
            flags.append(_flag("irreversible_action", "high",
                               f"{x['name']} can't be undone: put a human approval step in front of it"))
        if x.get("max_usd", 0) > AUTO_APPROVE_LIMIT_USD:
            flags.append(_flag("approval_limit", "high",
                               f"{x['name']} can move up to ${x['max_usd']}, above the ${AUTO_APPROVE_LIMIT_USD} auto-approve limit"))

    if pattern == "document_processing":
        expected = round(brief.get("daily_volume", 0) * brief.get("review_rate", DEFAULT_REVIEW_RATE))
        capacity = brief.get("review_capacity_per_day", 0)
        if expected > capacity:
            flags.append(_flag("review_queue_overflow", "high",
                               f"about {expected} reviews a day against capacity {capacity}"))
    if pattern == "knowledge_assistant" and brief.get("per_user_permissions") and not brief.get("acl_sync_in_scope"):
        flags.append(_flag("permissions_sync", "high",
                           "documents have per-user permissions but permission sync is not in scope"))
    if pattern == "coding_assistant" and brief.get("agent_can_push") and not brief.get("branch_protection"):
        flags.append(_flag("unguarded_repo_writes", "high",
                           "the agent can push code but branches aren't protected by required human review"))

    labelled = brief.get("labelled_examples", 0)
    if labelled < MIN_GOLDEN_SET:
        flags.append(_flag("no_golden_set", "medium",
                           f"only {labelled} labelled examples; build a golden set of at least {MIN_GOLDEN_SET} before launch"))
    if brief.get("latency") == "overnight" and brief.get("platform") in NO_BATCH_PLATFORMS:
        flags.append(_flag("batch_unavailable", "medium",
                           f"Message Batches isn't available on {brief.get('platform')}: budget at standard prices or check the cloud's own batch option"))
    if brief.get("needs_citations") and brief.get("needs_structured_output"):
        flags.append(_flag("citations_with_schema", "low",
                           "citations and structured outputs can't be combined in one request"))

    flags.sort(key=lambda f: (SEVERITY_ORDER[f["severity"]], f["code"]))
    return flags


def recommend(brief):
    """Pick a reference architecture for a customer brief and explain the risks."""
    scores = fit_scores(brief)
    ranked = sorted(PATTERNS, key=lambda p: (-scores[p], PATTERNS.index(p)))
    best, second = ranked[0], ranked[1]
    if scores[best] < MIN_FIT:
        pattern, runner_up, confidence = None, None, "no_fit"
    else:
        pattern = best
        runner_up = second if scores[second] > 0 else None
        confidence = "close" if scores[best] - scores[second] <= CLOSE_MARGIN else "clear"
    flags = flags_for(brief, pattern)
    go = pattern is not None and not any(f["severity"] == "high" for f in flags)
    return {"customer": brief.get("customer"), "pattern": pattern, "runner_up": runner_up,
            "confidence": confidence, "scores": scores, "flags": flags, "go": go}


# --- Try it out (not graded) ---
for b in BRIEFS:
    r = recommend(b)
    if not r:
        print(b["customer"], "-> (not implemented yet)")
        continue
    print(f"{r['customer']}: {r['pattern']} ({r['confidence']}), go={r['go']}")
    for f in r["flags"]:
        print(f"   [{f['severity']}] {f['code']}: {f['reason']}")
