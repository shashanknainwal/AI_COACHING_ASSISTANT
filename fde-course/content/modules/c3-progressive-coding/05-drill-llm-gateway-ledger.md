---
title: "Drill: An LLM Gateway Ledger"
type: drill
minutes: 60
timeLimit: 60
levels:
  - "Keys and quotas"
  - "Owner rankings"
  - "Rate limits"
  - "Revocation and history"
hints:
  - "Before Level 1, give each key a record that can grow: owner, quota, tokens used, and a list of accepted uses as (time, tokens). Levels 3 and 4 both read that list."
  - "Write record_usage's return cases as a comment first: missing key, rate limited, over quota, accepted. Return early for each rejection, before you change anything."
  - "Rankings and listings all use the same \"name(value)\" shape. One small formatting helper and a tuple sort key like (-total, owner) cover Level 2."
  - "Revoking should flip a flag on the record, not delete it. Level 4's usage_between still needs the key's history after it is revoked."
---

This drill is an original problem in the same format as the progressive coding screens candidates describe (Reported): one class, four levels, a clock. It is shorter than a real screen, so the 60-minute target is tight on purpose. Model the data with Level 4 in mind, even though you can't see it yet.

You are building the ledger behind an internal LLM gateway. Teams get API keys with token quotas. The gateway records usage, ranks teams by spend, enforces rate limits, and answers questions about past usage after a key is revoked.

## The rules

- Implement a class called `Gateway` in the editor. Every method takes `timestamp` (an integer) as its first argument, and timestamps only ever increase from one call to the next.
- Press **Submit** to run the checks for the levels you can see. When every check for a level passes, the next level opens below.
- The clock is a target, not a wall. If time runs out, keep going: finishing late is still practice.
- Hints and the AI tutor are off while the clock runs, the same as a real assessment.

## Level 1: Keys and quotas

A key belongs to an owner (a team name) and has a token quota for its lifetime.

- `create_key(timestamp, key_id, owner, quota)`: create a key with `quota` tokens available and none used. Return `True`, or `False` if a key with that id already exists (leave it unchanged).
- `record_usage(timestamp, key_id, tokens)`: record that the key used `tokens` tokens (a positive integer) at `timestamp`. Return the quota remaining after this use, as an integer.
  - Return `None` if the key doesn't exist.
  - Return `-1` if the use would take the total used **above** the quota. A rejected use is not recorded and changes nothing. Using exactly the remaining amount is allowed and leaves `0`.
- `get_remaining(timestamp, key_id)`: return the quota minus the tokens used, or `None` if the key doesn't exist.

## Level 2: Owner rankings

Finance wants to see which teams spend the most.

- `top_owners(timestamp, n)`: return up to `n` owners ranked by total tokens used across all of their keys, highest first, ties broken by owner name. Format each as `"owner(tokens_used)"`. Every owner with at least one key appears, even with `0` used. If `n` is larger than the number of owners, return them all; if `n` is `0` or less, return `[]`.
- `keys_for(timestamp, owner)`: return that owner's keys sorted by key id, each formatted as `"key_id(remaining)"`. Return `[]` if the owner has no keys.
- Rejected uses never count toward totals.

## Level 3: Rate limits

One runaway script can drain a team's quota in seconds. Add per-key rate limits.

- `set_rate_limit(timestamp, key_id, max_requests, window)`: from now on, the key accepts at most `max_requests` uses in any window of length `window`. A later call replaces the earlier limit. Return `True`, or `False` if the key doesn't exist.
- `record_usage` now returns `-2` when the key already has `max_requests` recorded uses with time `t` in `(timestamp - window, timestamp]`. The lower bound is exclusive: a use at exactly `timestamp - window` no longer counts.
- Check the rate limit **before** the quota. A use rejected for either reason is not recorded, and rejected uses never count toward the rate limit.
- Uses recorded before the limit was set count toward it.

## Level 4: Revocation and history

A key leaked in a public repo. Security revokes it, then asks how much it was used last week.

- `revoke_key(timestamp, key_id)`: revoke the key. Return `True`, or `False` if the key doesn't exist or is already revoked.
- After a key is revoked:
  - `record_usage` and `get_remaining` return `None`, and `set_rate_limit` returns `False`, as if the key didn't exist;
  - it disappears from `top_owners` and `keys_for`, and its usage no longer counts toward its owner's total. An owner with no active keys drops out of `top_owners`;
  - its id can't be used again: `create_key` with that id returns `False`.
- `usage_between(timestamp, key_id, start, end)`: return the total tokens of accepted uses with `start <= t < end`. Return `0` if there are none. This works for revoked keys too. Return `None` only if the key never existed.
