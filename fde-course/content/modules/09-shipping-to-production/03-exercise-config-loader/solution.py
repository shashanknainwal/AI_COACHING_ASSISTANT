class ConfigError(Exception):
    """Raised with every configuration problem at once (given)."""

    def __init__(self, errors):
        super().__init__("Invalid configuration:\n" + "\n".join(f"- {e}" for e in errors))
        self.errors = errors


# Every setting the Brightway assistant reads from its environment (given).
SETTINGS = {
    "ANTHROPIC_API_KEY": {"type": "str", "required": True, "secret": True},
    "APP_ENV": {"type": "str", "required": True, "choices": ["dev", "staging", "prod"]},
    "TRIAGE_MODEL": {"type": "str", "default": "claude-sonnet-5-5",
                     "choices": ["claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-5-5"]},
    "MAX_TOKENS": {"type": "int", "default": 1024, "min": 1, "max": 64000},
    "REQUEST_TIMEOUT_S": {"type": "float", "default": 30.0, "min": 1, "max": 600},
    "ENABLE_AUTO_CREDIT": {"type": "bool", "default": False},
    "ALLOWED_ORIGINS": {"type": "list", "default": []},
    "LOG_LEVEL": {"type": "str", "default": "INFO", "choices": ["DEBUG", "INFO", "WARNING", "ERROR"]},
    "DATABASE_URL": {"type": "str", "required": True, "secret": True},
}
TRUE_VALUES = {"true", "1", "yes", "on"}
FALSE_VALUES = {"false", "0", "no", "off"}


def parse_value(name, raw, spec):
    kind = spec["type"]
    if kind == "int":
        try:
            value = int(raw)
        except ValueError:
            raise ValueError(f"{name} must be an integer, got {raw!r}")
    elif kind == "float":
        try:
            value = float(raw)
        except ValueError:
            raise ValueError(f"{name} must be a number, got {raw!r}")
    elif kind == "bool":
        if raw.lower() in TRUE_VALUES:
            return True
        if raw.lower() in FALSE_VALUES:
            return False
        raise ValueError(f"{name} must be true or false, got {raw!r}")
    elif kind == "list":
        return [item.strip() for item in raw.split(",") if item.strip()]
    else:
        value = raw
    if "choices" in spec and value not in spec["choices"]:
        raise ValueError(f"{name} must be one of {', '.join(spec['choices'])}, got {raw!r}")
    if "min" in spec and not spec["min"] <= value <= spec["max"]:
        raise ValueError(f"{name} must be between {spec['min']} and {spec['max']}, got {raw}")
    return value


def load_config(env, settings=SETTINGS):
    config, errors = {}, []
    for name, spec in settings.items():
        raw = env.get(name, "").strip()
        if not raw:
            if spec.get("required"):
                errors.append(f"{name} is required")
            else:
                config[name.lower()] = spec.get("default")
            continue
        try:
            config[name.lower()] = parse_value(name, raw, spec)
        except ValueError as e:
            errors.append(str(e))
    if config.get("app_env") == "prod":
        if config.get("log_level") == "DEBUG":
            errors.append("LOG_LEVEL must not be DEBUG when APP_ENV is prod")
        if "*" in config.get("allowed_origins", []):
            errors.append("ALLOWED_ORIGINS must not contain * when APP_ENV is prod")
    if errors:
        raise ConfigError(errors)
    return config


def redacted(config, settings=SETTINGS):
    safe = {}
    for key, value in config.items():
        if settings.get(key.upper(), {}).get("secret") and value:
            safe[key] = "****" + value[-4:] if len(value) >= 12 else "****"
        else:
            safe[key] = value
    return safe


# --- Try it out (not graded) ---
STAGING = {
    "ANTHROPIC_API_KEY": "sk-ant-api03-demo-key-7f3a\n",   # a trailing newline from a secrets file
    "APP_ENV": "staging",
    "MAX_TOKENS": "2048",
    "ENABLE_AUTO_CREDIT": "Yes",
    "ALLOWED_ORIGINS": "https://help.brightway.example, https://admin.brightway.example,",
    "DATABASE_URL": "postgres://triage:s3cret@db.internal:5432/triage",
}
BROKEN_PROD = {"APP_ENV": "prod", "MAX_TOKENS": "lots", "LOG_LEVEL": "DEBUG", "TRIAGE_MODEL": "claude-sonnet",
               "ENABLE_AUTO_CREDIT": "maybe", "REQUEST_TIMEOUT_S": "0"}

config = load_config(STAGING)
if config:
    print("staging config:", redacted(config))
try:
    load_config(BROKEN_PROD)
    print("BROKEN_PROD loaded?!")
except ConfigError as e:
    print(e)
