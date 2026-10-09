---
title: "Design It: Document Q&A at p95 Under 2 Seconds"
type: written
minutes: 40
sections:
  - key: requirements
    label: 1. Requirements and numbers
    prompt: "Your clarifying questions, what '2 seconds' means in your design, and the numbers you size for (corpus, queries, peak)."
    words: [80, 250]
  - key: architecture
    label: 2. Ingestion, index and request path
    prompt: "How 2 million pages become a searchable index, and the online path from question to answer. Name the models and where each runs."
    words: [150, 450]
  - key: latency
    label: 3. Latency budget
    prompt: "A step-by-step budget that adds up to your p95 target, and what you'd do when one step blows it."
    words: [80, 300]
  - key: quality
    label: 4. Evals and launch gate
    prompt: "How you'd measure retrieval and answers separately, and the thresholds you'd launch on."
    words: [80, 300]
  - key: risks
    label: 5. Failure modes and cost
    prompt: "What breaks at this scale, how you'd notice, and a rough cost per question and per month."
    words: [80, 300]
rubric:
  - name: Scoping and the latency definition
    points: 15
    lookFor: "Clarifies whether 2 seconds means first token or complete answer, what kind of documents and questions, query volume and peak, and states explicit sizing numbers (pages to tokens to chunks to index size)."
  - name: Retrieval architecture
    points: 25
    lookFor: "A credible ingestion pipeline (parsing, structure-aware chunking, embeddings, incremental updates and deletes) and an online path with hybrid search, reranking and a bounded amount of context, with reasons and at least one rejected alternative."
  - name: Latency budget
    points: 25
    lookFor: "A per-step budget that sums to the target, streaming, a fast model or low effort on the critical path, tail-latency tactics (timeouts, skipping optional steps, caching frequent queries or the stable prompt prefix), and latency figures labelled as assumptions to measure."
  - name: Evals and quality bar
    points: 20
    lookFor: "Separate retrieval metrics (for example recall at k on a labelled set) and answer metrics (correctness, citation support, declining when the answer isn't there), latency measured as p95 under realistic load, and a launch gate with thresholds."
  - name: Failure modes and cost math
    points: 15
    lookFor: "Realistic failures (bad PDF parsing, tables lost in chunking, stale or deleted pages, injection inside documents, slow model at peak) with detection and response, plus a cost per question from token counts and real prices, scaled to a month."
passScore: 70
graderNotes: "The heart of this prompt is the latency budget. Mark down hard if the answer never says what the 2 seconds measures, gives no per-step budget, or has a budget that doesn't add up. Mark down answers that stuff dozens of chunks into the prompt without discussing the latency and cost of that. Reference math the learner may use: 2 million pages at roughly 500 tokens a page is about 1 billion tokens; at 400-500 token chunks that is roughly 2-2.5 million chunks; 1,024-dimension float32 vectors are 4 KB each, so roughly 8-10 GB of vectors. Accept other reasonable assumptions if stated. A typical per-question cost on Claude Sonnet 5.5 with about 4,000 input tokens and 300 output tokens is about $0.011 before caching (4,000 x $2/M + 300 x $10/M); on Claude Haiku 5.5 about $0.00055. Do not penalize specific latency numbers for a model step if they are labelled as assumptions; do penalize presenting invented vendor latency numbers as facts. Choosing Claude Haiku 5.5 for the answer step to hit latency is fine if they say how they'd confirm quality on the eval set."
---

Leo Martins, a staff engineer coaching you for applied AI loops, drops a printed prompt on the table. "This is the latency version of the design round. Perplexity candidates report AI system design rounds about serving under latency limits (Reported), and you'll get the same pressure anywhere a product is user-facing. The trap is treating 2 seconds as a vibe. Make it a budget." Leo is a fictional coach; the prompt below is original practice, not a reported question.

## The prompt

> A legal-research startup has 2 million pages of court filings, contracts and regulatory guidance, mostly PDFs, some scanned. Lawyers type questions and expect a short answer with citations to the exact pages. The product team has one hard requirement: p95 latency under 2 seconds. About 1% of pages change or are added each week. Design the service.

Answer in the five sections on the right, as you'd talk through it in a 45-minute round.

## How to approach it

1. **Pin down "2 seconds".** First token or full answer? Measured where: the server or the user's browser? Under what load? Your whole design depends on the answer, so state your interpretation and size for it.
2. **Size the corpus with arithmetic.** Pages to tokens to chunks to vector storage. Say your per-page token assumption.
3. **Build the budget.** List every step on the critical path with a millisecond figure and make it add up. Mark which numbers are assumptions you'd measure in week one.
4. **Decide what's optional.** Which steps can you skip, cache or run in parallel when you're over budget? Reranking, query rewriting and long context are the usual candidates.
5. **Measure retrieval on its own.** If the right page never reaches the model, no prompt will fix it.
6. **Do the cost math.** Tokens per question times price times volume.

Useful facts: Claude Haiku 5.5 costs $0.10 per million input tokens and $0.50 per million output tokens for prompts up to 100K tokens; Claude Sonnet 5.5 is $2 and $10; Claude Opus 5.5 is $4 and $20. Cache reads cost $0.20 per million tokens on Opus 5.5 and $0.10 on Sonnet 5.5 (5% of base input). Prompt caching is a prefix match, so keep the stable instructions first. Claude Haiku 5.5 supports an `effort` setting from `low` to `max`; lower effort is faster. Any latency figure for a model call is something you assume and then measure, so label it that way.

When you submit, Claude grades your design against the interviewer rubric below.
