class SyncEngine:
    """Incremental sync from a rate-limited source API into a destination store.

    Model chosen before Level 1:
      - source: record_id -> (updated_at, data, deleted)
      - a sync key is the tuple (updated_at, record_id); watermarks and cursors are keys
      - every request goes through one _request() helper that pages and checks the budget
    """

    START = (0, "")

    def __init__(self):
        self.source = {}
        self.dest = {}
        self.wm = self.START
        self.page_size = None
        self.per_minute = None
        self.request_times = []
        self.bf = None  # {"cursor": key, "since": int, "upper": key}

    # -- helpers -------------------------------------------------------
    def _keys_after(self, cursor, upper=None, since=None):
        keys = []
        for rid, (upd, _data, _deleted) in self.source.items():
            k = (upd, rid)
            if k <= cursor:
                continue
            if upper is not None and k > upper:
                continue
            if since is not None and upd < since:
                continue
            keys.append(k)
        keys.sort()
        return keys

    def _can_request(self, ts):
        if self.per_minute is None:
            return True
        recent = sum(1 for t in self.request_times if t > ts - 60)
        return recent < self.per_minute

    def _request(self, ts, cursor, upper=None, since=None):
        """One API call. Returns (keys, full) or None when the budget is spent."""
        if not self._can_request(ts):
            return None
        self.request_times.append(ts)
        keys = self._keys_after(cursor, upper, since)
        if self.page_size is not None:
            full = len(keys) >= self.page_size
            keys = keys[: self.page_size]
        else:
            full = False
        return keys, full

    def _copy(self, key):
        upd, rid = key
        _u, data, deleted = self.source[rid]
        if deleted:
            self.dest.pop(rid, None)
        else:
            self.dest[rid] = data

    # -- Level 1 -------------------------------------------------------
    def upsert(self, timestamp, record_id, updated_at, data):
        self.source[record_id] = (updated_at, data, False)
        return True

    def sync(self, timestamp):
        pulled = 0
        while self.bf is not None:
            got = self._request(timestamp, self.bf["cursor"], self.bf["upper"], self.bf["since"])
            if got is None:
                return pulled
            keys, full = got
            for k in keys:
                self._copy(k)
                self.bf["cursor"] = k
            pulled += len(keys)
            if not full:
                self.bf = None
        while True:
            got = self._request(timestamp, self.wm)
            if got is None:
                return pulled
            keys, full = got
            for k in keys:
                self._copy(k)
                self.wm = k
            pulled += len(keys)
            if not full:
                return pulled

    def get(self, timestamp, record_id):
        return self.dest.get(record_id)

    def watermark(self, timestamp):
        return self.wm

    def count(self, timestamp):
        return len(self.dest)

    # -- Level 2 -------------------------------------------------------
    def set_limits(self, timestamp, page_size, per_minute):
        for v in (page_size, per_minute):
            if not isinstance(v, int) or isinstance(v, bool) or v <= 0:
                return False
        self.page_size = page_size
        self.per_minute = per_minute
        return True

    def requests_made(self, timestamp):
        return len(self.request_times)

    def lag(self, timestamp):
        return len(self._keys_after(self.wm))

    # -- Level 3 -------------------------------------------------------
    def backfill(self, timestamp, since):
        if self.bf is not None:
            return False
        self.bf = {"cursor": (since, ""), "since": since, "upper": self.wm}
        return True

    def backfill_status(self, timestamp):
        return "idle" if self.bf is None else "running"

    # -- Level 4 -------------------------------------------------------
    def delete(self, timestamp, record_id, updated_at):
        cur = self.source.get(record_id)
        if cur is None or cur[2]:
            return False
        self.source[record_id] = (updated_at, None, True)
        return True

    def rewind(self, timestamp, updated_at):
        target = (updated_at, "")
        if target >= self.wm:
            return False
        self.wm = target
        return True


if __name__ == "__main__":
    s = SyncEngine()
    s.upsert(1, "r1", 100, {"name": "Ada"})
    s.upsert(2, "r2", 105, {"name": "Lin"})
    print(s.sync(3), s.watermark(3), s.get(4, "r1"))
