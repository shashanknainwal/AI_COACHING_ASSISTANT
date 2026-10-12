---
title: "Module A6 Quiz"
type: quiz
minutes: 12
questions:
  - q: "A retailer wants support automation. What is the strongest early evidence that the pattern fits?"
    options:
      - "The CEO has seen a competitor's chatbot demo and wants one live by next quarter"
      - "A ticket export where a few API-backed intents cover most volume"
      - "The help desk vendor already offers an AI add-on the team could switch on"
      - "Average handle time is above ten minutes across most ticket categories"
    answer: 1
    explain: "Repetitive intents whose actions have APIs are what an agent can actually resolve. A ticket export lets you check that in an afternoon."
  - q: "In the support-automation pattern, where should a $100 refund limit be enforced?"
    options:
      - "In the system prompt, stated clearly and repeated near the end of the prompt"
      - "In the triage model's output schema, as an enum of allowed refund amounts"
      - "In the refund tool's code, with larger refunds sent for approval"
      - "In the weekly human review of a random sample of agent conversations"
    answer: 2
    explain: "The prompt states policy; the tool enforces it. Code limits hold even when the model is talked into something by a clever message."
  - q: "Ostrava Re runs on Amazon Bedrock and needs schema-constrained JSON from its extraction step. What should you raise?"
    options:
      - "Bedrock's Messages-API endpoint lists structured outputs as unsupported; confirm"
      - "Structured outputs work identically on every platform, so nothing needs raising"
      - "Bedrock rejects PDF input, so the documents must be converted to text first"
      - "Structured outputs require Opus 5.5, so the cheaper extraction model won't work"
    answer: 0
    explain: "On Bedrock it's a version split: the newer Messages-API endpoint lists structured outputs as not supported, while the legacy InvokeModel integration supports them for some models. Confirm the path and model, or validate JSON in code. Claude Platform on AWS supports them."
  - q: "In a document extraction pipeline, raising the confidence threshold on critical fields usually..."
    options:
      - "raises both the straight-through rate and the accuracy of auto-posted documents"
      - "has no measurable effect once the extraction model is good enough"
      - "lowers the model bill, because fewer tokens are generated per document"
      - "cuts auto-posted errors but sends more documents to review"
    answer: 3
    explain: "Thresholds trade straight-through rate against error rate. Size the resulting review queue to the team's real capacity."
  - q: "Ardent Mutual's model spend is about $206 a day and human review about $3,600 a day. Which change is most likely worth testing?"
    options:
      - "Switching extraction from Sonnet 5.5 to Haiku 5.5 to cut the model bill further"
      - "Removing the random audit of straight-through packets to save reviewer time"
      - "A second pass on review-bound packets, letting agreeing ones skip review"
      - "Lowering every confidence threshold to 0.5 so more packets go straight through"
    answer: 2
    explain: "Review costs about 17 times the model. Spending a little more on the model to shrink the queue is the lever that moves the total."
  - q: "A customer must run everything on Google Vertex AI and wants overnight document processing. What should you raise in the first technical call?"
    options:
      - "Message Batches isn't listed for Vertex AI; budget at standard prices"
      - "Claude can't read PDF documents on Vertex AI, so OCR is required first"
      - "Prompt caching isn't available on Vertex AI, so input costs will be higher"
      - "Nothing, because every Claude feature works the same way on every platform"
    answer: 0
    explain: "Anthropic's platform availability table lists Message Batches for the Claude API and Claude Platform on AWS only, so budget at standard prices or check Google's own batch options. PDF input and prompt caching are listed for Vertex AI."
  - q: "Where should a knowledge assistant enforce document permissions?"
    options:
      - "In the answer prompt, by listing the documents this user is allowed to see"
      - "After generation, by scanning each answer for restricted content before display"
      - "In the user interface, by hiding citations that point to restricted documents"
      - "In the search query, so restricted chunks never reach the model"
    answer: 3
    explain: "If the model read a restricted chunk, it can paraphrase it. Filtering in retrieval is the only point early enough."
  - q: "Your UI wants a JSON payload with the answer, its citations and suggested follow-ups. What's the catch with Claude's API?"
    options:
      - "Citations only work on the Claude API itself, not on any of the cloud platforms"
      - "Citations and structured outputs can't share a request; build it in code"
      - "Structured outputs don't support arrays, so the citations list can't be returned"
      - "Citations require Opus 5.5, which makes every answer twice as expensive"
    answer: 1
    explain: "Combining them returns a 400, so build the payload from the citation blocks in your code. Citations are listed as available on the Claude API, Bedrock, Vertex AI and Foundry."
  - q: "A 40-turn agentic coding task costs about $1.78 with prompt caching and about $10.80 without. Why is the gap so large?"
    options:
      - "Uncached requests are billed at a premium rate on top of the standard input price"
      - "Caching also caches the model's output, so later turns generate fewer tokens"
      - "Each turn resends the history; caching reprices it at the cache-read rate"
      - "Caching reduces the number of turns the agent needs to finish the task"
    answer: 2
    explain: "Total input grows roughly with the square of the turn count. On Opus 5.5, cache reads are $0.20 per million against $4 for fresh input."
  - q: "Which situation makes agentic coding the wrong first step for a customer?"
    options:
      - "Little test coverage, and reviewers are already the bottleneck"
      - "The company has more than 1,000 engineers spread across many teams"
      - "Branch protection with required human review is already enforced everywhere"
      - "The engineering teams use both GitHub and GitLab for different repositories"
    answer: 0
    explain: "Without a checker, agent output can't be verified cheaply, and more PRs make a review bottleneck worse. Start with PR review or code Q&A."
---

Ten questions on the four reference architectures: fit, data flow, thresholds, permissions, platform differences and cost. You need 8 of 10 to pass.
