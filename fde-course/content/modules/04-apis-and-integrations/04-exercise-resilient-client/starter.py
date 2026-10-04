import time
import requests

BASE = "https://api.northwind.example"
TIMEOUT = 10
RETRYABLE_STATUS = {429, 500, 502, 503, 504}


def backoff_delay(attempt, base=1.0, cap=30.0):
    """base * 2 ** (attempt - 1), capped at cap. Attempts start at 1."""
    # TODO
    pass


def retry_after_seconds(response):
    """Retry-After as float seconds, or None if missing or not a number."""
    # TODO
    pass


def get_with_retries(session, url, params=None, max_attempts=5, base=1.0, cap=30.0):
    """GET with retries for transient failures. Returns response.json()."""
    # TODO
    pass


# --- Try it out (not graded) ---
session = requests.Session()
session.headers["Authorization"] = "Bearer nw_test_token"
start = time.monotonic()
result = get_with_retries(session, f"{BASE}/v1/shipments/SHP-2001")
print("Result:", result)
print(f"Simulated time waited: {time.monotonic() - start:.0f}s")

try:
    get_with_retries(session, f"{BASE}/v1/shipments/SHP-404")
except requests.HTTPError as e:
    print("Not retried, as expected:", e)
