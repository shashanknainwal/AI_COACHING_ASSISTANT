import requests
from requests import _sim


def _list_calls():
    return _sim.requests_to(r"/v1/shipments")


def test_make_session():
    """make_session() sets the bearer token and Accept header"""
    s = make_session("abc")
    assert isinstance(s, requests.Session), "return a requests.Session"
    headers = {k.lower(): v for k, v in s.headers.items()}
    assert headers.get("authorization") == "Bearer abc", f"Authorization header: got {headers.get('authorization')!r}"
    assert headers.get("accept") == "application/json", f"Accept header: got {headers.get('accept')!r}"


def test_fetch_page_request():
    """fetch_page() sends one request with limit, auth and a timeout"""
    _sim.calls.clear()
    data, cursor = fetch_page(make_session(TOKEN))
    calls = _list_calls()
    assert len(calls) == 1, f"fetch_page should make exactly 1 request, made {len(calls)}"
    c = calls[0]
    assert c.params.get("limit") == "50", f"send limit=50 (PAGE_SIZE); got {c.params.get('limit')!r}"
    assert "cursor" not in c.params and "status" not in c.params, "don't send cursor/status when they're None"
    assert c.timeout == TIMEOUT, f"pass timeout=TIMEOUT on every request; got {c.timeout!r}"
    assert c.header("Authorization") == f"Bearer {TOKEN}", "the request should carry the session's Authorization header"
    assert len(data) == 50 and cursor == "c_50", f"expected 50 rows and cursor 'c_50', got {len(data)} and {cursor!r}"


def test_fetch_page_with_cursor_and_status():
    """fetch_page() passes cursor and status when given"""
    _sim.calls.clear()
    fetch_page(make_session(TOKEN), cursor="c_50", status="delivered")
    c = _list_calls()[-1]
    assert c.params.get("cursor") == "c_50" and c.params.get("status") == "delivered", f"got params {c.params}"


def test_fetch_all_gets_everything():
    """fetch_all() returns all 127 shipments in 3 requests"""
    _sim.calls.clear()
    got = fetch_all(make_session(TOKEN))
    assert isinstance(got, list), "fetch_all should return a list"
    assert len(got) == 127, f"expected 127 shipments, got {len(got)}"
    assert [s["id"] for s in got] == [s["id"] for s in SHIPMENTS], "shipments should be in API order with no duplicates"
    calls = _list_calls()
    assert len(calls) == 3, f"127 rows at 50 per page is 3 requests; you made {len(calls)}"
    assert [c.params.get("cursor") for c in calls] == [None, "c_50", "c_100"], f"cursors sent: {[c.params.get('cursor') for c in calls]}"


def test_fetch_all_with_status():
    """fetch_all(status=...) passes the filter on every page"""
    _sim.calls.clear()
    got = fetch_all(make_session(TOKEN), status="exception")
    assert len(got) == 18 and all(s["status"] == "exception" for s in got), f"expected 18 exception shipments, got {len(got)}"
    assert all(c.params.get("status") == "exception" for c in _list_calls()), "send the status filter on every page"


def test_bad_token_raises():
    """A wrong token raises requests.HTTPError (401) instead of returning nothing"""
    try:
        fetch_all(make_session("wrong"))
    except requests.HTTPError as e:
        assert e.response.status_code == 401, f"expected a 401, got {e.response.status_code}"
    else:
        raise AssertionError("expected requests.HTTPError for a 401; did you call raise_for_status()?")


def test_pagination_loop_detected():
    """A cursor that repeats raises RuntimeError('pagination loop')"""
    saved = list(_sim._routes)
    _sim._routes.clear()
    _sim.route("GET", r"/v1/shipments", lambda req: {"data": [{"id": "X", "status": "pending"}], "next_cursor": "c_1"})
    try:
        fetch_all(make_session(TOKEN))
    except RuntimeError as e:
        assert str(e) == "pagination loop", f"message should be 'pagination loop', got {str(e)!r}"
    else:
        raise AssertionError("expected RuntimeError('pagination loop')")
    finally:
        _sim._routes[:] = saved


def test_count_by_status():
    """count_by_status() counts and sorts keys"""
    got = count_by_status(SHIPMENTS)
    assert got == {"delivered": 54, "exception": 18, "in_transit": 37, "pending": 18}, f"got {got}"
    assert list(got) == sorted(got), "keys should be in alphabetical order"
    assert count_by_status([]) == {}
