---
title: "War Room: A 30-Minute Incident Drill"
type: drill
minutes: 40
timeLimit: 30
levels:
  - "Stabilise"
  - "Root cause"
  - "Patch with a test"
  - "Status update"
hints:
  - "Spend the first three minutes reading, not coding: list the files with os.walk, then read CHANGELOG.md, relay/config.py and the last lines of relay.log before the deploy and after it."
  - "Stabilise means stop the damage with the smallest reversible change. The README says settings can be overridden without a code change. Which 2.4.0 setting stops the relay from honouring Retry-After?"
  - "Compare the key= values in relay.log before and after 09:12. Then count invoice_created lines per event in erp_audit.log with collections.Counter."
  - "Your regression check needs two cases: one event with two different attempt numbers (keys must match), and two events with the same customer but different ids (keys must differ)."
  - "Write the update for someone who wasn't in the room: when, what release, how many duplicates and dead letters, what you did, why it happened, what's next, when you'll post again."
---

You're on site at Marram Commerce when the client's finance team calls: their ERP is creating **duplicate invoices**, and orders are vanishing into a dead-letter queue. Petra Havel (fictional) pulls you into a room with a laptop and the incident channel open. "You have half an hour before I have to tell their CFO something. Find it, stop it, fix it, and write me the update."

This drill is timed at 30 minutes, with the tutor off. It's about debugging someone else's service under pressure, which no amount of spec-following practises. The service, the release and the client are fictional.

## The rules

- Your editor is a scratch file. The service is on disk at `/tmp/relay_incident/service/` (a package called `relay`, with `CHANGELOG.md` and `README.md`), and the raw logs are at `/tmp/relay_incident/logs/relay.log` and `/tmp/relay_incident/logs/erp_audit.log`. Read them from your code with `open()` and `os.walk`, and print what you need. The starter shows how.
- `relay` is importable (`import relay.worker`). `relay.worker.deliver_all(events, erp, settings)` replays a window of events against a faithful fake of the client's ERP (`relay.erp.FakeERP`), and `relay.sample_events.EVENTS` is the captured incident window. Use them to try ideas.
- Each level asks you to define something in your file. Don't edit the files on disk; the checks reload the service from disk.
- The incident channel will interrupt you. Petra's messages, as they arrive:
  - **Minute 0:** "Finance says some orders have two invoices. Also the dead-letter alert fired at 09:13."
  - **Minute 8:** "Can we just roll back? Deploy says that takes 40 minutes. Is there anything faster?"
  - **Minute 15:** "Finance needs the exact list of orders with duplicate invoices so they can void them."
  - **Minute 25:** "I'm walking into the CFO call in five minutes. Update, please."

## Level 1: Stabilise

Stop the damage first. Root cause can wait ten minutes; the client's ERP can't.

- Define `stabilise()` returning a dict of **settings overrides**: keys from `relay.config.SETTINGS` with new values.
- The checks replay the incident window with your overrides applied. No event may be dead-lettered, and the ERP should see at most a handful of `429` responses.
- Don't change any service file. A settings override is the change you can make in two minutes and undo in one.

## Level 2: Root cause

The override stopped the retry storm, but replays still create duplicate invoices. Find out why, and collect the facts finance and Petra need.

- Define `ROOT_CAUSE` as a dict with:
  - `"file"`: the path of the file inside the service that causes the duplicates, like `"relay/name.py"`;
  - `"function"`: the function in it;
  - `"introduced_in"`: the release that introduced it;
  - `"duplicated_events"`: the ids of every event in `erp_audit.log` that was invoiced more than once, sorted;
  - `"dead_lettered"`: the ids of every event `relay.log` reports as dead-lettered, sorted.
- Compute the two lists from the log files, not by hand.

## Level 3: Patch with a test

- Define `fixed_idempotency_key(event, attempt)`: the corrected key function. The checks swap it into the service and replay the window.
- Define `check_idempotency_key(key_fn)`: a regression check that raises `AssertionError` if `key_fn` is wrong and returns quietly if it's right. It must pass on your fix and fail on the 2.4.0 version and on other broken keys the checks try. (It's named `check_` rather than `test_` on purpose.)

## Level 4: Status update

- Define `STATUS_UPDATE`, a string of 40 to 180 words for Petra to read on the CFO call. The checks look for these facts, so put them in plainly:
  - when it started and which release;
  - the impact in numbers: how many duplicate invoices, how many dead-lettered events;
  - what you did to stabilise it;
  - the cause in one sentence, and that there's a fix with a regression test;
  - when the next update will come (`Next update HH:MM`).
- Don't say there was no impact, and don't call a known cause unknown.
- One thing the checks don't test but a reviewer would: some dead-lettered events were invoiced before the relay gave up on them. Replaying them blindly after the fix creates new duplicates. A strong update says you'll check before replaying.
