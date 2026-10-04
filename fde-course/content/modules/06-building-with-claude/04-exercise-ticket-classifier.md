---
title: "Exercise: An Injection-Resistant Ticket Classifier"
type: exercise
minutes: 30
hints:
  - "`build_system_prompt`: build a list of lines and join with `\"\\n\"`. Each category line is `f\"- {name}: {description}\"`; each example is four lines: `<example>`, `<ticket>…</ticket>`, `<category>…</category>`, `</example>`."
  - "`escape_tags`: replace `&` first, then `<` and `>`: `text.replace(\"&\", \"&amp;\").replace(\"<\", \"&lt;\").replace(\">\", \"&gt;\")`."
  - "`wrap_ticket`: `f\"<ticket>\\n{escape_tags(text)}\\n</ticket>\"`."
  - "`CLASSIFY_SCHEMA`: `category` (string, enum of the category names), `needs_human` (boolean), `reason` (string), all required, `additionalProperties: False`."
  - "`classify`: return `{\"category\": \"other\", \"needs_human\": True, \"reason\": \"refused\"}` on a refusal; otherwise parse the JSON text block."
  - "`route`: check `fraud_report` first, then `needs_human`, then return `f\"auto:{category}\"`."
---

Harbor Bank receives about 4,000 support tickets a day. Today a team triages them by hand. You'll build the classifier: a production-quality prompt built from definitions and examples, injection defenses, structured output, and routing rules that keep risky tickets with humans.

## Your task

**1. `build_system_prompt(categories, examples)`** returns a prompt with exactly this structure (lines joined with `"\n"`):

```
You classify Harbor Bank customer-support tickets so they reach the right team.

<categories>
- card_dispute: The customer made a card purchase but disputes it (wrong amount, double charge, item not received).
- ...one line per category, "- name: description"...
</categories>

<examples>
<example>
<ticket>Why was I charged $35 for a wire transfer?</ticket>
<category>fees</category>
</example>
...one block per example...
</examples>

<rules>
...the RULES text, unchanged...
</rules>
```

Start with `INTRO`, then a blank line, then each section, with a blank line between sections.

**2. `escape_tags(text)`** replaces `&` with `&amp;`, `<` with `&lt;`, and `>` with `&gt;` (in that order).

**3. `wrap_ticket(text)`** returns `"<ticket>\n" + escape_tags(text) + "\n</ticket>"`.

**4. `CLASSIFY_SCHEMA`**: `{"category": <enum of category names>, "needs_human": <boolean>, "reason": <string>}`, all required, no extra properties.

**5. `classify(client, ticket)`** calls Claude with `model=MODEL`, `max_tokens` ≥ 1024, `system=build_system_prompt(CATEGORIES, EXAMPLES)`, one user message `wrap_ticket(ticket)`, `output_config` with `effort: "low"` **and** the JSON schema format. On a refusal, return `{"category": "other", "needs_human": True, "reason": "refused"}`; otherwise return the parsed dict.

**6. `route(result)`** returns the queue: `"fraud-team"` for any `fraud_report` (always, whatever `needs_human` says); otherwise `"human-review"` if `needs_human` is true; otherwise `"auto:<category>"`.

Press **Run** to classify five tickets, including an injection attempt, then **Submit**.
