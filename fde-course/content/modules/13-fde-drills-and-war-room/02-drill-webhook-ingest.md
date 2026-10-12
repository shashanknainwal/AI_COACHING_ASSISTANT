---
title: "Drill: Idempotent Webhook Ingest"
type: drill
minutes: 70
timeLimit: 70
levels:
  - "Ingest and dedupe"
  - "Out-of-order delivery"
  - "Gap timeouts and replay"
  - "Voids and point-in-time balance"
hints:
  - "Before Level 1, give every event a record (payload, status, arrival time) keyed by event id, and give every account its own record. Level 4 asks for balances at past times, so also keep an append-only list of (time, amount change) per account from the start."
  - "Compare the whole payload, (account, seq, kind, amount), to tell a duplicate from a conflict. Keep track of which event owns each (account, seq) so a second event for a taken seq is caught too."
  - "Level 3 is easiest with one catch-up helper called first in every public method. For each account with held events: find the oldest arrival time among them, add the timeout, and if that moment is not later than now, skip every seq below the lowest held seq and drain."
  - "Record a skip at the moment it became due (never earlier than when the timeout was set), not at the time of the call that noticed it. Write the balance changes from the drain at that same moment."
  - "A voided held event stays in the held set so it fills its seq when the drain reaches it, but the drain must not add its amount."
---

Marram Commerce's payment provider sends webhooks for every charge and refund. Petra Havel, Marram's VP Engineering (a fictional persona), describes the problem the way customers usually do: "We double-counted a refund last month, and twice we applied events in the wrong order. We need an inbox that is boringly correct."

Webhook providers retry, reorder and replay. Your inbox has to absorb all three. This is an original problem in the progressive format candidates describe for practical coding screens (**Reported**; see module C3). Before you press Start, spend five minutes on the data model: read lesson 01 if you haven't.

## The rules

- Implement a class called `WebhookInbox`. Every method takes `timestamp` (an integer) as its first argument, and timestamps never decrease from one call to the next.
- Press **Submit** to run the checks for the levels you can see. When every check for a level passes, the next level opens.
- The hidden checks test how features combine, not only each feature alone. Expect a Level 4 check that uses Level 2 and Level 3 behaviour at the same time.
- Hints and the tutor are off while the clock runs. If time runs out, note your level and keep going.

## Level 1: Ingest and dedupe

Each webhook carries an event id, an account, a per-account sequence number `seq`, a kind and an amount in cents. Until Level 2, events arrive in seq order and you can ignore `seq` except as part of the payload.

- `receive(timestamp, event_id, account, seq, kind, amount)`: return one of these strings:
  - `"rejected"` if `kind` isn't `"charge"` or `"refund"`, or `amount` isn't a positive integer. A rejected event is not recorded, so its id can be used again.
  - `"duplicate"` if this event id was received before with the same account, seq, kind and amount. Nothing changes.
  - `"conflict"` if this event id was received before with a different payload. Nothing changes.
  - `"accepted"` otherwise. The event is applied.
- `balance(timestamp, account)`: the sum of applied charges minus applied refunds. An unknown account has balance `0`.
- `event_count(timestamp, account)`: the number of applied events for the account.

```python
b = WebhookInbox()
b.receive(1, "e1", "acme", 1, "charge", 500)   # "accepted"
b.receive(2, "e1", "acme", 1, "charge", 500)   # "duplicate"
b.receive(3, "e1", "acme", 1, "charge", 900)   # "conflict"
b.balance(4, "acme")                           # 500
```

## Level 2: Out-of-order delivery

The provider doesn't guarantee order. Events must be applied in seq order per account, starting at seq 1.

- If an event's seq is the next one the account expects, apply it, then apply any held events that are now next in line, in seq order. Return `"accepted"`.
- If its seq is further ahead, hold it without applying it. Return `"held"`.
- If another event id already owns this account's seq (applied or held), return `"conflict"`. The duplicate and conflict checks from Level 1 come first, so redelivering a held event returns `"duplicate"`.
- `pending(timestamp, account)`: the held seqs for the account, sorted. `[]` for an unknown account.
- `applied_seq(timestamp, account)`: the highest seq such that every seq up to it has been applied. `0` if none. (Later levels add skipped and voided seqs; they count as dealt with too.)
- `balance` and `event_count` count applied events only.

## Level 3: Gap timeouts and replay

Some events never arrive. The account can't wait forever.

- `set_gap_timeout(timestamp, seconds)`: from now on, once the oldest event still held for an account has waited `seconds` (measured from when it arrived), every missing seq below the lowest held seq is **skipped**, and the held events that are now next in line are applied. Repeat while it applies. Return `True`, or `False` if `seconds` isn't a positive integer (keep the old setting). A new timeout replaces the old one.
- A skip happens at the moment it becomes due, which is that event's arrival time plus the timeout, or the time the timeout was set if that is later. Any call with a timestamp at or after that moment must see it.
- `missing(timestamp, account)`: the skipped seqs for the account that still haven't arrived, sorted.
- If an event arrives for a skipped seq, apply it immediately and return `"late"`. It leaves `missing`.
- `replay(timestamp, account, from_seq)`: the event ids of applied events with seq at or above `from_seq`, sorted by seq. Late events appear at their seq position. Held events are not included.

## Level 4: Voids and point-in-time balance

Finance asks: "what was this account's balance at 14:02, and why?"

- `void(timestamp, event_id)`: cancel an event. Return `True`, or `False` if the event is unknown or already voided.
  - Voiding an applied event reverses its amount from now on and removes it from `event_count` and `replay`.
  - Voiding a held event means it will never move money, and it leaves `pending`. Its seq still counts as filled, so later seqs can apply when the gap before it fills.
  - Redelivering a voided event returns `"duplicate"`. It stays voided.
- `balance_at(timestamp, account, at)`: the balance as of time `at`. A change made at exactly `at` counts.
  - An event counts from the moment it was **applied**, not when it arrived. A held event counts from when the drain applied it, a skip-triggered drain at its due time, a late event at its arrival.
  - A void counts from the time of the `void` call.
  - If `at` is later than `timestamp`, answer with what has happened up to `timestamp`.
