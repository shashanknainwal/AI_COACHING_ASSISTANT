def _make(dedupe="first", sort=False, oversize_mode="skip", over_cmp="gt", bytes_cmp="gt",
          rec_extra=0, drop_last=False, empty_batch=False):
    def impl(records, max_records, max_bytes):
        recs = list(records)
        if dedupe == "last":
            last = {r["id"]: i for i, r in enumerate(recs)}
            recs = [r for i, r in enumerate(recs) if last[r["id"]] == i]
        elif dedupe == "first":
            seen, keep = set(), []
            for r in recs:
                if r["id"] not in seen:
                    seen.add(r["id"])
                    keep.append(r)
            recs = keep
        if sort:
            recs = sorted(recs, key=lambda r: r["id"])
        batches, oversized, cur, cur_b = [], [], [], 0
        for r in recs:
            too_big = r["size"] > max_bytes if over_cmp == "gt" else r["size"] >= max_bytes
            if too_big:
                if oversize_mode == "skip":
                    oversized.append(r["id"])
                    continue
                if cur:
                    batches.append(cur)
                batches.append([r["id"]])
                oversized.append(r["id"])
                cur, cur_b = [], 0
                continue
            over = cur_b + r["size"] > max_bytes if bytes_cmp == "gt" else cur_b + r["size"] >= max_bytes
            if cur and (len(cur) + 1 > max_records + rec_extra or over):
                batches.append(cur)
                cur, cur_b = [], 0
            cur.append(r["id"])
            cur_b += r["size"]
        if cur and not drop_last:
            batches.append(cur)
        if empty_batch and not batches:
            batches = [[]]
        return {"batches": batches, "oversized": oversized}
    return impl


_CORRECT = _make()
_MUTANTS = {
    "bytes": _make(bytes_cmp="ge"),
    "records": _make(rec_extra=1),
    "nodedupe": _make(dedupe="none"),
    "lastwins": _make(dedupe="last"),
    "oversized_batched": _make(oversize_mode="batch"),
    "sorted": _make(sort=True),
    "droplast": _make(drop_last=True),
    "emptybatch": _make(empty_batch=True),
    "oversize_edge": _make(over_cmp="ge"),
}


def _checks():
    return [(n, f) for n, f in sorted(globals().items()) if n.startswith("check_") and callable(f)]


def _killed(name):
    mutant = _MUTANTS[name]
    for _, fn in _checks():
        try:
            fn(mutant)
        except Exception:  # noqa: BLE001 - any failure kills the mutant
            return True
    return False


def test_has_at_least_three_checks():
    """You wrote at least three check_ functions"""
    assert len(_checks()) >= 3, f"found {len(_checks())} check_ functions; write at least three"


def test_checks_pass_on_correct_code():
    """Every check passes on the correct implementation"""
    for n, fn in _checks():
        try:
            fn(_CORRECT)
        except AssertionError as exc:
            raise AssertionError(f"{n} fails on the correct code: {exc}") from None
        except Exception as exc:  # noqa: BLE001
            raise AssertionError(f"{n} crashes on the correct code: {type(exc).__name__}: {exc}") from None


def test_catches_mutant_1():
    """Catches a boundary mistake on the byte limit"""
    assert _killed("bytes"), "a batch whose sizes add up to exactly max_bytes is allowed"


def test_catches_mutant_2():
    """Catches a boundary mistake on the record limit"""
    assert _killed("records"), "a batch may hold at most max_records records"


def test_catches_mutant_3():
    """Catches a version that forgot duplicates"""
    assert _killed("nodedupe"), "an id that appears twice is sent once"


def test_catches_mutant_4():
    """Catches a version that handles duplicates the wrong way round"""
    assert _killed("lastwins"), "which occurrence of a duplicate is kept, and where does it sit?"


def test_catches_mutant_5():
    """Catches a version that sends oversized records anyway"""
    assert _killed("oversized_batched"), "oversized records never appear in a batch"


def test_catches_mutant_6():
    """Catches a version that doesn't keep the input order"""
    assert _killed("sorted"), "records must be sent in the order given"


def test_catches_mutant_7():
    """Catches a version that loses records at the end"""
    assert _killed("droplast"), "the last, partly filled batch must be sent"


def test_catches_mutant_8():
    """Catches a version with an odd result for empty input"""
    assert _killed("emptybatch"), "what should no records produce?"


def test_catches_mutant_9():
    """Catches a boundary mistake on what counts as oversized"""
    assert _killed("oversize_edge"), "a record of exactly max_bytes fits in a batch on its own"
