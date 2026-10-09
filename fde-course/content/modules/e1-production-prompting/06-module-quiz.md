---
title: "Module E1 Quiz"
type: quiz
minutes: 10
questions:
  - q: "Your extraction system prompt starts with today's date so the model can resolve 'last Friday'. Prompt caching never hits. What's the best fix?"
    options:
      - "Add a cache_control marker to the date line"
      - "Move the date into the user turn, after the stable system prompt"
      - "Switch to a model with a larger context window"
      - "Shorten the system prompt below the caching minimum"
    answer: 1
    explain: "Caching is a prefix match over tools, then system, then messages. A value that changes every day at the top of the system prompt invalidates everything after it. Volatile values go last."
  - q: "A customer's prompt says 'Think step by step before answering' and 'Respond ONLY with valid JSON'. On Claude Opus 5.5, what should replace these two lines?"
    options:
      - "Nothing; both still work best as prose"
      - "An assistant prefill of '{' and a higher temperature"
      - "The effort setting for thinking depth, and output_config.format for the JSON"
      - "A forced tool_choice that returns the JSON as tool input"
    answer: 2
    explain: "Thinking depth is controlled by effort (adaptive thinking is always on for Opus 5.5) and format by a schema. Prefill and forced tool_choice both return a 400 on Opus 5.5, and sampling parameters like temperature are rejected."
  - q: "Structured outputs return schema-valid JSON. Which problem do they NOT protect you from?"
    options:
      - "A well-formed serial number that doesn't appear anywhere in the email"
      - "A missing required field"
      - "A value outside the enum"
      - "Extra text before the JSON"
    answer: 0
    explain: "The API guarantees syntax and shape. Whether a value is grounded in the input is a check your code has to make, for example a substring check against the source text."
  - q: "Which response should your extractor check for BEFORE it parses the JSON?"
    options:
      - "usage.cache_read_input_tokens"
      - "stop_reason being 'refusal' or 'max_tokens'"
      - "The response's request-id header"
      - "Whether content[0] is a text block"
    answer: 1
    explain: "A refusal may not match the schema (and can have empty content), and a max_tokens cut-off leaves incomplete JSON. Branch on stop_reason first. Don't rely on content[0]: current models often put a thinking block first."
  - q: "Your schema needs 'quantity between 1 and 50'. You call messages.create with output_config.format and a raw schema. Where is that rule enforced?"
    options:
      - "By the API, through minimum and maximum"
      - "By the model, because the prompt mentions it"
      - "Nowhere, so it can't be enforced"
      - "In your validator (or by the SDK's client-side checks when you use messages.parse)"
    answer: 3
    explain: "Numeric limits like minimum and maximum aren't supported by structured outputs. The Python and TypeScript SDKs strip them and validate client-side in their helpers; with a raw create() call, your code checks the range."
  - q: "Which schema choice best reduces made-up values in a 'sku' field?"
    options:
      - "Free text with a description saying 'only use real SKUs'"
      - "An enum of the catalog SKUs plus an 'unknown' value"
      - "An enum of the catalog SKUs only, so the model must pick a real one"
      - "Making sku optional so the model can leave it out"
    answer: 1
    explain: "An enum stops invented values, and the escape hatch gives the model an honest answer for ambiguous inputs. Without 'unknown', an ambiguous email is forced into a real SKU that looks exactly like a correct one."
  - q: "A product manager wants a 'reasoning' field where the model writes out its full step-by-step thinking for every extraction. What's the best response?"
    options:
      - "Add it; more output always helps auditing"
      - "Add it, but put it last in the schema"
      - "Use evidence quotes per key field for auditors and log summarized thinking blocks separately, because asking the model to reproduce its reasoning in the output can be declined on current models"
      - "Turn thinking off so the reasoning appears in the text instead"
    answer: 2
    explain: "On Claude Opus 5.5 and Sonnet 5.5, prompts that push the model to reproduce its internal reasoning in the response can be refused with category reasoning_extraction. Evidence quotes are checkable; summarized thinking blocks show how the model thought. Thinking can't be disabled on Opus 5.5."
  - q: "Your extractor's answer fails grounding validation. What's the best retry policy?"
    options:
      - "Retry once, appending the assistant turn and a user turn listing the exact errors; then send it to human review"
      - "Retry the identical request until it passes"
      - "Retry with a regex that extracts the JSON more leniently"
      - "Drop the case silently and move on"
    answer: 0
    explain: "Showing Claude exactly what failed fixes most grounding mistakes in one turn. Blind or unlimited retries cost money and rarely help; after one retry, a human is cheaper."
  - q: "A prompt change raises 'all fields correct' from 50% to 70%, and due_date accuracy stays at 90%. What can still be hiding?"
    options:
      - "Nothing: unchanged accuracy means unchanged behavior"
      - "Only a change in latency"
      - "A drop in the number of cases"
      - "A fix on one case and a regression on another in the same field, cancelling out"
    answer: 3
    explain: "Averages net out. Only a case-by-case diff of (case, field) pairs shows that one invoice got fixed and another got a made-up due date."
  - q: "Which release rule fits an invoice extractor whose totals feed a payment run?"
    options:
      - "Ship if overall accuracy goes up"
      - "Ship if every field's accuracy stays within tolerance AND no critical field (total, currency) regresses on any case"
      - "Ship if at least half the fields improve"
      - "Ship if the new prompt is shorter"
    answer: 1
    explain: "Field-level tolerance catches broad drops, and a zero-tolerance rule on critical fields catches the single case that would move money wrongly, even when the averages look fine."
---

Ten questions on production prompting, structured outputs and prompt regression testing. You need 8 of 10 to pass.
