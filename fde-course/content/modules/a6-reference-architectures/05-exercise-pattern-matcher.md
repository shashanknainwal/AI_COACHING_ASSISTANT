---
title: "Exercise: A Pattern Matcher for Customer Briefs"
type: exercise
minutes: 40
hints:
  - "`fit_scores`: loop over `PATTERNS`. Add `JOB_POINTS` when `brief.get(\"job\") == FIT[p][\"job\"]`, `USER_POINTS` when `brief.get(\"users\") in FIT[p][\"users\"]`, and `INPUT_POINTS * len(set(brief.get(\"inputs\", [])) & FIT[p][\"inputs\"])`."
  - "`recommend`: rank with `sorted(PATTERNS, key=lambda p: (-scores[p], PATTERNS.index(p)))`. Below `MIN_FIT` means `pattern=None`, `runner_up=None`, `confidence=\"no_fit\"`. Otherwise the runner-up is the second pattern if its score is above 0."
  - "`flags_for`: build a list of `{\"code\", \"severity\", \"reason\"}` dicts in any order, then `flags.sort(key=lambda f: (SEVERITY_ORDER[f[\"severity\"]], f[\"code\"]))`. Python's sort is stable, so two `irreversible_action` flags stay in brief order."
  - "Skip an action entirely when `action.get(\"human_approval\")` is true. Otherwise flag `irreversible_action` when `reversible` is False and `approval_limit` when `max_usd > AUTO_APPROVE_LIMIT_USD` (missing `max_usd` counts as 0)."
  - "The three mismatch flags and the three pattern-specific risks only apply when `pattern` is not None (and, for the specific risks, only for their own pattern). `no_golden_set`, `batch_unavailable` and `citations_with_schema` apply to every brief, even with no pattern."
---

Grace here. Sales hands me five or six new customer briefs a week, and the first thing I do with each is the same: which reference architecture is this, how sure am I, and what in the brief will hurt us if nobody says it out loud in the first call? I'd like a tool that does that first pass consistently, so the account team arrives at discovery with the right questions.

You'll write it. It's plain Python: a brief is a dictionary of structured requirements, and your code scores it against the four patterns from this module, picks one, and flags mismatches and risks with reasons a salesperson can read. The scoring tables and thresholds are given at the top of the file. Five real-looking (fictional) briefs are loaded as `BRIEFS` so you can see the output.

This is a triage aid, not an architect. Its job is to make sure the hard questions get asked, not to answer them.

## A brief

```python
{
    "customer": "Ostrava Re",
    "job": "extract_from_documents",        # what they want the system to do
    "users": "back_office",                   # who uses it
    "inputs": ["pdf", "scans", "email_attachments"],
    "daily_volume": 9000,
    "review_capacity_per_day": 900,           # documents people can review a day
    "latency": "overnight",                   # "interactive" | "minutes" | "overnight"
    "platform": "bedrock",                    # "anthropic_api" | "claude_platform_aws" | "bedrock" | "vertex" | "foundry"
    "write_actions": [{"name": "post_claim_fields", "reversible": True, "max_usd": 0}],
    "labelled_examples": 2000,
    "needs_structured_output": True,
}
```

Any field may be missing. Treat a missing list as empty, a missing number as 0 and a missing flag as False. Optional fields used below: `review_rate`, `per_user_permissions`, `acl_sync_in_scope`, `agent_can_push`, `branch_protection`, `needs_citations`, `needs_structured_output`, and `human_approval` on an action.

## Your task

**1. `fit_scores(brief)`** returns `{pattern: score}` for every pattern in `PATTERNS`. For each pattern in `FIT`: `JOB_POINTS` (5) if the job matches, `USER_POINTS` (2) if `users` is in the pattern's users, and `INPUT_POINTS` (1) for each input the brief shares with the pattern's inputs.

**2. `flags_for(brief, pattern)`** returns a list of `{"code", "severity", "reason"}` dicts, sorted by severity (`high`, `medium`, `low`, via `SEVERITY_ORDER`) and then by code. `pattern` may be `None`.

Mismatches, only when `pattern` is not None (assumptions in `ASSUMES`):

| Code | Severity | When | Reason must mention |
|---|---|---|---|
| `latency_mismatch` | medium | the brief's latency isn't in the pattern's allowed set | the brief's latency |
| `read_only_pattern` | high | the brief has write actions and the pattern doesn't allow them | every action name |
| `users_mismatch` | low | the brief's users aren't the pattern's users | |

Action risks, for every action without `human_approval: True`:

| Code | Severity | When | Reason must mention |
|---|---|---|---|
| `irreversible_action` | high | `reversible` is False (one flag per action) | the action name |
| `approval_limit` | high | `max_usd` is above `AUTO_APPROVE_LIMIT_USD` ($100) | the action name and amount |

Pattern-specific risks, only for their own pattern:

| Code | Pattern | Severity | When | Reason must mention |
|---|---|---|---|---|
| `review_queue_overflow` | document_processing | high | `round(daily_volume * review_rate)` exceeds `review_capacity_per_day`; `review_rate` defaults to `DEFAULT_REVIEW_RATE` (0.15) | both numbers, as plain integers |
| `permissions_sync` | knowledge_assistant | high | `per_user_permissions` and not `acl_sync_in_scope` | |
| `unguarded_repo_writes` | coding_assistant | high | `agent_can_push` and not `branch_protection` | |

General risks, for every brief:

| Code | Severity | When | Reason must mention |
|---|---|---|---|
| `no_golden_set` | medium | `labelled_examples` below `MIN_GOLDEN_SET` (100) | the count |
| `batch_unavailable` | medium | latency is `"overnight"` and the platform is in `NO_BATCH_PLATFORMS` | |
| `citations_with_schema` | low | `needs_citations` and `needs_structured_output` | |

The last two encode real API facts from this module: the Message Batches API is listed for the Claude API and Claude Platform on AWS but not for Bedrock, Vertex AI or Foundry, and citations can't be combined with structured outputs in one request.

**3. `recommend(brief)`** returns:

```python
{"customer": "Ostrava Re", "pattern": "document_processing", "runner_up": None,
 "confidence": "clear", "scores": {...}, "flags": [...], "go": False}
```

- Rank patterns by score, highest first; ties go to the pattern listed first in `PATTERNS`.
- If the best score is below `MIN_FIT` (5): `pattern` and `runner_up` are `None`, `confidence` is `"no_fit"`.
- Otherwise `pattern` is the best, `runner_up` is the second-ranked pattern if its score is above 0 (else `None`), and `confidence` is `"close"` when best minus second is at most `CLOSE_MARGIN` (2), else `"clear"`.
- `flags` is `flags_for(brief, pattern)`.
- `go` is True only when there is a pattern and no `high` flag.

Don't modify the briefs. Press **Run** to see Grace's five briefs, then **Submit**.

## Defend it

Original practice questions in the style of an architect case round:

- "Your matcher says 'close' between knowledge assistant and document processing. What do you ask the customer to break the tie?" Ask what happens to the answer: does a person read it, or does a system ingest it?
- "Why does an irreversible action block `go` while a missing golden set doesn't?" A missing golden set delays launch; an unguarded irreversible action causes harm after launch. Both need fixing, at different times.
- "A salesperson wants to delete the `batch_unavailable` flag because it 'scares the customer'. What do you say?" It can double the model bill. Better to raise it in week one than in the first invoice.
- "What can't a rule-based matcher see?" Politics, data quality, who owns the budget, whether the process should exist at all. That's what discovery is for.
