class Gateway:
    """An LLM gateway that tracks API keys, token quotas and rate limits.
    Timestamps only ever increase between calls."""

    def __init__(self):
        # key_id -> {"owner", "quota", "used", "uses": [(t, tokens)], "limit", "revoked"}
        self.keys = {}

    # --- shared helpers -------------------------------------------------
    @staticmethod
    def _fmt(name, value):
        return f"{name}({value})"

    def _active(self, key_id):
        key = self.keys.get(key_id)
        if key is None or key["revoked"]:
            return None
        return key

    # --- level 1 --------------------------------------------------------
    def create_key(self, timestamp, key_id, owner, quota):
        if key_id in self.keys:
            return False
        self.keys[key_id] = {
            "owner": owner,
            "quota": quota,
            "used": 0,
            "uses": [],
            "limit": None,
            "revoked": False,
        }
        return True

    def record_usage(self, timestamp, key_id, tokens):
        key = self._active(key_id)
        if key is None:
            return None
        if key["limit"] is not None:
            max_requests, window = key["limit"]
            recent = sum(1 for t, _ in key["uses"] if timestamp - window < t <= timestamp)
            if recent >= max_requests:
                return -2
        if key["used"] + tokens > key["quota"]:
            return -1
        key["used"] += tokens
        key["uses"].append((timestamp, tokens))
        return key["quota"] - key["used"]

    def get_remaining(self, timestamp, key_id):
        key = self._active(key_id)
        if key is None:
            return None
        return key["quota"] - key["used"]

    # --- level 2 --------------------------------------------------------
    def top_owners(self, timestamp, n):
        if n <= 0:
            return []
        totals = {}
        for key in self.keys.values():
            if key["revoked"]:
                continue
            totals[key["owner"]] = totals.get(key["owner"], 0) + key["used"]
        ranked = sorted(totals, key=lambda o: (-totals[o], o))
        return [self._fmt(o, totals[o]) for o in ranked[:n]]

    def keys_for(self, timestamp, owner):
        return [
            self._fmt(key_id, key["quota"] - key["used"])
            for key_id, key in sorted(self.keys.items())
            if key["owner"] == owner and not key["revoked"]
        ]

    # --- level 3 --------------------------------------------------------
    def set_rate_limit(self, timestamp, key_id, max_requests, window):
        key = self._active(key_id)
        if key is None:
            return False
        key["limit"] = (max_requests, window)
        return True

    # --- level 4 --------------------------------------------------------
    def revoke_key(self, timestamp, key_id):
        key = self._active(key_id)
        if key is None:
            return False
        key["revoked"] = True
        return True

    def usage_between(self, timestamp, key_id, start, end):
        key = self.keys.get(key_id)
        if key is None:
            return None
        return sum(tokens for t, tokens in key["uses"] if start <= t < end)
