import copy


def _brief(**kw):
    b = {"customer": "Test Co", "job": "resolve_customer_requests", "users": "customers",
         "inputs": ["chat", "email"], "daily_volume": 1000, "latency": "interactive",
         "platform": "anthropic_api", "write_actions": [], "labelled_examples": 500}
    b.update(kw)
    return b


def _codes(flags):
    return [f["code"] for f in flags]


def test_fit_scores():
    """fit_scores() adds job, user and input points for every pattern"""
    s = fit_scores(_brief(inputs=["chat", "email", "pdf"]))
    assert isinstance(s, dict) and set(s) == set(PATTERNS), f"score every pattern in PATTERNS; got {s}"
    assert s["support_automation"] == 5 + 2 + 2, f"job 5 + users 2 + two shared inputs = 9; got {s['support_automation']}"
    assert s["document_processing"] == 1, f"only 'pdf' overlaps document_processing; got {s['document_processing']}"
    assert s["knowledge_assistant"] == 0 and s["coding_assistant"] == 0, f"no overlap means 0; got {s}"
    s = fit_scores({"job": "x", "users": "y"})
    assert s == {p: 0 for p in PATTERNS}, f"missing inputs count as no inputs; got {s}"


def test_recommend_clear_and_close():
    """recommend() picks the best pattern and says whether the call is clear or close"""
    r = recommend(_brief(inputs=["chat", "email"]))
    assert r["pattern"] == "support_automation", f"got {r['pattern']}"
    assert r["confidence"] == "clear", f"9 vs 0 is a clear call; got {r['confidence']}"
    assert r["runner_up"] is None, "a runner-up with score 0 is no runner-up: use None"
    assert r["customer"] == "Test Co" and r["scores"]["support_automation"] == 9
    # Back-office team asking to "answer questions" over policies and PDFs: close call.
    b = _brief(job="answer_employee_questions", users="back_office", inputs=["pdf", "scans", "forms", "policies"])
    r = recommend(b)
    assert r["pattern"] == "knowledge_assistant", f"the job match (5 + 1 input = 6) wins; got {r['pattern']} with {r['scores']}"
    assert r["runner_up"] == "document_processing", f"got {r['runner_up']}"
    assert r["confidence"] == "close", f"6 vs 5 is within CLOSE_MARGIN; got {r['confidence']}"


def test_recommend_ties_and_no_fit():
    """Ties go to the earlier pattern in PATTERNS; a brief with too low a score gets no pattern"""
    # support_automation: job 5 + chat 1 = 6; coding_assistant: users 2 + four inputs = 6.
    b = _brief(users="developers", inputs=["repos", "pull_requests", "issues", "ci_logs", "chat"])
    r = recommend(b)
    assert r["scores"]["support_automation"] == 6 and r["scores"]["coding_assistant"] == 6, f"got {r['scores']}"
    assert r["pattern"] == "support_automation" and r["runner_up"] == "coding_assistant", \
        f"on a tie, the pattern listed first in PATTERNS wins; got {r['pattern']}, {r['runner_up']}"
    assert r["confidence"] == "close", f"a tie is a close call; got {r['confidence']}"

    b = _brief(job="nothing_we_know", users="customers", inputs=["chat", "email", "web_form", "phone_transcripts"])
    r = recommend(b)
    assert r["scores"]["support_automation"] == 6, f"users 2 + four inputs = 6; got {r['scores']}"
    assert r["pattern"] == "support_automation", "6 clears MIN_FIT even without a job match"
    b = _brief(job="nothing_we_know", users="employees", inputs=["chat", "email", "repos"])
    r = recommend(b)
    assert r["pattern"] is None and r["runner_up"] is None, f"best score 2 is below MIN_FIT; got {r['pattern']}"
    assert r["confidence"] == "no_fit" and r["go"] is False, f"got {r['confidence']}, go={r['go']}"


def test_mismatch_flags():
    """flags_for() reports latency, read-only and user mismatches against the pattern's assumptions"""
    b = _brief(job="answer_employee_questions", users="customers", latency="overnight", inputs=["wiki"],
               write_actions=[{"name": "file_ticket", "reversible": True, "max_usd": 0},
                              {"name": "reset_password", "reversible": True, "max_usd": 0}])
    f = flags_for(b, "knowledge_assistant")
    assert _codes(f) == ["read_only_pattern", "latency_mismatch", "users_mismatch"], \
        f"expected high, medium, low in that order; got {_codes(f)}"
    assert [x["severity"] for x in f] == ["high", "medium", "low"]
    assert "file_ticket" in f[0]["reason"] and "reset_password" in f[0]["reason"], \
        f"name every write action in the read-only reason; got {f[0]['reason']!r}"
    assert "overnight" in f[1]["reason"], f"say what latency the brief needs; got {f[1]['reason']!r}"
    assert flags_for(_brief(), "support_automation") == [], "a clean brief on its own pattern has no flags"


