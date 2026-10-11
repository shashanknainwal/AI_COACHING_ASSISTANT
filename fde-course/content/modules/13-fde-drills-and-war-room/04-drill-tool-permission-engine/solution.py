class ToolGate:
    """Permission engine for an agent's tools: scopes, roles, denies, approvals, audit.

    Model chosen before Level 1: every permission change is appended to a log of
    (time, op, args). Current permissions, and permissions at any past time, come
    from replaying that log, so Level 4's could_call is a filter, not a rewrite.
    """

    def __init__(self):
        self.log = []          # (time, op, args)
        self.requests = {}     # id -> dict
        self.req_seq = 0
        self.approval = {}     # tool -> (role, ttl)
        self.audit_log = []    # (principal, line)

    # -- state ---------------------------------------------------------
    def _state(self, at=None):
        tools, direct, roles, assigned, denies = {}, {}, {}, {}, {}
        for t, op, a in self.log:
            if at is not None and t > at:
                break
            if op == "tool":
                tools[a[0]] = a[1]
            elif op == "grant":
                direct.setdefault(a[0], set()).add(a[1])
            elif op == "revoke":
                direct.get(a[0], set()).discard(a[1])
            elif op == "role":
                roles[a[0]] = set(a[1])
            elif op == "assign":
                assigned.setdefault(a[0], set()).add(a[1])
            elif op == "unassign":
                assigned.get(a[0], set()).discard(a[1])
            elif op == "deny":
                denies.setdefault(a[0], set()).add(a[1])
        return {"tools": tools, "direct": direct, "roles": roles, "assigned": assigned, "denies": denies}

    @staticmethod
    def _matches(grant, scope):
        if grant == "*" or grant == scope:
            return True
        return grant.endswith(":*") and scope.startswith(grant[:-1])

    def _sources(self, st, principal, scope):
        out = []
        for g in st["direct"].get(principal, ()):
            if self._matches(g, scope):
                out.append("direct:" + g)
        for r in st["assigned"].get(principal, ()):
            if any(self._matches(g, scope) for g in st["roles"].get(r, ())):
                out.append("role:" + r)
        for d in st["denies"].get(principal, ()):
            if self._matches(d, scope):
                out.append("deny:" + d)
        return sorted(out)

    def _allowed(self, st, principal, tool):
        if tool not in st["tools"]:
            return False
        src = self._sources(st, principal, st["tools"][tool])
        return bool(src) and not any(s.startswith("deny:") for s in src)

    def _audit(self, principal, line):
        self.audit_log.append((principal, line))

    def _catch_up(self, ts):
        for rid in sorted(self.requests, key=lambda r: (self.requests[r]["expires"], self.requests[r]["n"])):
            req = self.requests[rid]
            if req["status"] == "pending" and req["expires"] <= ts:
                req["status"] = "expired"
                self._audit(req["principal"], f"{req['expires']} expire {rid}")

    # -- Level 1 -------------------------------------------------------
    def add_tool(self, timestamp, name, scope):
        self._catch_up(timestamp)
        if name in self._state()["tools"]:
            return False
        self.log.append((timestamp, "tool", (name, scope)))
        return True

    def grant(self, timestamp, principal, scope):
        self._catch_up(timestamp)
        if scope in self._state()["direct"].get(principal, ()):
            return False
        self.log.append((timestamp, "grant", (principal, scope)))
        return True

    def revoke(self, timestamp, principal, scope):
        self._catch_up(timestamp)
        if scope not in self._state()["direct"].get(principal, ()):
            return False
        self.log.append((timestamp, "revoke", (principal, scope)))
        return True

    def call(self, timestamp, principal, tool):
        self._catch_up(timestamp)
        st = self._state()
        if tool not in st["tools"]:
            result = "unknown_tool"
        elif not self._allowed(st, principal, tool):
            result = "denied"
        elif tool in self.approval:
            role, ttl = self.approval[tool]
            self.req_seq += 1
            rid = f"req{self.req_seq}"
            self.requests[rid] = {"n": self.req_seq, "principal": principal, "tool": tool, "role": role,
                                  "expires": timestamp + ttl, "status": "pending"}
            result = "pending:" + rid
        else:
            result = "allowed"
        self._audit(principal, f"{timestamp} call {tool} -> {result}")
        return result

    # -- Level 2 -------------------------------------------------------
    def define_role(self, timestamp, role, scopes):
        self._catch_up(timestamp)
        self.log.append((timestamp, "role", (role, tuple(scopes))))
        return True

    def assign(self, timestamp, principal, role):
        self._catch_up(timestamp)
        st = self._state()
        if role not in st["roles"] or role in st["assigned"].get(principal, ()):
            return False
        self.log.append((timestamp, "assign", (principal, role)))
        return True

    def unassign(self, timestamp, principal, role):
        self._catch_up(timestamp)
        if role not in self._state()["assigned"].get(principal, ()):
            return False
        self.log.append((timestamp, "unassign", (principal, role)))
        return True

    def deny(self, timestamp, principal, scope):
        self._catch_up(timestamp)
        self.log.append((timestamp, "deny", (principal, scope)))
        return True

    def explain(self, timestamp, principal, tool):
        self._catch_up(timestamp)
        st = self._state()
        if tool not in st["tools"]:
            return None
        return self._sources(st, principal, st["tools"][tool])

    # -- Level 3 -------------------------------------------------------
    def require_approval(self, timestamp, tool, approver_role, ttl):
        self._catch_up(timestamp)
        if tool not in self._state()["tools"]:
            return False
        if not isinstance(ttl, int) or isinstance(ttl, bool) or ttl <= 0:
            return False
        self.approval[tool] = (approver_role, ttl)
        return True

    def _decide(self, timestamp, request_id, approver, verb):
        self._catch_up(timestamp)
        req = self.requests.get(request_id)
        st = self._state()
        ok = (
            req is not None
            and req["status"] == "pending"
            and approver != req["principal"]
            and req["role"] in st["assigned"].get(approver, ())
        )
        if not ok:
            self._audit(approver, f"{timestamp} {verb} {request_id} -> refused")
            return False
        if verb == "reject":
            req["status"] = "rejected"
        elif self._allowed(st, req["principal"], req["tool"]):
            req["status"] = "approved"
        else:
            req["status"] = "denied"
        self._audit(approver, f"{timestamp} {verb} {request_id} -> {req['status']}")
        return req["status"] in ("approved", "rejected")

    def approve(self, timestamp, request_id, approver):
        return self._decide(timestamp, request_id, approver, "approve")

    def reject(self, timestamp, request_id, approver):
        return self._decide(timestamp, request_id, approver, "reject")

    def status(self, timestamp, request_id):
        self._catch_up(timestamp)
        req = self.requests.get(request_id)
        return req["status"] if req else None

    # -- Level 4 -------------------------------------------------------
    def audit(self, timestamp, principal):
        self._catch_up(timestamp)
        return [line for p, line in self.audit_log if p == principal]

    def could_call(self, timestamp, principal, tool, at):
        self._catch_up(timestamp)
        return self._allowed(self._state(at), principal, tool)


if __name__ == "__main__":
    g = ToolGate()
    g.add_tool(1, "refund", "billing:write")
    g.grant(2, "agent-7", "billing:*")
    print(g.call(3, "agent-7", "refund"))  # allowed
