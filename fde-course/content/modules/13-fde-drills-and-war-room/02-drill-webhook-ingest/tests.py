def _box():
    return WebhookInbox()


# Level 1 ----------------------------------------------------------------
def test_l1_accept_and_balance():
    """Accepted charges and refunds move the balance"""
    b = _box()
    assert b.receive(1, "e1", "acme", 1, "charge", 500) == "accepted"
    assert b.receive(2, "e2", "acme", 2, "refund", 120) == "accepted"
    assert b.balance(3, "acme") == 380, "balance is charges minus refunds"
    assert b.event_count(4, "acme") == 2


def test_l1_duplicate_delivery_is_ignored():
    """The same event delivered twice is applied once"""
    b = _box()
    b.receive(1, "e1", "acme", 1, "charge", 500)
    assert b.receive(2, "e1", "acme", 1, "charge", 500) == "duplicate", "same id and same payload is a duplicate"
    assert b.receive(9, "e1", "acme", 1, "charge", 500) == "duplicate", "a retry much later is still a duplicate"
    assert b.balance(10, "acme") == 500, "duplicates must not change the balance"
    assert b.event_count(11, "acme") == 1


def test_l1_same_id_different_payload_is_conflict():
    """Reusing an event id with a different payload is a conflict and changes nothing"""
    b = _box()
    b.receive(1, "e1", "acme", 1, "charge", 500)
    assert b.receive(2, "e1", "acme", 1, "charge", 900) == "conflict", "different amount, same id"
    assert b.receive(3, "e1", "zeta", 1, "charge", 500) == "conflict", "different account, same id"
    assert b.balance(4, "acme") == 500
    assert b.balance(5, "zeta") == 0


def test_l1_rejects_bad_events_without_recording_them():
    """Invalid kind or amount is rejected and the id stays free"""
    b = _box()
    assert b.receive(1, "e1", "acme", 1, "payout", 50) == "rejected", "unknown kind"
    assert b.receive(2, "e2", "acme", 1, "charge", 0) == "rejected", "amount must be positive"
    assert b.receive(3, "e3", "acme", 1, "charge", -5) == "rejected"
    assert b.receive(4, "e1", "acme", 1, "charge", 50) == "accepted", "a rejected id was never recorded"
    assert b.balance(5, "acme") == 50


def test_l1_unknown_account_and_separate_accounts():
    """Accounts are independent and unknown accounts read as zero"""
    b = _box()
    b.receive(1, "a1", "acme", 1, "charge", 10)
    b.receive(2, "z1", "zeta", 1, "charge", 70)
    assert b.balance(3, "acme") == 10
    assert b.balance(4, "zeta") == 70
    assert b.balance(5, "nobody") == 0
    assert b.event_count(6, "nobody") == 0


# Level 2 ----------------------------------------------------------------
def test_l2_out_of_order_events_are_held():
    """An event ahead of the next expected seq is held, not applied"""
    b = _box()
    assert b.receive(1, "e3", "acme", 3, "charge", 300) == "held"
    assert b.receive(2, "e2", "acme", 2, "charge", 200) == "held"
    assert b.balance(3, "acme") == 0, "held events don't count yet"
    assert b.pending(4, "acme") == [2, 3]
    assert b.applied_seq(5, "acme") == 0


def test_l2_gap_fill_drains_in_order():
    """Filling the gap applies the held events in seq order"""
    b = _box()
    b.receive(1, "e3", "acme", 3, "refund", 50)
    b.receive(2, "e2", "acme", 2, "charge", 200)
    assert b.receive(3, "e1", "acme", 1, "charge", 100) == "accepted"
    assert b.balance(4, "acme") == 250
    assert b.pending(5, "acme") == []
    assert b.applied_seq(6, "acme") == 3
    assert b.event_count(7, "acme") == 3


def test_l2_partial_drain_stops_at_next_gap():
    """Draining stops at the next missing seq"""
    b = _box()
    b.receive(1, "e5", "acme", 5, "charge", 5)
    b.receive(2, "e2", "acme", 2, "charge", 2)
    b.receive(3, "e1", "acme", 1, "charge", 1)
    assert b.applied_seq(4, "acme") == 2
    assert b.pending(5, "acme") == [5]
    assert b.balance(6, "acme") == 3


