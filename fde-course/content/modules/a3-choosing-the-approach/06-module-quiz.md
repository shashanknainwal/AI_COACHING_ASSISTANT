---
title: "Module A3 Quiz"
type: quiz
minutes: 12
questions:
  - q: "A distributor's product catalogue changes daily and users need answers with a link to the source. Which approach fits first?"
    options:
      - "Fine-tune a model on the catalogue every week"
      - "Retrieval over the catalogue with citations"
      - "An autonomous agent that browses the catalogue website"
      - "A longer system prompt that lists every product"
    answer: 1
    explain: "Knowledge that changes often and needs citations points to retrieval. Fine-tuning freezes facts at training time and can't cite; a static prompt goes stale."
  - q: "Which is the strongest reason NOT to fine-tune to add company knowledge?"
    options:
      - "Fine-tuned models can't produce JSON"
      - "Fine-tuning is always more expensive per token than prompting"
      - "The knowledge is frozen at training time, can't be cited, and ignores per-user permissions"
      - "Fine-tuning only works on small models"
    answer: 2
    explain: "Facts baked into weights go stale, can't point to a source, and are visible to every user. Retrieval addresses all three."
  - q: "A bank wants to flag wires over $10,000 to accounts opened in the last 30 days. What do you recommend?"
    options:
      - "A rule or query; use an LLM only for messy parts such as free-text payment memos"
      - "An agent that reviews every wire"
      - "Fine-tuning on past suspicious wires"
      - "Retrieval over the bank's AML policy"
    answer: 0
    explain: "The condition is structured and exact. Rules are cheaper, deterministic and auditable. Saying 'this part doesn't need an LLM' builds trust."
  - q: "When does an agent beat a fixed workflow?"
    options:
      - "Whenever the task uses more than one tool"
      - "When the customer asks for one by name"
      - "When latency must be as low as possible"
      - "When the number and order of steps depend on what the model finds along the way"
    answer: 3
    explain: "If you can write the steps down in advance, a workflow is cheaper, faster and easier to test. Agents earn their cost when the path isn't known up front."
  - q: "A 5,000-person company wants AI help for drafting, research and questions over shared documents for all staff. What's usually the right first move?"
    options:
      - "Build a custom internal chat app on the API"
      - "Buy seats on a team or enterprise plan with connectors to their existing tools"
      - "Fine-tune a model on their intranet"
      - "Wait for a vendor to build an industry-specific product"
    answer: 1
    explain: "General employee productivity is what Claude's apps are for. Building and maintaining a custom chat app rarely adds value here; save builds for specific, high-volume workflows."
  - q: "In a 12-month cost model, the build option is cheapest but buying goes live three months earlier. Over 6 months, buying is cheaper. What belongs in your recommendation?"
    options:
      - "Only the 12-month result, since it's the longer horizon"
      - "Only the 6-month result, since executives prefer short horizons"
      - "Both, stated with the horizon, plus which assumptions (review rate, go-live date) would flip the ranking"
      - "Neither; cost shouldn't drive the decision"
    answer: 2
    explain: "The horizon is part of the answer. State it, show where the curves cross, and name the assumptions that move the result."
  - q: "A support assistant costs about $0.04 per ticket in model fees and saves about $3.27 per ticket in agent time. Which assumption should the pilot measure most carefully?"
    options:
      - "The share of tickets resolved and the time saved per drafted reply"
      - "The per-token price of the model"
      - "The cache write multiplier"
      - "The number of output tokens per call"
    answer: 0
    explain: "The sensitivity table shows token prices barely move the net saving; resolution rate and time saved move it by double digits."
  - q: "According to Anthropic's cost-optimization guidance, which order should levers be applied in?"
    options:
      - "Switch to a cheaper model first, then add caching"
      - "Lower effort first, then batch, then caching"
      - "Route every task to the smallest model, then fix quality problems"
      - "Free wins first (caching, input and output hygiene, batch), then tradeoffs (effort, then model choice)"
    answer: 3
    explain: "Free wins cut cost without touching quality. Effort and model choice trade capability for cost, so they come last and are checked against an eval."
  - q: "A customer on Google Vertex AI plans to halve its nightly extraction bill with Anthropic's Message Batches API. What do you check first?"
    options:
      - "Whether the nightly job uses streaming"
      - "Platform availability: Anthropic lists Message Batches for the Claude API and Claude Platform on AWS, not Vertex AI, so confirm Vertex's own batch options and prices"
      - "Whether their prompts are under 1,000 tokens"
      - "Nothing; batch pricing is the same everywhere"
    answer: 1
    explain: "Feature availability varies by platform. Check before promising a saving, and confirm the cloud's own batch offering with its current docs."
---

Nine questions on choosing an approach, build versus buy, and cost at scale. You need 8 correct to pass.
