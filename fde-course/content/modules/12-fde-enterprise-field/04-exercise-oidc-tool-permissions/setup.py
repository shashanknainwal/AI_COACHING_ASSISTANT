import base64
import hashlib
import hmac
import json


def _b64(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


# Quarrybank's identity provider, simulated. A real IdP publishes RSA or EC
# public keys at a JWKS URL; this one uses shared HMAC secrets so the exercise
# runs on the standard library.
_SECRETS = {"qb-2026-09": b"qb-demo-secret-september", "qb-2026-10": b"qb-demo-secret-october"}
QUARRYBANK_JWKS = {"keys": [
    {"kid": kid, "kty": "oct", "alg": "HS256", "k": _b64(secret)} for kid, secret in _SECRETS.items()
]}
NOW = 1791000000  # a fixed "current time" in Unix seconds


def sign_token(claims, kid="qb-2026-10", secret=None, alg="HS256"):
    """Mint a token the way the simulated IdP would (for the demo and tests)."""
    secret = secret if secret is not None else _SECRETS.get(kid, b"unknown")
    header = _b64(json.dumps({"alg": alg, "typ": "JWT", "kid": kid}).encode())
    payload = _b64(json.dumps(claims).encode())
    sig = _b64(hmac.new(secret, f"{header}.{payload}".encode(), hashlib.sha256).digest())
    return f"{header}.{payload}.{sig}"
