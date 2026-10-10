---
title: "Module E1 Quiz"
type: quiz
minutes: 10
questions:
  - q: "Your extraction system prompt starts with today's date so the model can resolve 'last Friday'. Prompt caching never hits. What's the best fix?"
    options:
      - "Add a cache_control marker directly on the date line itself"
      - "Move the date into the user turn, after the stable system prompt"
      - "Switch to a model with a larger context window for the prompt"
      - "Shorten the system prompt so it falls below the caching minimum"
    answer: 1
    explain: "Caching is a prefix match over tools, then system, then messages. A value that changes every day at the top of the system prompt invalidates everything after it. Volatile values go last, and the request still needs a cache_control marker to opt in."
  - q: "A customer's prompt says 'Think step by step before answering' and 'Respond ONLY with valid JSON'. On Claude Opus 5.5, what should replace these two lines?"
    options:
      - "effort for thinking depth, and output_config.format for the JSON"
      - "An assistant prefill of '{' plus a lower temperature setting"
      - "Nothing; both instructions still work best when written as prose"
      - "A forced tool_choice whose tool input carries the JSON answer"
    answer: 0
    explain: "Thinking depth is controlled by effort (adaptive thinking is always on for Opus 5.5) and format by a schema. Prefill and forced tool_choice both return a 400 on Opus 5.5, and sampling parameters like temperature are rejected."
  - q: "Structured outputs return schema-valid JSON. Which problem do they NOT protect you from?"
    options:
      - "A required field that is missing from the returned object"
      - "A value that falls outside the enum you declared in the schema"
      - "A well-formed serial number that never appears in the email"
      - "Extra explanatory text printed before or after the JSON"
    answer: 2
    explain: "The API guarantees syntax and shape. Whether a value is grounded in the input is a check your code has to make, for example a substring check against the source text."
  - q: "What should your extractor check BEFORE it parses the JSON?"
    options:
      - "usage.cache_read_input_tokens, to confirm the prompt was cached"
      - "The request-id header, so the call can be traced in the logs"
      - "Whether content[0] is a text block rather than a tool call"
      - "stop_reason, for 'refusal' or 'max_tokens'"
    answer: 3
    explain: "A refusal may not match the schema (and can have empty content), and a max_tokens cut-off leaves incomplete JSON. Branch on stop_reason first. Don't rely on content[0]: current models often put a thinking block first."
  - q: "Your schema needs 'quantity between 1 and 50'. You call messages.create with output_config.format and a raw schema. Where is that rule enforced?"
    options:
      - "By the API, through the schema's minimum and maximum keywords"
      - "In your own validator code after the response comes back"
      - "By the model, because the system prompt states the range"
      - "Nowhere; ranges cannot be enforced on structured output"
    answer: 1
    explain: "Numeric limits like minimum and maximum aren't supported by structured outputs. The Python and TypeScript SDKs strip them and validate client-side in their parse helpers; with a raw create() call, your code checks the range."
  - q: "Which schema choice best reduces made-up values in a 'sku' field?"
    options:
      - "An enum of catalog SKUs plus an 'unknown' value"
      - "Free text, with a description saying 'only use real SKUs'"
      - "An enum of catalog SKUs only, so the model must pick a real one"
      - "Make sku optional so the model can leave it out when unsure"
    answer: 0
    explain: "An enum stops invented values, and the escape hatch gives the model an honest answer for ambiguous inputs. Without 'unknown', an ambiguous email is forced into a real SKU that looks exactly like a correct one."
  - q: "A product manager wants a long 'reasoning' field where the model writes out its full step-by-step thinking for every extraction. What's the best response?"
    options:
      - "Add it and place it first, so the model reasons before answering"
      - "Turn thinking off so the reasoning appears in the text instead"
      - "Offer a one-sentence rationale and evidence quotes instead"
      - "Add it at the end of the schema so it can't affect the fields"
    answer: 2
    explain: "Adaptive thinking already deliberates before the first output token, so field order doesn't need to force reasoning first. A short rationale plus checkable evidence quotes serves auditors. A field that pushes the model to reproduce its internal reasoning can be declined on Opus 5.5 and Sonnet 5.5 (reasoning_extraction), and thinking can't be disabled on Opus 5.5."
  - q: "Your extractor's answer fails grounding validation. What's the best retry policy?"
    options:
      - "Retry the identical request until it passes validation"
      - "Retry with a lenient regex that pulls JSON out of the text"
      - "Drop the case quietly and report it in the weekly metrics"
      - "Retry once with the exact errors, then send it to a human"
    answer: 3
    explain: "Showing Claude exactly what failed fixes most grounding mistakes in one turn. Blind or unlimited retries cost money and rarely help; after one retry, a human is cheaper."
  - q: "A prompt change raises 'all fields correct' from 50% to 70%, and due_date accuracy stays at 90%. What can still be hiding?"
    options:
      - "A fix and a regression in the same field cancelling out"
      - "Nothing: unchanged accuracy means unchanged behavior on every case"
      - "Only a latency change, since accuracy is already measured per field"
      - "A drop in the number of golden cases scored by the new version"
    answer: 0
    explain: "Averages net out. Only a case-by-case diff of (case, field) pairs shows that one invoice got fixed and another got a made-up due date."
  - q: "Which release rule fits an invoice extractor whose totals feed a payment run?"
    options:
      - "Ship whenever overall all-fields accuracy goes up by two points"
      - "Fields within tolerance and no critical-field regression on any case"
      - "Ship if at least half of the fields improve and none drop to zero"
      - "Ship if the new prompt is shorter and scores the same on average"
    answer: 1
    explain: "Field-level tolerance catches broad drops, and a zero-tolerance rule on critical fields catches the single case that would move money wrongly, even when the averages look fine. Before blocking on one case from a real model, rerun it to rule out run-to-run noise."
---

Ten questions on production prompting, structured outputs and prompt regression testing. You need 8 of 10 to pass.
