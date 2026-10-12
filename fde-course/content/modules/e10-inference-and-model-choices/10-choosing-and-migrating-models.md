---
title: "Choosing Models and Migrating Safely: Opus 5.5, Sonnet 5.5, Haiku 5.5 and Fable 5.1"
type: reading
minutes: 18
---

> **By the end of this lesson** you'll be able to choose between the current Claude models for a workload with numbers, set effort deliberately, list the request shapes that return a 400 after moving to Opus 5.5, and run a migration that doesn't silently break caching, thinking or quality.

## How this comes up

Two customer conversations come up again and again. The first: "Which model should we use?" The second: "We moved to the new model and half our requests 400." In an interview, the first tests judgment and the second tests whether you've read the migration notes. Both have concrete answers. Every fact below comes from the Claude API skill's `models.md` and `model-migration.md`. Model details change, so re-check them before a customer meeting.

## The current lineup

Prices are in US dollars per million tokens.

| Model | ID | Input / output | Cache read | Effort default | Use it for |
|---|---|---|---|---|---|
| Claude Haiku 5.5 | `claude-haiku-5-5` | $0.10 / $0.50 for prompts up to 100K tokens; $0.50 / $2.50 above | 0.1x input | `medium` | High-volume, latency-sensitive work: classification, routing, extraction, sub-agents |
| Claude Sonnet 5.5 | `claude-sonnet-5-5` | $2 / $10 | $0.10 (0.05x) | `high` | Most production chat and agent work |
| Claude Opus 5.5 | `claude-opus-5-5` | $4 / $20 | $0.20 (0.05x) | `medium` | Long-running agentic coding and knowledge work. The default model for new code. |
| Claude Fable 5.1 | `claude-fable-5-1` | $10 / $50 | $0.25 (0.025x) | check the docs | The most demanding reasoning and long-horizon agentic work |

All four have a 1M-token context window and 128K max output. All of them think by default (adaptive thinking). Thinking tokens are billed as output, count toward `max_tokens`, and sit inside time to first token. Claude Haiku 4.5 ($1 / $5, 200K context, no `effort`) is the legacy cheap tier. Use Haiku 5.5 for new work.

A few facts that change designs:

- **Fable 5.1 requires data retention.** Organisations on zero data retention, or with retention under 30 days, get a 400 on every request. It has no Priority Tier, and it shares one rate-limit pool with Fable 5.
- **Haiku 5.5 bills on the larger rate card** once a prompt passes 100K tokens. A workload that grows into the 1M window changes price as well as size.
- **Haiku 5.5 has no server-side fallback** for refusals. Opus 5.5 and Fable 5.1 support opt-in `fallbacks` on the Claude API (not on Bedrock, Vertex or Foundry).
- **Each model has its own rate-limit pool.** Re-check your tier's limits before moving volume.

## Choosing: cost per completed task, not price per token

The list price is the wrong number. The migration notes say, for example, that Opus 5.5 at its default `medium` effort matched or beat Opus 5 at `high` on many coding and analysis tasks with fewer tokens. On most agentic coding evals, Sonnet 5.5 at `medium` scored higher than Sonnet 5 at `high`, at under a fifth of the cost. Fewer turns and fewer retries can beat a lower per-token price.

A method you can defend:

1. **Build the eval first.** Use 100 to 300 real cases with a grader you trust (E4, E8).
2. **Sweep model by effort.** For example, Haiku 5.5 at low and medium, Sonnet 5.5 at low, medium and high, and Opus 5.5 at medium. Set `output_config.effort` explicitly on every run. Defaults differ by model, so "the default" isn't one setting.
3. **Record quality, cost per completed task and p95 latency** for each cell, including thinking tokens in output.
4. **Pick the cheapest cell that meets the quality bar,** then check its tail on hard slices.
5. **Route if the workload is mixed.** Cheap model for easy cases, stronger model for hard ones (E5's router). Every route has its own prompt cache, though, so splitting traffic splits cache hits.

### Worked example: classify 2 million support emails a month

Each email is about 1,500 tokens of prompt (1,000 of which are a cached instruction prefix) plus 30 visible output tokens.

| Setup | Thinking assumption | Cost per email | Monthly |
|---|---|---|---|
| Haiku 5.5, `effort: "low"` | about 50 thinking tokens | 500 x $0.10 + 1,000 x $0.01 + 80 x $0.50, per million = $0.0001 | about $200 |
| Sonnet 5.5, `effort: "low"` | about 50 thinking tokens | 500 x $2 + 1,000 x $0.10 + 80 x $10, per million = $0.0019 | about $3,800 |
| Sonnet 5.5, effort not set (default `high`) | about 400 thinking tokens | 500 x $2 + 1,000 x $0.10 + 430 x $10, per million = $0.0054 | about $10,800 |

The thinking-token counts are assumptions for the arithmetic, and the occasional cache write is left out. Measure yours from `usage.output_tokens`. If Haiku 5.5 at `low` meets the quality bar, it costs about 2% of Sonnet 5.5 at its default. Leaving effort unset was the most expensive choice in the table.

## Effort, in practice

- Levels are `low`, `medium`, `high`, `xhigh` and `max`. Names don't mean the same amount of thinking across models.
- **To get less thinking, lower effort before you add "think less" prompts.** The migration notes say lowering effort reduces thinking, cost and latency more reliably than prompting does.
- Size `max_tokens` for thinking plus the answer. A limit sized for a model without thinking cuts replies off.
- Changing the top-level `effort` between requests invalidates the prompt cache. Per-message effort (a beta on some models) keeps it.
- Thinking text comes back empty by default (`display: "omitted"`). Set `display: "summarized"` if you need to read the reasoning. Never ask the model to write its reasoning into the answer. That can be declined with `stop_details.category: "reasoning_extraction"`.

## Migrating to Opus 5.5: what returns a 400

Moving a Claude Opus 5 integration to Opus 5.5 is mostly a model-ID change, plus these breaking changes.

| Request shape | What happens on Opus 5.5 | Replace with |
|---|---|---|
| `thinking: {type: "disabled"}` | 400 at every effort level | Omit `thinking`; lower `output_config.effort` (start at `low` if latency matters) |
| `thinking: {type: "enabled", budget_tokens: N}` | 400 | Same as above |
| `tool_choice: {type: "any"}` or `{type: "tool", name}` | 400, also on token counting and Batches | `auto` plus a prompt instruction, `strict: true` on the tool, and a check that the call happened; or structured outputs if you only wanted JSON |
| A final `assistant` message (prefill) | 400 (rejected since the Opus 4.6 family) | Structured outputs via `output_config.format`, or a system instruction |
| `temperature`, `top_p`, `top_k` | 400 (removed since Opus 4.7) | Remove them. Use prompting, and lower effort if you wanted consistency. |
| A `computer_20251124` tool on the Claude API or Google Cloud | 400 | `{type: "computer_toolset_20260801"}` with no name or display size, and an updated agent loop. Amazon Bedrock still accepts the old tool. |
| Editing or trimming earlier turns that carry thinking blocks | 400 by default for accounts created on or after 2026-08-31 ("preserved thinking") | Append-only history, plus server-side compaction or context editing |

Changes that fail no request but change behaviour:

- **The effort default drops** from `high` (Opus 5) to `medium`. Set it explicitly and re-run the sweep.
- **Text between tool calls comes back in thinking blocks.** Short progress notes the model wrote as text now arrive as `thinking` blocks, empty under the default display. A UI that renders only `text` goes quiet during long turns. The notes describe a `display: "updates"` option (beta) for this.
- **Broader safety classifiers.** `bio` joins `cyber` and `reasoning_extraction`. Handle `stop_reason: "refusal"` before reading content, and ship a fallback opt-in from day one.
- **Model binding.** On the Claude API, only Fable 5.1 and Mythos 5.1 can read Opus 5.5's thinking blocks. A router or fallback that moves a conversation to Opus 5 continues without the earlier reasoning. The request succeeds and the blocks are dropped.

### Preserved thinking, in one paragraph

On Opus 5.5, Sonnet 5.5, Haiku 5.5 and Fable 5.1, thinking blocks are tied to the conversation that produced them. The system prompt, the tools and every earlier message must be byte-identical to when the block was produced. Harnesses that build `messages` themselves often break this. They inject a reminder and later delete it, change the system prompt mid-session, add tools mid-session, or summarise old turns while replaying newer ones. Each fix is append-only: a mid-conversation `role: "system"` message instead of editing `system`, the full tool set declared at the start, and server-side compaction or context editing instead of rewriting history. Keeping the prefix identical also raises prompt-cache hit rates.

## A migration runbook

1. **Inventory** every call site: model, `thinking`, `tool_choice`, final assistant turns, sampling parameters, tool types, history edits. The next exercise automates the request-body part.
2. **Fix the 400s** in code, then run the suite against the new model at an explicit effort.
3. **Re-baseline** quality, cost per completed task and p95 latency on your eval. Compare like with like: the old model at its old effort against the new one at the chosen effort.
4. **Canary** a small share of traffic. Watch the 400 rate, the refusal rate, cache hit rate and stop reasons.
5. **Keep the old model ID ready** for rollback. Remember that a rollback mid-conversation drops the new model's thinking blocks.

> **Key takeaways**
> - Choose by cost per completed task at an explicit effort, measured on your eval. Defaults differ: Opus 5.5 and Haiku 5.5 run at `medium`, Sonnet 5.5 at `high`.
> - Thinking is billed as output and sits inside TTFT. Lower effort before you prompt for brevity.
> - On Opus 5.5, these return a 400: disabled thinking, thinking budgets, forced `tool_choice`, prefill, sampling parameters, and the old computer-use tool on the Claude API and Google Cloud.
> - Preserved thinking means append-only history. Edits to earlier turns 400 by default for new accounts.
> - Fable 5.1 needs data retention, has no Priority Tier and costs the most. Pick it only when the eval says you need it.
