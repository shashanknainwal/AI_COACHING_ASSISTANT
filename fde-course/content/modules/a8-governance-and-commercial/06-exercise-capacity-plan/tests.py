import copy

_LIM = {"p": {"rpm": 1000, "itpm": 1_000_000, "otpm": 200_000}}


def _wl(**kw):
    w = {"calls_per_minute": 100, "input_tokens": 5000, "cache_read_tokens": 4000,
         "cache_write_tokens": 0, "output_tokens": 500}
    w.update(kw)
    return w


def _rows(workload, peak, limits, **kw):
    rows = capacity_plan(workload, peak, limits, **kw)
    assert isinstance(rows, list), f"capacity_plan should return a list of rows, got {rows!r}"
    assert len(rows) == len(limits), f"expected one row per platform ({len(limits)}), got {len(rows)}"
    return rows


def test_peak_requests_and_row_shape():
    """Peak calls per minute are rounded up, and each row has the documented keys"""
    r = _rows(_wl(calls_per_minute=101), 1.5, _LIM)[0]
    for key in ("platform", "peak_rpm", "peak_itpm", "peak_otpm", "utilization", "breaches", "tight", "status", "binding"):
        assert key in r, f"row is missing {key!r}: {r!r}"
    assert r["platform"] == "p", f"platform should be the limits key, got {r['platform']!r}"
    assert r["peak_rpm"] == 152, f"101 calls/min x 1.5 = 151.5, rounded up to 152 requests; got {r['peak_rpm']}"


def test_cache_reads_excluded_from_itpm_by_default():
    """Cache reads don't count toward ITPM unless the platform says they do"""
    r = _rows(_wl(), 2.0, _LIM)[0]
    assert r["peak_itpm"] == 200 * 1000, f"200 calls x (5000 - 4000 cached) = 200,000 ITPM; got {r['peak_itpm']}"
    lim = {"p": dict(_LIM["p"], cache_reads_count=True)}
    r2 = _rows(_wl(), 2.0, lim)[0]
    assert r2["peak_itpm"] == 200 * 5000, f"with cache_reads_count=True all 5000 input tokens count: expected 1,000,000, got {r2['peak_itpm']}"


def test_cache_writes_count_toward_itpm():
    """Cache writes still count toward ITPM"""
    r = _rows(_wl(cache_read_tokens=3000, cache_write_tokens=1500), 1.0, _LIM)[0]
    assert r["peak_itpm"] == 100 * 2000, f"100 calls x (5000 - 3000 read) = 200,000; writes count. Got {r['peak_itpm']}"


def test_output_and_utilization():
    """OTPM uses output tokens (thinking included) and utilization is need / limit to 3 places"""
    r = _rows(_wl(output_tokens=900), 3.0, _LIM)[0]
    assert r["peak_otpm"] == 300 * 900, f"expected 270,000 OTPM, got {r['peak_otpm']}"
    assert r["utilization"] == {"rpm": 0.3, "itpm": 0.3, "otpm": 1.35}, f"got {r['utilization']!r}"


def test_breach_tight_ok():
    """Over the limit is a breach; above headroom is tight; otherwise ok"""
    r = _rows(_wl(output_tokens=900), 3.0, _LIM)[0]
    assert r["breaches"] == ["otpm"] and r["status"] == "breach", f"OTPM at 135% should be a breach: {r!r}"
    t = _rows(_wl(output_tokens=600), 3.0, _LIM)[0]  # 180,000 / 200,000 = 0.9
    assert t["breaches"] == [] and t["tight"] == ["otpm"] and t["status"] == "tight", f"90% with headroom 0.8 should be tight: {t!r}"
    ok = _rows(_wl(output_tokens=600), 3.0, _LIM, headroom=0.95)[0]
    assert ok["status"] == "ok" and ok["tight"] == [], f"90% with headroom 0.95 should be ok: {ok!r}"
    exact = _rows(_wl(output_tokens=500), 2.0, {"p": {"rpm": 1000, "itpm": 1_000_000, "otpm": 100_000}})[0]
    assert exact["breaches"] == [] and exact["tight"] == ["otpm"], \
        f"exactly at the limit (100,000 of 100,000) is tight, not a breach: {exact!r}"


