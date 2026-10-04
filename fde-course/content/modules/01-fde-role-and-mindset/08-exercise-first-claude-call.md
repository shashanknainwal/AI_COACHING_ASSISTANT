---
title: "Exercise: An Executive Summary Bot with the Anthropic SDK"
type: exercise
minutes: 25
hints:
  - "Call `client.messages.create(model=MODEL, max_tokens=1024, system=SYSTEM_PROMPT, messages=[...])`. The messages list needs one dict: `{\"role\": \"user\", \"content\": ...}`."
  - "Put the notes inside the user message, for example: `f\"Summarize these kickoff notes for the executive sponsor:\\n\\n{notes}\"`."
  - "Check `response.stop_reason` before reading the content. If it equals `\"refusal\"`, return `None`."
  - "Don't use `response.content[0].text`: the first block is a thinking block. Join the `.text` of every block whose `.type == \"text\"`, then `.strip()` the result."
  - "Cost: `usage.input_tokens / 1_000_000 * input_price + usage.output_tokens / 1_000_000 * output_price`, then `round(..., 6)`."
---

After the Brightline kickoff, the sponsor (Dana, VP Operations) asks for a short summary she can forward to her CEO. You'll write it many times over the next months, so you decide to automate a first draft with Claude.

## Your task

The editor already creates the client and defines `MODEL`. Complete three things.

**1. `SYSTEM_PROMPT`**: a system prompt string that tells Claude its role. It must mention that the audience is an **executive** (the word "executive" must appear) and ask for a short summary. Write it the way you'd brief a sharp human assistant.

**2. `summarize_for_exec(client, notes)`**:

- Call `client.messages.create` with:
  - `model=MODEL`
  - `max_tokens` of **at least 1024**
  - `system=SYSTEM_PROMPT`
  - `messages` containing **one user message** whose content includes the full `notes` text
- If `stop_reason` is `"refusal"`, return `None`.
- Otherwise return the **text** of the response: join every block whose `type` is `"text"`, then strip surrounding whitespace.

**3. `estimate_cost(usage, input_price=4.0, output_price=20.0)`**: given a response's `usage` object, return the cost of the call in US dollars, rounded to 6 decimal places. Prices are **per million tokens** (defaults are Claude Opus 5.5 pricing).

## Things the tests check

- You passed the right parameters (model, `max_tokens`, system prompt, a single user message containing the notes).
- You don't assume the first content block is text. The simulated response, like a real Opus 5.5 response, starts with a **thinking block**.
- You handle a refusal without crashing.
- Your cost math is right.

Press **Run** to see your summary and its cost, then **Submit**.

> **FDE tip:** Treat LLM output as a *draft for a human*, especially anything going to an executive. A good pattern is "Claude drafts, FDE edits, FDE sends." You'll learn to measure and improve draft quality with evals in Module 8.