def test_l2_seq_conflict_and_held_duplicate():
    """A second event for a taken seq conflicts; redelivering a held event is a duplicate"""
    b = _box()
    b.receive(1, "e1", "acme", 1, "charge", 10)
    assert b.receive(2, "x1", "acme", 1, "charge", 10) == "conflict", "seq 1 already belongs to e1"
    b.receive(3, "e3", "acme", 3, "charge", 30)
    assert b.receive(4, "e3", "acme", 3, "charge", 30) == "duplicate", "held events are known events"
    assert b.receive(5, "x3", "acme", 3, "charge", 99) == "conflict", "seq 3 is held for e3"
    b.receive(6, "e2", "acme", 2, "charge", 20)
    assert b.balance(7, "acme") == 60


def test_l2_accounts_keep_their_own_sequence():
    """Each account has its own seq counter"""
    b = _box()
    assert b.receive(1, "z2", "zeta", 2, "charge", 5) == "held"
    assert b.receive(2, "a1", "acme", 1, "charge", 7) == "accepted"
    assert b.pending(3, "zeta") == [2]
    assert b.pending(4, "acme") == []
    assert b.applied_seq(5, "nobody") == 0
    assert b.pending(6, "nobody") == []


# Level 3 ----------------------------------------------------------------
def test_l3_gap_timeout_skips_and_applies():
    """After the timeout the gap is skipped and held events apply"""
    b = _box()
    b.receive(1, "e1", "acme", 1, "charge", 10)
    b.receive(10, "e4", "acme", 4, "charge", 40)
    assert b.set_gap_timeout(11, 30) is True
    assert b.balance(39, "acme") == 10, "not due until 10 + 30"
    assert b.balance(40, "acme") == 50, "due exactly at 40"
    assert b.missing(41, "acme") == [2, 3]
    assert b.applied_seq(42, "acme") == 4


def test_l3_timeout_counts_from_oldest_held_event():
    """The deadline runs from the earliest-received held event"""
    b = _box()
    b.set_gap_timeout(0, 20)
    b.receive(5, "e3", "acme", 3, "charge", 3)
    b.receive(15, "e6", "acme", 6, "charge", 6)
    assert b.pending(24, "acme") == [3, 6]
    assert b.pending(25, "acme") == [6], "5 + 20 = 25: seqs 1-2 are skipped and 3 applies; 6 has waited only 10"
    assert b.missing(26, "acme") == [1, 2]
    assert b.balance(34, "acme") == 3
    assert b.balance(35, "acme") == 9, "15 + 20 = 35: seqs 4-5 are skipped and 6 applies"
    assert b.missing(36, "acme") == [1, 2, 4, 5]


def test_l3_late_event_after_skip():
    """An event for a skipped seq is applied as 'late'"""
    b = _box()
    b.set_gap_timeout(0, 10)
    b.receive(1, "e2", "acme", 2, "charge", 20)
    assert b.missing(11, "acme") == [1]
    assert b.receive(12, "e1", "acme", 1, "charge", 10) == "late"
    assert b.missing(13, "acme") == []
    assert b.balance(14, "acme") == 30
    assert b.receive(15, "e1", "acme", 1, "charge", 10) == "duplicate", "a late event redelivered is still a duplicate"


def test_l3_bad_timeout_is_refused():
    """set_gap_timeout refuses zero, negative and non-integer values"""
    b = _box()
    assert b.set_gap_timeout(1, 0) is False
    assert b.set_gap_timeout(2, -5) is False
    assert b.set_gap_timeout(3, 2.5) is False
    b.receive(4, "e2", "acme", 2, "charge", 1)
    assert b.pending(500, "acme") == [2], "no timeout configured means gaps wait forever"


def test_l3_timeout_set_late_skips_at_set_time():
    """Setting a timeout that is already overdue skips the gap immediately"""
    b = _box()
    b.receive(1, "e2", "acme", 2, "charge", 20)
    b.set_gap_timeout(100, 5)
    assert b.pending(100, "acme") == [], "already waited 99 seconds"
    assert b.missing(100, "acme") == [1]


