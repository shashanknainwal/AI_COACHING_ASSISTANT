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
    """Convert one raw string to its typed value, or raise ValueError with a clear message."""
    # TODO
    pass


def load_config(env, settings=SETTINGS):
    """Read every setting from env. Return {lowercase_name: value} or raise ConfigError with ALL problems."""
    # TODO
    pass


def redacted(config, settings=SETTINGS):
    """A copy of config that is safe to log: secrets replaced with "****" plus their last 4 characters."""
    # TODO
    pass


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
