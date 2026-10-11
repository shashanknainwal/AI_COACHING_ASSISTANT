class WebhookInbox:
    """Idempotent webhook ingest with ordering, gap timeouts, replay and voids.

    Model chosen before Level 1 (the point of the drill):
      - events: event_id -> record (payload, status, times)
      - per account: next expected seq, held events, skipped seqs
      - history: account -> append-only list of (time, delta) for balance_at
    Every public method starts with _catch_up(timestamp).
    """

    KINDS = ("charge", "refund")

    def __init__(self):
        self.events = {}
        self.accounts = {}
        self.timeout = None
        self.timeout_set_at = 0

    # -- helpers -------------------------------------------------------
    def _acct(self, account):
        if account not in self.accounts:
            self.accounts[account] = {
                "next": 1,
                "held": {},        # seq -> event_id
                "owner": {},       # seq -> event_id (held, applied or voided)
                "missing": set(),  # skipped seqs that never arrived
                "history": [],     # (time, delta)
                "last_skip": 0,
            }
        return self.accounts[account]

    def _delta(self, ev):
        return ev["amount"] if ev["kind"] == "charge" else -ev["amount"]

    def _apply(self, a, event_id, at):
        ev = self.events[event_id]
        if ev["status"] == "voided":
            return
        ev["status"] = "applied"
        ev["applied_at"] = at
        a["history"].append((at, self._delta(ev)))

    def _drain(self, a, at):
        while a["next"] in a["held"]:
            eid = a["held"].pop(a["next"])
            self._apply(a, eid, at)
            a["next"] += 1

    def _catch_up(self, timestamp):
        if self.timeout is None:
            return
        for a in self.accounts.values():
            while a["held"]:
                oldest = min(self.events[e]["received_at"] for e in a["held"].values())
                due = max(oldest + self.timeout, self.timeout_set_at, a["last_skip"])
                if due > timestamp:
                    break
                lowest = min(a["held"])
                for s in range(a["next"], lowest):
                    a["missing"].add(s)
                a["next"] = lowest
                a["last_skip"] = due
                self._drain(a, due)

    # -- Level 1 -------------------------------------------------------
    def receive(self, timestamp, event_id, account, seq, kind, amount):
        self._catch_up(timestamp)
        if kind not in self.KINDS or not isinstance(amount, int) or isinstance(amount, bool) or amount <= 0:
            return "rejected"
        payload = (account, seq, kind, amount)
        if event_id in self.events:
            return "duplicate" if self.events[event_id]["payload"] == payload else "conflict"
        a = self._acct(account)
        if seq in a["owner"]:
            return "conflict"
        self.events[event_id] = {"payload": payload, "account": account, "seq": seq, "kind": kind,
                                 "amount": amount, "status": "new", "received_at": timestamp}
        a["owner"][seq] = event_id
        if seq in a["missing"]:
            a["missing"].discard(seq)
            self._apply(a, event_id, timestamp)
            return "late"
        if seq == a["next"]:
            self._apply(a, event_id, timestamp)
            a["next"] += 1
            self._drain(a, timestamp)
            return "accepted"
        if seq < a["next"]:
            # seq already passed with no owner: only possible for a skipped seq, handled above
            return "conflict"
        self.events[event_id]["status"] = "held"
        a["held"][seq] = event_id
        return "held"

    def balance(self, timestamp, account):
        self._catch_up(timestamp)
        a = self.accounts.get(account)
        return sum(d for _, d in a["history"]) if a else 0

    def event_count(self, timestamp, account):
        self._catch_up(timestamp)
        return sum(1 for e in self.events.values() if e["account"] == account and e["status"] == "applied")

    # -- Level 2 -------------------------------------------------------
    def pending(self, timestamp, account):
        self._catch_up(timestamp)
        a = self.accounts.get(account)
        if not a:
            return []
        return sorted(s for s, eid in a["held"].items() if self.events[eid]["status"] != "voided")

    def applied_seq(self, timestamp, account):
        self._catch_up(timestamp)
        a = self.accounts.get(account)
        return a["next"] - 1 if a else 0

    # -- Level 3 -------------------------------------------------------
    def set_gap_timeout(self, timestamp, seconds):
        self._catch_up(timestamp)
        if not isinstance(seconds, int) or isinstance(seconds, bool) or seconds <= 0:
            return False
        self.timeout = seconds
        self.timeout_set_at = timestamp
        self._catch_up(timestamp)
        return True

    def missing(self, timestamp, account):
        self._catch_up(timestamp)
        a = self.accounts.get(account)
        return sorted(a["missing"]) if a else []

    def replay(self, timestamp, account, from_seq):
        self._catch_up(timestamp)
        a = self.accounts.get(account)
        if not a:
            return []
        out = []
        for seq in sorted(a["owner"]):
            ev = self.events[a["owner"][seq]]
            if seq >= from_seq and ev["status"] == "applied":
                out.append(a["owner"][seq])
        return out

    # -- Level 4 -------------------------------------------------------
    def void(self, timestamp, event_id):
        self._catch_up(timestamp)
        ev = self.events.get(event_id)
        if ev is None or ev["status"] == "voided":
            return False
        a = self.accounts[ev["account"]]
        if ev["status"] == "applied":
            a["history"].append((timestamp, -self._delta(ev)))
        ev["status"] = "voided"
        return True

    def balance_at(self, timestamp, account, at):
        self._catch_up(timestamp)
        a = self.accounts.get(account)
        if not a:
            return 0
        return sum(d for t, d in a["history"] if t <= at)


if __name__ == "__main__":
    box = WebhookInbox()
    print(box.receive(1, "e1", "acme", 1, "charge", 500))   # accepted
    print(box.receive(2, "e1", "acme", 1, "charge", 500))   # duplicate
    print(box.balance(3, "acme"))                           # 500
