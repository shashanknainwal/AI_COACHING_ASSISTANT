---
title: "Drill: A Tool and Permission Engine"
type: drill
minutes: 70
timeLimit: 70
levels:
  - "Tools and grants"
  - "Roles and denies"
  - "Approvals"
  - "Audit and point-in-time access"
hints:
  - "Level 4 asks whether someone could call a tool at a past time. If every permission change (tool added, grant, revoke, role defined, assign, unassign, deny) is appended to a log of (time, op, args) from Level 1, then current permissions and past permissions come from the same replay function."
  - "Write one function that lists the matching sources for a principal and a scope ('direct:...', 'role:...', 'deny:...'). The allow decision, explain and could_call all use it."
  - "A wildcard grant 'crm:*' matches when the scope starts with 'crm:' (keep the colon). '*' alone matches everything."
  - "Expire requests in a catch-up helper called first in every public method, in order of expiry time, and write the audit line with the expiry time, not the current time."
  - "approve checks, in order: the request exists and is pending, the approver isn't the requester, the approver holds the role now. Only then re-check the requester's permission."
---

Marram Commerce is putting an agent in front of its support team. The agent calls tools: look up a customer, update a record, issue a refund. Petra Havel (fictional) has one condition from her security lead: "Permissions live in code we can test, not in the prompt. And when something goes wrong, I want to know who could do what, and when."

Every FDE who ships an agent with real tools builds some version of this. This drill is an original problem in the progressive format (**Reported**; see module C3).

## The rules

- Implement a class called `ToolGate`. Every method takes `timestamp` (an integer) as its first argument, and timestamps never decrease from one call to the next.
- Press **Submit** to run the checks for the levels you can see. Hidden checks combine features across levels.
- Hints and the tutor are off while the clock runs.

## Level 1: Tools and grants

A **scope** is a string like `"crm:read"`. A **principal** is any name: an agent, a person, a service.

- `add_tool(timestamp, name, scope)`: register a tool that needs `scope`. Return `True`, or `False` if a tool with that name exists (leave it unchanged).
- `grant(timestamp, principal, scope)`: give the principal a scope directly. Return `True`, or `False` if they already have exactly that grant.
- `revoke(timestamp, principal, scope)`: remove a direct grant. Return `True`, or `False` if they don't have exactly that grant string.
- A grant covers a tool's scope if it is equal to it, if it is `"*"`, or if it ends in `":*"` and the scope starts with everything before the `*` (so `"crm:*"` covers `"crm:write"` but not `"crmx:read"`).
- `call(timestamp, principal, tool)`: return `"unknown_tool"` if the tool doesn't exist, `"allowed"` if some grant covers its scope, and `"denied"` otherwise.

```python
g = ToolGate()
g.add_tool(1, "refund", "billing:write")
g.grant(2, "agent-7", "billing:*")
g.call(3, "agent-7", "refund")    # "allowed"
```

## Level 2: Roles and denies

- `define_role(timestamp, role, scopes)`: define a role as a list of scopes (wildcards allowed). Defining an existing role replaces its scopes, and the change applies to everyone who has the role. Return `True`.
- `assign(timestamp, principal, role)` and `unassign(timestamp, principal, role)`: return `True`, or `False` if the role isn't defined (assign), already assigned (assign) or not assigned (unassign).
- `deny(timestamp, principal, scope)`: an explicit deny. If any of the principal's denies covers a tool's scope (same matching rules), `call` returns `"denied"` whatever their grants. Return `True`.
- `explain(timestamp, principal, tool)`: every source that covers the tool's scope, sorted as strings: `"direct:<grant>"` for each matching direct grant, `"role:<role>"` once for each assigned role with a matching scope, `"deny:<scope>"` for each matching deny. Return `[]` if nothing matches and `None` for an unknown tool.

## Level 3: Approvals

Refunds need a second pair of eyes.

- `require_approval(timestamp, tool, approver_role, ttl)`: from now on, an allowed call to this tool doesn't run. Instead it creates a request and `call` returns `"pending:<id>"`, with ids `"req1"`, `"req2"`, ... counting across all tools. Return `True`, or `False` if the tool doesn't exist or `ttl` isn't a positive integer. A new setting applies to requests created after it.
- Permission is checked first: a call that would be denied still returns `"denied"`.
- `approve(timestamp, request_id, approver)` and `reject(timestamp, request_id, approver)`: the request must be pending, the approver must not be the requester, and the approver must hold `approver_role` at this moment. Otherwise return `False` and change nothing.
  - `reject` then sets the status to `"rejected"` and returns `True`.
  - `approve` re-checks the requester's permission now. If they still have it, the status becomes `"approved"` and it returns `True`. If not, the status becomes `"denied"` and it returns `False`.
- A pending request **expires** at its creation time plus its ttl. Any call at or after that moment sees it as `"expired"`.
- `status(timestamp, request_id)`: `"pending"`, `"approved"`, `"rejected"`, `"denied"` or `"expired"`, or `None` for an unknown id.

## Level 4: Audit and point-in-time access

The incident review starts with two questions: "what did this agent try to do?" and "was it allowed to, at the time?"

- `audit(timestamp, principal)`: the principal's audit lines, oldest first:
  - every `call`: `"<time> call <tool> -> <result>"`, where result is exactly what `call` returned;
  - every `approve` or `reject` attempt, in the approver's audit: `"<time> approve <id> -> <outcome>"` (or `reject`), where outcome is the request's new status, or `"refused"` if the attempt returned `False` without changing anything;
  - every expiry, in the requester's audit: `"<time> expire <id>"`, using the time it expired.
- `could_call(timestamp, principal, tool, at)`: `True` if the permissions in force at time `at` (tools, grants, roles and their definitions, assignments and denies) allowed the call, ignoring approvals. A change made at exactly `at` counts. If `at` is later than `timestamp`, answer with what is true now.
