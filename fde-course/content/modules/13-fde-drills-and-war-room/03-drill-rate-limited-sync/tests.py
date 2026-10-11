def _eng():
    return SyncEngine()


def _seed(s, n, start=100, prefix="r"):
    for i in range(n):
        s.upsert(1, f"{prefix}{i:02d}", start + i, {"v": i})


# Level 1 ----------------------------------------------------------------
def test_l1_first_sync_pulls_everything():
    """The first sync copies every source record and moves the watermark"""
    s = _eng()
    assert s.watermark(0) == (0, ""), "the watermark starts at (0, '')"
    s.upsert(1, "r1", 100, {"name": "Ada"})
    s.upsert(2, "r2", 105, {"name": "Lin"})
    assert s.get(3, "r1") is None, "nothing is in the destination before a sync"
    assert s.sync(4) == 2
    assert s.get(5, "r1") == {"name": "Ada"}
    assert s.watermark(6) == (105, "r2")
    assert s.count(7) == 2


def test_l1_incremental_sync_pulls_only_changes():
    """A second sync pulls only records changed after the watermark"""
    s = _eng()
    s.upsert(1, "r1", 100, "a")
    s.upsert(2, "r2", 105, "b")
    s.sync(3)
    assert s.sync(4) == 0, "nothing changed"
    s.upsert(5, "r1", 110, "a2")
    assert s.sync(6) == 1
    assert s.get(7, "r1") == "a2"
    assert s.watermark(8) == (110, "r1")


def test_l1_tie_on_updated_at_is_not_lost():
    """A record with the watermark's updated_at but a later id is still pulled"""
    s = _eng()
    s.upsert(1, "b", 100, "B")
    s.sync(2)
    s.upsert(3, "c", 100, "C")
    s.upsert(4, "a", 100, "A")
    assert s.sync(5) == 1, "(100, 'c') is after (100, 'b'); (100, 'a') is not"
    assert s.get(6, "c") == "C"
    assert s.get(7, "a") is None, "the incremental sync can't see a key at or before the watermark"


def test_l1_pull_order_is_by_updated_at_then_id():
    """The watermark ends at the largest (updated_at, record_id)"""
    s = _eng()
    s.upsert(1, "z", 100, 1)
    s.upsert(2, "a", 100, 2)
    s.upsert(3, "m", 90, 3)
    s.sync(4)
    assert s.watermark(5) == (100, "z")


# Level 2 ----------------------------------------------------------------
def test_l2_pages_until_a_short_page():
    """With a page size, sync keeps requesting while pages come back full"""
    s = _eng()
    assert s.set_limits(0, 3, 100) is True
    _seed(s, 7)
    assert s.sync(2) == 7
    assert s.requests_made(3) == 3, "pages of 3, 3, 1"


def test_l2_exact_multiple_needs_an_empty_page():
    """A full last page means one more request to learn there is nothing left"""
    s = _eng()
    s.set_limits(0, 3, 100)
    _seed(s, 6)
    assert s.sync(2) == 6
    assert s.requests_made(3) == 3, "pages of 3, 3, then an empty page"


def test_l2_rate_limit_stops_and_resumes():
    """Running out of budget stops the sync with progress kept"""
    s = _eng()
    s.set_limits(0, 2, 2)
    _seed(s, 7)
    assert s.sync(10) == 4, "two requests of two records"
    assert s.watermark(10) == (103, "r03"), "progress is saved page by page"
    assert s.lag(10) == 3
    assert s.sync(30) == 0, "both requests happened within the last 60 seconds"
    assert s.sync(70) == 3, "at 70 the requests from 10 are out of the window"
    assert s.lag(71) == 0


def test_l2_window_is_sliding():
    """A request at time t frees up budget at t + 60, not earlier"""
    s = _eng()
    s.set_limits(0, 1, 2)
    _seed(s, 5)
    assert s.sync(0) == 2
    assert s.sync(59) == 0, "requests at 0 still count at 59"
    assert s.sync(60) == 2, "at 60 they are 60 seconds old and drop out"
    assert s.requests_made(61) == 4


def test_l2_set_limits_validates():
    """set_limits refuses non-positive or non-integer values and keeps the old ones"""
    s = _eng()
    s.set_limits(0, 2, 5)
    assert s.set_limits(1, 0, 5) is False
    assert s.set_limits(2, 3, -1) is False
    assert s.set_limits(3, 2.0, 5) is False
    _seed(s, 5)
    s.sync(4)
    assert s.requests_made(5) == 3, "page size is still 2"


def test_l2_lag_counts_changes_after_watermark():
    """lag counts source records whose key is after the watermark"""
    s = _eng()
    _seed(s, 3)
    assert s.lag(2) == 3
    s.sync(3)
    s.upsert(4, "r00", 500, "x")
    assert s.lag(5) == 1, "an updated record counts again"


# Level 3 ----------------------------------------------------------------
def test_l3_backfill_catches_late_arrivals():
    """A record written with an old updated_at is missed by incremental sync but caught by backfill"""
    s = _eng()
    _seed(s, 3)
    s.sync(2)
    s.upsert(3, "late", 101, "skewed clock")
    assert s.sync(4) == 0, "(101, 'late') is before the watermark (102, 'r02')"
    assert s.backfill(5, 100) is True
    assert s.backfill_status(6) == "running"
    assert s.sync(7) == 4, "the backfill re-pulls r00, late, r01 and r02"
    assert s.get(8, "late") == "skewed clock"
    assert s.backfill_status(9) == "idle"
    assert s.watermark(10) == (102, "r02"), "a backfill never moves the main watermark"


