import random
import time

import anthropic

client = anthropic.Anthropic()
MODEL = "claude-opus-5-5"

# Statuses worth retrying besides 5xx: request timeout, conflict, rate limit.
RETRYABLE_STATUS = {408, 409, 429}


def is_retryable(exc):
    """True for connection errors and timeouts, 408, 409, 429 and every 5xx (including 529 overloaded)."""
    # TODO
    pass


def retry_after_seconds(exc):
    """Seconds from the error's retry-after header, or None if it's missing, unreadable or negative."""
    # TODO
    pass


def backoff_delay(attempt, retry_after=None, base=1.0, cap=20.0, rand=random.random):
    """Delay before retry number `attempt` (0 for the first retry).

    The server's retry-after wins when present. Otherwise use full jitter:
    a random point between 0 and min(cap, base * 2**attempt).
    """
    # TODO
    pass


def call_with_retries(client, params, *, max_attempts=4, deadline_s=60.0, attempt_timeout_s=30.0,
                      rand=random.random, log=None):
    """Call messages.create with our own retry policy. Returns the Message or raises the last error."""
    # TODO
    pass


# --- Try it out (not graded) ---
log = []
params = {
    "model": MODEL,
    "max_tokens": 1024,
    "messages": [{"role": "user", "content": "Extract vendor, total and currency from invoice INV-20931."}],
}
try:
    response = call_with_retries(client, params, log=log)
except anthropic.APIError as exc:
    response = None
    print("Gave up:", type(exc).__name__)
for entry in log:
    print(entry)
if response is not None:
    print("Answer:", response.content[-1].text)
