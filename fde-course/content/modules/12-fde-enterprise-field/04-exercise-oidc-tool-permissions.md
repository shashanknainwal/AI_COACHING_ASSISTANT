---
title: "Exercise: Validate the SSO Token, Then Scope the Agent's Tools"
type: exercise
minutes: 40
hints:
  - "`find_key`: loop over `jwks[\"keys\"]`, match on `kid` and `kty == \"oct\"`, and return `b64url_decode(key[\"k\"])`."
  - "`verify_jwt` order: split into three parts, decode the header, check `alg`, find the key, check the signature, and only then decode the payload and check `iss`, `aud`, `exp`, `nbf`."
  - "The signature is `hmac.new(key, f\"{header_b64}.{payload_b64}\".encode(), hashlib.sha256).digest()`. Compare it to `b64url_decode(sig_b64)` with `hmac.compare_digest`, never with `==`."
  - "`aud` can be a string or a list: `audiences = aud if isinstance(aud, list) else [aud]`. Expired means `now > exp + leeway`; not yet valid means `now + leeway < nbf`."
  - "In `authorize`, to tell \"mfa required\" from \"tool not granted\", check whether the tool would be allowed if the user had MFA: `allowed_tools(dict(claims, amr=[\"mfa\"]), ...)`."
---

Sana Iqbal here. The triage assistant now has tools that touch accounts: look one up, search the knowledge base, and, for team leads, refund a fee. Our identity team has registered the app with our identity provider. After sign-in, every request to your backend carries a signed token with the user's groups.

Two rules from our security architecture review. First, the backend verifies every token itself; a token that hasn't been verified is just text a user sent you. Second, the model never decides who may do what. The groups in a verified token decide which tools the agent is even offered, and the two tools that move money or open fraud cases also need multi-factor sign-in.

## What is simulated, and what production uses

Real identity providers sign tokens with **RS256** or **ES256**: a private key at the provider, public keys published at a JWKS URL. Your backend fetches that key set, caches it, and refreshes it when it sees an unknown `kid` (the provider rotates keys). Verifying RSA or EC signatures needs a crypto library, so in production use a maintained JWT library and configure it with the issuer, audience and allowed algorithms.

This exercise uses **HS256** (an HMAC with a shared secret) so it runs on the standard library. The JWKS holds `"kty": "oct"` keys whose `"k"` is the base64url-encoded secret. The **order of the checks**, the claims, the clock-skew allowance and the group-to-tool mapping are the same as in production. That's what you're practising. `setup.py` gives you `QUARRYBANK_JWKS`, a fixed `NOW` and `sign_token(claims, kid=..., secret=..., alg=...)` to mint test tokens.

## Your task

`ISSUER`, `AUDIENCE`, `LEEWAY`, `GROUP_TOOLS`, `MFA_TOOLS`, `TokenError` and `b64url_decode` are given.

**1. `find_key(jwks, kid)`** returns the decoded secret (bytes) of the `oct` key with that `kid`, or `None`.

**2. `verify_jwt(token, jwks, issuer, audience, now, leeway=LEEWAY)`** returns the claims dict, or raises `TokenError(reason)` with exactly one of these reasons, checked in this order:

| Step | Reason |
|---|---|
| Not three dot-separated parts, or the header isn't valid JSON | `"malformed"` |
| Header `alg` isn't `"HS256"` (this includes `"none"`) | `"unsupported alg"` |
| No key for the header's `kid` | `"unknown kid"` |
| HMAC-SHA256 of `"<header>.<payload>"` doesn't match the signature | `"bad signature"` |
| `iss` isn't `issuer` | `"bad issuer"` |
| `aud` (a string or a list) doesn't contain `audience` | `"bad audience"` |
| No `exp` claim | `"missing exp"` |
| `now > exp + leeway` | `"expired"` |
| `nbf` present and `now + leeway < nbf` | `"not yet valid"` |

The signature comes before every claim. A forged token that is also expired must be reported as `"bad signature"`, because you never read claims you haven't verified.

**3. `allowed_tools(claims, group_tools, mfa_tools)`** returns the sorted union of tools granted by the user's `groups`. Unknown groups grant nothing. If `"mfa"` isn't in the `amr` claim, remove every tool in `mfa_tools`. No groups means no tools.

**4. `authorize(token, tool, jwks, now)`** uses `ISSUER`, `AUDIENCE`, `GROUP_TOOLS` and `MFA_TOOLS` and returns:

```python
{"allowed": True, "reason": "ok", "user": "u-4471"}
{"allowed": False, "reason": "mfa required", "user": "u-4471"}      # granted by group, but no MFA
{"allowed": False, "reason": "tool not granted", "user": "u-4471"}
{"allowed": False, "reason": "expired", "user": None}               # any TokenError reason
```

`user` is the `sub` claim, or `None` when the token was rejected.

## Example

```python
lead = sign_token({"iss": ISSUER, "aud": AUDIENCE, "sub": "u-4471", "exp": NOW + 3600,
                   "groups": ["qb-support-leads"], "amr": ["pwd"]})
authorize(lead, "issue_fee_refund", QUARRYBANK_JWKS, NOW)
# {"allowed": False, "reason": "mfa required", "user": "u-4471"}
```

## Where this sits in the agent

Call `allowed_tools` once per request and pass **only those tools** in the `tools` list to Claude. Then check `authorize` again when the model asks to call one, before you run it. The first check keeps the model from seeing tools it can't use. The second catches anything that slips through, such as a tool name injected into a conversation. Log `sub`, the tool and the decision for every call: that audit trail is what Quarrybank's security team will ask to see.