def test_action_flags():
    """Irreversible actions and actions above the $100 limit are high risks unless a human approves them"""
    acts = [{"name": "issue_refund", "reversible": False, "max_usd": 250},
            {"name": "send_voucher", "reversible": True, "max_usd": 100},
            {"name": "cancel_order", "reversible": False, "max_usd": 0},
            {"name": "wire_payment", "reversible": False, "max_usd": 5000, "human_approval": True}]
    f = flags_for(_brief(write_actions=acts), "support_automation")
    assert _codes(f) == ["approval_limit", "irreversible_action", "irreversible_action"], \
        f"sorted by severity then code, actions in brief order within a code; got {_codes(f)}"
    assert "issue_refund" in f[0]["reason"] and "250" in f[0]["reason"], f"name the action and amount; got {f[0]['reason']!r}"
    assert "issue_refund" in f[1]["reason"] and "cancel_order" in f[2]["reason"], [x["reason"] for x in f]
    assert all("wire_payment" not in x["reason"] for x in f), "human_approval: True clears both action flags"
    assert all("send_voucher" not in x["reason"] for x in f), "exactly $100 is within the limit"


def test_pattern_specific_risks():
    """Review overflow, permission sync and unguarded repo writes only apply to their own pattern"""
    b = _brief(daily_volume=9000, review_capacity_per_day=900)
    f = flags_for(b, "document_processing")
    over = [x for x in f if x["code"] == "review_queue_overflow"]
    assert over and over[0]["severity"] == "high", f"9000 x 0.15 = 1350 reviews > 900; got {_codes(f)}"
    assert "1350" in over[0]["reason"] and "900" in over[0]["reason"], f"show both numbers; got {over[0]['reason']!r}"
    f = flags_for(dict(b, review_rate=0.1), "document_processing")
    assert "review_queue_overflow" not in _codes(f), "900 expected reviews fits a capacity of 900"
    assert "review_queue_overflow" not in _codes(flags_for(b, "support_automation")), "only for document_processing"

    k = _brief(per_user_permissions=True)
    assert "permissions_sync" in _codes(flags_for(k, "knowledge_assistant"))
    assert "permissions_sync" not in _codes(flags_for(dict(k, acl_sync_in_scope=True), "knowledge_assistant"))
    assert "permissions_sync" not in _codes(flags_for(k, "support_automation"))

    c = _brief(agent_can_push=True)
    assert "unguarded_repo_writes" in _codes(flags_for(c, "coding_assistant"))
    assert "unguarded_repo_writes" not in _codes(flags_for(dict(c, branch_protection=True), "coding_assistant"))


def test_general_risks():
    """Golden set, batch availability and citations-with-schema apply whatever the pattern"""
    f = flags_for(_brief(labelled_examples=40), "support_automation")
    assert _codes(f) == ["no_golden_set"] and "40" in f[0]["reason"], f"got {f}"
    assert flags_for(_brief(labelled_examples=100), "support_automation") == [], "exactly 100 is enough"
    assert "no_golden_set" in _codes(flags_for({"customer": "x"}, None)), "missing labelled_examples counts as 0"

    for platform in ("bedrock", "vertex", "foundry"):
        f = flags_for(_brief(latency="overnight", platform=platform), "document_processing")
        assert "batch_unavailable" in _codes(f), f"no Message Batches on {platform}; got {_codes(f)}"
    for platform in ("anthropic_api", "claude_platform_aws"):
        f = flags_for(_brief(latency="overnight", platform=platform), "document_processing")
        assert "batch_unavailable" not in _codes(f), f"Message Batches works on {platform}"
    f = flags_for(_brief(latency="minutes", platform="bedrock"), "document_processing")
    assert "batch_unavailable" not in _codes(f), "only overnight work needs batch"

    f = flags_for(_brief(needs_citations=True, needs_structured_output=True), "support_automation")
    assert f and f[0]["code"] == "citations_with_schema" and f[0]["severity"] == "low", f"got {f}"


def test_go_decision():
    """go is True only when a pattern fits and no high-severity flag remains"""
    assert recommend(_brief())["go"] is True
    assert recommend(_brief(labelled_examples=10))["go"] is True, "medium flags don't block go"
    r = recommend(_brief(write_actions=[{"name": "close_account", "reversible": False, "max_usd": 0}]))
    assert r["go"] is False and r["flags"][0]["code"] == "irreversible_action", r


def test_grace_briefs():
    """The five briefs in BRIEFS come out as Grace expects (and are not modified)"""
    before = copy.deepcopy(BRIEFS)
    got = {b["customer"]: recommend(b) for b in BRIEFS}
    assert BRIEFS == before, "don't modify the briefs"
    fen = got["Fenwick Outdoor"]
    assert fen["pattern"] == "support_automation" and fen["go"] is False
    assert _codes(fen["flags"]) == ["approval_limit", "irreversible_action"], _codes(fen["flags"])
    ost = got["Ostrava Re"]
    assert ost["pattern"] == "document_processing"
    assert _codes(ost["flags"]) == ["review_queue_overflow", "batch_unavailable"], _codes(ost["flags"])
    hal = got["Halden Pharma"]
    assert _codes(hal["flags"]) == ["permissions_sync", "read_only_pattern", "citations_with_schema"], _codes(hal["flags"])
    qua = got["Quayside Bank"]
    assert qua["pattern"] == "coding_assistant" and qua["go"] is True and _codes(qua["flags"]) == ["no_golden_set"]
    mar = got["Marlow General Hospital"]
    assert mar["pattern"] is None and mar["confidence"] == "no_fit"
    assert _codes(mar["flags"]) == ["no_golden_set"], "with no pattern, only the general risks apply"
