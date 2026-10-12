def _gate():
    g = ToolGate()
    g.add_tool(0, "lookup", "crm:read")
    g.add_tool(0, "update", "crm:write")
    g.add_tool(0, "refund", "billing:write")
    return g


# Level 1 ----------------------------------------------------------------
def test_l1_exact_grant_allows_one_tool():
    """A direct grant allows tools with exactly that scope"""
    g = _gate()
    assert g.call(1, "bot", "lookup") == "denied", "no grants yet"
    assert g.grant(2, "bot", "crm:read") is True
    assert g.call(3, "bot", "lookup") == "allowed"
    assert g.call(4, "bot", "update") == "denied", "crm:read doesn't cover crm:write"
    assert g.call(5, "bot", "nope") == "unknown_tool"


def test_l1_wildcards():
    """'crm:*' covers every crm scope and '*' covers everything"""
    g = _gate()
    g.grant(1, "bot", "crm:*")
    assert g.call(2, "bot", "lookup") == "allowed"
    assert g.call(3, "bot", "update") == "allowed"
    assert g.call(4, "bot", "refund") == "denied"
    g.grant(5, "root", "*")
    assert g.call(6, "root", "refund") == "allowed"


def test_l1_wildcard_needs_the_colon():
    """'crm:*' must not match a scope like 'crmx:read'"""
    g = _gate()
    g.add_tool(1, "odd", "crmx:read")
    g.grant(2, "bot", "crm:*")
    assert g.call(3, "bot", "odd") == "denied"


def test_l1_add_tool_grant_and_revoke_return_values():
    """Duplicate tools and grants return False; revoke works once"""
    g = _gate()
    assert g.add_tool(1, "lookup", "other:read") is False, "tool names are unique"
    assert g.grant(2, "bot", "crm:read") is True
    assert g.grant(3, "bot", "crm:read") is False, "already granted"
    assert g.revoke(4, "bot", "crm:read") is True
    assert g.revoke(5, "bot", "crm:read") is False
    assert g.revoke(6, "bot", "crm:*") is False, "revoke matches the exact grant string"
    assert g.call(7, "bot", "lookup") == "denied"


def test_l1_revoke_exact_keeps_wildcard():
    """Revoking an exact scope leaves a wildcard grant in place"""
    g = _gate()
    g.grant(1, "bot", "crm:*")
    g.grant(2, "bot", "crm:read")
    g.revoke(3, "bot", "crm:read")
    assert g.call(4, "bot", "lookup") == "allowed", "crm:* still covers it"


# Level 2 ----------------------------------------------------------------
def test_l2_roles_grant_scopes():
    """Assigned roles add their scopes; redefining a role takes effect at once"""
    g = _gate()
    assert g.assign(1, "ana", "support") is False, "role not defined yet"
    g.define_role(2, "support", ["crm:read"])
    assert g.assign(3, "ana", "support") is True
    assert g.assign(4, "ana", "support") is False, "already assigned"
    assert g.call(5, "ana", "lookup") == "allowed"
    assert g.call(6, "ana", "update") == "denied"
    g.define_role(7, "support", ["crm:*"])
    assert g.call(8, "ana", "update") == "allowed", "the new definition applies to existing members"
    assert g.unassign(9, "ana", "support") is True
    assert g.unassign(10, "ana", "support") is False
    assert g.call(11, "ana", "lookup") == "denied"


def test_l2_deny_beats_every_grant():
    """An explicit deny wins over direct, wildcard and role grants"""
    g = _gate()
    g.define_role(1, "admin", ["*"])
    g.assign(2, "max", "admin")
    g.grant(3, "max", "billing:write")
    assert g.call(4, "max", "refund") == "allowed"
    g.deny(5, "max", "billing:*")
    assert g.call(6, "max", "refund") == "denied"
    assert g.call(7, "max", "update") == "allowed", "the deny only covers billing"


def test_l2_explain_lists_sources_sorted():
    """explain shows every matching source, sorted, and None for unknown tools"""
    g = _gate()
    g.define_role(1, "support", ["crm:read", "crm:*"])
    g.define_role(2, "ops", ["crm:read"])
    g.assign(3, "ana", "support")
    g.assign(4, "ana", "ops")
    g.grant(5, "ana", "crm:read")
    assert g.explain(6, "ana", "lookup") == ["direct:crm:read", "role:ops", "role:support"], "a role is listed once"
    g.deny(7, "ana", "crm:read")
    assert g.explain(8, "ana", "lookup") == ["deny:crm:read", "direct:crm:read", "role:ops", "role:support"]
    assert g.explain(9, "ana", "refund") == []
    assert g.explain(10, "ana", "ghost") is None


def test_l2_unassign_keeps_other_paths():
    """Removing one path to a scope leaves the others working"""
    g = _gate()
    g.define_role(1, "a", ["crm:read"])
    g.define_role(2, "b", ["crm:*"])
    g.assign(3, "u", "a")
    g.assign(4, "u", "b")
    g.unassign(5, "u", "a")
    assert g.call(6, "u", "lookup") == "allowed"
    assert g.explain(7, "u", "lookup") == ["role:b"]


# Level 3 ----------------------------------------------------------------
def _approvals():
    g = _gate()
    g.define_role(0, "lead", ["crm:read"])
    g.grant(0, "bot", "billing:write")
    g.assign(0, "lena", "lead")
    g.require_approval(0, "refund", "lead", 100)
    return g


