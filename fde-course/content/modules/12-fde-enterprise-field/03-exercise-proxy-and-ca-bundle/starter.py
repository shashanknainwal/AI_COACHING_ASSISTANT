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
    # TODO
    pass


def check_ca_bundle(path):
    """Check that a CA bundle exists and looks like an appended PEM bundle."""
    # TODO
    pass


def bypasses_proxy(host, no_proxy):
    """True if NO_PROXY sends this host direct instead of through the proxy."""
    # TODO
    pass


def build_client_config(env):
    """The proxy and CA settings to hand the HTTP client, plus every problem found."""
    # TODO
    pass


def diagnose(error_text):
    """Map a raw connection error to a code in DIAGNOSES."""
    # TODO
    pass


# --- Try it out (not graded) ---
print("Good config:", build_client_config(QUARRYBANK_ENV))
broken = dict(QUARRYBANK_ENV, NO_PROXY="localhost,anthropic.com", QB_CA_BUNDLE="/tmp/quarrybank/corp-root-only.pem", QB_TLS_VERIFY="false")
print("Broken config:", build_client_config(broken))
for err in ["[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate in certificate chain",
            "ProxyError: 403 Forbidden by policy",
            "httpx.ConnectTimeout: timed out"]:
    code = diagnose(err)
    print(f"{err[:45]:<46} -> {code}: {DIAGNOSES.get(code, '')}")
