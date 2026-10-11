---
title: "Digital Natives and Model Migrations"
type: reading
minutes: 16
---

> **By the end of this lesson you will be able to:**
> - Adjust your approach for a digital-native customer: speed, API depth and cost per unit.
> - Diagnose the common 400s when a team moves to Claude Opus 5.5.
> - Run an eval-gated cutover with a canary and a fallback.
> - Explain preserved thinking and why history-trimming code breaks.

Most of this track assumes a large enterprise: committees, security reviews, months. Digital natives are different. A 70-person startup builds its product on the API, ships daily, and calls you when something breaks at 11 p.m. The architect's value here is depth on the API, fast diagnosis and a disciplined way to change models.

## How digital natives differ

| | Enterprise | Digital native |
|---|---|---|
| Buyer | CIO, committee | CTO or founding engineer |
| Speed | Months | Days |
| Questions | Security, governance, rollout | Latency, cost per unit, rate limits, model behaviour |
| What wins trust | A careful plan | A fixed bug and a better eval |
| Risk | Slow adoption | Shipping a model change straight to production |

Match their pace, but bring the one habit they often lack: an eval gate before a model change.

## What breaks when you move to Claude Opus 5.5

From the model-migration guide in the claude-api skill (checked 2026-10-10). Coming from an older model such as Claude Sonnet 4.5, these are the changes that return a 400 or change behaviour:

| Symptom | Cause | Fix |
|---|---|---|
| 400 on a request whose `messages` end with an assistant turn | Assistant prefill is rejected (since the 4.6 models) | Structured outputs (`output_config.format`) for JSON shape; a system-prompt instruction for style |
| 400 on `tool_choice: {"type": "tool"}` or `"any"` | Forced tool use is rejected on Opus 5.5 | `auto` plus a clear instruction and `strict: true` on the tool; check a call happened and retry if not. If the forced call only existed to get JSON, use structured outputs |
| 400 on `thinking: {"type": "disabled"}` or `budget_tokens` | Thinking can't be disabled on Opus 5.5 | Remove the field; use `output_config.effort` (`low` for fast routes) |
| 400 on `temperature` | Sampling parameters are rejected on the newest models | Remove them; use evals, not temperature, for consistency |
| 400 after a few turns of an agent | Preserved thinking: editing or trimming earlier turns breaks the binding | Append-only history; compaction or context editing instead of trimming |
| Answers cut off | `max_tokens` covers thinking too | Raise it (the guide suggests 64K as a start for long agentic turns) |
| Code reads `content[0].text` and crashes | A thinking block often comes first | Read blocks by `type` |
| Longer or shorter outputs, different cost | Default effort is `medium` on Opus 5.5 | Set `effort` explicitly and re-run the sweep |
| `stop_reason: "refusal"` on some inputs | Safety classifiers (cyber, bio, reasoning extraction) | Handle refusal before reading content; opt in to fallbacks |

### Preserved thinking, in plain terms

On Opus 5.5, thinking blocks are tied to the exact conversation they came from: the system prompt, the tools and every earlier message. If your code later edits or removes an earlier turn and replays a thinking block, the request fails. The guide says this is enforced by default for accounts created on or after August 31, 2026; older accounts can opt in. Common culprits: trimming old tool results to save tokens, rewriting the system prompt mid-session, adding tools mid-session, and home-made summarisation that keeps later turns with their thinking. The fix is append-only history plus the documented compaction or context-editing features. Claude Code, the Agent SDK and Managed Agents already keep the prefix intact.

Two related facts matter for fallbacks: if a router sends a turn to another model (say Opus 5 after a refusal), that model doesn't read Opus 5.5's thinking blocks, so it continues without that reasoning. The API drops what the target can't read; the request still succeeds.

## The eval-gated cutover

A model change is a deploy. Treat it like one.

1. **Freeze a golden set** from production: real inputs with known-good outputs, including the hard and failing cases. A few hundred is a start.
2. **Fix the 400s first** on a branch, against the old model where possible (most fixes, like structured outputs, work there too).
3. **Run old and new on the golden set.** Compare quality per task, cost per unit, latency (thinking sits inside time to first token) and refusal rate. Set `effort` explicitly and try at least two levels.
4. **Gate:** agree the bar before you look. For example, "no task drops more than one point; cost per receipt within 10%."
5. **Canary:** route 1%, then 10%, of live traffic to the new model behind a flag, with dashboards on errors, refusals and the eval's online proxy.
6. **Keep a fallback:** the old model ID stays configured, and the flag flips back in one step. Opus 5 remains available, per the guide.
7. **Promote,** then retire the old path after a quiet period.

The worst migration is the common one: change the model string in config on a Friday, ship, and find out from customers.

## What to say to a startup CTO

- "Roll back first, then fix. Your users shouldn't be the eval."
- "These are four known API changes, not model quality problems. Each has a documented fix."
- "Give me 200 real examples and we'll know by tomorrow whether Opus 5.5 is better for you, and at what effort."

> **Key takeaways**
> - Digital natives buy with depth and speed; bring the eval gate they often skip.
> - Prefill, forced tool_choice, disabled thinking and temperature all return 400 on Opus 5.5; each has a documented replacement.
> - Preserved thinking means append-only history; trimming earlier turns breaks requests.
> - Size `max_tokens` for thinking, read blocks by type, set effort explicitly, handle refusals.
> - Cut over behind a flag: golden set, agreed gate, canary, one-step fallback.
