import json


class StreamClient:
    """A server-sent events client: parsing, ids, reconnection, replay dedupe, message assembly."""

    MAX_DELAY = 30000

    def __init__(self):
        self.buf = ""
        self.skip_lf = False
        self.started = False
        self.data = []
        self.etype = ""
        self.id_buf = None        # pending id (committed at the next blank line)
        self.id_in_block = False
        self.last_id = None       # committed last event id
        self.retry = 3000
        self.connected = True
        self.next_allowed = 0
        self.delivered_this_conn = 0
        self.empty_conns = 0
        self.max_int_id = None
        self.msgs = {}            # msg id -> {"text": str, "done": bool}
        self.done_order = []
        self.error_count = 0

    # -- parsing -------------------------------------------------------
    def _lines(self, chunk):
        if self.skip_lf and chunk.startswith("\n"):
            chunk = chunk[1:]
        self.skip_lf = False
        self.buf += chunk
        if not self.started and self.buf:
            self.started = True
            if self.buf.startswith("﻿"):
                self.buf = self.buf[1:]
        lines = []
        i = 0
        start = 0
        while i < len(self.buf):
            c = self.buf[i]
            if c == "\n" or c == "\r":
                lines.append(self.buf[start:i])
                if c == "\r":
                    if i + 1 < len(self.buf):
                        if self.buf[i + 1] == "\n":
                            i += 1
                    else:
                        self.skip_lf = True
                start = i + 1
            i += 1
        self.buf = self.buf[start:]
        return lines

    def _line(self, line, out):
        if line == "":
            self._dispatch(out)
            return
        if line.startswith(":"):
            return
        if ":" in line:
            field, value = line.split(":", 1)
            if value.startswith(" "):
                value = value[1:]
        else:
            field, value = line, ""
        if field == "event":
            self.etype = value
        elif field == "data":
            self.data.append(value)
        elif field == "id":
            if "\0" not in value:
                self.id_buf = value
                self.id_in_block = True
        elif field == "retry":
            if value and all(ch in "0123456789" for ch in value):
                self.retry = int(value)

    def _dispatch(self, out):
        had_data = bool(self.data)
        etype = self.etype or "message"
        data = "\n".join(self.data)
        own_id = self.id_in_block
        self.data, self.etype, self.id_in_block = [], "", False
        candidate = self.id_buf
        if own_id and candidate is not None and candidate.isdigit() and self.max_int_id is not None \
                and int(candidate) <= self.max_int_id:
            self.id_buf = self.last_id          # dropped replay: change nothing
            return
        self.last_id = candidate
        if not had_data:
            return
        if own_id and candidate is not None and candidate.isdigit():
            self.max_int_id = int(candidate) if self.max_int_id is None else max(self.max_int_id, int(candidate))
        event = {"type": etype, "data": data, "id": self.last_id}
        self.delivered_this_conn += 1
        self._assemble(event)
        out.append(event)

    def _assemble(self, ev):
        if ev["type"] not in ("start", "delta", "stop"):
            return
        try:
            body = json.loads(ev["data"])
            mid = body["msg"]
        except (ValueError, KeyError, TypeError):
            self.error_count += 1
            return
        m = self.msgs.get(mid)
        if ev["type"] == "start":
            if m is not None:
                self.error_count += 1
                return
            self.msgs[mid] = {"text": "", "done": False}
        elif m is None or m["done"]:
            self.error_count += 1
        elif ev["type"] == "delta":
            text = body.get("text")
            if not isinstance(text, str):
                self.error_count += 1
                return
            m["text"] += text
        else:
            m["done"] = True
            self.done_order.append(mid)

    # -- Level 1 -------------------------------------------------------
    def feed(self, timestamp, chunk):
        if not self.connected:
            return []
        out = []
        for line in self._lines(chunk):
            self._line(line, out)
        return out

    # -- Level 2 -------------------------------------------------------
    def last_event_id(self, timestamp):
        return self.last_id

    def retry_ms(self, timestamp):
        return self.retry

    # -- Level 3 -------------------------------------------------------
    def disconnect(self, timestamp):
        if not self.connected:
            return None
        self.connected = False
        self.buf, self.skip_lf = "", False
        self.data, self.etype, self.id_in_block = [], "", False
        self.id_buf = self.last_id
        if self.delivered_this_conn:
            self.empty_conns = 0
        else:
            self.empty_conns += 1
        delay = min(self.retry * (2 ** self.empty_conns) if self.empty_conns else self.retry, self.MAX_DELAY)
        self.next_allowed = timestamp + delay
        return self.next_allowed

    def connect(self, timestamp):
        if self.connected or timestamp < self.next_allowed:
            return False
        self.connected = True
        self.delivered_this_conn = 0
        return True

    def headers(self, timestamp):
        return {"Last-Event-ID": self.last_id} if self.last_id else {}

    # -- Level 4 -------------------------------------------------------
    def message(self, timestamp, msg_id):
        m = self.msgs.get(msg_id)
        return dict(m) if m else None

    def completed(self, timestamp):
        return list(self.done_order)

    def errors(self, timestamp):
        return self.error_count


if __name__ == "__main__":
    c = StreamClient()
    print(c.feed(1, "data: hello\n"))     # []
    print(c.feed(2, "\n"))                # [{'type': 'message', 'data': 'hello', 'id': None}]
