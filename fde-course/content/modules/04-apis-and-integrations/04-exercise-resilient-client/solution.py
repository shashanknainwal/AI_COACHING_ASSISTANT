import time
import requests

BASE = "https://api.northwind.example"
TIMEOUT = 10
RETRYABLE_STATUS = {429, 500, 502, 503, 504}


def backoff_delay(attempt, base=1.0, cap=30.0):
    return min(cap, base * 2 ** (attempt - 1))


def retry_after_seconds(response):
    value = response.headers.get("Retry-After")
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def get_with_retries(session, url, params=None, max_attempts=5, base=1.0, cap=30.0):
    for attempt in range(1, max_attempts + 1):
        last = attempt == max_attempts
        try:
            response = session.get(url, params=params, timeout=TIMEOUT)
        except (requests.Timeout, requests.ConnectionError):
            if last:
                raise
            time.sleep(backoff_delay(attempt, base, cap))
            continue
        if response.status_code in RETRYABLE_STATUS:
            if last:
                response.raise_for_status()
            wait = retry_after_seconds(response)
            time.sleep(wait if wait is not None else backoff_delay(attempt, base, cap))
            continue
        response.raise_for_status()
        return response.json()


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
