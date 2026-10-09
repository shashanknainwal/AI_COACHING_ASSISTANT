---
title: "Evaluating Agents and RAG Systems"
type: reading
minutes: 5
---

> **By the end of this lesson you will be able to:**
> - Evaluate an agent's trajectory, not just its final answer
> - Write checks for required steps, forbidden actions, budgets and limits
> - Measure retrieval separately from generation with recall@k and MRR

Jordan's agent issues store credit and answers policy questions from the help center. A credit can look right in the reply and still be given the wrong way.

## Right answer, wrong way

```
question: "My lamp order B-1001 is late. Can you make it right?"
trace:    lookup_order(B-1001) → issue_store_credit(C-100, $25)
answer:   "Sorry about the delay! I've added $25 in store credit."
```

The reply is fine, but the agent **never checked the shipment**. The next customer who says "late" about an on-time order gets free money. **Trajectory evals** check the sequence of tool calls, using the traces you already record (Module 7).

| Check | Catches | Example expectation |
|---|---|---|
| **Required steps, in order** | Skipped verification | `lookup_order` before `track_shipment` before `issue_store_credit` |
| **Forbidden actions** | Unjustified actions | No `issue_store_credit` on "where is my order?" |
| **Budgets** | Loops, wasted calls | At most 5 API calls |
| **Argument limits** | Policy violations | Credit ≤ $25 for a gold member's late order |
| **Answer content** | Wrong or missing facts | Mentions "$25" |

Write **conditions that must hold**, not one exact path: requiring exactly `[lookup, track, credit]` fails good runs with an extra harmless lookup. For actions with real consequences, **zero tolerance**: one credit above the limit blocks release, whatever the average.

Also check **resulting state** in a test environment (does C-100 have exactly $25 more?), which catches a tool that reports success but writes the wrong amount. Grade the reply separately (lesson 3) and report both: "process correct 92%, reply correct 95%".

## Evaluating RAG: two halves

A RAG answer fails either in **retrieval** (Claude never saw the right chunk) or in **generation** (it had the chunk and still answered wrongly). Measure them separately, or you'll spend a week rewriting prompts to fix a search problem.

**Retrieval metrics**, from queries labeled with their relevant chunks:

- **Recall@k:** share of relevant chunks in the top k. If a question needs two chunks and one appears in the top 3, recall@3 is 0.5. The key RAG metric: what isn't retrieved can't be used.
- **MRR:** 1 / rank of the first relevant result (1.0 if first, 0.5 if second, 0 if missing), averaged over queries.

A larger k raises recall but sends more text (cost, distraction). Choose k from data.

**Generation metrics**, with retrieval held fixed by supplying the correct chunks: correctness against a reference, groundedness, citation accuracy, and **abstention** on unanswerable questions ("Do you price match competitors?"). A system that never says "I don't know" invents policies.

Build sets from production logs, from Claude-drafted question-answer pairs you review (add real phrasing like "refund my couch"), and from every production failure.

> **Key takeaways**
> - Grade the trajectory as well as the reply.
> - Checks: required steps in order, forbidden actions, budgets, argument limits, answer content; policy violations block release.
> - Measure retrieval (recall@k, MRR) separately from generation (correctness, groundedness, citations, abstention).
