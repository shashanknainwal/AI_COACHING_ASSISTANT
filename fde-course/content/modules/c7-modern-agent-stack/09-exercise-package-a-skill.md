---
title: "Exercise: Package the Exception Playbook as a Skill"
type: exercise
minutes: 45
hints:
  - "Start with the script: it's plain Python. Map each code to a category, then apply the thresholds from `PLAYBOOK_NOTES`. 'Over EUR 10,000' and 'more than 48 hours' are strict comparisons."
  - "Progressive disclosure: the description is always loaded, the body loads when the skill triggers, and reference files load only when the body says to read them. So the body holds the steps and names each file by path; the thresholds and code tables go in `references/`."
  - "The description does the routing. Write what the skill covers and then 'Use when ...' followed by the words people actually use: stuck, held, damaged, missed, late, refused, next steps, playbook. Keep invoice and billing words out, or you'll steal the other skill's queries."
  - "`run_trigger_eval` builds the skill list from the SKILL.md it's given (`parse_skill_md`), adds `COMPETING_SKILLS`, and calls `route(query, skills)` for each case. `run_behaviour_eval` does `exec` on the script string in a fresh dict and calls `classify_exception`."
  - "If a trigger case fails, print `_tokens(query)` and `_tokens(description)` and compare. Fix the description; don't touch the router."
---

Rhea forwards a message from the operations lead: "Our exception playbook is a wiki page nobody reads at 2 a.m. When a container shows up damaged, people improvise." Rhea wants the playbook in a form every Claude-based tool at Cindervale can load on demand: the support agent, the dispatch bot and engineers' Claude Code sessions. "Package it once as a Skill. And I want proof it loads when it should and does the right thing when it does. Run an eval, like you would for a prompt."

A Skill is a folder with a `SKILL.md` file (YAML frontmatter with `name` and `description`, then Markdown instructions) plus optional `scripts/` and `references/` files. The playbook text (`PLAYBOOK_NOTES`), a competing skill (`COMPETING_SKILLS`), `parse_skill_md`, a toy router `route(query, skills)`, `TRIGGER_CASES`, `BEHAVIOUR_CASES`, `SKILL_NAME` and `BODY_MAX_LINES` are given.

## Your task

**1. `SKILL_FILES`** maps paths to file contents:

- `SKILL.md`: frontmatter with `name: shipment-exceptions` and a `description` (at most 1024 characters, no angle brackets, saying what the skill does and "Use when ..."). The body is 8 to 60 lines: the steps, a pointer to the script, and the path of each reference file with when to read it.
- At least two reference files under `references/` (8 or more lines each) that hold the detail: the code table and the escalation thresholds. The thresholds must not appear in the body.
- `scripts/classify_exception.py`: defines `classify_exception(event)` returning `{"category", "first_action", "escalate"}` per the playbook.

| Code | Category | First action | Escalate when |
|---|---|---|---|
| `CUS-HOLD` | `customs_hold` | `request_missing_documents` | `hold_days` over 3 |
| `DMG` | `damage` | `photograph_and_file_claim` | `value_eur` over 10,000 |
| `PU-MISS` | `missed_pickup` | `rebook_next_slot` | `customer_tier` is `"gold"` |
| `LATE` | `delay` | `notify_consignee` | `delay_hours` over 48 |
| `REF` | `refused_delivery` | `contact_shipper` | always |
| anything else | `unknown` | `route_to_duty_manager` | always |

**2. `run_trigger_eval(skill_files, cases)`** routes each query against your skill plus `COMPETING_SKILLS` and returns `{"passed", "total", "failures"}`, where each failure is `{"query", "expected", "got"}`. All nine cases must pass: five should load your skill, two belong to the invoices skill, and two should load nothing.

**3. `run_behaviour_eval(skill_files, cases)`** executes the packaged script and checks it against each case, returning `{"passed", "total", "failures"}`.

## Example

```text
name: shipment-exceptions | description length: 403 | body lines: 24
trigger eval: {'passed': 9, 'total': 9, 'failures': []}
behaviour eval: {'passed': 10, 'total': 10, 'failures': []}
```

## Why it's built this way

- **Description for routing, body for behaviour.** Only the name and description sit in context all the time. A description that says *when* to use the skill is what makes it load; the body is never read if it doesn't.
- **Scripts for anything deterministic.** The thresholds are rules, so a script applies them the same way every time, and the model runs it instead of re-deriving the rules from prose.
- **Test both halves.** A trigger eval (does it load on the right queries, and stay out of the way on the wrong ones) and a behaviour eval (does it do the right thing once loaded). The router here is a word-overlap toy; a real model judges meaning. The discipline carries over: a fixed set of should-trigger and should-not-trigger queries, run on every description change. The capstone kit runs this eval against the real model.
- **One package, many surfaces.** The same folder works in Claude Code (`.claude/skills/shipment-exceptions/`), on the Messages API through the Skills API with code execution, and on Managed Agents. Agent Skills on the Messages API aren't available on Amazon Bedrock or Google Vertex AI, so check the customer's platform before promising it.

In a debrief, expect: "Your skill never triggers in production. What do you check first?"
