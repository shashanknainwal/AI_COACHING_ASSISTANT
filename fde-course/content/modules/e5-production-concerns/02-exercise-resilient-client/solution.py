import random
import time

import anthropic

client = anthropic.Anthropic()
MODEL = "claude-opus-5-5"

# Statuses worth retrying besides 5xx: request timeout, conflict, rate limit.
RETRYABLE_STATUS = {408, 409, 429}


def is_retryable(exc):
    """True for connection errors and timeouts, 408, 409, 429 and every 5xx (including 529 overloaded)."""
    if isinstance(exc, anthropic.APIConnectionError):
        return True
    if isinstance(exc, anthropic.APIStatusError):
        return exc.status_code in RETRYABLE_STATUS or exc.status_code >= 500
    return False


def retry_after_seconds(exc):
    """Seconds from the error's retry-after header, or None if it's missing, unreadable or negative."""
    response = getattr(exc, "response", None)
    headers = getattr(response, "headers", None)
    if headers is None:
        return None
    value = headers.get("retry-after")
    if value is None:
        return None
    try:
        seconds = float(value)
    except (TypeError, ValueError):
        return None
    return seconds if seconds >= 0 else None


def backoff_delay(attempt, retry_after=None, base=1.0, cap=20.0, rand=random.random):
    """Delay before retry number `attempt` (0 for the first retry).

    The server's retry-after wins when present. Otherwise use full jitter:
    a random point between 0 and min(cap, base * 2**attempt).
    """
    if retry_after is not None:
        return float(retry_after)
    return rand() * min(cap, base * 2 ** attempt)


def _status_label(exc):
    if isinstance(exc, anthropic.APITimeoutError):
        return "timeout"
    if isinstance(exc, anthropic.APIConnectionError):
        return "connection"
    return exc.status_code


def call_with_retries(client, params, *, max_attempts=4, deadline_s=60.0, attempt_timeout_s=30.0,
                      rand=random.random, log=None):
    """Call messages.create with our own retry policy. Returns the Message or raises the last error."""
    if log is None:
        log = []
    start = time.monotonic()
    for attempt in range(max_attempts):
        remaining = deadline_s - (time.monotonic() - start)
        timeout = min(attempt_timeout_s, remaining)
        try:
            response = client.with_options(max_retries=0, timeout=timeout).messages.create(**params)
        except anthropic.APIError as exc:
            entry = {"attempt": attempt + 1, "status": _status_label(exc),
                     "request_id": getattr(exc, "request_id", None), "wait": None}
            log.append(entry)
            if not is_retryable(exc) or attempt == max_attempts - 1:
                raise
            delay = backoff_delay(attempt, retry_after_seconds(exc), rand=rand)
            if time.monotonic() - start + delay >= deadline_s:
                raise  # waiting would blow the caller's deadline: fail now
            entry["wait"] = delay
            time.sleep(delay)
            continue
        log.append({"attempt": attempt + 1, "status": 200, "request_id": response._request_id, "wait": None})
        return response


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
