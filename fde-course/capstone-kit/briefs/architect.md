# Capstone brief: Applied AI Architect track

**Goal:** a working demo with an eval on a customer-style dataset, plus the documents an architect brings to a technical decision: the total cost, the platform fit and the security story.

**Time:** about 12 to 18 hours. **Budget:** under $5.

## Build

1. Choose a fictional customer in a sector you know (write a one-paragraph profile: size, systems, constraints, who signs off). Build a public or synthetic dataset that looks like their data: 100+ records or documents. No real customer data.
2. A demo of one use case on the real API (extraction, triage, RAG answers or a small agent), starting from `app/`.
3. An eval: 40+ labelled cases, 3 runs, results with intervals, at two model or effort configs.

## Documents

| Deliverable | What it must contain |
|---|---|
| Demo-with-eval README | What the demo does, how to run it, the eval method and results with counts and intervals, the limits a customer must hear |
| TCO sheet | Volume assumptions; measured tokens per request including thinking; cost per request and per month at two configs; caching and batch effects with the model named for every saving; people and platform costs; a sensitivity line (what if volume triples) |
| Platform-fit memo (1 page) | Where the customer could run Claude: the Anthropic API, Claude Platform on AWS, Amazon Bedrock, Google Vertex AI or Microsoft Foundry; which features your design needs on each (check the current platform availability docs, for example Message Batches is not on Bedrock, Vertex or Foundry); your recommendation and what you'd confirm |
| Security brief (1 to 2 pages) | Data flows, what leaves the customer boundary, retention and logging, prompt injection exposure and controls, least privilege for tools, the questions a CISO will ask and your answers |
| Decision record | 3 to 5 decisions with alternatives and evidence |

## The deep-dive questions to be ready for

Original practice questions: Why is this worth building at their volume? Which number in your TCO are you least sure of? What would make you recommend a different platform? What happens when the eval and the customer's opinion disagree?
