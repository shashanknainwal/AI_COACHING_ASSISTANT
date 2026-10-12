import copy

_GULL = {
    "name": "gullwing",
    "pagination": {"type": "page", "param": "p", "items_field": "items", "has_more_field": "more"},
    "fields": {
        "external_id": {"path": "ref"},
        "status": {"path": "s", "transform": "lookup", "table": {"1": "picked_up", "2": "delivered"}},
        "weight_kg": {"path": "dims.kg"},
        "charge": {"path": "price_cents", "transform": "cents_to_dollars"},
        "source_updated_at": {"path": "ts"},
    },
}


def _pager(pages, kind):
    calls = []
    def fetch(params):
        calls.append(dict(params))
        if kind == "cursor":
            i = int(params.get("cursor") or 0)
            return {"data": pages[i], "next_cursor": str(i + 1) if i + 1 < len(pages) else None}
        i = params["p"] - 1
        return {"items": pages[i], "more": i + 1 < len(pages)}
    return fetch, calls


def test_get_path():
    """get_path() follows dotted paths and returns None for any missing step"""
    rec = {"a": {"b": {"c": 5}}, "n": None, "z": 0}
    assert get_path(rec, "a.b.c") == 5, f"got {get_path(rec, 'a.b.c')!r}"
    assert get_path(rec, "z") == 0, "a falsy value like 0 is still a value"
    for path in ["a.x", "n.name", "q", "a.b.c.d"]:
        assert get_path(rec, path) is None, f"get_path(rec, {path!r}) should be None, got {get_path(rec, path)!r}"


def test_apply_transform():
    """apply_transform() handles every transform in TRANSFORMS"""
    cases = [
        (7, {}, 7),
        ("x", {"transform": "none"}, "x"),
        ("IT", {"transform": "lookup", "table": {"IT": "in_transit"}}, "in_transit"),
        (750, {"transform": "lbs_to_kg"}, 340.2),
        (41250, {"transform": "cents_to_dollars"}, 412.5),
        ("48.20", {"transform": "to_float"}, 48.2),
        ("10/03/2026 08:15", {"transform": "dmy_to_iso"}, "2026-03-10T08:15:00Z"),
    ]
    for value, spec, want in cases:
        got = apply_transform(value, spec)
        assert got == want, f"apply_transform({value!r}, {spec}) should be {want!r}, got {got!r}"


def test_apply_transform_errors():
    """apply_transform() raises ValueError for unknown lookup values and unknown transforms"""
    for value, spec, msg in [("ZZ", {"transform": "lookup", "table": {"IT": "x"}}, "unknown value ZZ"),
                             (1, {"transform": "teleport"}, "unknown transform teleport")]:
        try:
            apply_transform(value, spec)
        except ValueError as exc:
            assert str(exc) == msg, f"expected ValueError({msg!r}), got {str(exc)!r}"
            continue
        assert False, f"apply_transform({value!r}, {spec}) should raise ValueError"


def test_validate_config():
    """validate_config() finds bad pagination, unknown fields and transforms, missing tables and required fields"""
    assert validate_config(NORTHWIND_CONFIG) == [], f"the Northwind config is valid, got {validate_config(NORTHWIND_CONFIG)!r}"
    bad = {"pagination": {"type": "offset"},
           "fields": {"external_id": {"path": "id"}, "colour": {"path": "c"},
                      "status": {"path": "s", "transform": "lookup"}, "charge": {"path": "p", "transform": "magic"}}}
    got = validate_config(bad)
    want = ["unknown pagination type: offset", "unknown target field: colour", "status: lookup needs a table",
            "charge: unknown transform magic", "missing required field: weight_kg", "missing required field: source_updated_at"]
    assert got == want, f"expected {want}, got {got!r}"


def test_map_record_northwind():
    """map_record() with NORTHWIND_CONFIG reproduces the Module 4 mapping"""
    src = {"id": "SHP-1003", "status_code": "DL", "weight_lbs": 750, "charge_cents": 41250,
           "consignee": {"name": "Brightway Retail", "city": "Dallas"}, "updated_at": "2026-03-10T08:15:00Z"}
    got = map_record(src, NORTHWIND_CONFIG)
    want = {"external_id": "SHP-1003", "status": "delivered", "weight_kg": 340.2, "charge": 412.5,
            "customer_name": "Brightway Retail", "city": "Dallas", "source_updated_at": "2026-03-10T08:15:00Z"}
    assert got == want, f"expected {want}, got {got!r}"


