---
title: "Exercise: RFP Answer Checker"
type: exercise
minutes: 30
hints:
  - "Start `check_row` by working out `expected`: look the topic up in `facts`; if it's there, map its status with `EXPECTED`; if it isn't, the expected answer is `to_confirm`."
  - "Compare statuses in this order: invalid status; then, if they differ, expected `to_confirm` means an `unsourced` error; given `to_confirm` means an `underclaim` warning; otherwise compare ranks (not_supported 0, partial 1, comply 2): higher is `overclaim` (error), lower is `underclaim` (warning)."
  - "Lower-case the text once, then loop over `ROADMAP_PHRASES` in order and add one `roadmap:` error per phrase found. Do the same with `HEDGE_WORDS`, but only when the status is `comply`, and add warnings."
  - "Blank means empty after `.strip()`. `partial` and `not_supported` need text (`explain:` error); `to_confirm` needs an owner (`owner:` error)."
  - "`review` maps `check_row` over the rows in order, sums `len(r['errors'])` and `len(r['warnings'])`, and sets `ready` to `error_count == 0`."
---

Owen Hartwell again, from **Brackenridge Bank** (fictional). This time I'm on the other side of the table: we're issuing an RFP for our AI platform, and I've sat on enough evaluation panels to know what goes wrong in vendor answers. "Comply" with a paragraph of exceptions. Roadmap promises. SLAs nobody can find in the contract.

You're helping a vendor team answer an RFP like ours. They keep a fact sheet of documented answers, and I want a checker that compares their draft against it before anything goes out. It should block overclaims and roadmap language, and warn about underclaims and hedging.

The fact sheet loaded as `FACT_SHEET` is **illustrative**: a dated snapshot of what lessons 01, 05 and 09 say, not a source of truth. Your functions must work for any fact sheet in the same shape.

## The data

```python
FACT_SHEET = {
    "eu_only_inference": {"status": "partial", "note": "...", "source": "..."},
    "uptime_sla_with_credits": {"status": "unknown", "note": "contract term", "source": "legal"},
    ...
}
```

Fact statuses map to the expected answer: `yes` to `comply`, `partial` to `partial`, `no` to `not_supported`, `unknown` to `to_confirm` (the `EXPECTED` dict in the starter). `ROADMAP_PHRASES` and `HEDGE_WORDS` are loaded for you.

An answer row:

```python
{"id": "Q2", "topic": "eu_only_inference", "status": "comply",
 "text": "Generally yes, and an EU option is on the roadmap.", "owner": ""}
```

## Your task

**1. `check_row(row, facts)`** returns `{"id", "expected", "given", "errors", "warnings"}`. Every message starts with its code and a colon. Run the checks in this order:

| Code | Kind | When |
|---|---|---|
| `status` | error | The status isn't one of `comply`, `partial`, `not_supported`, `to_confirm` (skip the comparison checks) |
| `unsourced` | error | Expected is `to_confirm` (unknown fact, or topic not in the sheet) and the answer says anything else. Name the topic. |
| `underclaim` | warning | The answer is `to_confirm` but the fact is documented, or the answer claims less than the fact (rank: not_supported < partial < comply) |
| `overclaim` | error | The answer claims more than the fact |
| `roadmap` | error | Once per phrase from `ROADMAP_PHRASES` found in the text, case-insensitive, in list order |
| `explain` | error | Status is `partial` or `not_supported` and the text is blank |
| `owner` | error | Status is `to_confirm` and the owner is blank |
| `hedged` | warning | Status is `comply`; once per word from `HEDGE_WORDS` found in the text |

**2. `review(rows, facts)`** returns `{"rows": [...], "error_count": int, "warning_count": int, "ready": bool}`. Keep rows in order. `ready` is true only when there are no errors. Don't modify the inputs.

## Example

The draft in the starter has four rows. The checker should report:

- **Q1** (US-only inference, comply): clean.
- **Q2** (EU-only inference, comply, "generally... on the roadmap"): an overclaim and a roadmap error, plus a hedged warning. The documented answer is partial: EU options on Bedrock and Vertex AI, not on the Claude API or Foundry.
- **Q3** (uptime SLA with credits, comply, "99.5% uptime"): unsourced. That number is the Priority Tier target for existing commitments, not an SLA in the customer's contract.
- **Q4** (fine-tuning, partial, no text): unsourced, because it isn't on the fact sheet, and an explain error.

Not ready to send. That's the point: the checker catches the cells that would otherwise become contract disputes.

> **Architect tip:** A checker like this doesn't replace judgement. It makes the review meeting short: you only discuss the flagged rows, and every flag comes with the documented answer next to it.
