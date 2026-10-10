GOOD = {"ANTHROPIC_API_KEY": "sk-ant-api03-abcdefgh1234", "APP_ENV": "dev", "DATABASE_URL": "postgres://u:p@db:5432/app"}


def _errors(env):
    try:
        load_config(env)
    except ConfigError as e:
        return e.errors
    raise AssertionError(f"expected ConfigError for {env}")


def test_parse_value_types():
    """parse_value() converts ints, floats, bools and lists"""
    assert parse_value("N", "42", {"type": "int"}) == 42
    assert parse_value("T", "2.5", {"type": "float"}) == 2.5
    for raw in ("true", "TRUE", "1", "yes", "On"):
        assert parse_value("B", raw, {"type": "bool"}) is True, raw
    for raw in ("false", "0", "No", "OFF"):
        assert parse_value("B", raw, {"type": "bool"}) is False, raw
    assert parse_value("L", " a, b ,,c ", {"type": "list"}) == ["a", "b", "c"], "strip items and drop empty ones"
    assert parse_value("S", "hello", {"type": "str"}) == "hello"


def test_parse_value_errors():
    """parse_value() raises ValueError with exact, helpful messages"""
    cases = [
        ("MAX_TOKENS", "abc", {"type": "int"}, "MAX_TOKENS must be an integer, got 'abc'"),
        ("TIMEOUT", "fast", {"type": "float"}, "TIMEOUT must be a number, got 'fast'"),
        ("FLAG", "maybe", {"type": "bool"}, "FLAG must be true or false, got 'maybe'"),
        ("APP_ENV", "production", {"type": "str", "choices": ["dev", "prod"]}, "APP_ENV must be one of dev, prod, got 'production'"),
        ("MAX_TOKENS", "0", {"type": "int", "min": 1, "max": 100}, "MAX_TOKENS must be between 1 and 100, got 0"),
        ("MAX_TOKENS", "101", {"type": "int", "min": 1, "max": 100}, "MAX_TOKENS must be between 1 and 100, got 101"),
    ]
    for name, raw, spec, message in cases:
        try:
            parse_value(name, raw, spec)
        except ValueError as e:
            assert str(e) == message, f"got {str(e)!r}, expected {message!r}"
        else:
            raise AssertionError(f"{name}={raw!r} should raise ValueError")
    assert parse_value("N", "100", {"type": "int", "min": 1, "max": 100}) == 100, "bounds are inclusive"


def test_load_config_defaults():
    """load_config() fills defaults and uses lowercase keys"""
    got = load_config(GOOD)
    assert got == {"anthropic_api_key": "sk-ant-api03-abcdefgh1234", "app_env": "dev", "triage_model": "claude-sonnet-5-5",
                   "max_tokens": 1024, "request_timeout_s": 30.0, "enable_auto_credit": False, "allowed_origins": [],
                   "log_level": "INFO", "database_url": "postgres://u:p@db:5432/app"}, f"got {got}"


def test_load_config_strips_and_treats_empty_as_missing():
    """Whitespace is stripped, and an empty value counts as missing"""
    env = dict(GOOD, ANTHROPIC_API_KEY="  sk-ant-api03-abcdefgh1234\n", MAX_TOKENS=" 2048 ", LOG_LEVEL="")
    got = load_config(env)
    assert got["anthropic_api_key"] == "sk-ant-api03-abcdefgh1234" and got["max_tokens"] == 2048
    assert got["log_level"] == "INFO", "an empty LOG_LEVEL falls back to the default"
    assert _errors(dict(GOOD, APP_ENV="   ")) == ["APP_ENV is required"]


def test_load_config_reports_every_error():
    """All problems are reported together, in SETTINGS order"""
    env = {"APP_ENV": "staging", "MAX_TOKENS": "lots", "ENABLE_AUTO_CREDIT": "maybe", "TRIAGE_MODEL": "claude-sonnet"}
    assert _errors(env) == [
        "ANTHROPIC_API_KEY is required",
        "TRIAGE_MODEL must be one of claude-opus-5-5, claude-sonnet-5-5, claude-haiku-5-5, got 'claude-sonnet'",
        "MAX_TOKENS must be an integer, got 'lots'",
        "ENABLE_AUTO_CREDIT must be true or false, got 'maybe'",
        "DATABASE_URL is required",
    ]


def test_prod_rules():
    """Production forbids DEBUG logging and wildcard origins"""
    env = dict(GOOD, APP_ENV="prod", LOG_LEVEL="DEBUG", ALLOWED_ORIGINS="https://a.example,*")
    assert _errors(env) == ["LOG_LEVEL must not be DEBUG when APP_ENV is prod",
                            "ALLOWED_ORIGINS must not contain * when APP_ENV is prod"]
    assert load_config(dict(GOOD, LOG_LEVEL="DEBUG", ALLOWED_ORIGINS="*"))["log_level"] == "DEBUG", "fine outside prod"


def test_redacted():
    """redacted() hides secrets and leaves other values alone"""
    config = load_config(GOOD)
    safe = redacted(config)
    assert safe["anthropic_api_key"] == "****1234" and safe["database_url"] == "****/app"
    assert safe["max_tokens"] == 1024 and safe["app_env"] == "dev"
    assert config["anthropic_api_key"] == "sk-ant-api03-abcdefgh1234", "don't modify the original config"
    short = redacted({"anthropic_api_key": "abc123", "log_level": "INFO"})
    assert short == {"anthropic_api_key": "****", "log_level": "INFO"}, "secrets shorter than 12 characters show nothing"
