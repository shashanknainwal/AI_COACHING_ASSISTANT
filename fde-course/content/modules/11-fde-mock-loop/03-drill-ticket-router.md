---
title: "Round 2: A Ticket-Routing Service"
type: drill
minutes: 75
timeLimit: 75
levels:
  - "Ingest and route"
  - "SLAs and queue stats"
  - "Escalation over time"
  - "Audit history and replay"
hints:
  - "Level 4 asks where a ticket was at any past time. Keep a per-ticket list of (time, event text, queue, status) from Level 1 and append to it on every change. Then history, queue_at and open_at are all reads over that list."
  - "Escalations (Level 3) are easiest if every public method starts with the same helper that applies every move due at or before its timestamp."
  - "For one ticket, the next move time is max(entered + after, rule_created). Loop while that time is not later than the current timestamp, so chains like tier1 -> tier2 -> oncall happen in one call."
  - "Record an escalation at the time it happened, not at the timestamp of the call that noticed it, and set the ticket's 'entered' time to that same moment."
---

Round 2 of your mock loop. Theo Brandt hands you the problem the way a practical screen would: "A customer's support team routes tickets by hand from a shared inbox. They want a small service: route by rules, track SLAs, escalate tickets that sit too long, and answer the question every escalation review starts with, 'where was this ticket, and when?'"

This is an original problem in the progressive format candidates describe for practical coding screens (**Reported**; see module C3). One class, four levels, 75 minutes. No AI help, no tutor, no searching for solutions.

## The rules

- Implement a class called `TicketRouter`. Every method takes `timestamp` (an integer) as its first argument, and timestamps never decrease from one call to the next.
- Press **Submit** to run the checks for the levels you can see. When every check for a level passes, the next level opens.
- Write down the minute you clear each level. Lesson 06 uses those times for your score.
- If the clock runs out, note which level you were on and keep going. Finishing late is still practice, but it scores lower.

## Level 1: Ingest and route

Tickets arrive with an id and a subject. Rules send them to queues.

- `add_rule(timestamp, keyword, queue)`: add a routing rule. Return the rule's number: `1` for the first rule, then `2`, `3`, and so on.
- `ingest(timestamp, ticket_id, subject)`: create an open ticket and route it. Check the rules in the order they were added; the first rule whose keyword appears in the subject, ignoring case, wins. If no rule matches, the ticket goes to the queue `"triage"`. Return the queue name, or `None` if a ticket with that id already exists (leave it unchanged). Rules only affect tickets ingested after they were added.
- `get_ticket(timestamp, ticket_id)`: return `"queue:status"`, for example `"billing:open"` or `"billing:closed"`, or `None` if the ticket doesn't exist.
- `close(timestamp, ticket_id)`: close an open ticket. Return `True`, or `False` if the ticket doesn't exist or is already closed.
- `list_queue(timestamp, queue)`: return the ids of the open tickets in `queue`, sorted.

Example:

```python
r = TicketRouter()
r.add_rule(1, "invoice", "billing")       # 1
r.ingest(2, "T1", "Invoice is wrong")     # "billing"
r.ingest(3, "T2", "Printer on fire")      # "triage"
r.get_ticket(4, "T1")                     # "billing:open"
```

## Level 2: SLAs and queue stats

The customer's contract promises response times per queue.

- `set_sla(timestamp, queue, limit)`: from now on, tickets routed to `queue` at ingest get a due time of ingest time plus `limit`. Return `True`, or `False` if `limit` isn't a positive integer. A new limit replaces the old one for future tickets only.
- A ticket's due time is fixed when it is ingested. A ticket ingested into a queue with no SLA has no due time and never breaches.
- A ticket is **breached** if it is open and `timestamp` is later than its due time, or if it was closed at a time later than its due time. Closing exactly at the due time is on time.
- `queue_stats(timestamp, queue)`: return `{"open": n, "closed": n, "breached": n}` for the tickets currently in `queue`. Breached tickets are also counted as open or closed.
- `overdue(timestamp)`: return the ids of open, breached tickets across all queues, sorted by due time, then by id.

## Level 3: Escalation over time

Tickets that sit in a queue too long should move up.

- `add_escalation(timestamp, from_queue, after, to_queue)`: an open ticket that has been in `from_queue` for `after` time units moves to `to_queue`. Return `True`, or `False` (changing nothing) if `after` isn't a positive integer or `from_queue` equals `to_queue`. A new rule for the same `from_queue` replaces the old one.
- A ticket's time in a queue starts when it entered that queue (at ingest, or when it last moved). It moves at `entered + after`, but a rule never moves a ticket at a time before the rule was added: if that time has already passed, the ticket moves at the rule's own timestamp.
- Moves happen at their time. Any call with a timestamp at or after the move must see it, and a moved ticket can move again under the next queue's rule.
- Closed tickets never move. A ticket's due time doesn't change when it moves, and `queue_stats` counts tickets in their current queue.
- `remove_escalation(timestamp, from_queue)`: remove the rule. Return `True`, or `False` if there was none.
- `escalation_count(timestamp, ticket_id)`: return how many times the ticket has been escalated, or `None` if it doesn't exist.

## Level 4: Audit history and replay

The customer's support lead asks, after a bad week: "Which tickets were sitting in tier 1 on Tuesday at noon?"

- `reroute(timestamp, ticket_id, queue)`: a person moves an open ticket to `queue`. Its time in queue starts again at `timestamp`. Return `True`, or `False` if the ticket doesn't exist, is closed, or is already in `queue`.
- `history(timestamp, ticket_id)`: return the ticket's events in order, or `None` if it doesn't exist. Formats: `"5:ingested:tier1"`, `"15:escalated:tier1->tier2"`, `"30:rerouted:tier2->network"`, `"40:closed"`. An escalation is recorded at the time it happened, not when a later call noticed it.
- `queue_at(timestamp, ticket_id, at)`: return the queue the ticket was in at time `at`, or `None` if it didn't exist yet (or doesn't exist at all). A change at exactly `at` counts. A closed ticket stays in the queue it was closed in.
- `open_at(timestamp, queue, at)`: return the sorted ids of tickets that were open in `queue` at time `at`. A ticket closed at exactly `at` is not open.

## After the round

Record three things before you look at the solution: the level you reached, the minute you cleared each level, and the one decision that cost you the most time. Lesson 06 turns these into your round score.
