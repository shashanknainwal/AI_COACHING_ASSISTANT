---
title: "Round 2: Design a Claims Platform Across Three Regions"
type: written
minutes: 50
sections:
  - key: requirements
    label: 1. Requirements and numbers
    prompt: "The questions you'd ask, the assumptions you'd make, and the numbers you design for: volume per region, peaks, documents per claim, tokens per claim, latency needs, and what 'done' means for a claim."
    words: [80, 250]
  - key: architecture
    label: 2. Pipeline and components
    prompt: "The flow from 'claim arrives' to 'adjuster acts': intake, document processing, extraction, checks, routing, summary. Which steps use a model and which are plain code, and how it connects to each region's claims system."
    words: [150, 400]
  - key: residency
    label: 3. Regional topology and data residency
    prompt: "Where each region's data is processed and stored, including model calls, logs, indexes and backups. Which platform you'd use in each region and what you'd confirm before committing. What happens when a region's model endpoint is down."
    words: [100, 350]
  - key: decisions
    label: 4. Decision boundaries and model choice
    prompt: "What the system may decide on its own, what it only recommends, and what only a licensed adjuster decides. Which model does which step, and why."
    words: [80, 300]
  - key: evals
    label: 5. Evals and monitoring
    prompt: "How you prove extraction and routing quality before launch, per region and language, and how you catch drift after launch."
    words: [80, 300]
  - key: cost
    label: 6. Cost, peaks and rollout
    prompt: "Cost per claim and per month with the arithmetic, how you handle a catastrophe surge, and a phased rollout across the three regions."
    words: [60, 250]
rubric:
  - name: Scoping with numbers
    points: 15
    lookFor: "Breaks the 50,000 claims down by region and line, states documents and tokens per claim, sizes the catastrophe peak, and asks the questions that change the design (what counts as 'simple', who owns residency interpretation, which systems are the source of truth)."
  - name: Pipeline architecture
    points: 20
    lookFor: "A coherent pipeline: intake from each claims system, OCR or PDF handling, classification of documents, structured extraction against a schema with validation, deterministic business rules in code, fraud-vendor integration, routing to queues, and an adjuster-facing summary with citations to source documents. Model steps and plain-code steps are clearly separated. At least one alternative considered and rejected with a reason."
  - name: Regional topology and residency
    points: 20
    lookFor: "Three regional stacks (US, EU, Australia) with processing and storage in-region: model endpoints, document storage, logs, traces, eval data, indexes and backups. Platform choice per region that fits the customer's clouds (AWS for US and Australia, Azure for the EU), with an explicit plan to confirm model and feature availability in each specific cloud region. Failover stays in-region or degrades to a manual queue; never silently sends EU or Australian data to another region. Only anonymised aggregates cross regions."
  - name: Decision boundaries and model choice
    points: 15
    lookFor: "The model extracts, classifies, flags and summarises; it never denies or reduces a claim. Any auto-approval is limited to a narrow, rule-defined class (for example low value, complete documents, no fraud flag) with code enforcing the limits. Model routing by task (a smaller model for classification, a stronger one for complex summaries) with reasons."
  - name: Evals and monitoring
    points: 15
    lookFor: "A labelled golden set from historical claims per region, language and line; field-level extraction accuracy; routing precision and recall; error analysis on the costly mistakes (a wrongly fast-tracked claim). Ongoing sampling with adjuster review, drift monitoring by region, and a regression gate for prompt or model changes."
  - name: Cost, peaks and rollout
    points: 15
    lookFor: "A cost per claim from token counts and real prices, a monthly total, a surge plan for 4x volume (queueing, prioritisation, rate limits planned per region, batch processing for non-urgent work where the platform offers it), and a phased rollout starting with one region and one line, shadow mode before live routing."
passScore: 70
graderNotes: "The key judgements are residency and decision rights. Mark down hard: a single global endpoint or a shared vector store or log pipeline across regions; cross-region failover for EU or Australian data; asserting that a specific model is available in a specific cloud region without saying it must be confirmed; letting the model deny or reduce claims; auto-approval with no code-enforced limits; no plan for the catastrophe surge. Reference arithmetic (assumptions may differ if stated): about 15,000 input tokens and 1,500 output tokens per claim for extraction on Sonnet 5.5 is about $0.03 + $0.015 = $0.045; adding a summary step of similar size gives roughly $0.08 to $0.10 a claim, so about $4,000 to $5,000 a month for 50,000 claims; Opus 5.5 is roughly double. Any estimate in that order of magnitude with shown arithmetic is fine; model cost is small next to adjuster time. An answer with no cost estimate cannot score above 7 on the cost criterion. Reward stated assumptions and a short list of things to confirm with the customer's legal team and the cloud vendors over long component lists. Don't reward invented product features or claims about specific certifications."
---

