from fde_datasets import northstar

HEADER = "shipment_id,customer_id,carrier,origin,destination,ship_date,promised_date,weight_kg,value_usd\n"


def test_parse_date():
    """parse_date() accepts the three export formats"""
    assert parse_date("2026-04-02") == "2026-04-02" and parse_date("04/03/2026") == "2026-04-03"
    assert parse_date(" Apr 4 2026 ") == "2026-04-04" and parse_date("Dec 31 2026") == "2026-12-31"
    assert parse_date("2026-13-45") is None and parse_date("") is None and parse_date("soon") is None


def test_small_normalizers():
    """normalize_id(), normalize_carrier() and parse_money() handle real variants"""
    assert normalize_id(" ns - 2001 ") == "NS-2001" and normalize_id("NS-2002") == "NS-2002"
    for raw, want in [("fastfreight ", "FastFreight"), ("Fast Freight Inc.", "FastFreight"), ("FAST FREIGHT", "FastFreight"),
                      ("Blueline Express LLC", "BlueLine Express"), ("blue line express", "BlueLine Express"),
                      ("Northpeak", "NorthPeak Carriers"), ("North Peak Carriers Inc", "NorthPeak Carriers")]:
        assert normalize_carrier(raw) == want, f"{raw!r} -> {normalize_carrier(raw)!r}"
    assert normalize_carrier("Speedy Trucks Co") is None, "unknown carriers return None"
    assert parse_money('$12,800.00') == 12800.0 and parse_money("540.00") == 540.0


def test_clean_shipments_matches_reference():
    """clean_shipments() turns the raw export into exactly the clean data"""
    shipments, issues = clean_shipments(northstar.SHIPMENTS_CSV)
    assert shipments == northstar.clean_data()[0], "every field should match northstar.clean_data()[0]"
    assert issues == {"rows": 24, "duplicates": 3, "bad_dates": ["NS-2021"], "missing_weight": ["NS-2010", "NS-2016"],
                      "unknown_carrier": []}, f"issues: {issues}"


def test_clean_shipments_small():
    """Duplicates are skipped, bad dates excluded, unknown carriers kept and reported"""
    csv_text = HEADER + ('X-1,C-01,Speedy Trucks,"A","B",2026-04-01,04/02/2026,,"$1,000.00"\n'
                         'x-1,C-01,FastFreight,"A","B",2026-04-01,2026-04-02,5,10.00\n'
                         'X-2,C-02,Northpeak,"A","B",someday,2026-04-02,5,10.00\n')
    shipments, issues = clean_shipments(csv_text)
    assert list(shipments) == ["X-1"] and shipments["X-1"]["carrier"] is None and shipments["X-1"]["value_usd"] == 1000.0
    assert shipments["X-1"]["weight_kg"] is None
    assert issues == {"rows": 3, "duplicates": 1, "bad_dates": ["X-2"], "missing_weight": ["X-1"], "unknown_carrier": ["X-1"]}


def test_latest_events():
    """latest_events() normalizes IDs and keeps the most recent event"""
    latest = latest_events(northstar.CARRIER_EVENTS)
    assert len(latest) == 22
    ref = northstar.clean_data()[1]
    assert all(latest[k] == ref[k] for k in ref), "latest events should match northstar.clean_data()[1]"
    small = latest_events([{"shipment_id": "a-1", "ts": "2026-01-02T00:00:00Z", "code": "DELAY", "detail": "x"},
                           {"shipment_id": "A - 1", "ts": "2026-01-01T00:00:00Z", "code": "IN_TRANSIT", "detail": "y"}])
    assert small == {"A-1": {"code": "DELAY", "ts": "2026-01-02T00:00:00Z", "detail": "x"}}, "order in the list doesn't matter"


def test_build_queue():
    """build_queue() joins exceptions to customers, most urgent first, and reports orphans"""
    shipments, latest, customers = northstar.clean_data()
    latest = dict(latest, **{"NS-9999": {"code": "DELAY", "ts": "t", "detail": "?"},
                             "NS-9998": {"code": "DELIVERED", "ts": "t", "detail": "?"}})
    queue, orphans = build_queue(shipments, latest, customers)
    assert orphans == ["NS-9999"], "only exception events count; NS-9998 here is DELIVERED"
    assert [q["shipment_id"] for q in queue] == ["NS-2017", "NS-2001", "NS-2006", "NS-2018", "NS-2014", "NS-2003",
                                                 "NS-2008", "NS-2011", "NS-2005", "NS-2016", "NS-2019"], [q["shipment_id"] for q in queue]
    assert queue[0] == {"shipment_id": "NS-2017", "customer": "Halvorsen Medical Supply", "tier": "platinum", "sla_hours": 2,
                        "code": "CUSTOMS_HOLD", "detail": "Held at border: inspection requested", "carrier": "BlueLine Express",
                        "value_usd": 26700.0, "event_ts": "2026-04-09T15:10:00Z"}, f"got {queue[0]}"
