---
title: "Exercise: Get Through the TLS-Inspecting Proxy"
type: exercise
minutes: 35
hints:
  - "`parse_proxy`: `urlsplit(url)` gives you `.scheme`, `.hostname`, `.port` and `.username`. Use `parts.port or DEFAULT_PORTS[scheme]` for the port."
  - "`check_ca_bundle`: return early for a missing file and for an empty one. Otherwise count `PEM_MARKER` in the text; 0 and 1 are both problems."
  - "`bypasses_proxy`: split NO_PROXY on commas, strip and lowercase each entry, skip empty ones. `*` matches everything; `.example.com` matches the domain and its subdomains; `example.com` matches itself and anything ending in `.example.com`."
  - "`build_client_config`: build the `problems` list in the order of the table. Wrap `parse_proxy` in `try/except ValueError` and add `f\"proxy: {exc}\"`. Prefix every CA problem with `ca_bundle: `."
  - "`diagnose`: lowercase the text once, then check the codes in the order given. Order matters: a TLS error message can contain other numbers."
---

Sana Iqbal again. Your triage service deploys tomorrow into our VPC. All outbound traffic goes through our inspecting proxy, which re-signs every certificate with the Quarrybank Root CA. Last month a vendor "fixed" this by setting `verify=False`. Our security team found it in code review, and the vendor isn't with us anymore.

I want the service to check its own network configuration at startup and refuse to start with a clear message if anything is wrong. And when a connection fails, I want the log line to say what's probably wrong, so on-call doesn't have to guess.

## What is simulated

Nothing in this exercise opens a network connection. `setup.py` writes a few files under `/tmp/quarrybank/`. The "certificates" in them are placeholders with real PEM markers, so you check structure, not cryptography. You build the configuration you would hand to the real client, and check it. In production that looks like this:

```python
import os, ssl
from anthropic import Anthropic, DefaultHttpxClient

cfg = build_client_config(os.environ)
if cfg["problems"]:
    raise SystemExit("network config: " + "; ".join(cfg["problems"]))
ctx = ssl.create_default_context(cafile=cfg["ca_bundle"])
client = Anthropic(http_client=DefaultHttpxClient(proxy=cfg["proxy"], verify=ctx))
```

The SDK documents `DefaultHttpxClient(proxy=...)` for proxies. Passing an SSL context as `verify` is how the httpx family takes a custom trust store. Confirm the argument against the docs for the HTTP library your SDK version uses (SDK 1.x uses `httpx2`) before you ship.

## Your task

`API_HOST`, `PEM_MARKER`, `DEFAULT_PORTS` and `DIAGNOSES` are given.

**1. `parse_proxy(url)`** returns `{"scheme", "host", "port", "has_credentials"}`.
- The scheme must be `http` or `https`, otherwise raise `ValueError("unsupported proxy scheme: ...")`.
- A URL with no host raises `ValueError("proxy URL has no host")`.
- A missing port defaults to 80 for http and 443 for https.
- `has_credentials` is true when the URL contains `user:password@`.

**2. `check_ca_bundle(path)`** returns `{"ok", "certs", "problems"}`:

| File | `certs` | `problems` |
|---|---|---|
| Doesn't exist | 0 | `["missing: <path>"]` |
| Empty or whitespace | 0 | `["empty"]` |
| No `PEM_MARKER` | 0 | `["no PEM certificates"]` |
| Exactly one certificate | 1 | one problem starting `"only 1 certificate"` (they replaced the bundle instead of appending to it) |
| Two or more | the count | `[]` |

`ok` is true when there are no problems.

**3. `bypasses_proxy(host, no_proxy)`** returns true if the comma-separated `NO_PROXY` list sends `host` direct. Matching ignores case and spaces. `*` matches everything. `.quarrybank.internal` matches `quarrybank.internal` and any subdomain. `anthropic.com` matches itself and any host ending in `.anthropic.com`, but not `notanthropic.com`.

**4. `build_client_config(env)`** returns `{"proxy", "ca_bundle", "problems"}`. Check in this order and add problems in this order:

| Check | Problem |
|---|---|
| `HTTPS_PROXY` (or `https_proxy`) missing | `"HTTPS_PROXY not set"`, and `proxy` is `None` |
| Proxy URL fails `parse_proxy` | `"proxy: <error message>"`, and `proxy` is `None` |
| Proxy URL has credentials | starts with `"proxy credentials in the URL"` (keep the proxy) |
| `QB_CA_BUNDLE` missing | `"QB_CA_BUNDLE not set"` |
| Bundle check fails | each problem prefixed `"ca_bundle: "`, and `ca_bundle` is `None` |
| `API_HOST` bypasses the proxy per `NO_PROXY` | starts with `"api.anthropic.com is in NO_PROXY"` |
| `QB_TLS_VERIFY` is `0`, `false` or `no` (any case) | starts with `"TLS verification disabled"` |

**5. `diagnose(error_text)`** returns a key of `DIAGNOSES`, checking case-insensitively in this order: `CERTIFICATE_VERIFY_FAILED` gives `"tls"`; `407` gives `"proxy_auth"`; `403` gives `"allowlist"`; `timed out`, `ConnectTimeout` or `Connection refused` gives `"no_route"`; anything else is `"unknown"`.

## Example

```python
build_client_config({"HTTPS_PROXY": "http://proxy.quarrybank.internal:8080",
                     "NO_PROXY": "localhost,anthropic.com",
                     "QB_CA_BUNDLE": "/tmp/quarrybank/corp-root-only.pem"})
# {"proxy": "http://proxy.quarrybank.internal:8080", "ca_bundle": None,
#  "problems": ["ca_bundle: only 1 certificate: ...", "api.anthropic.com is in NO_PROXY: ..."]}
```

Press **Run** to check a good and a broken configuration and diagnose three real-looking errors.

> **FDE tip:** Ask for the corporate root CA and the proxy address in the kickoff, in writing, with the name of the person who owns them. Then test one real streamed request through the proxy in week one, not in the week of the go-live.