def test_l3_only_one_backfill_at_a_time():
    """A second backfill is refused while one is running"""
    s = _eng()
    _seed(s, 2)
    s.sync(2)
    assert s.backfill(3, 0) is True
    assert s.backfill(4, 50) is False
    s.sync(5)
    assert s.backfill(6, 50) is True, "allowed again once the first one finishes"


def test_l3_backfill_upper_bound_is_watermark_at_start():
    """Records changed after the backfill started are left to the incremental sync"""
    s = _eng()
    s.set_limits(0, 10, 100)
    _seed(s, 3)
    s.sync(2)
    s.backfill(3, 0)
    s.upsert(4, "new", 200, "N")
    s.upsert(5, "r00", 300, "moved")
    pulled = s.sync(6)
    assert pulled == 4, f"backfill pulls r01 and r02 (r00 moved past the bound); incremental pulls new and r00, got {pulled}"
    assert s.get(7, "r00") == "moved"
    assert s.requests_made(8) == 3, "the first sync made one request; this sync made one backfill page and one incremental page"


def test_l3_backfill_spends_budget_first():
    """Under a rate limit, the backfill gets the requests before the incremental sync"""
    s = _eng()
    s.set_limits(0, 2, 2)
    _seed(s, 4)
    s.sync(0)
    s.sync(60)
    assert s.watermark(60) == (103, "r03")
    s.backfill(61, 100)
    s.upsert(62, "fresh", 900, "F")
    assert s.sync(120) == 4, "both requests go to the backfill: r00, r01, then r02, r03"
    assert s.get(121, "fresh") is None, "the incremental sync had no budget left"
    assert s.backfill_status(121) == "running", "the last backfill page was full, so it isn't finished"
    assert s.sync(180) == 1, "an empty backfill page finishes it, then incremental pulls 'fresh'"
    assert s.backfill_status(181) == "idle"
    assert s.get(181, "fresh") == "F"


def test_l3_backfill_since_filters_old_records():
    """Backfill only covers records with updated_at at or after since"""
    s = _eng()
    s.upsert(1, "old", 50, "O")
    s.upsert(2, "mid", 100, "M")
    s.sync(3)
    s.upsert(4, "old", 50, "O2")
    s.upsert(5, "mid", 100, "M2")
    s.backfill(6, 100)
    s.sync(7)
    assert s.get(8, "mid") == "M2"
    assert s.get(9, "old") == "O", "updated_at 50 is before since=100"


# Level 4 ----------------------------------------------------------------
def test_l4_delete_propagates():
    """A tombstone is pulled like a change and removes the destination copy"""
    s = _eng()
    s.upsert(1, "r1", 100, "a")
    s.upsert(2, "r2", 101, "b")
    s.sync(3)
    assert s.delete(4, "r1", 110) is True
    assert s.delete(5, "r1", 111) is False, "already deleted"
    assert s.delete(6, "ghost", 112) is False
    assert s.sync(7) == 1
    assert s.get(8, "r1") is None
    assert s.count(9) == 1
    assert s.watermark(10) == (110, "r1")


def test_l4_upsert_after_delete_resurrects():
    """Writing a deleted record again brings it back"""
    s = _eng()
    s.upsert(1, "r1", 100, "a")
    s.sync(2)
    s.delete(3, "r1", 110)
    s.upsert(4, "r1", 120, "back")
    assert s.sync(5) == 1, "the source holds only the latest version"
    assert s.get(6, "r1") == "back"


def test_l4_late_delete_needs_backfill():
    """A delete with a skewed timestamp is invisible to incremental sync until a backfill"""
    s = _eng()
    s.upsert(1, "r1", 100, "a")
    s.upsert(2, "r2", 200, "b")
    s.sync(3)
    s.delete(4, "r1", 150)
    assert s.sync(5) == 0
    assert s.get(6, "r1") == "a"
    s.backfill(7, 100)
    s.sync(8)
    assert s.get(9, "r1") is None, "the backfill applies the tombstone"


def test_l4_rewind_repulls_and_respects_limits():
    """rewind moves the watermark back; the re-pull goes through the rate limit"""
    s = _eng()
    s.set_limits(0, 2, 2)
    _seed(s, 4)
    s.sync(0)
    s.sync(60)
    assert s.rewind(61, 200) is False, "can't rewind forwards"
    assert s.rewind(62, 102) is True
    assert s.watermark(62) == (102, "")
    assert s.lag(62) == 2
    assert s.sync(120) == 2
    assert s.watermark(121) == (103, "r03")


def test_l4_rewind_during_backfill_and_delete():
    """Rewind, a running backfill and tombstones combine correctly"""
    s = _eng()
    s.set_limits(0, 1, 3)
    s.upsert(1, "a", 100, "A")
    s.upsert(2, "b", 110, "B")
    s.upsert(3, "c", 120, "C")
    s.sync(10)
    assert s.watermark(10) == (120, "c")
    s.backfill(11, 100)
    s.delete(12, "b", 115)
    s.rewind(13, 110)
    assert s.sync(80) == 3, "three requests: backfill pulls a, then b's tombstone, then c (each page of 1 is full)"
    assert s.get(81, "b") is None
    assert s.backfill_status(81) == "running"
    assert s.sync(140) == 2, "backfill's empty page, then incremental from (110, '') pulls b's tombstone and c"
    assert s.watermark(141) == (120, "c")
    assert s.count(142) == 2
