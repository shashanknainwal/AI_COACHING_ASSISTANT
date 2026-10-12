---
title: "Module A8 Quiz"
type: quiz
minutes: 12
questions:
  - q: "A bank's model risk team says an LLM application can't be validated because it isn't deterministic. What's the strongest response?"
    options:
      - "Validate the bank's system on its own data: measure variance with repeated runs, benchmark it and monitor it."
      - "Set temperature to zero on the newest models so every run returns the same output for validators."
      - "Ask the vendor for the model weights and training data so validators can inspect the model directly."
      - "Classify it as a non-model tool so it falls outside the model risk policy and skips validation."
    answer: 0
    explain: "SR 11-7 and SS1/23 still expect vendor models to be validated; the bank tests the system it built. Sampling parameters such as temperature are rejected on the newest models, weights aren't provided, and reclassifying to avoid validation is the opposite of effective challenge."
  - q: "A bank builds a credit-decision assistant on Claude for its own underwriters in the EU. Under the AI Act, which description of the roles is most likely?"
    options:
      - "Anthropic is the provider of the high-risk system, and the bank is only a deployer of it."
      - "The bank is likely provider and deployer of the system; Anthropic is a GPAI model provider."
      - "Neither has duties, because a human underwriter makes the final decision on every application."
      - "The cloud platform hosting the model becomes the provider of the high-risk AI system."
    answer: 1
    explain: "The bank built the AI system and put it into service under its own authority, so it's likely the provider as well as the deployer. Anthropic provides a general-purpose AI model. Creditworthiness of natural persons is an Annex III area; counsel confirms the roles."
  - q: "A customer asks when the EU AI Act's Annex III high-risk obligations apply. What's the best answer?"
    options:
      - "They have applied since February 2025, at the same time as the prohibited practices."
      - "They apply from 2 August 2026, exactly as the original regulation set out."
      - "An amending regulation delayed them (reported: December 2027); check current status with counsel."
      - "They only apply once harmonised standards are published, so there's no date yet."
    answer: 2
    explain: "The original date was 2 August 2026. An amending regulation, reported as in force from late July 2026, moved Annex III to December 2027, and the standards-based trigger was dropped in negotiation. Prohibitions and GPAI obligations already apply. Always say 'check current status'."
  - q: "On the Claude API, which tokens count toward the input-tokens-per-minute (ITPM) limit on most models?"
    options:
      - "All input tokens, including cache reads, plus the max_tokens value requested for the output."
      - "Only cache reads, because uncached tokens are already counted against the requests limit."
      - "Only the tokens after the last cache breakpoint; cache writes are excluded from the limit."
      - "Uncached input tokens and cache writes; cache reads don't count on most models."
    answer: 3
    explain: "The rate-limits page says input_tokens and cache_creation_input_tokens count, and cache_read_input_tokens don't on most models. That's why caching raises effective throughput. max_tokens doesn't count toward OTPM either; only tokens actually generated do."
  - q: "A customer asks to buy Priority Tier for guaranteed capacity on Claude Sonnet 5.5. What do you say?"
    options:
      - "Priority Tier is no longer sold and isn't supported on Sonnet 5.5; I'll bring in the account team."
      - "Priority Tier is available on 1, 3, 6 or 12 month terms; I'll draft the commitment for you now."
      - "Set service_tier to 'auto' on each request and Priority Tier capacity is assigned automatically."
      - "Priority Tier guarantees 99.9% uptime under your SLA, so it's the right choice for this workload."
    answer: 0
    explain: "The service tiers page says Priority Tier commitments are no longer available for purchase, and it lists Sonnet 5.5 among the unsupported models. Existing commitments continue to contract end. Its 99.5% uptime target isn't a customer SLA. For guaranteed capacity the page points to sales."
  - q: "Under an existing Priority Tier commitment, how do cache reads burn down the input commitment?"
    options:
      - "They don't count at all, just as they're excluded from the standard ITPM limit."
      - "At 0.1 tokens per token read, reflecting the lower price of cache reads."
      - "At 1.25 tokens per token, the same rate as a 5-minute cache write."
      - "At 1 token per token, like any other input token sent with the request."
    answer: 1
    explain: "The documented burn-down rates are 0.1 for cache reads, 1.25 for 5-minute writes, 2.0 for 1-hour writes, 1 for other input, and 1.1 for US-only inference on Claude 4.6 and later. Unlike the standard ITPM limit, cache reads do count here, at a tenth."
  - q: "How does billing work for Claude Platform on AWS?"
    options:
      - "AWS bills Bedrock usage directly as a native service at AWS's own per-token rates."
      - "Customers prepay Anthropic credits, which AWS then deducts from their cloud commitment."
      - "Through AWS Marketplace in Claude Consumption Units, $0.01 each, metered hourly and billed in arrears."
      - "Anthropic invoices the customer directly every month, and AWS reports usage separately."
    answer: 2
    explain: "Usage is rated at standard prices, any negotiated discount is applied, and the total is converted to CCUs at $0.01 each, with discounts showing as fewer CCUs. There are no prepaid credits. Whether marketplace spend counts toward a cloud commitment is a question for the customer's cloud account team."
  - q: "A CIO who has standardised on Azure OpenAI asks, 'Is Claude better than GPT? Yes or no.' What's the best reply?"
    options:
      - "Yes. Claude is ahead on every public benchmark, so it's the safer choice for any workload you run."
      - "No. Your standard is good enough, so there's no reason for you to look at anything else today."
      - "Yes, mainly because the other vendor trains its models on enterprise customers' prompts and data."
      - "It depends on the workload. Let's run both on the same frozen set of your cases and compare."
    answer: 3
    explain: "Evidence on the customer's data beats claims. A fair bake-off includes the incumbent and agrees a decision rule first. Unsourced claims about a competitor's quality or data practices destroy credibility, and Claude is also available in Microsoft Foundry, so the Azure standard may not exclude it."
  - q: "An RFP asks: 'Provide a 99.9% uptime SLA with service credits.' What status and answer should the architect give?"
    options:
      - "Comply: Priority Tier targets 99.5% uptime, which is close enough to meet the requirement."
      - "To confirm: SLAs and credits are contract terms, owned by the account team and legal, with a date."
      - "Not supported: the vendor doesn't offer any uptime commitments to customers of any size."
      - "Partial: we'll reach 99.9% on the roadmap, and credits will follow in a future release."
    answer: 1
    explain: "Contract terms belong to legal and the account team. The Priority Tier target applies to existing commitments and isn't the customer's SLA, 'Not supported' asserts something you don't know, and roadmap promises don't belong in an RFP."
  - q: "An SI's design for an EU customer uses the Claude API with default inference, Message Batches and code execution. The customer is on Google Cloud and needs EU-only inference. What's the right call?"
    options:
      - "Approve it as drawn, and switch the deployment to an EU option once the platform adds one."
      - "Move it to Vertex AI unchanged, because Vertex supports the same features as the Claude API."
      - "Use Vertex AI's eu multi-region, queue standard calls for the backlog and host the maths as a tool."
      - "Pin the deployment to a single German region on Vertex AI, which serves all current models."
    answer: 2
    explain: "On the Claude API inference_geo is us or global only, so the design breaks the requirement. Vertex AI's eu multi-region meets it, but Vertex has no Message Batches or code execution, and its single-region endpoints serve only Sonnet 4.6 and earlier. Price the lost batch discount and the regional premium."
---

Ten questions on model risk, the EU AI Act, capacity and commercials, competitive positioning, RFPs and partners. You need 8 to pass.
