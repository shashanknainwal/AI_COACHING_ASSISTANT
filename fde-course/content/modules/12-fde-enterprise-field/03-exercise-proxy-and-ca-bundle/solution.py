import os
from urllib.parse import urlsplit

API_HOST = "api.anthropic.com"
PEM_MARKER = "-----BEGIN CERTIFICATE-----"
DEFAULT_PORTS = {"http": 80, "https": 443}

DIAGNOSES = {
    "tls": "The corporate root CA isn't trusted. Point the client at a bundle that includes it.",
    "proxy_auth": "The proxy wants credentials. Ask how service accounts authenticate to it.",
    "allowlist": "The proxy refused the host. Raise a change ticket to allowlist it.",
    "no_route": "No route out. Check HTTPS_PROXY is set and that this subnet may use the proxy.",
    "unknown": "Capture the full error, the time and any request-id, then ask the network team.",
}

QUARRYBANK_ENV = {
    "HTTPS_PROXY": "http://proxy.quarrybank.internal:8080",
    "NO_PROXY": "localhost,127.0.0.1,.quarrybank.internal",
    "QB_CA_BUNDLE": "/tmp/quarrybank/ca-bundle.pem",
}


def parse_proxy(url):
    """Split a proxy URL into scheme, host, port and whether it embeds credentials."""
    parts = urlsplit(url)
    scheme = parts.scheme.lower()
    if scheme not in DEFAULT_PORTS:
        raise ValueError(f"unsupported proxy scheme: {scheme or '(none)'}")
    if not parts.hostname:
        raise ValueError("proxy URL has no host")
    return {
        "scheme": scheme,
        "host": parts.hostname,
        "port": parts.port or DEFAULT_PORTS[scheme],
        "has_credentials": parts.username is not None,
    }


def check_ca_bundle(path):
    """Check that a CA bundle exists and looks like an appended PEM bundle."""
    if not os.path.exists(path):
        return {"ok": False, "certs": 0, "problems": [f"missing: {path}"]}
    with open(path) as f:
        text = f.read()
    if not text.strip():
        return {"ok": False, "certs": 0, "problems": ["empty"]}
    certs = text.count(PEM_MARKER)
    problems = []
    if certs == 0:
        problems.append("no PEM certificates")
    elif certs == 1:
        problems.append("only 1 certificate: append the corporate root to the public bundle instead of replacing it")
    return {"ok": not problems, "certs": certs, "problems": problems}


def bypasses_proxy(host, no_proxy):
    """True if NO_PROXY sends this host direct instead of through the proxy."""
    host = host.lower()
    for entry in no_proxy.split(","):
        entry = entry.strip().lower()
        if not entry:
            continue
        if entry == "*":
            return True
        if entry.startswith("."):
            if host.endswith(entry) or host == entry[1:]:
                return True
        elif host == entry or host.endswith("." + entry):
            return True
    return False


def build_client_config(env):
    """The proxy and CA settings to hand the HTTP client, plus every problem found."""
    problems = []
    proxy = env.get("HTTPS_PROXY") or env.get("https_proxy")
    if not proxy:
        problems.append("HTTPS_PROXY not set")
        proxy = None
    else:
        try:
            info = parse_proxy(proxy)
            if info["has_credentials"]:
                problems.append("proxy credentials in the URL: load them from the secrets manager")
        except ValueError as exc:
            problems.append(f"proxy: {exc}")
            proxy = None

    ca_bundle = env.get("QB_CA_BUNDLE")
    if not ca_bundle:
        problems.append("QB_CA_BUNDLE not set")
        ca_bundle = None
    else:
        check = check_ca_bundle(ca_bundle)
        problems.extend(f"ca_bundle: {p}" for p in check["problems"])
        if not check["ok"]:
            ca_bundle = None

    if bypasses_proxy(API_HOST, env.get("NO_PROXY", "")):
        problems.append(f"{API_HOST} is in NO_PROXY: direct egress is blocked, so it must go through the proxy")

    if str(env.get("QB_TLS_VERIFY", "true")).strip().lower() in ("0", "false", "no"):
        problems.append("TLS verification disabled: never ship this")

    return {"proxy": proxy, "ca_bundle": ca_bundle, "problems": problems}


def diagnose(error_text):
    """Map a raw connection error to a code in DIAGNOSES."""
    text = error_text.lower()
    if "certificate_verify_failed" in text:
        return "tls"
    if "407" in text:
        return "proxy_auth"
    if "403" in text:
        return "allowlist"
    if "timed out" in text or "connecttimeout" in text or "connection refused" in text:
        return "no_route"
    return "unknown"


# --- Try it out (not graded) ---
print("Good config:", build_client_config(QUARRYBANK_ENV))
broken = dict(QUARRYBANK_ENV, NO_PROXY="localhost,anthropic.com", QB_CA_BUNDLE="/tmp/quarrybank/corp-root-only.pem", QB_TLS_VERIFY="false")
print("Broken config:", build_client_config(broken))
for err in ["[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate in certificate chain",
            "ProxyError: 403 Forbidden by policy",
            "httpx.ConnectTimeout: timed out"]:
    code = diagnose(err)
    print(f"{err[:45]:<46} -> {code}: {DIAGNOSES.get(code, '')}")
