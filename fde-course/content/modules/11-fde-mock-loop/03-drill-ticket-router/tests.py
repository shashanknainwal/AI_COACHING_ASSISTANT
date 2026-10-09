def _router():
    return TicketRouter()


# Level 1 ----------------------------------------------------------------
def test_l1_routes_by_first_matching_rule():
    """ingest routes by the first rule whose keyword is in the subject, else to triage"""
    r = _router()
    assert r.add_rule(1, "invoice", "billing") == 1, "add_rule returns 1 for the first rule"
    assert r.add_rule(2, "Login", "access") == 2, "rule numbers count up from 1"
    assert r.add_rule(3, "refund", "billing") == 3
    assert r.ingest(4, "T1", "Wrong INVOICE total") == "billing", "keyword matching is case-insensitive"
    assert r.ingest(5, "T2", "cannot login after refund") == "access", "the first rule added wins when several match"
    assert r.ingest(6, "T3", "Printer on fire") == "triage", "a ticket no rule matches goes to triage"


def test_l1_get_ticket_and_close():
    """get_ticket shows 'queue:status'; close works once"""
    r = _router()
    r.add_rule(1, "invoice", "billing")
    r.ingest(2, "T1", "invoice missing")
    assert r.get_ticket(3, "T1") == "billing:open"
    assert r.close(4, "T1") is True
    assert r.get_ticket(5, "T1") == "billing:closed"
    assert r.close(6, "T1") is False, "closing a closed ticket returns False"
    assert r.close(7, "nope") is False, "closing a missing ticket returns False"
    assert r.get_ticket(8, "nope") is None, "a missing ticket reads as None"


def test_l1_duplicates_and_listing():
    """Duplicate ids are refused and list_queue shows open tickets, sorted"""
    r = _router()
    r.add_rule(1, "invoice", "billing")
    assert r.ingest(2, "T9", "invoice A") == "billing"
    assert r.ingest(3, "T9", "something else") is None, "an existing ticket id returns None"
    assert r.get_ticket(4, "T9") == "billing:open", "a refused ingest must not change the ticket"
    r.ingest(5, "T2", "invoice B")
    r.ingest(6, "T5", "invoice C")
    r.close(7, "T5")
    assert r.list_queue(8, "billing") == ["T2", "T9"], "only open tickets, sorted by id"
    assert r.list_queue(9, "access") == [], "an unknown queue lists nothing"
    r.add_rule(10, "printer", "it")
    assert r.ingest(11, "T7", "printer jam") == "it", "a rule added later applies to new tickets"


# Level 2 ----------------------------------------------------------------
def test_l2_set_sla():
    """set_sla accepts positive integers only"""
    r = _router()
    assert r.set_sla(1, "billing", 60) is True
    assert r.set_sla(2, "billing", 0) is False, "a limit of 0 is refused"
    assert r.set_sla(3, "billing", -5) is False, "a negative limit is refused"


def test_l2_queue_stats_and_breaches():
    """queue_stats counts open, closed and breached tickets in a queue"""
    r = _router()
    r.add_rule(1, "invoice", "billing")
    r.set_sla(2, "billing", 10)
    r.ingest(10, "A", "invoice 1")   # due 20
    r.ingest(12, "B", "invoice 2")   # due 22
    r.ingest(14, "C", "invoice 3")   # due 24
    r.close(20, "A")                 # closed exactly at due: on time
    r.close(23, "B")                 # closed after due: breached
    assert r.queue_stats(24, "billing") == {"open": 1, "closed": 2, "breached": 1}, "closing at the due time is on time; after it is a breach; C is not late at 24"
    assert r.queue_stats(25, "billing") == {"open": 1, "closed": 2, "breached": 2}, "an open ticket past its due time is breached"
    assert r.queue_stats(26, "nothing") == {"open": 0, "closed": 0, "breached": 0}


