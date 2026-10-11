---
title: "Exercise: A Linter for the Opus 5.5 Migration"
type: exercise
minutes: 40
hints:
  - "Work through the rules in the order of the table and append findings as you go; the tests check the order. Use `body.get(...) or {}` so a missing `thinking` or `tool_choice` doesn't crash."
  - "Prefill: the last message has role `assistant`. The exception is a resumed `pause_turn`: its content is a list that contains a block of type `server_tool_use`. A string content is never the exception."
  - "Sampling: loop over `SAMPLING` (temperature, top_p, top_k) so the order is fixed. Computer tool: enumerate `tools` so you can build the path `tools.<i>.type`, and pick the severity from `platform`."
  - "`check_history`: first decide whether any earlier assistant message has a `thinking` or `redacted_thinking` block; if not, return None. Then compare `system`, then `tools`, then each earlier message by position (comparing `json.dumps(..., sort_keys=True)` is a simple way to compare deeply)."
  - "`report`: start from `{\"blocked\": 0}`, count each finding's rule, and add 1 to `blocked` for each body with at least one error."
---

Lumenfold is moving its agent and extraction routes from Claude Opus 5 to Opus 5.5. The model ID change is one line. Noor wants something better than "deploy and watch the 400s". She wants a linter that runs over a day of logged request bodies and says which will fail, where, and how to fix each one. Noor and Lumenfold are fictional.

The rules come from the migration notes summarised in lesson 10. You lint the request body that would be sent with `model: "claude-opus-5-5"`.

## Your task

**1. `lint(body, platform="anthropic")`** returns a list of findings `{"rule", "severity", "path", "fix"}` in this order (the `fix` text is yours):

| Rule | Severity | When | Path |
|---|---|---|---|
| `THINKING_DISABLED` | error | `thinking.type == "disabled"` | `thinking.type` |
| `THINKING_BUDGET` | error | `thinking.type == "enabled"` or `budget_tokens` is present | `thinking.budget_tokens` |
| `FORCED_TOOL_CHOICE` | error | `tool_choice.type` is `any` or `tool` | `tool_choice.type` |
| `PREFILL` | error | the last message is from `assistant`, unless its content list contains a `server_tool_use` block (re-sending a `pause_turn` response is how you resume) | `messages.<index>` |
| `SAMPLING_PARAM` | error | each of `temperature`, `top_p`, `top_k` present, in that order | the parameter name |
| `COMPUTER_TOOL` | error (warning on `"bedrock"`) | a tool of type `computer_20251124` | `tools.<i>.type` |
| `OUTPUT_FORMAT` | warning | top-level `output_format` (deprecated) | `output_format` |
| `EFFORT_UNSET` | warning | no `output_config.effort` (Opus 5.5 would run at `medium`) | `output_config.effort` |
| `MAX_TOKENS_LOW` | warning | `max_tokens` under `MIN_MAX_TOKENS` (4,000, a team rule: thinking counts toward it) | `max_tokens` |

`thinking: {type: "adaptive"}`, `tool_choice` `auto` or `none`, and the `computer_toolset_20260801` tool are all fine.

**2. `check_history(previous, current)`**: two consecutive requests in one conversation. If any assistant message in `previous` has a `thinking` or `redacted_thinking` block, the API checks that everything before it is unchanged. Return one `HISTORY_EDITED` error finding for the first difference you see, checked in this order:

1. `system` changed (path `system`)
2. `tools` changed (path `tools`)
3. an earlier message is changed or missing (path `messages.<i>`)

Return `None` if `current` only appends, or if there are no thinking blocks to invalidate.

**3. `will_400(body, platform)`**: `True` if there's any error finding.

**4. `report(bodies, platform)`**: `{"blocked": <bodies with an error>, "<RULE>": <count>, ...}`.

Press **Run** to lint three logged bodies, then **Submit**.

## Defend it

These are original practice questions in the style of a customer-facing technical round:

- "Half our requests 400 after the switch. Where do you start?" Group the 400s by error message, then run the linter on the bodies. Forced `tool_choice` and disabled thinking usually account for most of them. The error text names the field.
- "We used `tool_choice: tool` to guarantee JSON. What now?" If you only wanted JSON, use structured outputs (`output_config.format`). If you need the tool call, use `auto`, `strict: true`, an instruction in the prompt, and a check that a `tool_use` came back, with a retry if it didn't.
- "Our harness trims old turns to save tokens." On Opus 5.5 that 400s by default for accounts created on or after 2026-08-31, and it breaks the prompt cache for everyone. Use server-side compaction or context editing, and keep history append-only.
- "Why is the linter's effort rule only a warning?" The request succeeds. But Opus 5 defaulted to `high` and Opus 5.5 defaults to `medium`, so quality and cost change silently. Set it explicitly and re-run the eval.
