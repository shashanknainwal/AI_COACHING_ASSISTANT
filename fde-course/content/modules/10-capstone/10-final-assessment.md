---
title: Final Assessment
type: quiz
minutes: 20
questions:
  - q: A sponsor asks you to 'add AI' to their support process. What is your first step?
    options:
      - Pick a model and build a prototype this week
      - Send a pricing proposal
      - Ask IT for production access
      - 'Discover the actual workflow, the people involved and a measurable baseline before proposing a solution'
    answer: 3
    explain: FDEs start from the problem and the numbers. A baseline is what makes results provable later.
  - q: 'During discovery, Finance asks you to also rebuild invoice reconciliation, which doesn''t fit the 20-day budget. What''s the best response?'
    options:
      - 'Say clearly that it''s out of scope for this phase, explain why, and put it on the list for the next phase'
      - 'Agree, and work weekends'
      - Ignore the request
      - Do a rushed version of everything
    answer: 0
    explain: Clear scope protects the core deliverable; out-of-scope asks become the next phase.
  - q: NorthStar's export has three date formats and ten spellings of three carriers. What should you deliver along with the cleaned data?
    options:
      - Nothing; cleaning is invisible work
      - A request for a new export in the right format
      - 'A data-quality report (duplicates, bad dates, missing values, unknown values, orphan records) for the customer''s team'
      - A complaint to their IT team
    answer: 2
    explain: 'A data-quality report builds trust, shows what was fixed or excluded, and often leads to fixes at the source.'
  - q: Your SQL join between shipments and events returns more rows than shipments. What's the most likely cause?
    options:
      - 'A many-to-one join: each shipment has several events, so you need the latest event per shipment first'
      - The database is corrupted
      - SQL always duplicates rows
      - Too many columns
    answer: 0
    explain: 'Know the grain of each table before joining. Reduce events to one per shipment, then join.'
  - q: A partner API returns 429 errors during a nightly sync. What should your client do?
    options:
      - Retry immediately in a tight loop
      - Give up on the first error
      - Switch to a different API key
      - 'Retry with exponential backoff, honoring the retry-after header, up to a limit'
    answer: 3
    explain: Backoff with retry-after respects the provider's limits and recovers from transient errors.
  - q: 'After a tool_use turn, what must the next user message contain?'
    options:
      - 'A tool_result for every tool_use id in Claude''s turn, all in that one message'
      - Only the first tool's result
      - A summary of the tool results as plain text
      - Nothing; Claude remembers
    answer: 0
    explain: 'Append Claude''s full turn, then answer every tool_use id in the next user message.'
  - q: You need JSON with fixed fields from Claude Opus 5.5. What's the most reliable approach?
    options:
      - Ask nicely for JSON and hope
      - Prefill the assistant turn with an opening brace
      - 'Use structured outputs: output_config with a JSON schema'
      - Force a tool call with tool_choice
    answer: 2
    explain: Structured outputs guarantee the schema. Prefill and forced tool choice aren't supported on Opus 5.5.
  - q: Customer text is inserted into your prompt. Which practice best reduces prompt-injection risk?
    options:
      - Ask the customer not to inject
      - Use a longer system prompt
      - Lower max_tokens
      - 'Wrap and escape the text in tags, treat it as data, and keep risky actions behind code checks and approvals'
    answer: 3
    explain: 'Defense in depth: separate data from instructions, and limit what a manipulated model can do.'
  - q: A long system prompt is sent on every request but cache_read_input_tokens stays at 0. What do you check?
    options:
      - Whether the output is too long
      - Whether the API key is valid
      - 'Whether something in the prefix changes per request (like a timestamp), and whether the prefix meets the minimum cacheable length'
      - Whether the model supports text
    answer: 2
    explain: 'Caching is a prefix match with a minimum length; verify with usage, as the Module 9 incident showed.'
  - q: When should you build an agent rather than a workflow?
    options:
      - When the steps depend on what tools return and can't be drawn as a manageable flowchart
      - Always; agents are more advanced
      - When the task has exactly one step
      - When the budget is small
    answer: 0
    explain: Agents add cost and unpredictability; use them when the path really can't be fixed in advance.
  - q: NorthStar says messages must never promise refunds. Where should that rule be enforced?
    options:
      - Only in the system prompt
      - In the customer's email client
      - In the quarterly review
      - 'In the notify tool''s code (blocking such messages), plus the prompt, with every block audited'
    answer: 3
    explain: Mechanical rules belong in code the model can't bypass; the prompt helps it avoid triggering the guardrail.
  - q: An approval request to reroute a shipment times out. What should happen?
    options:
      - Reroute anyway
      - Retry the approval forever
      - 'Treat it as declined, tell Claude, open a ticket, and audit it'
      - Let Claude decide
    answer: 2
    explain: 'Fail closed: risky actions need an explicit yes.'
  - q: Your RAG system answers wrongly and the right chunk isn't in the top 3 results. What should you fix first?
    options:
      - The answer prompt
      - 'Retrieval: chunking, search method (keyword, embeddings, hybrid) or k'
      - The model
      - The output schema
    answer: 1
    explain: Measure retrieval (recall@k) separately; no prompt can use a chunk that was never retrieved.
  - q: 'An LLM judge agrees with humans 90% of the time, but it says ''pass'' to almost everything and 90% of answers are good. What does this suggest?'
    options:
      - The judge is excellent
      - The humans are wrong
      - 'Its Cohen''s kappa is near 0: it has little real skill; calibrate the rubric and include more failing cases'
      - Use a longer rubric and skip calibration
    answer: 2
    explain: Kappa corrects for chance agreement; raw accuracy can hide a useless judge.
  - q: 'The triage agent passes 11 of 13 eval cases, and one failure is a platinum customer marked P2. The gate requires 100% P1 recall. What do you tell the sponsor?'
    options:
      - Ship it; 85% is good
      - Hide the failure until after launch
      - 'Not ready yet: here''s the failure, the fix, and the date we''ll re-run the gate'
      - Lower the gate
    answer: 2
    explain: 'Gates agreed in advance protect critical slices. Honest, specific status builds trust.'
  - q: A new prompt scores 15/20 vs the current 14/20. What's the right conclusion?
    options:
      - 'The difference is within noise for 20 cases; look at case-by-case regressions and fixes, and use more cases'
      - It's 5 points better
      - The eval is broken
      - Ship both
    answer: 0
    explain: Use confidence intervals and paired comparisons before calling an improvement real.
  - q: Where should the production API key for the customer's deployment live?
    options:
      - 'In the repository, so deploys are easy'
      - In a shared document
      - In the system prompt
      - 'In the customer''s secrets manager, injected at runtime and scoped per environment'
    answer: 3
    explain: 'Never in code, docs or prompts. Rotate it, scope it, and revoke it first if it leaks.'
  - q: Errors spike right after a deploy. What do you do first?
    options:
      - 'Roll back, then investigate'
      - Investigate fully before touching anything
      - Write the post-mortem
      - Increase retries
    answer: 0
    explain: Mitigate first. Root cause comes after the customer impact stops.
  - q: 'Claude drafts your executive summary and it includes ''2,400 hours a year'', a number not in your data. What do you do?'
    options:
      - Keep it; it sounds right
      - 'Round it to 2,000'
      - 'Remove or correct it: every number in a readout must trace back to a source'
      - Add a disclaimer
    answer: 2
    explain: Fact-check every number. One wrong number in front of a CEO costs more trust than many right ones earn.
  - q: What should a final readout lead with?
    options:
      - A tour of the architecture
      - 'Every challenge you faced, in order'
      - A live demo
      - 'The recommendation and the decision needed, followed by results against the agreed targets'
    answer: 3
    explain: 'A readout is a decision meeting: answer first, then evidence, failures, risks and the ask.'
---

Twenty questions across the whole course: discovery and scoping, data and integrations, the Anthropic SDK, tools and agents, RAG, evals, production and the readout. You need **16 out of 20** to pass. You can retry as many times as you like.

Pass this assessment and complete every lesson to finish the course. Congratulations on making it here: you've done the work of a real Forward Deployed Engineer, from discovery notes to the executive readout.