def test_l2_sla_fixed_at_ingest():
    """A ticket's due time is set when it arrives; queues without an SLA never breach"""
    r = _router()
    r.add_rule(1, "invoice", "billing")
    r.ingest(2, "A", "invoice")          # no SLA yet: no due time
    r.set_sla(3, "billing", 5)
    r.ingest(4, "B", "invoice")          # due 9
    r.set_sla(5, "billing", 100)         # does not change B's due time
    r.ingest(6, "C", "invoice")          # due 106
    r.ingest(7, "D", "hello")            # triage has no SLA
    assert r.overdue(10) == ["B"], "only B is past due; A had no SLA when it arrived and the SLA change doesn't move B"
    assert r.queue_stats(1000, "triage")["breached"] == 0


def test_l2_overdue_order():
    """overdue lists open late tickets by due time, then id"""
    r = _router()
    r.add_rule(1, "invoice", "billing")
    r.add_rule(2, "login", "access")
    r.set_sla(3, "billing", 30)
    r.set_sla(4, "access", 10)
    r.ingest(10, "Z", "invoice")   # due 40
    r.ingest(20, "Y", "login")     # due 30
    r.ingest(20, "X", "login")     # due 30
    r.ingest(25, "W", "invoice")   # due 55
    assert r.overdue(30) == [], "nothing is late at exactly its due time"
    assert r.overdue(41) == ["X", "Y", "Z"], "sort by due time, then by ticket id"
    r.close(42, "Y")
    assert r.overdue(56) == ["X", "Z", "W"], "closed tickets are not overdue"


# Level 3 ----------------------------------------------------------------
def test_l3_escalates_after_time_in_queue():
    """An open ticket moves after 'after' units in a queue; get_ticket sees it"""
    r = _router()
    r.add_rule(1, "outage", "tier1")
    assert r.add_escalation(2, "tier1", 30, "tier2") is True
    r.ingest(10, "A", "outage in EU")
    assert r.get_ticket(39, "A") == "tier1:open"
    assert r.get_ticket(40, "A") == "tier2:open", "a ticket moves at entered + after; a call at exactly that time sees it"
    assert r.list_queue(41, "tier1") == []
    assert r.list_queue(41, "tier2") == ["A"]
    assert r.escalation_count(42, "A") == 1
    assert r.escalation_count(42, "nope") is None


def test_l3_chains_and_closed_tickets():
    """Escalations chain through queues; closed tickets never move"""
    r = _router()
    r.add_rule(1, "outage", "tier1")
    r.add_escalation(2, "tier1", 10, "tier2")
    r.add_escalation(3, "tier2", 5, "oncall")
    r.ingest(10, "A", "outage")     # tier2 at 20, oncall at 25
    r.ingest(11, "B", "outage")     # would move at 21
    r.close(15, "B")
    assert r.get_ticket(100, "A") == "oncall:open", "chain: tier1 -> tier2 at 20 -> oncall at 25"
    assert r.escalation_count(100, "A") == 2
    assert r.get_ticket(100, "B") == "tier1:closed", "closed tickets don't escalate"


def test_l3_rules_change_over_time():
    """A new rule never moves a ticket before it existed; removing a rule stops future moves"""
    r = _router()
    r.add_rule(1, "outage", "tier1")
    r.ingest(10, "A", "outage")
    r.ingest(50, "B", "outage")
    assert r.add_escalation(100, "tier1", 20, "tier2") is True
    assert r.list_queue(100, "tier2") == ["A", "B"], "tickets already past the limit move at the rule's own timestamp"
    r.ingest(101, "C", "outage")    # would move at 121
    assert r.remove_escalation(110, "tier1") is True
    assert r.remove_escalation(111, "tier1") is False, "removing a missing rule returns False"
    assert r.get_ticket(200, "C") == "tier1:open", "a removed rule moves nothing"
    assert r.add_escalation(201, "x", 0, "y") is False, "after must be a positive integer"
    assert r.add_escalation(202, "x", 5, "x") is False, "a queue can't escalate to itself"


