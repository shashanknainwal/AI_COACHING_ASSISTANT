import base64
import hashlib
import hmac
import json

ISSUER = "https://login.quarrybank.example/oauth2/default"
AUDIENCE = "api://triage-assistant"
LEEWAY = 60  # seconds of clock skew allowed

GROUP_TOOLS = {
    "qb-support-agents": ["lookup_account", "search_kb"],
    "qb-support-leads": ["lookup_account", "search_kb", "issue_fee_refund"],
    "qb-fraud": ["lookup_account", "flag_fraud_case"],
}
MFA_TOOLS = {"issue_fee_refund", "flag_fraud_case"}


class TokenError(Exception):
    """Raised with a short reason when a token is rejected."""


def b64url_decode(text):
    """Decode base64url without padding (given)."""
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def find_key(jwks, kid):
    """The HMAC secret (bytes) for this kid, or None."""
    for key in jwks.get("keys", []):
        if key.get("kid") == kid and key.get("kty") == "oct":
            return b64url_decode(key["k"])
    return None


def verify_jwt(token, jwks, issuer, audience, now, leeway=LEEWAY):
    """Verify signature first, then claims. Return the claims or raise TokenError."""
    parts = token.split(".")
    if len(parts) != 3:
        raise TokenError("malformed")
    header_b64, payload_b64, sig_b64 = parts
    try:
        header = json.loads(b64url_decode(header_b64))
    except ValueError:
        raise TokenError("malformed")
    if header.get("alg") != "HS256":
        raise TokenError("unsupported alg")
    key = find_key(jwks, header.get("kid"))
    if key is None:
        raise TokenError("unknown kid")
    expected = hmac.new(key, f"{header_b64}.{payload_b64}".encode(), hashlib.sha256).digest()
    try:
        signature = b64url_decode(sig_b64)
    except ValueError:
        raise TokenError("bad signature")
    if not hmac.compare_digest(signature, expected):
        raise TokenError("bad signature")
    try:
        claims = json.loads(b64url_decode(payload_b64))
    except ValueError:
        raise TokenError("malformed")

    if claims.get("iss") != issuer:
        raise TokenError("bad issuer")
    aud = claims.get("aud")
    audiences = aud if isinstance(aud, list) else [aud]
    if audience not in audiences:
        raise TokenError("bad audience")
    if "exp" not in claims:
        raise TokenError("missing exp")
    if now > claims["exp"] + leeway:
        raise TokenError("expired")
    if "nbf" in claims and now + leeway < claims["nbf"]:
        raise TokenError("not yet valid")
    return claims


def allowed_tools(claims, group_tools, mfa_tools):
    """Sorted tools this user's groups grant; MFA-only tools need 'mfa' in amr."""
    tools = set()
    for group in claims.get("groups", []):
        tools.update(group_tools.get(group, []))
    if "mfa" not in claims.get("amr", []):
        tools -= set(mfa_tools)
    return sorted(tools)


def authorize(token, tool, jwks, now):
    """Can the agent call this tool for the user holding this token?"""
    try:
        claims = verify_jwt(token, jwks, ISSUER, AUDIENCE, now)
    except TokenError as exc:
        return {"allowed": False, "reason": str(exc), "user": None}
    user = claims.get("sub")
    if tool in allowed_tools(claims, GROUP_TOOLS, MFA_TOOLS):
        return {"allowed": True, "reason": "ok", "user": user}
    if tool in allowed_tools(dict(claims, amr=["mfa"]), GROUP_TOOLS, MFA_TOOLS):
        return {"allowed": False, "reason": "mfa required", "user": user}
    return {"allowed": False, "reason": "tool not granted", "user": user}


# --- Try it out (not graded) ---
base = {"iss": ISSUER, "aud": AUDIENCE, "sub": "u-4471", "exp": NOW + 3600, "nbf": NOW - 10}
lead = sign_token(dict(base, groups=["qb-support-leads"], amr=["pwd", "mfa"]))
lead_no_mfa = sign_token(dict(base, groups=["qb-support-leads"], amr=["pwd"]))
agent = sign_token(dict(base, groups=["qb-support-agents"], amr=["pwd"]))
forged = agent.rsplit(".", 1)[0] + "." + lead.rsplit(".", 1)[1]
for label, token, tool in [("lead, refund", lead, "issue_fee_refund"),
                           ("lead, no MFA", lead_no_mfa, "issue_fee_refund"),
                           ("agent, refund", agent, "issue_fee_refund"),
                           ("agent, lookup", agent, "lookup_account"),
                           ("forged signature", forged, "lookup_account")]:
    print(f"{label:<18}", authorize(token, tool, QUARRYBANK_JWKS, NOW))
