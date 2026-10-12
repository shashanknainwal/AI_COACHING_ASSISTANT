---
title: "Write It: A One-Page Solution Design for Holloway Community Bank"
type: written
minutes: 45
sections:
  - key: context
    label: 1. Context, goals and non-goals
    prompt: "The problem in Holloway's numbers, what the solution will do, and what it explicitly won't do in phase 1."
    words: [100, 220]
  - key: success
    label: 2. Success criteria and evals
    prompt: "Metrics with baseline, target and how each is measured. The golden set, the eval metrics and the launch gate."
    words: [100, 250]
  - key: architecture
    label: 3. Architecture and data flow
    prompt: "Components and the flow of one complaint, step by step. Name the model and how Holloway reaches it. Include at least one alternative you rejected and why."
    words: [150, 300]
  - key: security
    label: 4. Security and data handling
    prompt: "Data classes, access, audit trail, where data goes and what you still need to confirm."
    words: [60, 180]
  - key: rollout
    label: 5. Rollout, risks and cost
    prompt: "Phases with the condition to move on, the top risks with mitigations, and the model cost per complaint and per month with your arithmetic."
    words: [100, 250]
  - key: open
    label: 6. Open questions
    prompt: "What you don't know yet, who will find out, and by when."
    words: [40, 120]
rubric:
  - name: Goals and quantified success criteria
    points: 20
    lookFor: "Goals tied to Holloway's numbers (34-minute handling, 3.5-day acknowledgement vs 2-day policy, 11% misclassification, 4% missed reportable complaints, 2,100 backlog). Each success metric has a baseline, a target and a measurement method. Non-goals are explicit and sensible (e.g. no letters sent without analyst approval)."
  - name: Architecture fit and tradeoffs
    points: 20
    lookFor: "A coherent flow (ingest, classify and extract, reportable check, draft acknowledgement, analyst review, route) that fits the stated constraints: data stays in AWS-approved services, so Claude through Amazon Bedrock or Claude Platform on AWS; asynchronous rather than interactive. Names a model with a reason. At least one rejected alternative with a reason."
  - name: Security and data handling
    points: 15
    lookFor: "Identifies personal and financial data, least-privilege read-only access to core banking, an audit trail of every classification with its reason and the analyst's decision, logging and retention choices. Separates known facts from vendor or platform terms still to confirm."
  - name: Evals and rollout
    points: 20
    lookFor: "A golden set from historical QA-reviewed complaints with stated size and labellers; per-category and reportable-flag metrics, with recall on reportable complaints treated as the critical number; a launch gate; phases such as shadow mode then a limited pilot, with conditions to move on and a rollback rule."
  - name: Cost math
    points: 10
    lookFor: "Tokens per complaint times price times about 14,000 complaints a month, with assumptions stated and the arithmetic shown. Compares the result with the $4,000/month ceiling and with the analyst time at stake."
  - name: Risks and open questions
    points: 15
    lookFor: "Realistic risks (missed reportable complaint, wrong category, prompt injection inside complaint text, analyst over-trust, taxonomy changes) each with detection and mitigation. Open questions have owners and dates."
passScore: 70
graderNotes: "Mark down hard: any design that sends letters to customers without analyst approval; any design that ignores the AWS-only constraint; stating specific vendor certifications, retention periods or data terms as facts without a source (they should be open questions); metrics with no baseline; cost figures with no arithmetic. Reasonable model-spend estimates on Claude Sonnet 5.5 land roughly between $100 and $600 a month for 14,000 complaints (for example 5,000 cached prompt tokens at $0.10/M, 1,500 fresh input tokens at $2/M and 700 output tokens at $10/M is about $0.0105 per complaint, about $150 a month; if thinking at Sonnet 5.5's default high effort triples output to 2,100 tokens it is about $0.0245, about $340 a month); even Claude Opus 5.5 stays well under the $4,000 ceiling. Reward candidates who notice that model cost is small next to roughly 8,000 analyst hours a month, that missing a reportable complaint is a much worse error than over-flagging one (so the reportable check should favour recall and route doubtful cases to a person), and that batch processing is a poor fit here: its results can take up to 24 hours (the notes require drafts within an hour), availability differs by platform, and the saving is small at this spend. Candidates who use plain asynchronous calls from a queue are fine. If a candidate relies on structured outputs on Amazon Bedrock without noting that the Messages-API endpoint lists them as unsupported (or naming the legacy InvokeModel path and model), mark down slightly under Architecture; Claude Platform on AWS supports them. A one-page answer that makes fewer, well-justified decisions should beat a long component list."
---

