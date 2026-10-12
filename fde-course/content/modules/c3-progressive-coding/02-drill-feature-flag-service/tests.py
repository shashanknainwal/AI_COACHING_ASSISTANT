def _svc():
    return FlagService()


# Level 1 ----------------------------------------------------------------
def test_l1_create_and_read():
    """create_flag stores the default, and is_enabled reads it"""
    s = _svc()
    assert s.create_flag(1, "dark_mode", False) is True, "create_flag should return True for a new flag"
    assert s.is_enabled(2, "dark_mode", "u1") is False
    assert s.create_flag(3, "beta_search", True) is True
    assert s.is_enabled(4, "beta_search", "u1") is True


def test_l1_duplicates_and_missing():
    """Duplicates are refused and missing flags read as None"""
    s = _svc()
    s.create_flag(1, "a", True)
    assert s.create_flag(2, "a", False) is False, "creating an existing flag should return False"
    assert s.is_enabled(3, "a", "u1") is True, "a refused create must not change the flag"
    assert s.is_enabled(4, "nope", "u1") is None, "is_enabled on a missing flag should return None"
    assert s.set_flag(5, "nope", True) is False


def test_l1_set_and_delete():
    """set_flag flips a flag; delete_flag removes it"""
    s = _svc()
    s.create_flag(1, "a", False)
    assert s.set_flag(2, "a", True) is True
    assert s.is_enabled(3, "a", "u9") is True
    assert s.delete_flag(4, "a") is True
    assert s.is_enabled(5, "a", "u9") is None
    assert s.delete_flag(6, "a") is False, "deleting a missing flag should return False"
    assert s.create_flag(7, "a", False) is True, "a deleted name can be created again"


# Level 2 ----------------------------------------------------------------
def test_l2_overrides_beat_the_flag():
    """A per-user override wins over the flag's state"""
    s = _svc()
    s.create_flag(1, "a", False)
    assert s.set_override(2, "a", "vip", True) is True
    assert s.is_enabled(3, "a", "vip") is True
    assert s.is_enabled(4, "a", "other") is False
    s.set_flag(5, "a", True)
    assert s.is_enabled(6, "a", "vip") is True
    s.set_override(7, "a", "vip", False)
    assert s.is_enabled(8, "a", "vip") is False, "the latest override for a user should win"
    assert s.set_override(9, "missing", "vip", True) is False


def test_l2_list_flags_by_prefix():
    """list_flags returns 'name(on|off)' sorted by name, filtered by prefix"""
    s = _svc()
    s.create_flag(1, "search_v2", True)
    s.create_flag(2, "search_beta", False)
    s.create_flag(3, "checkout", True)
    assert s.list_flags(4, "search") == ["search_beta(off)", "search_v2(on)"]
    assert s.list_flags(5, "") == ["checkout(on)", "search_beta(off)", "search_v2(on)"]
    assert s.list_flags(6, "zzz") == []


def test_l2_top_overridden():
    """top_overridden ranks flags by distinct overridden users, ties by name"""
    s = _svc()
    for t, name in enumerate(["a", "b", "c", "d"], start=1):
        s.create_flag(t, name, False)
    s.set_override(10, "b", "u1", True)
    s.set_override(11, "b", "u2", True)
    s.set_override(12, "b", "u1", False)
    s.set_override(13, "c", "u1", True)
    s.set_override(14, "a", "u3", True)
    assert s.top_overridden(15, 2) == ["b(2)", "a(1)"], "count distinct users; break ties by name"
    assert s.top_overridden(16, 10) == ["b(2)", "a(1)", "c(1)"], "flags with no overrides are left out"


def test_l2_delete_clears_overrides():
    """Deleting a flag also deletes its overrides"""
    s = _svc()
    s.create_flag(1, "a", False)
    s.set_override(2, "a", "u1", True)
    s.delete_flag(3, "a")
    s.create_flag(4, "a", False)
    assert s.is_enabled(5, "a", "u1") is False, "a recreated flag must not inherit old overrides"
    assert s.top_overridden(6, 5) == []


