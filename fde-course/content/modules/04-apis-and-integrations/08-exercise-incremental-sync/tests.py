import requests
from requests import _sim

_GOOD = {"id": "SHP-1003", "status_code": "DL", "weight_lbs": 750, "charge_cents": 41250,
         "consignee": {"name": "Brightway Retail", "city": "Dallas"}, "updated_at": "2026-03-10T08:15:00Z"}


def _rec(i, code="IT", at="2026-03-10T08:00:00Z", **extra):
    r = {"id": f"T-{i}", "status_code": code, "weight_lbs": 100, "charge_cents": 1000,
         "consignee": {"name": "C", "city": "X"}, "updated_at": at}
    r.update(extra)
    return r


class _Api:
    """Temporarily replace the Northwind route with a test dataset."""

    def __init__(self, rows):
        self.rows = rows

    def __enter__(self):
        self.saved = list(_sim._routes)
        _sim._routes.clear()

        def handler(req):
            since = req.params.get("updated_since", "")
            limit = int(req.params.get("limit", 20))
            rows = sorted((r for r in self.rows if r["updated_at"] >= since), key=lambda r: (r["updated_at"], r["id"]))
            start = int(req.params.get("cursor", "c_0")[2:])
            nxt = f"c_{start + limit}" if start + limit < len(rows) else None
            return {"data": [dict(r) for r in rows[start:start + limit]], "next_cursor": nxt}

        _sim.route("GET", r"/v1/shipments", handler)
        _sim.calls.clear()
        return self

    def __exit__(self, *exc):
        _sim._routes[:] = self.saved


def test_map_record():
    """map_record() renames, converts units, maps status and flattens consignee"""
    got = map_record(dict(_GOOD))
    want = {"external_id": "SHP-1003", "status": "delivered", "weight_kg": 340.2, "charge": 412.5,
            "customer_name": "Brightway Retail", "city": "Dallas", "source_updated_at": "2026-03-10T08:15:00Z"}
    assert got == want, f"expected {want}, got {got}"


def test_map_record_missing_consignee():
    """A missing consignee maps to None names, not an error"""
    got = map_record(dict(_GOOD, consignee=None))
    assert got["customer_name"] is None and got["city"] is None, f"got {got}"


def test_map_record_errors():
    """Missing required fields and unknown statuses raise ValueError with the right message"""
    for src, msg in [(dict(_GOOD, weight_lbs=None), "missing weight_lbs"), ({k: v for k, v in _GOOD.items() if k != "id"}, "missing id"),
                     (dict(_GOOD, status_code=""), "missing status_code"), (dict(_GOOD, status_code="ZZ"), "unknown status ZZ")]:
        try:
            map_record(src)
        except ValueError as e:
            assert str(e) == msg, f"expected ValueError({msg!r}), got ValueError({str(e)!r})"
        else:
            raise AssertionError(f"expected ValueError({msg!r})")


def test_overlap_since():
    """overlap_since() subtracts 5 minutes, across midnight too"""
    assert overlap_since("2026-03-10T08:28:41Z") == "2026-03-10T08:23:41Z", f"got {overlap_since('2026-03-10T08:28:41Z')!r}"
    assert overlap_since("2026-03-11T00:02:00Z") == "2026-03-10T23:57:00Z"


def test_fetch_changes_pages_and_params():
    """fetch_changes() sends updated_since with overlap, max page size, timeout, and follows cursors"""
    rows = [_rec(i, at=f"2026-03-10T08:{i % 60:02d}:00Z") for i in range(120)]
    with _Api(rows):
        got = fetch_changes(requests.Session(), "2026-03-10T07:00:00Z")
        calls = _sim.requests_to(r"/v1/shipments")
    assert len(got) == 120, f"expected all 120 records, got {len(got)}"
    assert len(calls) == 3, f"120 records at 50 per page is 3 requests; got {len(calls)}"
    assert all(c.params.get("updated_since") == "2026-03-10T06:55:00Z" for c in calls), "send updated_since = watermark - 5 minutes on every page"
    assert all(c.params.get("limit") == "50" and c.timeout == TIMEOUT for c in calls), "use limit=PAGE_SIZE and timeout=TIMEOUT"
    assert [c.params.get("cursor") for c in calls] == [None, "c_50", "c_100"], f"cursors: {[c.params.get('cursor') for c in calls]}"


def test_sync_first_run():
    """A first sync creates good records, skips bad ones, and sets the watermark"""
    rows = [_rec(1), _rec(2, at="2026-03-10T08:10:00Z"), _rec(3, code="ZZ", at="2026-03-10T08:20:00Z")]
    target = {}
    with _Api(rows):
        s = sync(requests.Session(), target, INITIAL_WATERMARK)
    assert (s["created"], s["updated"], s["unchanged"], s["skipped"]) == (2, 0, 0, 1), f"got {s}"
    assert s["errors"] == [("T-3", "unknown status ZZ")], f"errors: {s['errors']}"
    assert s["watermark"] == "2026-03-10T08:20:00Z", "the watermark comes from the latest updated_at fetched, even for skipped records"
    assert set(target) == {"T-1", "T-2"} and target["T-1"]["status"] == "in_transit"


def test_sync_is_idempotent():
    """Re-running a sync with no source changes creates and updates nothing"""
    rows = [_rec(1), _rec(2, at="2026-03-10T08:10:00Z")]
    target = {}
    with _Api(rows):
        first = sync(requests.Session(), target, INITIAL_WATERMARK)
        snapshot = {k: dict(v) for k, v in target.items()}
        second = sync(requests.Session(), target, first["watermark"])
    assert (second["created"], second["updated"]) == (0, 0), f"second run should create/update nothing; got {second}"
    assert second["unchanged"] == 1, "the overlap re-fetches T-2 (08:10 >= 08:05), which should count as unchanged"
    assert target == snapshot and second["watermark"] == first["watermark"]


def test_sync_updates_and_watermark_never_moves_back():
    """Changed records count as updated; with nothing new the watermark stays put"""
    rows = [_rec(1, at="2026-03-10T08:00:00Z")]
    target = {}
    with _Api(rows):
        sync(requests.Session(), target, INITIAL_WATERMARK)
        rows[0] = _rec(1, code="DL", at="2026-03-10T09:00:00Z")
        s = sync(requests.Session(), target, "2026-03-10T08:00:00Z")
        assert s["updated"] == 1 and target["T-1"]["status"] == "delivered", f"got {s}"
        empty = sync(requests.Session(), target, "2026-03-10T12:00:00Z")
    assert empty["watermark"] == "2026-03-10T12:00:00Z", f"with nothing fetched keep the old watermark; got {empty['watermark']}"
