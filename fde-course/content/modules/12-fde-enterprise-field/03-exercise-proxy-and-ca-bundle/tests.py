_GOOD = {
    "HTTPS_PROXY": "http://proxy.quarrybank.internal:8080",
    "NO_PROXY": "localhost,.quarrybank.internal",
    "QB_CA_BUNDLE": "/tmp/quarrybank/ca-bundle.pem",
}


def test_parse_proxy_basic():
    """parse_proxy() splits scheme, host and port"""
    got = parse_proxy("http://proxy.quarrybank.internal:8080")
    assert got == {"scheme": "http", "host": "proxy.quarrybank.internal", "port": 8080, "has_credentials": False}, f"got {got!r}"


def test_parse_proxy_defaults_and_credentials():
    """parse_proxy() fills default ports and spots embedded credentials"""
    got = parse_proxy("https://svc-triage:hunter2@egress.quarrybank.internal")
    assert got is not None, "parse_proxy returned None"
    assert got["port"] == 443, f"https with no port should default to 443, got {got['port']!r}"
    assert got["has_credentials"] is True, "user:password@ in the URL means has_credentials is True"
    assert parse_proxy("http://p.internal")["port"] == 80, "http with no port should default to 80"


def test_parse_proxy_rejects():
    """parse_proxy() raises ValueError for unsupported schemes and missing hosts"""
    for bad in ["socks5://proxy:1080", "proxy.quarrybank.internal:8080", "http://:8080"]:
        try:
            parse_proxy(bad)
        except ValueError:
            continue
        assert False, f"parse_proxy({bad!r}) should raise ValueError"


def test_ca_bundle_good():
    """check_ca_bundle() accepts a bundle with several certificates"""
    got = check_ca_bundle("/tmp/quarrybank/ca-bundle.pem")
    assert got == {"ok": True, "certs": 3, "problems": []}, f"got {got!r}"


def test_ca_bundle_problems():
    """check_ca_bundle() reports missing, empty, non-PEM and replaced bundles"""
    missing = check_ca_bundle("/tmp/quarrybank/nope.pem")
    assert missing["ok"] is False and missing["problems"][0].startswith("missing"), f"got {missing!r}"
    empty = check_ca_bundle("/tmp/quarrybank/empty.pem")
    assert empty == {"ok": False, "certs": 0, "problems": ["empty"]}, f"got {empty!r}"
    der = check_ca_bundle("/tmp/quarrybank/root.der.txt")
    assert der == {"ok": False, "certs": 0, "problems": ["no PEM certificates"]}, f"got {der!r}"
    one = check_ca_bundle("/tmp/quarrybank/corp-root-only.pem")
    assert one["ok"] is False and one["certs"] == 1, f"a single-certificate bundle is a problem, got {one!r}"
    assert one["problems"][0].startswith("only 1 certificate"), f"got {one['problems']!r}"


def test_bypasses_proxy():
    """bypasses_proxy() matches exact hosts, domain suffixes, leading dots and *"""
    cases = [
        ("api.anthropic.com", "localhost,.quarrybank.internal", False),
        ("api.anthropic.com", "anthropic.com", True),
        ("api.anthropic.com", ".anthropic.com", True),
        ("anthropic.com", ".anthropic.com", True),
        ("notanthropic.com", "anthropic.com", False),
        ("API.Anthropic.com", " api.anthropic.com ,localhost", True),
        ("api.anthropic.com", "*", True),
        ("api.anthropic.com", "", False),
    ]
    for host, no_proxy, want in cases:
        got = bypasses_proxy(host, no_proxy)
        assert got is want, f"bypasses_proxy({host!r}, {no_proxy!r}) should be {want}, got {got!r}"


def test_config_good():
    """build_client_config() returns proxy and bundle with no problems for a good env"""
    got = build_client_config(_GOOD)
    assert got == {"proxy": _GOOD["HTTPS_PROXY"], "ca_bundle": _GOOD["QB_CA_BUNDLE"], "problems": []}, f"got {got!r}"
    lower = build_client_config({"https_proxy": _GOOD["HTTPS_PROXY"], "QB_CA_BUNDLE": _GOOD["QB_CA_BUNDLE"]})
    assert lower["proxy"] == _GOOD["HTTPS_PROXY"] and lower["problems"] == [], f"lowercase https_proxy should work too, got {lower!r}"


def test_config_problems_in_order():
    """build_client_config() lists proxy, CA, NO_PROXY and verification problems in order"""
    env = {
        "HTTPS_PROXY": "http://svc:pw@proxy.quarrybank.internal:8080",
        "NO_PROXY": "localhost,anthropic.com",
        "QB_CA_BUNDLE": "/tmp/quarrybank/corp-root-only.pem",
        "QB_TLS_VERIFY": "False",
    }
    got = build_client_config(env)
    assert got is not None, "build_client_config returned None"
    p = got["problems"]
    assert len(p) == 4, f"expected 4 problems, got {p!r}"
    assert p[0].startswith("proxy credentials"), f"first problem should be about credentials, got {p[0]!r}"
    assert p[1].startswith("ca_bundle: only 1 certificate"), f"second problem should be the CA bundle, got {p[1]!r}"
    assert p[2].startswith("api.anthropic.com is in NO_PROXY"), f"third problem should be NO_PROXY, got {p[2]!r}"
    assert p[3].startswith("TLS verification disabled"), f"fourth problem should be verification, got {p[3]!r}"
    assert got["ca_bundle"] is None, "a bundle that fails its check is not returned"


def test_config_missing_and_bad():
    """build_client_config() reports missing settings and a bad proxy URL"""
    got = build_client_config({})
    assert got["proxy"] is None and got["ca_bundle"] is None, f"got {got!r}"
    assert got["problems"] == ["HTTPS_PROXY not set", "QB_CA_BUNDLE not set"], f"got {got['problems']!r}"
    bad = build_client_config(dict(_GOOD, HTTPS_PROXY="socks5://p:1080"))
    assert bad["proxy"] is None, "an unparseable proxy is not returned"
    assert bad["problems"] and bad["problems"][0].startswith("proxy: unsupported proxy scheme"), f"got {bad['problems']!r}"


def test_diagnose():
    """diagnose() maps raw errors to tls, proxy_auth, allowlist, no_route or unknown"""
    cases = [
        ("[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate in certificate chain", "tls"),
        ("ProxyError: 407 Proxy Authentication Required", "proxy_auth"),
        ("Tunnel connection failed: 403 Forbidden", "allowlist"),
        ("httpx.ConnectTimeout: timed out", "no_route"),
        ("ConnectionRefusedError: [Errno 111] Connection refused", "no_route"),
        ("Something odd happened", "unknown"),
    ]
    for text, want in cases:
        got = diagnose(text)
        assert got == want, f"diagnose({text[:40]!r}...) should be {want!r}, got {got!r}"
