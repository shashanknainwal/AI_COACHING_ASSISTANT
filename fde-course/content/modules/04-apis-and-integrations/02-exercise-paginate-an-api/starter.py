import requests

BASE = "https://api.northwind.example"
TOKEN = "nw_test_token"   # in real code: os.environ["NORTHWIND_TOKEN"]
PAGE_SIZE = 50            # the API's maximum
TIMEOUT = 10              # seconds


def make_session(token):
    """A Session with the bearer token and JSON Accept header."""
    # TODO
    pass


def fetch_page(session, cursor=None, status=None, limit=PAGE_SIZE):
    """One request. Returns (data, next_cursor)."""
    # TODO
    pass


def fetch_all(session, status=None):
    """Follow next_cursor until it's None and return every shipment."""
    # TODO
    pass


def count_by_status(shipments):
    """{status: count} with keys in alphabetical order."""
    # TODO
    pass


# --- Try it out (not graded) ---
session = make_session(TOKEN)
shipments = fetch_all(session) if session else None
if shipments is not None:
    print(f"Fetched {len(shipments)} shipments")
    print("By status:", count_by_status(shipments))
    print("Exceptions only:", len(fetch_all(session, status="exception")))
