---
title: "Module A3 Quiz"
type: quiz
minutes: 12
questions:
  - q: "A distributor's product catalogue changes daily and users need answers with a link to the source. Which approach fits first?"
    options:
      - "Fine-tune a model on the full catalogue every week so it learns the new products"
      - "Retrieval over the catalogue with citations"
      - "An autonomous agent that browses the public catalogue website for each question"
      - "A longer system prompt that lists every product and is regenerated each morning"
    answer: 1
    explain: "Knowledge that changes often and needs citations points to retrieval. Fine-tuning freezes facts at training time and can't cite; a static prompt goes stale."
  - q: "Which is the strongest reason NOT to fine-tune to add company knowledge?"
    options:
      - "Fine-tuned models can't produce valid JSON output, so integrations would break"
      - "Fine-tuning is always more expensive per token than prompting a base model"
      - "Facts go stale, can't be cited, and ignore per-user permissions"
      - "Fine-tuning only works on small models, which are too weak for enterprise work"
    answer: 2
    explain: "Facts baked into weights go stale, can't point to a source, and are visible to every user. Retrieval addresses all three."
  - q: "A bank wants to flag wires over $10,000 to accounts opened in the last 30 days. What do you recommend?"
    options:
      - "A rule or query, with an LLM only for messy free-text memos"
      - "An agent that reviews every wire transfer and decides which ones to escalate"
      - "Fine-tuning a model on several years of past suspicious wire transfers"
      - "Retrieval over the bank's AML policy so the model can apply it to each wire"
    answer: 0
    explain: "The condition is structured and exact. Rules are cheaper, deterministic and auditable. Saying 'this part doesn't need an LLM' builds trust."
  - q: "When does an agent beat a fixed workflow?"
    options:
      - "Whenever the task needs more than one tool, such as search plus a database lookup"
      - "When the customer's executive sponsor asks for an agent by name in the brief"
      - "When latency must be as low as possible for an interactive user experience"
      - "When the steps depend on what the model finds along the way"
    answer: 3
    explain: "If you can write the steps down in advance, a workflow is cheaper, faster and easier to test. Agents earn their cost when the path isn't known up front."
  - q: "A 5,000-person company wants AI help for drafting, research and questions over shared documents for all staff. What's usually the right first move?"
    options:
      - "Build a custom internal chat app on the API, owned by the platform team"
      - "Buy seats on a team or enterprise plan with connectors to their tools"
      - "Fine-tune a model on the intranet so it knows the company's documents"
      - "Wait for a vendor to release an industry-specific product for their sector"
    answer: 1
    explain: "General employee productivity is what Claude's apps are for. Building and maintaining a custom chat app rarely adds value here; save builds for specific, high-volume workflows."
  - q: "In a 12-month cost model, the build option is cheapest but buying goes live three months earlier. Over 6 months, buying is cheaper. What belongs in your recommendation?"
    options:
      - "Only the 12-month result, because the longer horizon is the more complete picture"
      - "Only the 6-month result, because executives care most about short-term spend"
      - "Both, each with its horizon, plus the assumptions that flip the ranking"
      - "Neither; total cost of ownership shouldn't drive a build-or-buy decision at all"
    answer: 2
    explain: "The horizon is part of the answer. State it, show where the curves cross, and name the assumptions (review rate, go-live date) that move the result."
  - q: "A support assistant costs about $0.04 per ticket in model fees and saves about $3.27 per ticket in agent time. Which assumption should the pilot measure most carefully?"
    options:
      - "The share of tickets resolved and the time saved per draft"
      - "The per-token price of the model, since it drives the monthly bill"
      - "The cache write multiplier for the 5-minute and 1-hour lifetimes"
      - "The average number of output tokens the model returns on each call"
    answer: 0
    explain: "The sensitivity table shows token prices barely move the net saving; resolution rate and time saved move it by double digits."
  - q: "According to Anthropic's cost-optimization guidance, which order should levers be applied in?"
    options:
      - "Switch to a cheaper model first, then add prompt caching to recover quality"
      - "Lower the effort setting first, then batch, then add caching at the end"
      - "Route every task to the smallest model, then fix any quality problems found"
      - "Free wins first (caching, hygiene, batch), then effort, then model choice"
    answer: 3
    explain: "Free wins cut cost without touching quality. Effort and model choice trade capability for cost, so they come last and are checked against an eval."
  - q: "A customer on Google Vertex AI plans to halve its nightly extraction bill with Anthropic's Message Batches API. What do you check first?"
    options:
      - "Whether the nightly job streams its responses, since batches can't stream"
      - "Whether Batches is offered there; Anthropic lists it only for its own platforms"
      - "Whether every prompt in the job is under 1,000 tokens, the batch size limit"
      - "Nothing needs checking, because batch pricing is identical on every platform"
    answer: 1
    explain: "Anthropic lists Message Batches for the Claude API and Claude Platform on AWS, not Vertex AI. Check before promising a saving, and confirm the cloud's own batch offering with its current docs."
  - q: "Your Sonnet 5.5 cost estimate assumes 400 output tokens per call, and nobody has set effort. What's the risk?"
    options:
      - "None: thinking is free on Sonnet 5.5 and isn't counted in output tokens"
      - "Thinking tokens are billed as input, so the cached prefix gets more expensive"
      - "Sonnet 5.5 defaults to high effort; thinking bills as output, so it can run high"
      - "Sonnet 5.5 can't think at all, so the estimate is exactly right as written"
    answer: 2
    explain: "All three current models think by default. Sonnet 5.5 defaults to high effort, Opus 5.5 and Haiku 5.5 to medium. Thinking is billed as output and adds to time to first token, so set effort explicitly or add a thinking line."
---

Ten questions on choosing an approach, build versus buy, and cost at scale. You need 8 correct to pass.