def test_binding_metric_and_sorting():
    """Rows are sorted by platform name and 'binding' names the most-used meter"""
    lims = {
        "zeta": {"rpm": 1000, "itpm": 100_000, "otpm": 1_000_000},
        "alpha": {"rpm": 150, "itpm": 10_000_000, "otpm": 1_000_000},
    }
    rows = _rows(_wl(), 1.0, lims)
    assert [r["platform"] for r in rows] == ["alpha", "zeta"], f"sort rows by platform name, got {[r['platform'] for r in rows]}"
    assert rows[0]["binding"] == "rpm", f"alpha is limited by requests (100/150), got {rows[0]['binding']!r}"
    assert rows[1]["binding"] == "itpm", f"zeta is limited by input tokens (100,000/100,000), got {rows[1]['binding']!r}"


def test_inputs_not_modified_and_validation():
    """Inputs aren't modified; bad peak factors and impossible caching raise ValueError"""
    w, lim = _wl(), copy.deepcopy(_LIM)
    before = (copy.deepcopy(w), copy.deepcopy(lim))
    _rows(w, 2.0, lim)
    assert (w, lim) == before, "capacity_plan must not modify its arguments"
    for bad_peak in (0.5, 0):
        try:
            capacity_plan(w, bad_peak, lim)
        except ValueError:
            pass
        else:
            raise AssertionError(f"peak_factor {bad_peak} is below 1 and should raise ValueError")
    try:
        capacity_plan(_wl(cache_read_tokens=4000, cache_write_tokens=2000), 2.0, lim)
    except ValueError:
        pass
    else:
        raise AssertionError("cache reads + writes (6000) above input_tokens (5000) should raise ValueError")


_RATES = {"cache_read": 0.1, "cache_write_5m": 1.25, "cache_write_1h": 2.0, "us_only": 1.1}


def _burn(workload, peak, commit, rates=_RATES):
    r = priority_burndown(workload, peak, commit, rates)
    assert isinstance(r, dict), f"priority_burndown should return a dict, got {r!r}"
    return r


def test_burn_rates_per_call():
    """Cache reads burn 0.1, 5-minute writes 1.25, 1-hour writes 2.0, other input 1"""
    w = _wl(cache_read_tokens=4000, cache_write_tokens=400, input_tokens=5000)
    r = _burn(w, 1.0, {"itpm": 10**9, "otpm": 10**9})
    assert r["input_burn_per_call"] == 1500.0, f"4000 x 0.1 + 400 x 1.25 + 600 = 1500; got {r['input_burn_per_call']}"
    r1h = _burn(dict(w, cache_ttl="1h"), 1.0, {"itpm": 10**9, "otpm": 10**9})
    assert r1h["input_burn_per_call"] == 1800.0, f"with a 1h TTL: 400 + 800 + 600 = 1800; got {r1h['input_burn_per_call']}"
    assert r["output_burn_per_call"] == 500.0, f"output burns 1 per token, got {r['output_burn_per_call']}"


def test_us_only_multiplier():
    """inference_geo 'us' multiplies input and output burn by the us_only rate"""
    w = _wl(cache_read_tokens=0, inference_geo="us")
    r = _burn(w, 2.0, {"itpm": 10**9, "otpm": 10**9})
    assert r["input_burn_per_call"] == 5500.0, f"5000 x 1.1 = 5500, got {r['input_burn_per_call']}"
    assert r["output_burn_per_call"] == 550.0, f"500 x 1.1 = 550, got {r['output_burn_per_call']}"
    assert r["peak_input_burn"] == 200 * 5500, f"peak input burn = 200 calls x 5500, got {r['peak_input_burn']}"


def test_coverage_and_overflow():
    """Covered requests are limited by the tighter of input and output commitment"""
    w = _wl(cache_read_tokens=4000, cache_write_tokens=0)  # input burn 1400, output 500
    r = _burn(w, 3.0, {"itpm": 140_000, "otpm": 1_000_000})
    assert r["covered_rpm"] == 100, f"140,000 / 1,400 = 100 calls/min covered, got {r['covered_rpm']}"
    assert r["overflow_rpm"] == 200, f"300 at peak - 100 covered = 200 overflow to standard, got {r['overflow_rpm']}"
    assert r["covered_share"] == 0.333, f"100 / 300 = 0.333, got {r['covered_share']}"
    out = _burn(w, 3.0, {"itpm": 10**9, "otpm": 75_000})
    assert out["covered_rpm"] == 150, f"output-limited: 75,000 / 500 = 150, got {out['covered_rpm']}"
    big = _burn(w, 3.0, {"itpm": 10**9, "otpm": 10**9})
    assert big["covered_rpm"] == 300 and big["overflow_rpm"] == 0 and big["covered_share"] == 1.0, \
        f"a large commitment covers all 300 peak calls and no more: {big!r}"