def test_l3_replacing_a_rule_and_stats():
    """A new rule for the same queue replaces the old one; stats follow the current queue"""
    r = _router()
    r.add_rule(1, "outage", "tier1")
    r.set_sla(2, "tier1", 100)
    r.add_escalation(3, "tier1", 50, "tier2")
    r.ingest(10, "A", "outage")             # due 110; would move at 60
    r.add_escalation(20, "tier1", 30, "tier3")  # now moves at max(40, 20) = 40
    assert r.get_ticket(45, "A") == "tier3:open"
    assert r.queue_stats(200, "tier3") == {"open": 1, "closed": 0, "breached": 1}, "the due time set at ingest travels with the ticket"
    assert r.queue_stats(200, "tier1") == {"open": 0, "closed": 0, "breached": 0}


# Level 4 ----------------------------------------------------------------
def test_l4_history_records_every_change():
    """history lists ingest, escalations at their own time, reroutes and the close"""
    r = _router()
    r.add_rule(1, "outage", "tier1")
    r.add_escalation(2, "tier1", 10, "tier2")
    r.ingest(5, "A", "outage")
    assert r.reroute(30, "A", "network") is True
    r.close(40, "A")
    assert r.history(50, "A") == [
        "5:ingested:tier1",
        "15:escalated:tier1->tier2",
        "30:rerouted:tier2->network",
        "40:closed",
    ], "escalations are recorded at the time they happened, not when a call noticed them"
    assert r.history(51, "nope") is None


def test_l4_reroute_rules():
    """reroute moves an open ticket, resets its time in queue, and refuses no-ops"""
    r = _router()
    r.add_rule(1, "outage", "tier1")
    r.add_escalation(2, "tier2", 10, "oncall")
    r.ingest(5, "A", "outage")
    assert r.reroute(6, "A", "tier1") is False, "rerouting to the current queue returns False"
    assert r.reroute(7, "nope", "x") is False
    assert r.reroute(20, "A", "tier2") is True
    assert r.get_ticket(29, "A") == "tier2:open", "time in queue starts again at the reroute"
    assert r.get_ticket(30, "A") == "oncall:open"
    r.close(31, "A")
    assert r.reroute(32, "A", "tier1") is False, "a closed ticket can't be rerouted"


def test_l4_queue_at_replays_the_past():
    """queue_at answers 'where was this ticket at time at?'"""
    r = _router()
    r.add_rule(1, "outage", "tier1")
    r.add_escalation(2, "tier1", 10, "tier2")
    r.ingest(5, "A", "outage")
    r.reroute(40, "A", "network")
    assert r.queue_at(50, "A", 4) is None, "before the ticket arrived"
    assert r.queue_at(50, "A", 5) == "tier1", "a change at exactly 'at' counts"
    assert r.queue_at(50, "A", 14) == "tier1"
    assert r.queue_at(50, "A", 15) == "tier2"
    assert r.queue_at(50, "A", 45) == "network"
    assert r.queue_at(50, "nope", 45) is None


def test_l4_open_at_rebuilds_a_queue():
    """open_at lists the tickets open in a queue at a past time"""
    r = _router()
    r.add_rule(1, "outage", "tier1")
    r.add_escalation(2, "tier1", 20, "tier2")
    r.ingest(10, "A", "outage")   # tier2 at 30
    r.ingest(12, "B", "outage")
    r.close(15, "B")
    r.ingest(18, "C", "outage")   # tier2 at 38
    assert r.open_at(100, "tier1", 14) == ["A", "B"]
    assert r.open_at(100, "tier1", 15) == ["A"], "a ticket closed at exactly 'at' is not open"
    assert r.open_at(100, "tier1", 30) == ["C"]
    assert r.open_at(100, "tier2", 40) == ["A", "C"]
    assert r.open_at(100, "tier2", 5) == []


def test_l4_late_rule_is_recorded_at_its_own_time():
    """A ticket moved by a rule added late is recorded at the rule's timestamp"""
    r = _router()
    r.add_rule(1, "outage", "tier1")
    r.ingest(10, "A", "outage")
    r.add_escalation(100, "tier1", 20, "tier2")
    assert r.history(150, "A") == ["10:ingested:tier1", "100:escalated:tier1->tier2"], "the move happens when the rule appears, not at 10 + 20"
    assert r.queue_at(150, "A", 99) == "tier1"