Round 2 of your mock loop. Set a 50-minute timer, write in the six sections on the right, and use only the facts on this page. Architecture design rounds are reported in applied loops at every lab this course covers (**Reported**; see module C1). This prompt is original, and the insurer is fictional.

## The prompt

> Design a claims-processing platform for an insurer handling 50,000 claims a month across three regions with data-residency rules.

Grace adds the customer detail you'd get by asking. Assume anything else you need and say so.

## The customer: Aldermoor Insurance Group

| Fact | Detail |
|---|---|
| Claims per month | 50,000: United States 24,000, European Union 18,000 (Germany, Ireland, the Netherlands), Australia 8,000 |
| Lines | Motor 60%, home 30%, small commercial 10% |
| A typical claim | A first-notice-of-loss form plus about 11 documents (repair estimates, invoices, police reports, photos), about 16 pages in total |
| Languages | English, German, Dutch |
| Peaks | After a major storm, a region's daily volume can run at 4 times normal for about 10 days |
| Today | 380 adjusters. Simple claims take a median 9 days; complex claims 41 days. |
| Systems | Each region has its own claims system. The US runs an older platform with batch file exports; the EU and Australia share a newer platform with APIs. A third-party fraud-scoring service returns a score per claim. |
| Clouds | The US and Australia run on AWS. The EU runs on Azure, after an acquisition. |

The customer's requirements, as stated by their legal and claims leadership:

1. **Residency.** EU claims data, including anything sent to or returned from a model, must be processed and stored in the EU. Australian data must stay in Australia. US data must stay in the US. Only anonymised, aggregated metrics may leave a region.
2. **Decision rights.** Any denial or reduction of a claim is decided by a licensed adjuster. The system may recommend, never decide.
3. **The ask.** The Chief Claims Officer: "I want simple claims settled in two days, and my adjusters spending their time on the hard ones."

Treat the residency rules as the customer's requirements. Whether they're the correct reading of each region's law is for the customer's lawyers, and saying so is part of a good answer.

## What a strong answer covers

You don't need all of these. You need the important ones, with reasons.

1. **Numbers first.** Claims per region per day, at normal load and at a 4x surge. Tokens per claim. What "simple" means.
2. **Separate model work from rules.** The model reads documents and extracts fields. Code checks policy limits, coverage dates and thresholds. Don't ask a model to do arithmetic a rule can do.
3. **Residency is everything, not just the model call.** Document storage, logs, traces, eval sets, caches, indexes and backups all hold claim data.
4. **Plan the failure.** When the EU model endpoint is down, what happens? "Fail over to the US" is the answer that loses the round.
5. **Decision rights in code.** If anything is fast-tracked, code enforces the limits, not a prompt.
6. **Prove it per region.** A German repair invoice isn't an American one. Evals by region, language and line.

## Facts you may use

- Claude Opus 5.5 costs $4 per million input tokens and $20 per million output tokens. Claude Sonnet 5.5 costs $2 and $10. Claude Haiku 5.5 costs $0.10 and $0.50 for prompts up to 100K tokens.
- These models have a 1-million-token context window and accept PDF input.
- Claude is available through the Anthropic API and on Amazon Bedrock, Google Vertex AI and Microsoft Foundry. Features differ by platform, and which models are offered in which cloud region changes over time. Confirming model and feature availability in each specific region, in the vendor's current documentation, is part of your answer.
- The Anthropic API has a request parameter for controlling where inference runs (`inference_geo`). Check which geographies it supports today before relying on it for a residency rule.
- The Message Batches API takes 50% off token prices for work nobody is waiting on. It's available on the Anthropic API; check whether your chosen cloud platform offers batch processing before you plan around it.
- Structured outputs constrain a response to a JSON schema (`output_config.format`). You still validate the values in code.

When you submit, Claude grades your design against the rubric below. Write the score on your scorecard before you read the feedback in detail.
