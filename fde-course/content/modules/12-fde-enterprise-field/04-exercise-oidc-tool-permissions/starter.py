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
    # TODO
    pass


def verify_jwt(token, jwks, issuer, audience, now, leeway=LEEWAY):
    """Verify signature first, then claims. Return the claims or raise TokenError."""
    # TODO
    pass


def allowed_tools(claims, group_tools, mfa_tools):
    """Sorted tools this user's groups grant; MFA-only tools need 'mfa' in amr."""
    # TODO
    pass


def authorize(token, tool, jwks, now):
    """Can the agent call this tool for the user holding this token?"""
    # TODO
    pass


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
