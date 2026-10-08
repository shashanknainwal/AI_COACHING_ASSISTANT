class FlagService:
    """A feature-flag service. Timestamps only ever increase between calls."""

    def __init__(self):
        self.flags = {}        # name -> {"enabled": bool, "overrides": {user: bool}}
        self.history = {}      # name -> [(time, state)], state None means deleted
        self.pending = []      # [(at, seq, id, name, enabled)]
        self.seq = 0

    # --- shared helpers -------------------------------------------------
    def _record(self, time, name, state):
        self.history.setdefault(name, []).append((time, state))

    def _apply_due(self, timestamp):
        due = sorted(p for p in self.pending if p[0] <= timestamp)
        self.pending = [p for p in self.pending if p[0] > timestamp]
        for at, _, _, name, enabled in due:
            if name in self.flags:
                self.flags[name]["enabled"] = enabled
                self._record(at, name, enabled)

    # --- level 1 --------------------------------------------------------
    def create_flag(self, timestamp, name, default):
        self._apply_due(timestamp)
        if name in self.flags:
            return False
        self.flags[name] = {"enabled": default, "overrides": {}}
        self._record(timestamp, name, default)
        return True

    def set_flag(self, timestamp, name, enabled):
        self._apply_due(timestamp)
        if name not in self.flags:
            return False
        self.flags[name]["enabled"] = enabled
        self._record(timestamp, name, enabled)
        return True

    def is_enabled(self, timestamp, name, user_id):
        self._apply_due(timestamp)
        flag = self.flags.get(name)
        if flag is None:
            return None
        return flag["overrides"].get(user_id, flag["enabled"])

    def delete_flag(self, timestamp, name):
        self._apply_due(timestamp)
        if name not in self.flags:
            return False
        del self.flags[name]
        self.pending = [p for p in self.pending if p[3] != name]
        self._record(timestamp, name, None)
        return True

    # --- level 2 --------------------------------------------------------
    def set_override(self, timestamp, name, user_id, enabled):
        self._apply_due(timestamp)
        if name not in self.flags:
            return False
        self.flags[name]["overrides"][user_id] = enabled
        return True

    def list_flags(self, timestamp, prefix):
        self._apply_due(timestamp)
        return [f"{n}({'on' if f['enabled'] else 'off'})" for n, f in sorted(self.flags.items()) if n.startswith(prefix)]

    def top_overridden(self, timestamp, n):
        self._apply_due(timestamp)
        ranked = sorted(self.flags.items(), key=lambda kv: (-len(kv[1]["overrides"]), kv[0]))
        return [f"{name}({len(f['overrides'])})" for name, f in ranked if f["overrides"]][:n]

    # --- level 3 --------------------------------------------------------
    def schedule(self, timestamp, name, at, enabled):
        self._apply_due(timestamp)
        if name not in self.flags:
            return None
        self.seq += 1
        sched_id = f"sched{self.seq}"
        self.pending.append((at, self.seq, sched_id, name, enabled))
        self._apply_due(timestamp)
        return sched_id

    def cancel_schedule(self, timestamp, schedule_id):
        self._apply_due(timestamp)
        before = len(self.pending)
        self.pending = [p for p in self.pending if p[2] != schedule_id]
        return len(self.pending) < before

    # --- level 4 --------------------------------------------------------
    def state_at(self, timestamp, name, at):
        self._apply_due(timestamp)
        state = None
        for time, value in self.history.get(name, []):
            if time > at:
                break
            state = value
        return state

    def rollback(self, timestamp, name, to):
        self._apply_due(timestamp)
        if name not in self.flags:
            return False
        past = self.state_at(timestamp, name, to)
        if past is None:
            return False
        return self.set_flag(timestamp, name, past)