def test_map_record_missing():
    """map_record() sets missing optional fields to None and raises for missing required ones"""
    src = {"id": "S1", "status_code": "PU", "weight_lbs": 10, "charge_cents": 100, "consignee": None, "updated_at": "t"}
    got = map_record(src, NORTHWIND_CONFIG)
    assert got["customer_name"] is None and got["city"] is None, f"got {got!r}"
    try:
        map_record(dict(src, weight_lbs=None), NORTHWIND_CONFIG)
    except ValueError as exc:
        assert str(exc) == "missing weight_kg", f"expected 'missing weight_kg', got {str(exc)!r}"
    else:
        assert False, "a missing required field should raise ValueError"
    third = map_record({"ref": "G1", "s": "2", "dims": {"kg": 4.0}, "price_cents": 999, "ts": "t"}, _GULL)
    assert third["status"] == "delivered" and third["city"] is None and third["charge"] == 9.99, f"a target field the config doesn't mention is None, got {third!r}"


def test_polar_config():
    """Your POLAR_CONFIG is valid and maps Polar Express records to the same schema"""
    assert validate_config(POLAR_CONFIG) == [], f"POLAR_CONFIG has problems: {validate_config(POLAR_CONFIG)!r}"
    p = POLAR_CONFIG["pagination"]
    assert (p.get("type"), p.get("param"), p.get("items_field"), p.get("has_more_field")) == ("page", "page", "shipments", "has_more"), f"Polar pages with ?page=N and returns shipments and has_more, got {p!r}"
    samples = [
        ({"trk_no": "PX-1", "state": "OUT_FOR_DELIVERY", "wt_kg": 12.5, "amt_usd": "48.20", "recipient": "R",
          "dest_city": "Austin", "last_event_ts": "10/03/2026 08:15", "svc_level": "GROUND"},
         {"external_id": "PX-1", "status": "in_transit", "weight_kg": 12.5, "charge": 48.2, "customer_name": "R",
          "city": "Austin", "source_updated_at": "2026-03-10T08:15:00Z"}),
        ({"trk_no": "PX-2", "state": "IN_TRANSIT", "wt_kg": 1.0, "amt_usd": "5", "recipient": None,
          "dest_city": None, "last_event_ts": "01/12/2026 23:59"},
         {"external_id": "PX-2", "status": "in_transit", "weight_kg": 1.0, "charge": 5.0, "customer_name": None,
          "city": None, "source_updated_at": "2026-12-01T23:59:00Z"}),
    ]
    for state, want_status in [("PICKED_UP", "picked_up"), ("DELIVERED", "delivered"), ("EXCEPTION", "exception")]:
        got = map_record(dict(samples[0][0], state=state), POLAR_CONFIG)["status"]
        assert got == want_status, f"Polar state {state} should map to {want_status!r}, got {got!r}"
    for src, want in samples:
        got = map_record(src, POLAR_CONFIG)
        assert got == want, f"expected {want}, got {got!r}"


def test_fetch_all_cursor_and_page():
    """fetch_all() walks cursor and page pagination to the end"""
    fetch, calls = _pager([[1, 2], [3], [4, 5]], "cursor")
    got = fetch_all(fetch, NORTHWIND_CONFIG)
    assert got == [1, 2, 3, 4, 5], f"expected all items across 3 pages, got {got!r}"
    assert calls == [{}, {"cursor": "1"}, {"cursor": "2"}], f"first call has no cursor, then pass next_cursor; got {calls!r}"
    fetch2, calls2 = _pager([["a"], ["b", "c"]], "page")
    got2 = fetch_all(fetch2, _GULL)
    assert got2 == ["a", "b", "c"], f"got {got2!r}"
    assert calls2 == [{"p": 1}, {"p": 2}], f"page numbers start at 1 under the config's param name; got {calls2!r}"


def test_run_connector():
    """run_connector() maps every record and collects errors with the source ID"""
    before = copy.deepcopy(NORTHWIND_CONFIG)
    got = run_connector(northwind_fetch, NORTHWIND_CONFIG)
    assert got is not None, "run_connector returned None"
    assert [r["external_id"] for r in got["records"]] == ["SHP-1001", "SHP-1002", "SHP-1008"], f"got {got['records']!r}"
    assert got["errors"] == [("SHP-1011", "unknown value ZZ"), ("SHP-1012", "missing weight_kg")], f"got {got['errors']!r}"
    assert NORTHWIND_CONFIG == before, "don't modify the config"
    polar = run_connector(polar_fetch, POLAR_CONFIG)
    assert len(polar["records"]) == 4 and polar["errors"] == [("PX-88216", "unknown value HELD_AT_CUSTOMS")], f"got {polar!r}"


def test_run_connector_rejects_bad_config():
    """run_connector() refuses an invalid config before fetching anything"""
    calls = []
    def fetch(params):
        calls.append(params)
        return {"data": [], "next_cursor": None}
    bad = copy.deepcopy(NORTHWIND_CONFIG)
    del bad["fields"]["charge"]
    try:
        run_connector(fetch, bad)
    except ValueError as exc:
        assert "missing required field: charge" in str(exc), f"the error should list the problems, got {str(exc)!r}"
    else:
        assert False, "an invalid config should raise ValueError"
    assert calls == [], "validate before fetching"