# Level 3 ----------------------------------------------------------------
def test_l3_schedule_applies_on_time():
    """A scheduled change takes effect once its time arrives"""
    s = _svc()
    s.create_flag(1, "launch", False)
    assert s.schedule(2, "launch", 10, True) == "sched1"
    assert s.is_enabled(9, "launch", "u1") is False, "not yet: the change is due at 10"
    assert s.is_enabled(10, "launch", "u1") is True, "due at 10 means on at 10"
    assert s.schedule(11, "missing", 20, True) is None


def test_l3_schedules_apply_in_time_order():
    """Several due schedules apply in time order, then creation order"""
    s = _svc()
    s.create_flag(1, "a", False)
    s.schedule(2, "a", 20, True)
    s.schedule(3, "a", 15, False)
    s.schedule(4, "a", 15, True)
    assert s.list_flags(30, "a") == ["a(on)"], "15:off, 15:on, then 20:on"
    s.schedule(31, "a", 40, False)
    assert s.schedule(32, "a", 50, True) == "sched5", "ids count up across all flags"


def test_l3_cancel_and_delete():
    """Cancelled or deleted flags' schedules never fire"""
    s = _svc()
    s.create_flag(1, "a", False)
    s.create_flag(2, "b", False)
    sa = s.schedule(3, "a", 10, True)
    s.schedule(4, "b", 10, True)
    assert s.cancel_schedule(5, sa) is True
    assert s.cancel_schedule(6, sa) is False, "cancelling twice should return False"
    s.delete_flag(7, "b")
    s.create_flag(8, "b", False)
    assert s.is_enabled(11, "a", "u") is False
    assert s.is_enabled(12, "b", "u") is False, "deleting a flag drops its pending schedules"


def test_l3_cannot_cancel_applied():
    """A schedule that already fired can't be cancelled"""
    s = _svc()
    s.create_flag(1, "a", False)
    sid = s.schedule(2, "a", 5, True)
    assert s.cancel_schedule(6, sid) is False
    assert s.is_enabled(7, "a", "u") is True


# Level 4 ----------------------------------------------------------------
def test_l4_state_at():
    """state_at answers what the flag was at a past time"""
    s = _svc()
    s.create_flag(10, "a", False)
    s.set_flag(20, "a", True)
    s.set_flag(30, "a", False)
    assert s.state_at(40, "a", 5) is None, "the flag didn't exist yet"
    assert s.state_at(41, "a", 10) is False
    assert s.state_at(42, "a", 25) is True
    assert s.state_at(43, "a", 30) is False


def test_l4_history_uses_schedule_time():
    """A scheduled change is recorded at its scheduled time, not when it was noticed"""
    s = _svc()
    s.create_flag(1, "a", False)
    s.schedule(2, "a", 10, True)
    assert s.state_at(50, "a", 12) is True, "the change happened at 10"
    assert s.state_at(51, "a", 9) is False


def test_l4_future_at_ignores_pending():
    """state_at for a future time counts only changes applied so far"""
    s = _svc()
    s.create_flag(1, "a", False)
    s.schedule(2, "a", 100, True)
    assert s.state_at(10, "a", 200) is False, "the change at 100 is still pending at timestamp 10"
    assert s.state_at(150, "a", 200) is True, "by timestamp 150 the scheduled change has been applied"


def test_l4_history_survives_delete():
    """History covers deletes and re-creation; overrides don't count"""
    s = _svc()
    s.create_flag(1, "a", True)
    s.set_override(2, "a", "u1", False)
    s.delete_flag(5, "a")
    s.create_flag(8, "a", False)
    assert s.state_at(9, "a", 3) is True, "state_at ignores per-user overrides"
    assert s.state_at(10, "a", 6) is None, "deleted between 5 and 8"
    assert s.state_at(11, "a", 8) is False


def test_l4_rollback():
    """rollback restores a past state as a new change"""
    s = _svc()
    s.create_flag(1, "a", False)
    s.set_flag(5, "a", True)
    assert s.rollback(10, "a", 3) is True
    assert s.is_enabled(11, "a", "u") is False
    assert s.state_at(12, "a", 10) is False, "the rollback is recorded at its own time"
    assert s.state_at(13, "a", 7) is True, "earlier history is kept"
    assert s.rollback(14, "a", 0) is False, "the flag didn't exist at 0"
    assert s.rollback(15, "missing", 3) is False
