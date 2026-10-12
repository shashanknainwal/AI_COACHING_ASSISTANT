import re
import fde_clock


def _fresh():
    client.messages.batches = _Batches()
    fde_clock.reset()
    return client.messages.batches


def test_build_requests_ids():
    """build_requests() makes valid, unique custom_ids and maps them back to order ids"""
    reqs, id_map = build_requests(ORDERS)
    assert len(reqs) == len(ORDERS), "one request per order"
    ids = [r["custom_id"] for r in reqs]
    assert all(re.match(CUSTOM_ID_PATTERN, c) for c in ids), f"custom_id must match {CUSTOM_ID_PATTERN}; order ids like PO#4401/2 don't: {ids[:3]}"
    assert len(set(ids)) == len(ids), "custom_ids must be unique"
    assert [id_map[c] for c in ids] == [o["order_id"] for o in ORDERS], "id_map must map each custom_id back to its order_id"


def test_build_requests_params():
    """build_requests() sets model, effort, a cached system prompt and no stream"""
    reqs, _ = build_requests(ORDERS[:2])
    p = reqs[0]["params"]
    assert p.get("model") == MODEL and p.get("max_tokens") == MAX_TOKENS, p
    assert p.get("output_config") == {"effort": "low"}, "set effort explicitly"
    assert p.get("system") == [{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral", "ttl": "1h"}}], \
        "identical system block with a 1-hour cache_control in every request"
    assert p.get("messages") == [{"role": "user", "content": ORDERS[0]["text"]}]
    assert "stream" not in p, "stream isn't allowed in a batch"


def test_run_batch_polls_then_reads():
    """run_batch() polls with sleeps until the batch ends, then reads every result"""
    api = _fresh()
    reqs, _ = build_requests(ORDERS[:4])
    batch_id, results = run_batch(client, reqs, poll_seconds=60)
    assert batch_id == "msgbatch_sim_001", batch_id
    assert api.results_read_early == 0, "don't ask for results before processing_status is 'ended'"
    assert fde_clock.sleeps and all(s == 60 for s in fde_clock.sleeps), f"sleep poll_seconds between polls: {fde_clock.sleeps[:5]}"
    assert 20 <= len(fde_clock.sleeps) <= 30, f"a 25-minute batch polled every 60 s needs about 25 sleeps, you made {len(fde_clock.sleeps)}"
    assert set(results) == {r["custom_id"] for r in reqs}, "results keyed by custom_id (they arrive in any order)"


def test_process_retries_only_retryable():
    """process() resubmits errored and expired requests, never invalid ones"""
    api = _fresh()
    out = process(client, ORDERS, max_rounds=3)
    assert out["rounds"] == 3 and len(out["batch_ids"]) == 3, out
    sizes = [len(ids) for ids in api.created]
    assert sizes == [24, 4, 2], f"round 1 sends all 24, round 2 only the 4 retryable failures, round 3 the 2 still failing: {sizes}"
    assert out["failed"] == {"PO#4415/1": "invalid_request_error", "PO#4419/2": "api_error"}, out["failed"]
    assert len(out["labels"]) == 22, f"22 orders should end up labelled, got {len(out['labels'])}"
    assert out["labels"]["PO#4402/3"] == "returns" and out["labels"]["PO#4401/2"] == "billing", out["labels"]
    assert out["labels"]["PO#4403/1"] == "other", "the order that hit an api_error once succeeds in round 2"
    assert out["labels"]["PO#4411/3"] == "other", "the order that failed twice succeeds in round 3"


def test_process_respects_max_rounds():
    """process() stops after max_rounds and reports the last failure reason"""
    _fresh()
    out = process(client, ORDERS, max_rounds=1)
    assert out["rounds"] == 1, out["rounds"]
    assert out["failed"] == {"PO#4415/1": "invalid_request_error", "PO#4403/1": "api_error", "PO#4407/2": "expired",
                             "PO#4411/3": "overloaded_error", "PO#4419/2": "api_error"}, out["failed"]


def test_process_stops_when_done():
    """process() makes no extra batch when nothing is left to retry"""
    api = _fresh()
    clean = [o for o in ORDERS if "[" not in o["text"] and o["text"]]
    out = process(client, clean, max_rounds=3)
    assert out["rounds"] == 1 and len(api.created) == 1 and not out["failed"], out