def test_l3_replay_lists_applied_events_in_seq_order():
    """replay returns applied events from a seq, in seq order, including late ones"""
    b = _box()
    b.set_gap_timeout(0, 10)
    b.receive(1, "e1", "acme", 1, "charge", 1)
    b.receive(2, "e3", "acme", 3, "charge", 3)
    b.receive(3, "e5", "acme", 5, "charge", 5)
    assert b.replay(4, "acme", 1) == ["e1"], "held events are not replayed"
    b.receive(20, "e2", "acme", 2, "charge", 2)
    assert b.replay(21, "acme", 1) == ["e1", "e2", "e3", "e5"], "e2 arrived late but sits at seq 2"
    assert b.replay(22, "acme", 3) == ["e3", "e5"]
    assert b.replay(23, "nobody", 1) == []


# Level 4 ----------------------------------------------------------------
def test_l4_void_applied_event():
    """Voiding an applied event reverses it"""
    b = _box()
    b.receive(1, "e1", "acme", 1, "charge", 100)
    b.receive(2, "e2", "acme", 2, "charge", 50)
    assert b.void(3, "e1") is True
    assert b.balance(4, "acme") == 50
    assert b.event_count(5, "acme") == 1
    assert b.void(6, "e1") is False, "already voided"
    assert b.void(7, "ghost") is False, "unknown event"


def test_l4_duplicate_after_void_does_not_resurrect():
    """A retried delivery of a voided event stays voided"""
    b = _box()
    b.receive(1, "e1", "acme", 1, "charge", 100)
    b.void(2, "e1")
    assert b.receive(3, "e1", "acme", 1, "charge", 100) == "duplicate"
    assert b.balance(4, "acme") == 0
    assert b.replay(5, "acme", 1) == [], "voided events are not replayed"


def test_l4_void_held_event_unblocks_later_seqs():
    """A voided held event still fills its seq, but never moves money"""
    b = _box()
    b.receive(1, "e2", "acme", 2, "charge", 200)
    b.receive(2, "e3", "acme", 3, "charge", 300)
    assert b.void(3, "e2") is True
    assert b.pending(4, "acme") == [3], "voided held events leave pending"
    b.receive(5, "e1", "acme", 1, "charge", 100)
    assert b.applied_seq(6, "acme") == 3
    assert b.balance(7, "acme") == 400, "e2 was voided before it applied"
    assert b.replay(8, "acme", 1) == ["e1", "e3"]


def test_l4_balance_at_uses_application_times():
    """balance_at counts held events from the time they were applied"""
    b = _box()
    b.receive(10, "e2", "acme", 2, "charge", 20)
    b.receive(20, "e1", "acme", 1, "charge", 10)
    b.void(30, "e2")
    assert b.balance_at(40, "acme", 15) == 0, "e2 was held at 15"
    assert b.balance_at(40, "acme", 20) == 30, "both applied at 20"
    assert b.balance_at(40, "acme", 29) == 30
    assert b.balance_at(40, "acme", 30) == 10, "the void counts at 30"
    assert b.balance_at(40, "nobody", 30) == 0


def test_l4_balance_at_timeout_and_late():
    """Skips count at their due time and late events at arrival"""
    b = _box()
    b.set_gap_timeout(0, 10)
    b.receive(5, "e2", "acme", 2, "charge", 20)
    b.receive(50, "e1", "acme", 1, "refund", 5)
    assert b.balance_at(60, "acme", 14) == 0
    assert b.balance_at(60, "acme", 15) == 20, "the gap was skipped at 5 + 10, even though nobody called until 50"
    assert b.balance_at(60, "acme", 49) == 20
    assert b.balance_at(60, "acme", 50) == 15, "the late refund counts from its arrival"


def test_l4_balance_at_future_time_answers_up_to_now():
    """balance_at with a future time reports only what has happened so far"""
    b = _box()
    b.set_gap_timeout(0, 100)
    b.receive(1, "e2", "acme", 2, "charge", 20)
    assert b.balance_at(50, "acme", 1000) == 0, "the skip is due at 101, after the current time 50"
    assert b.balance_at(101, "acme", 1000) == 20


def test_l4_late_event_then_void_and_replay():
    """Late, voided and replayed events interact correctly"""
    b = _box()
    b.set_gap_timeout(0, 10)
    b.receive(1, "e1", "acme", 1, "charge", 1)
    b.receive(2, "e3", "acme", 3, "charge", 3)
    b.receive(20, "e2", "acme", 2, "charge", 2)
    assert b.void(21, "e2") is True
    assert b.replay(22, "acme", 1) == ["e1", "e3"]
    assert b.balance(23, "acme") == 4
    assert b.missing(24, "acme") == []
    assert b.balance_at(25, "acme", 20) == 6
