class TicketRouter:
    """A ticket-routing service. Timestamps only ever increase between calls."""

    def __init__(self):
        self.rules = []            # (keyword_lower, queue), checked in order
        self.tickets = {}          # id -> dict
        self.sla = {}              # queue -> limit
        self.escalations = {}      # from_queue -> (after, to_queue, created)

    # --- helpers ----------------------------------------------------------
    def _log(self, t, at, text):
        t["history"].append((at, text, t["queue"], t["status"]))

    def _move(self, t, at, new_queue, kind):
        old = t["queue"]
        t["queue"] = new_queue
        t["entered"] = at
        self._log(t, at, f"{at}:{kind}:{old}->{new_queue}")

    def _apply_escalations(self, timestamp):
        # Each ticket escalates independently, so handle them one at a time.
        for tid, t in self.tickets.items():
            while t["status"] == "open":
                rule = self.escalations.get(t["queue"])
                if rule is None:
                    break
                after, to_queue, created = rule
                when = max(t["entered"] + after, created)
                if when > timestamp:
                    break
                self._move(t, when, to_queue, "escalated")

    def _breached(self, t, timestamp):
        if t["due"] is None:
            return False
        if t["status"] == "open":
            return timestamp > t["due"]
        return t["closed_at"] > t["due"]

    # --- level 1 ----------------------------------------------------------
    def add_rule(self, timestamp, keyword, queue):
        self._apply_escalations(timestamp)
        self.rules.append((keyword.lower(), queue))
        return len(self.rules)

    def ingest(self, timestamp, ticket_id, subject):
        self._apply_escalations(timestamp)
        if ticket_id in self.tickets:
            return None
        queue = "triage"
        low = subject.lower()
        for keyword, q in self.rules:
            if keyword in low:
                queue = q
                break
        limit = self.sla.get(queue)
        t = {
            "queue": queue,
            "status": "open",
            "entered": timestamp,
            "due": timestamp + limit if limit else None,
            "closed_at": None,
            "history": [],
        }
        self.tickets[ticket_id] = t
        self._log(t, timestamp, f"{timestamp}:ingested:{queue}")
        return queue

    def get_ticket(self, timestamp, ticket_id):
        self._apply_escalations(timestamp)
        t = self.tickets.get(ticket_id)
        if t is None:
            return None
        return f"{t['queue']}:{t['status']}"

    def close(self, timestamp, ticket_id):
        self._apply_escalations(timestamp)
        t = self.tickets.get(ticket_id)
        if t is None or t["status"] != "open":
            return False
        t["status"] = "closed"
        t["closed_at"] = timestamp
        self._log(t, timestamp, f"{timestamp}:closed")
        return True

    def list_queue(self, timestamp, queue):
        self._apply_escalations(timestamp)
        return sorted(tid for tid, t in self.tickets.items()
                      if t["queue"] == queue and t["status"] == "open")

    # --- level 2 ----------------------------------------------------------
    def set_sla(self, timestamp, queue, limit):
        self._apply_escalations(timestamp)
        if not isinstance(limit, int) or limit <= 0:
            return False
        self.sla[queue] = limit
        return True

    def queue_stats(self, timestamp, queue):
        self._apply_escalations(timestamp)
        stats = {"open": 0, "closed": 0, "breached": 0}
        for t in self.tickets.values():
            if t["queue"] != queue:
                continue
            stats[t["status"]] += 1
            if self._breached(t, timestamp):
                stats["breached"] += 1
        return stats

    def overdue(self, timestamp):
        self._apply_escalations(timestamp)
        late = [(t["due"], tid) for tid, t in self.tickets.items()
                if t["status"] == "open" and self._breached(t, timestamp)]
        return [tid for _, tid in sorted(late)]

    # --- level 3 ----------------------------------------------------------
    def add_escalation(self, timestamp, from_queue, after, to_queue):
        self._apply_escalations(timestamp)
        if not isinstance(after, int) or after <= 0 or from_queue == to_queue:
            return False
        self.escalations[from_queue] = (after, to_queue, timestamp)
        self._apply_escalations(timestamp)
        return True

    def remove_escalation(self, timestamp, from_queue):
        self._apply_escalations(timestamp)
        return self.escalations.pop(from_queue, None) is not None

    def escalation_count(self, timestamp, ticket_id):
        self._apply_escalations(timestamp)
        t = self.tickets.get(ticket_id)
        if t is None:
            return None
        return sum(1 for _, text, _, _ in t["history"] if ":escalated:" in text)

    # --- level 4 ----------------------------------------------------------
    def reroute(self, timestamp, ticket_id, queue):
        self._apply_escalations(timestamp)
        t = self.tickets.get(ticket_id)
        if t is None or t["status"] != "open" or t["queue"] == queue:
            return False
        self._move(t, timestamp, queue, "rerouted")
        self._apply_escalations(timestamp)
        return True

    def history(self, timestamp, ticket_id):
        self._apply_escalations(timestamp)
        t = self.tickets.get(ticket_id)
        if t is None:
            return None
        return [text for _, text, _, _ in t["history"]]

    def _state_at(self, t, at):
        state = None
        for when, _, queue, status in t["history"]:
            if when > at:
                break
            state = (queue, status)
        return state

    def queue_at(self, timestamp, ticket_id, at):
        self._apply_escalations(timestamp)
        t = self.tickets.get(ticket_id)
        if t is None:
            return None
        state = self._state_at(t, at)
        return state[0] if state else None

    def open_at(self, timestamp, queue, at):
        self._apply_escalations(timestamp)
        result = []
        for tid, t in self.tickets.items():
            state = self._state_at(t, at)
            if state == (queue, "open"):
                result.append(tid)
        return sorted(result)


# --- Try it out (not graded) ---
r = TicketRouter()
r.add_rule(1, "invoice", "billing")
print(r.ingest(2, "T1", "Invoice is wrong"))   # billing
print(r.get_ticket(3, "T1"))                    # billing:open
