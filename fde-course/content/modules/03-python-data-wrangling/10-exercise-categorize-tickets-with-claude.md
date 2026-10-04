---
title: "Exercise: Categorize Support Tickets with Claude, Rules First"
type: exercise
minutes: 35
hints:
  - "`rule_category`: lowercase the text, then `for keyword, category in RULES.items(): if keyword in text: return category`. Return None if nothing matches."
  - "`chunks`: `[items[i:i + size] for i in range(0, len(items), size)]`."
  - "`build_prompt`: start with `PROMPT_HEADER`, then one line per item: `f\"{index}. {text}\"`, joined with newlines."
  - "In `categorize`, start with `labels = [rule_category(t) for t in tickets]`, then collect `pending = [(i, t) for i, t in enumerate(tickets) if labels[i] is None]`."
  - "For each batch: call the API with `output_config={\"format\": {\"type\": \"json_schema\", \"schema\": BATCH_SCHEMA}}`. If `stop_reason != \"end_turn\"`, set every index in the batch to \"other\" and move on."
  - "After parsing, only accept results whose index is in the batch and whose category is in `CATEGORIES`. Any batch index still None becomes \"other\"."
  - "`estimate_cost`: `calls = math.ceil(n / batch_size)`; input = `calls * overhead + n * tokens_per_ticket`; output = `n * output_per_ticket`; cost = `input * 4 / 1e6 + output * 20 / 1e6`, rounded to 4 decimals. Return 0.0 when n is 0."
---

Cobalt's support team has a backlog of uncategorized tickets, and they want every ticket labeled so they can see where problems cluster. You'll build the labeling job the way an experienced FDE would: free keyword rules for the obvious tickets, then Claude in batches for the rest, with careful validation and a cost estimate.

## Your task

**1. `rule_category(text)`** returns the category of the **first** keyword in `RULES` (in dictionary order) that appears in the lowercased text, or `None`.

**2. `chunks(items, size)`** splits a list into consecutive lists of at most `size` items.

**3. `build_prompt(batch)`** takes a list of `(index, text)` tuples and returns `PROMPT_HEADER` followed by one line per ticket, `"<index>. <text>"`, all joined with newlines.

**4. `BATCH_SCHEMA`**: a JSON Schema for

```python
{"results": [{"index": 3, "category": "product defect"}, ...]}
```

`index` is an `"integer"`, `category` uses `"enum": CATEGORIES`, every object has `"additionalProperties": False`, and all properties are required.

**5. `categorize(client, tickets, batch_size=10)`** returns a list of categories, one per ticket, in the same order:
1. Apply `rule_category` to every ticket.
2. Send only the unlabeled tickets to Claude, as `(index, text)` tuples, in batches of `batch_size`. Each request uses `model=MODEL`, `max_tokens` of at least 2048, `system=SYSTEM_PROMPT`, one user message with `build_prompt(batch)`, and structured outputs with `BATCH_SCHEMA`.
3. If a response's `stop_reason` isn't `"end_turn"`, label every ticket in that batch `"other"`.
4. Otherwise, accept results only if the index belongs to the batch and the category is in `CATEGORIES`. Batch tickets with no valid result become `"other"`.
5. Don't call Claude at all if the rules labeled everything.

**6. `estimate_cost(n, batch_size, tokens_per_ticket=60, overhead=400, output_per_ticket=15)`** returns the estimated cost in dollars for `n` tickets on Claude Opus 5.5, rounded to 4 decimals, using the formula from the lesson.

Press **Run** to label Cobalt's tickets, then **Submit**. The tests check your results *and* how many API calls you made.
