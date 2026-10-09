---
title: "Module A6 Quiz"
type: quiz
minutes: 12
questions:
  - q: "A retailer wants support automation. What is the strongest early evidence that the pattern fits?"
    options:
      - "The CEO has seen a competitor's chatbot demo"
      - "A ticket export where a handful of intents with API-backed actions cover most of the volume"
      - "The help desk vendor offers an AI add-on"
      - "Average handle time is above ten minutes"
    answer: 1
    explain: "Repetitive intents whose actions have APIs are what an agent can actually resolve. A ticket export lets you check that in an afternoon."
  - q: "In the support-automation pattern, where should a $100 refund limit be enforced?"
    options:
      - "In the system prompt, stated clearly"
      - "In the triage model's output schema"
      - "In the refund tool's code, with larger refunds sent to a human approval queue"
      - "In the weekly review of conversations"
    answer: 2
    explain: "The prompt states policy; the tool enforces it. Code limits hold even when the model is talked into something by a clever message."
  - q: "At Calder Home, the agent costs about $239 a day. What usually decides the business case?"
    options:
      - "The resolution rate: how many contacts no longer need a person"
      - "Whether the agent uses Haiku or Sonnet for triage"
      - "The prompt cache hit rate"
      - "The number of tools the agent has"
    answer: 0
    explain: "If a human-handled contact costs dollars and a model conversation costs cents, the share of tickets fully resolved dominates the economics."
  - q: "In a document extraction pipeline, raising the confidence threshold on critical fields usually..."
    options:
      - "raises both the straight-through rate and accuracy"
      - "has no effect once the model is good enough"
      - "lowers the model bill"
      - "lowers the error rate in auto-posted documents but sends more documents to human review"
    answer: 3
    explain: "Thresholds trade straight-through rate against error rate. Size the resulting review queue to the team's real capacity."
  - q: "Ardent Mutual's model spend is about $206 a day and human review about $3,600 a day. Which change is most likely worth testing?"
    options:
      - "Switching extraction from Sonnet 5.5 to Haiku 5.5 to cut the model bill"
      - "Removing the random audit of straight-through packets"
      - "A second extraction pass on review-bound packets, using agreement between passes to let some skip review"
      - "Lowering every threshold to 0.5"
    answer: 2
    explain: "Review costs about 17 times the model. Spending a little more on the model to shrink the queue is the lever that moves the total."
  - q: "A customer must run everything on Google Vertex AI and wants overnight document processing. What should you raise in the first technical call?"
    options:
      - "The Message Batches API, and its 50% discount, is not listed for Vertex AI, so budget at standard prices or check Google's own batch options"
      - "Claude can't read PDFs on Vertex AI"
      - "Prompt caching is not available on Vertex AI"
      - "Nothing; every Claude feature works the same on every platform"
    answer: 0
    explain: "Anthropic's platform availability table lists Message Batches for the Claude API and Claude Platform on AWS only. PDF input and prompt caching are listed for Vertex AI."
  - q: "Where should a knowledge assistant enforce document permissions?"
    options:
      - "In the answer prompt, by listing what the user may see"
      - "After generation, by scanning answers for restricted content"
      - "In the user interface, by hiding restricted citations"
      - "Inside the search query, so restricted chunks are never retrieved or shown to the model"
    answer: 3
    explain: "If the model read a restricted chunk, it can paraphrase it. Filtering in retrieval is the only point early enough."
  - q: "Your UI wants a JSON payload with the answer, its citations and suggested follow-ups. What's the catch with Claude's API?"
    options:
      - "Citations only work on the Claude API, not on cloud platforms"
      - "Citations and structured outputs can't be combined in one request, so build the payload from the citation blocks in your code"
      - "Structured outputs don't support arrays"
      - "Citations require Opus 5.5"
    answer: 1
    explain: "Combining them returns a 400. Citations are listed as available on the Claude API, Bedrock, Vertex AI and Foundry."
  - q: "A 40-turn agentic coding task costs about $1.78 with prompt caching and about $10.80 without. Why is the gap so large?"
    options:
      - "Uncached requests are billed at a premium rate"
      - "Caching also caches the model's output"
      - "Each turn resends the growing conversation; caching reprices the repeated part at the cache-read rate, a small fraction of base input"
      - "Caching reduces the number of turns"
    answer: 2
    explain: "Total input grows roughly with the square of the turn count. On Opus 5.5, cache reads are $0.20 per million against $4 for fresh input."
  - q: "Which situation makes agentic coding the wrong first step for a customer?"
    options:
      - "The codebase has little meaningful test coverage and reviewers are already the bottleneck"
      - "The company has more than 1,000 engineers"
      - "Branch protection with required human review is already enforced"
      - "The team uses both GitHub and GitLab"
    answer: 0
    explain: "Without a checker, agent output can't be verified cheaply, and more PRs make a review bottleneck worse. Start with PR review or code Q&A."
---

Ten questions on the four reference architectures: fit, data flow, thresholds, permissions, platform differences and cost. You need 8 of 10 to pass.
