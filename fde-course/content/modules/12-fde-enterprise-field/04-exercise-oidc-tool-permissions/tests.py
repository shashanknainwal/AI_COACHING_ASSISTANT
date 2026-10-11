import base64
import json

_BASE = {"iss": ISSUER, "aud": AUDIENCE, "sub": "u-1", "exp": NOW + 600, "nbf": NOW - 5}


def _reason(token, **kw):
    args = dict(jwks=QUARRYBANK_JWKS, issuer=ISSUER, audience=AUDIENCE, now=NOW)
    args.update(kw)
    try:
        verify_jwt(token, args["jwks"], args["issuer"], args["audience"], args["now"])
    except TokenError as exc:
        return str(exc)
    except Exception as exc:  # noqa: BLE001
        return f"raised {type(exc).__name__} instead of TokenError: {exc}"
    return "accepted"


def _expect(token, want):
    got = _reason(token)
    assert got == want, f"expected {want!r}, got {got!r}"


def test_find_key():
    """find_key() returns the decoded secret for a kid, or None"""
    got = find_key(QUARRYBANK_JWKS, "qb-2026-10")
    assert got == b"qb-demo-secret-october", f"expected the decoded bytes secret, got {got!r}"
    assert find_key(QUARRYBANK_JWKS, "qb-2025-01") is None, "an unknown kid should return None"
    rsa_only = {"keys": [{"kid": "x", "kty": "RSA", "n": "abc", "e": "AQAB"}]}
    assert find_key(rsa_only, "x") is None, "only 'oct' keys hold an HMAC secret"


def test_valid_token():
    """verify_jwt() returns the claims of a valid token"""
    claims = dict(_BASE, groups=["qb-fraud"])
    got = verify_jwt(sign_token(claims), QUARRYBANK_JWKS, ISSUER, AUDIENCE, NOW)
    assert got == claims, f"expected the claims back, got {got!r}"
    old_key = sign_token(claims, kid="qb-2026-09")
    assert _reason(old_key) == "accepted", "a token signed with an older key still in the JWKS is valid"


def test_malformed_and_alg():
    """verify_jwt() rejects malformed tokens and any alg other than HS256 (including none)"""
    assert _reason("not-a-jwt") == "malformed", f"got {_reason('not-a-jwt')!r}"
    assert _reason("a.b") == "malformed", "two segments is malformed"
    none_token = sign_token(_BASE, alg="none")
    assert _reason(none_token) == "unsupported alg", f"alg none must be rejected, got {_reason(none_token)!r}"
    rs = sign_token(_BASE, alg="RS256")
    assert _reason(rs) == "unsupported alg", f"got {_reason(rs)!r}"


def test_unknown_kid():
    """verify_jwt() rejects a kid that isn't in the JWKS (a rotated-out key)"""
    token = sign_token(_BASE, kid="qb-2025-01", secret=b"retired")
    assert _reason(token) == "unknown kid", f"got {_reason(token)!r}"


def test_bad_signature():
    """verify_jwt() rejects a tampered payload or a wrong key"""
    good = sign_token(_BASE)
    h, p, s = good.split(".")
    evil = dict(_BASE, groups=["qb-support-leads"], amr=["mfa"])
    p2 = base64.urlsafe_b64encode(json.dumps(evil).encode()).rstrip(b"=").decode()
    assert _reason(f"{h}.{p2}.{s}") == "bad signature", "a changed payload must fail the signature check"
    wrong = sign_token(_BASE, kid="qb-2026-10", secret=b"guessed")
    assert _reason(wrong) == "bad signature", f"got {_reason(wrong)!r}"


def test_signature_before_claims():
    """verify_jwt() checks the signature before any claim"""
    expired_and_forged = sign_token(dict(_BASE, exp=NOW - 9999, iss="https://evil.example"), secret=b"guessed")
    got = _reason(expired_and_forged)
    assert got == "bad signature", f"never read claims from an unverified token: expected 'bad signature', got {got!r}"


def test_issuer_and_audience():
    """verify_jwt() checks iss and aud (aud may be a string or a list)"""
    _expect(sign_token(dict(_BASE, iss="https://login.other.example")), "bad issuer")
    _expect(sign_token(dict(_BASE, aud="api://other-app")), "bad audience")
    assert _reason(sign_token(dict(_BASE, aud=["api://other-app", AUDIENCE]))) == "accepted", "a list containing our audience is fine"
    _expect(sign_token(dict(_BASE, aud=["api://other-app"])), "bad audience")


def test_time_claims_with_leeway():
    """verify_jwt() enforces exp and nbf with LEEWAY seconds of skew"""
    assert _reason(sign_token(dict(_BASE, exp=NOW - 30))) == "accepted", "30 s past exp is inside the 60 s leeway"
    _expect(sign_token(dict(_BASE, exp=NOW - 61)), "expired")
    assert _reason(sign_token(dict(_BASE, nbf=NOW + 30))) == "accepted", "nbf 30 s ahead is inside the leeway"
    _expect(sign_token(dict(_BASE, nbf=NOW + 61)), "not yet valid")
    no_exp = dict(_BASE)
    del no_exp["exp"]
    _expect(sign_token(no_exp), "missing exp")


def test_allowed_tools():
    """allowed_tools() unions group grants, ignores unknown groups and needs MFA for sensitive tools"""
    claims = {"groups": ["qb-support-leads", "qb-fraud", "qb-cafeteria"], "amr": ["pwd", "mfa"]}
    got = allowed_tools(claims, GROUP_TOOLS, MFA_TOOLS)
    assert got == ["flag_fraud_case", "issue_fee_refund", "lookup_account", "search_kb"], f"got {got!r}"
    no_mfa = allowed_tools(dict(claims, amr=["pwd"]), GROUP_TOOLS, MFA_TOOLS)
    assert no_mfa == ["lookup_account", "search_kb"], f"without mfa in amr the MFA tools are removed, got {no_mfa!r}"
    assert allowed_tools({}, GROUP_TOOLS, MFA_TOOLS) == [], "no groups means no tools (default deny)"


def test_authorize():
    """authorize() returns allowed, reason and user"""
    lead = sign_token(dict(_BASE, sub="u-9", groups=["qb-support-leads"], amr=["mfa"]))
    lead_pwd = sign_token(dict(_BASE, sub="u-9", groups=["qb-support-leads"], amr=["pwd"]))
    agent = sign_token(dict(_BASE, sub="u-2", groups=["qb-support-agents"]))
    cases = [
        (lead, "issue_fee_refund", {"allowed": True, "reason": "ok", "user": "u-9"}),
        (lead_pwd, "issue_fee_refund", {"allowed": False, "reason": "mfa required", "user": "u-9"}),
        (agent, "issue_fee_refund", {"allowed": False, "reason": "tool not granted", "user": "u-2"}),
        (agent, "search_kb", {"allowed": True, "reason": "ok", "user": "u-2"}),
        (sign_token(dict(_BASE, exp=NOW - 999)), "search_kb", {"allowed": False, "reason": "expired", "user": None}),
    ]
    for token, tool, want in cases:
        got = authorize(token, tool, QUARRYBANK_JWKS, NOW)
        assert got == want, f"authorize(..., {tool!r}) should be {want}, got {got!r}"