def test_l3_call_needing_approval_returns_pending():
    """An allowed call to an approval tool creates a pending request"""
    g = _approvals()
    assert g.call(1, "bot", "refund") == "pending:req1"
    assert g.call(2, "bot", "refund") == "pending:req2", "every call is a new request"
    assert g.call(3, "eve", "refund") == "denied", "permission is checked before approval"
    assert g.status(4, "req1") == "pending"
    assert g.status(5, "req99") is None


def test_l3_approve_and_reject():
    """A lead can approve or reject; status follows"""
    g = _approvals()
    g.call(1, "bot", "refund")
    g.call(2, "bot", "refund")
    assert g.approve(3, "req1", "lena") is True
    assert g.status(4, "req1") == "approved"
    assert g.approve(5, "req1", "lena") is False, "no longer pending"
    assert g.reject(6, "req2", "lena") is True
    assert g.status(7, "req2") == "rejected"


def test_l3_approver_rules():
    """Approvers need the role and can't approve their own request"""
    g = _approvals()
    g.grant(1, "lena", "billing:write")
    g.call(2, "lena", "refund")
    assert g.approve(3, "req1", "lena") is False, "no self-approval"
    assert g.approve(4, "req1", "bot") is False, "bot isn't a lead"
    assert g.status(5, "req1") == "pending", "refused approvals change nothing"
    g.unassign(6, "lena", "lead")
    g.call(7, "bot", "refund")
    assert g.approve(8, "req2", "lena") is False, "the role is checked at approval time"


def test_l3_requests_expire():
    """A request expires at creation time plus the ttl"""
    g = _approvals()
    g.call(10, "bot", "refund")
    assert g.status(109, "req1") == "pending"
    assert g.status(110, "req1") == "expired", "10 + 100 = 110"
    assert g.approve(111, "req1", "lena") is False


def test_l3_approval_rechecks_requester():
    """If the requester lost access while waiting, approval ends the request as denied"""
    g = _approvals()
    g.call(1, "bot", "refund")
    g.deny(2, "bot", "billing:write")
    assert g.approve(3, "req1", "lena") is False
    assert g.status(4, "req1") == "denied"


def test_l3_require_approval_validates_and_applies_to_new_calls():
    """require_approval checks its input; a new ttl applies to later requests only"""
    g = _approvals()
    assert g.require_approval(1, "ghost", "lead", 10) is False
    assert g.require_approval(2, "refund", "lead", 0) is False
    g.call(3, "bot", "refund")
    g.require_approval(4, "refund", "lead", 10)
    g.call(5, "bot", "refund")
    assert g.status(16, "req2") == "expired", "5 + 10"
    assert g.status(16, "req1") == "pending", "req1 keeps its ttl of 100"


# Level 4 ----------------------------------------------------------------
def test_l4_audit_lines():
    """audit lists a principal's calls in order with their results"""
    g = _approvals()
    g.call(1, "bot", "refund")
    g.call(2, "bot", "ghost")
    g.grant(3, "bot", "crm:read")
    g.call(4, "bot", "lookup")
    g.call(5, "bot", "update")
    assert g.audit(6, "bot") == [
        "1 call refund -> pending:req1",
        "2 call ghost -> unknown_tool",
        "4 call lookup -> allowed",
        "5 call update -> denied",
    ]


def test_l4_audit_decisions_and_expiry():
    """Approver decisions go to the approver's audit; expiry goes to the requester's at its due time"""
    g = _approvals()
    g.call(1, "bot", "refund")
    g.call(2, "bot", "refund")
    g.approve(3, "req1", "bot")
    g.approve(4, "req1", "lena")
    g.call(150, "bot", "lookup")
    assert g.audit(151, "lena") == ["4 approve req1 -> approved"]
    assert g.audit(152, "bot") == [
        "1 call refund -> pending:req1",
        "2 call refund -> pending:req2",
        "3 approve req1 -> refused",
        "102 expire req2",
        "150 call lookup -> denied",
    ]


def test_l4_denied_by_recheck_is_audited():
    """An approval that fails the requester re-check is audited as denied"""
    g = _approvals()
    g.call(1, "bot", "refund")
    g.revoke(2, "bot", "billing:write")
    g.approve(3, "req1", "lena")
    assert g.audit(4, "lena") == ["3 approve req1 -> denied"]


def test_l4_could_call_at_past_times():
    """could_call answers from the permissions in force at that time"""
    g = _gate()
    g.grant(10, "bot", "crm:read")
    g.define_role(20, "w", ["crm:write"])
    g.assign(30, "bot", "w")
    g.revoke(40, "bot", "crm:read")
    g.define_role(50, "w", ["crm:*"])
    assert g.could_call(60, "bot", "lookup", 9) is False
    assert g.could_call(60, "bot", "lookup", 10) is True, "a change at exactly 'at' counts"
    assert g.could_call(60, "bot", "lookup", 45) is False, "revoked at 40, role only had crm:write"
    assert g.could_call(60, "bot", "lookup", 50) is True, "the role was redefined at 50"
    assert g.could_call(60, "bot", "update", 29) is False
    assert g.could_call(60, "bot", "update", 30) is True


def test_l4_could_call_tools_denies_and_future():
    """Tools added later, denies and future times are handled"""
    g = _gate()
    g.grant(5, "bot", "*")
    g.add_tool(20, "export", "data:read")
    g.deny(30, "bot", "data:read")
    assert g.could_call(40, "bot", "export", 10) is False, "the tool didn't exist at 10"
    assert g.could_call(40, "bot", "export", 25) is True
    assert g.could_call(40, "bot", "export", 35) is False
    assert g.could_call(40, "bot", "refund", 1000) is True, "a future time answers with what is true now"
    assert g.could_call(40, "ghost", "refund", 35) is False