Grace forwards you her discovery notes and a short message: *"Holloway wants a design they can take to their CISO and head of compliance next week. One page. Make the decisions, show the numbers, and be honest about what we don't know yet."*

Holloway Community Bank and everyone in it are fictional.

## Grace's discovery notes

**The workflow.** Holloway is a regional bank with about 1.2 million customers. A team of 26 complaints analysts handles about **14,000 complaints a month** arriving by email, web form, and notes logged by branch and call-centre staff. For each one an analyst reads it, classifies it into one of **23 categories** in Holloway's internal taxonomy, decides whether it is **reportable** under Holloway's compliance policy, extracts the account, product and any disputed amount, drafts an acknowledgement letter from approved templates, and routes it to a resolution team.

**The numbers.** Median handling time is **34 minutes** per complaint. Holloway's policy is to acknowledge within **2 business days**; the current median is **3.5**, and the backlog is about **2,100**. Quality-assurance sampling finds **11%** of complaints misclassified and **4%** of reportable complaints initially missed. The head of compliance, Andrea Voss, says missed reportable complaints are "the number that keeps me up at night".

**The data.** Complaints live in Holloway's CRM, hosted in Holloway's own AWS account, with an API. Account and product data come from the core banking system through a read-only API. Letter templates are in a document library. An average complaint is about 600 words. The taxonomy, reportability policy and instructions come to about 5,000 tokens.

**The constraints.**
- Information security policy: customer data may only be processed in services approved under Holloway's **AWS** agreement. The CISO, Marcus Bell, reviews every new AI vendor; reviews take about six weeks.
- Compliance: **no letter goes to a customer without an analyst's approval**, and every classification needs an **audit trail** showing what was decided, why, and by whom.
- Nobody waits on a screen for this: drafts are needed within an hour of a complaint arriving.
- Budget: model spend must stay under **$4,000 a month** in year one. Holloway has one engineer available half-time for 12 weeks.

## The task

Write a **one-page solution design** (about 700–1,000 words across the six sections on the right) that Holloway's CISO, head of compliance and IT lead could review. Use the structure from lesson 04, compressed to the decisions.

Useful facts for the cost math: Claude Opus 5.5 costs $4 per million input tokens and $20 per million output tokens; Claude Sonnet 5.5 costs $2 and $10; cache reads cost $0.20 per million tokens on Opus 5.5 and $0.10 on Sonnet 5.5 (5% of base input); Claude Haiku 5.5 costs $0.10 and $0.50 for prompts up to 100K tokens. Thinking tokens are billed as output: Sonnet 5.5 defaults to `high` effort and Opus 5.5 and Haiku 5.5 to `medium`, so state the `effort` you'd set or add a thinking line. A stable prefix (instructions, taxonomy, policy) is a good fit for prompt caching. Batch processing on the Anthropic API costs 50% less, but results arrive asynchronously within a 24-hour window, and not every option is available on every platform; check both before you rely on it. If your design depends on structured outputs (schema-constrained JSON), check the platform: Claude Platform on AWS supports them, while Amazon Bedrock's newer Messages-API endpoint lists them as not supported (the legacy `InvokeModel` integration supports them for some models). Module A2 covers platform differences in depth.

## What good looks like

- **Decisions, not options.** Pick a model, a platform path and a rollout, and say why in one line each.
- **The asymmetric risk is the design.** A missed reportable complaint is far worse than an extra one flagged for review. Your thresholds, evals and human review should reflect that.
- **Numbers everywhere.** Baselines from the notes, targets you'd defend, and cost with the arithmetic shown.
- **Honest unknowns.** Anything about a vendor's or platform's data terms that you haven't verified goes in open questions, with an owner.

Submit for review when you're done. Claude grades your design against the rubric below, tells you the strongest part and the one change to make first. Revise and resubmit as often as you like.
