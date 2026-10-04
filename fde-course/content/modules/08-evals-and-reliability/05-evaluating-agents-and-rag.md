---
title: "Evaluating Agents and RAG Systems"
type: reading
minutes: 15
---

> **By the end of this lesson you will be able to:**
> - Evaluate an agent's process (its trajectory), not just its final answer
> - Write trajectory checks for required steps, forbidden actions, budgets and limits
> - Measure retrieval separately from generation with recall@k and MRR
> - Diagnose whether a RAG failure comes from retrieval or from the answer step

## Right answer, wrong way

Look at this agent run:

```
question: "My lamp order B-1001 is late. Can you make it right?"
trace:    lookup_order(B-1001) → issue_store_credit(C-100, $25)
answer:   "Sorry about the delay! I've added $25 in store credit."
```

The answer is what a final-answer eval expects. But the agent **never checked the shipment**. It gave credit because the customer *said* the order was late. The next customer who says "my order is late" about an on-time order gets free money too.

Agents need **trajectory evals**: checks on the sequence of tool calls, not only on the final text. You already record traces (Module 7), so this costs nothing extra to collect.

## Trajectory checks

Most useful checks fall into five groups:

| Check | Catches | Example expectation |
|---|---|---|
| **Required steps, in order** | Skipped verification | `lookup_order` before `track_shipment` before `issue_store_credit` |
| **Forbidden actions** | Actions the request didn't justify | No `issue_store_credit` on a "where is my order?" question |
| **Budgets** | Loops, retries, wasted calls | At most 5 API calls |
| **Argument limits** | Policy violations inside allowed actions | Credit ≤ $25 for a gold member's late order |
| **Answer content** | Wrong or missing facts in the reply | Mentions "$25" |

Write expectations for **what must be true**, not the one exact path you'd take. Requiring the exact trace (`[lookup, track, credit]` and nothing else) fails good runs that make an extra harmless lookup. "Required tools appear in this order" allows harmless variation and still catches skipped steps.

For actions with real consequences, **zero tolerance** is the norm: one run that issues credit above the limit is a release blocker, whatever the average score.

### Outcome checks

When an agent changes state (issues credit, updates a record), also check the **resulting state** in a test environment: after the run, does C-100 have exactly $25 more credit? State checks catch bugs that traces miss, like a tool that reports success but writes the wrong amount.

### Grading the final reply

The reply itself can be graded with the methods from lesson 3: code checks for required facts, an LLM judge for tone and correctness. Keep the two separate in your report: "process correct 92%, reply correct 95%" tells you where to look.

## Evaluating RAG: two halves

A RAG answer can fail in two places:

1. **Retrieval** didn't find the right chunk, so Claude never saw the fact.
2. **Generation** had the right chunk but answered wrongly, ignored it, or cited the wrong source.

Measure them separately. Otherwise you'll spend a week rewriting prompts to fix what is really a search problem.

### Retrieval metrics

For each test query, label which chunks are **relevant** (the ones containing the answer). Then:

- **Recall@k:** the share of relevant chunks that appear in the top k results. If a question needs two chunks and only one appears in the top 3, recall@3 is 0.5. This is the most important retrieval metric for RAG: if the chunk isn't in the top k, Claude can't use it.
- **MRR (mean reciprocal rank):** for each query, 1 / the rank of the first relevant result (1.0 if it's first, 0.5 if second, 0 if missing), averaged over queries. It rewards putting the right chunk near the top.

Track both as you change chunking, search method (keyword, embeddings, hybrid) and k. A larger k raises recall but sends more text to Claude (more cost, more distraction). Choose k from data.

### Generation metrics

Hold retrieval fixed by giving the answer step the **correct** chunks, then grade:

- **Correctness:** does the answer match the reference? (code checks or a judge)
- **Groundedness:** is every claim supported by the provided documents?
- **Citation accuracy:** are cited IDs real, retrieved, and actually relevant?
- **Abstention:** when the documents don't contain the answer, does it say so?

Include **unanswerable questions** in the set ("Do you price match competitors?"). A RAG system that never says "I don't know" will invent policies.

## Building the sets cheaply

- **From production logs:** sample real questions, then have a domain expert mark the relevant chunks and write reference answers.
- **From documents:** Claude can draft question-answer pairs from each chunk. Review them, then add real user phrasing, because people don't ask questions in the documents' words ("refund my couch").
- **From failures:** every bad answer found in production becomes a test case.

> **Key takeaways**
> - Agents can reach the right answer the wrong way; grade the trajectory as well as the reply.
> - Trajectory checks: required steps in order, forbidden actions, budgets, argument limits and answer content.
> - Write expectations as conditions that must hold, not one exact path, and treat policy violations as blockers.
> - Measure RAG retrieval (recall@k, MRR) separately from generation (correctness, groundedness, citations, abstention).
