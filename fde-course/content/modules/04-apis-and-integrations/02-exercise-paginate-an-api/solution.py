import requests

BASE = "https://api.northwind.example"
TOKEN = "nw_test_token"   # in real code: os.environ["NORTHWIND_TOKEN"]
PAGE_SIZE = 50            # the API's maximum
TIMEOUT = 10              # seconds


def make_session(token):
    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {token}", "Accept": "application/json"})
    return session


def fetch_page(session, cursor=None, status=None, limit=PAGE_SIZE):
    params = {"limit": limit}
    if cursor is not None:
        params["cursor"] = cursor
    if status is not None:
        params["status"] = status
    response = session.get(f"{BASE}/v1/shipments", params=params, timeout=TIMEOUT)
    response.raise_for_status()
    body = response.json()
    return body["data"], body["next_cursor"]


def fetch_all(session, status=None):
    results, cursor, seen = [], None, set()
    while True:
        data, next_cursor = fetch_page(session, cursor=cursor, status=status)
        results.extend(data)
        if next_cursor is None:
            return results
        if next_cursor in seen:
            raise RuntimeError("pagination loop")
        seen.add(next_cursor)
        cursor = next_cursor


def count_by_status(shipments):
    counts = {}
    for s in shipments:
        counts[s["status"]] = counts.get(s["status"], 0) + 1
    return dict(sorted(counts.items()))


# --- Try it out (not graded) ---
session = make_session(TOKEN)
shipments = fetch_all(session) if session else None
if shipments is not None:
    print(f"Fetched {len(shipments)} shipments")
    print("By status:", count_by_status(shipments))
    print("Exceptions only:", len(fetch_all(session, status="exception")))
