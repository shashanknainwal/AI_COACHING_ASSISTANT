---
title: "Measuring Retrieval"
type: reading
minutes: 18
---

> **By the end of this lesson** you'll be able to compute recall@k, MRR and nDCG by hand, build a labelled query set from real traffic without biasing it toward your current system, tell how big a difference has to be before it's real, and separate retrieval failures from generation failures in a broken RAG answer.

## How this shows up in interviews

"How would you know it works?" is a follow-up to almost every design answer, and for RAG the expected answer starts with measuring retrieval on its own (**Reported**, as a common pattern in applied AI system design rounds). A candidate who says "we'd check if the answers look good" loses points. A candidate who says "recall@5 on 200 labelled queries from production logs, with an oracle-context run to bound generation quality" sounds like someone who has shipped one.

If you took the FDE track, its lesson "Evaluating Agents and RAG Systems" introduces recall@k and MRR. Here you go further: graded relevance, labelling strategy, noise, and error attribution. Calibrating LLM judges is covered in E4.

## The metrics

Take one query. Its labelled relevant chunks are **A** (highly relevant, grade 2) and **B** (partly relevant, grade 1). Your system returns:

```
rank:   1   2   3   4   5
chunk:  X   A   Y   B   Z
```

| Metric | Question it answers | This query |
|---|---|---|
| **Hit rate@k** | Is at least one relevant chunk in the top k? | @1: 0, @3: 1 |
| **Recall@k** | What share of the relevant chunks are in the top k? | @3: 1/2 = 0.5, @5: 2/2 = 1.0 |
| **Precision@k** | What share of the top k is relevant? | @5: 2/5 = 0.4 |
| **MRR** (reciprocal rank, averaged over queries) | How high is the **first** relevant chunk? | 1/2 = 0.5 |
| **nDCG@k** | How good is the whole ordering, with graded relevance? | 0.643 (below) |

### nDCG, simply

Each relevant result earns its grade, discounted by how far down it is: `gain / log2(rank + 1)`. Sum those to get DCG. Then divide by the DCG of the **perfect** ordering (IDCG), so the score lands between 0 and 1.

```
DCG  = 2/log2(3) + 1/log2(5)  = 1.262 + 0.431 = 1.693   (A at rank 2, B at rank 4)
IDCG = 2/log2(2) + 1/log2(3)  = 2.000 + 0.631 = 2.631   (A at rank 1, B at rank 2)
nDCG = 1.693 / 2.631 = 0.643
```

Some teams use `2^grade - 1` as the gain, which rewards highly relevant results more. Say which one you use.

### Which metric for which job

- **Recall@k** is the RAG metric that matters most. The model can only use what you send it, so `k` should be the number of chunks you actually put in the prompt.
- **MRR** matters when one chunk answers the question and position matters, for example when you show a "top result" in the UI.
- **nDCG** matters when relevance is graded and several chunks contribute, for example when tuning a reranker.
- **Precision@k** matters for cost and distraction: irrelevant chunks cost tokens and can pull the answer off course.

```python
import math

def recall_at_k(ranked, relevant, k):
    return len(set(ranked[:k]) & set(relevant)) / len(relevant)

def reciprocal_rank(ranked, relevant):
    return next((1 / r for r, d in enumerate(ranked, 1) if d in relevant), 0.0)

def ndcg_at_k(ranked, grades, k):  # grades: {chunk_id: 1 or 2}
    dcg = sum(grades.get(d, 0) / math.log2(r + 1) for r, d in enumerate(ranked[:k], 1))
    ideal = sorted(grades.values(), reverse=True)[:k]
    idcg = sum(g / math.log2(r + 1) for r, g in enumerate(ideal, 1))
    return dcg / idcg if idcg else 0.0
```

## Building a labelled query set from real traffic

Synthetic questions written from the documents share the documents' vocabulary, so they flatter lexical search. Real users say "refund my couch", not "furniture return policy". Start from logs.

1. **Sample, then stratify.** Pull a few thousand real queries, dedupe them, strip personal data, then sample across intents, products and frequency. Keep both head queries (asked daily) and tail queries (asked once). A set of 100 to 300 queries is a reasonable first version.
2. **Pool the candidates.** For each query, gather the top 10 from **several** retrievers (BM25, dense, hybrid) and label the union. Labelling only your current system's results bakes its blind spots into the "truth".
3. **Grade with written guidelines.** 2 = answers the question, 1 = useful context, 0 = not relevant. Have two people label a shared subset and check that they agree. If they don't, fix the guidelines before you trust the numbers.
4. **Label passages, not chunk ids.** Re-chunking renames chunks. Store the document id plus the relevant passage text, and count a chunk as relevant if it contains (or overlaps) that passage. Then you can compare chunking strategies on the same labels.
5. **Keep unanswerable queries.** Some real questions have no answer in the corpus. Recall is undefined for them, so keep them out of the recall average and use them to test abstention.
6. **Let Claude draft, humans decide.** An LLM can propose relevance grades for thousands of pairs. Calibrate it against human labels on a sample before trusting it (E4 covers this).
7. **Version the set** and add every production failure you find.

## Is the difference real?

With 200 queries and recall@5 at 0.80, the standard error is `sqrt(0.8 x 0.2 / 200) ≈ 0.028`, so a 95% interval is about **±5.5 points**. A new chunker scoring 0.82 is not evidence of anything on its own.

Because both systems run on the **same** queries, compare them per query: count the queries where the new system wins and where it loses. "Better on 31 queries, worse on 9" is a much stronger signal than two averages. And read the losses. They're often a category (version-specific questions, error codes) that tells you what to fix.

## Retrieval error or generation error?

A wrong RAG answer has two suspects. Find out which one before you change anything.

| Right chunk in the prompt? | Answer correct? | Diagnosis | Fix |
|---|---|---|---|
| Yes | Yes | Working | Keep it in the regression set |
| No | No | **Retrieval failure** | Chunking, search, filters, k |
| Yes | No | **Generation failure** | Prompt, model, document format, abstention rules |
| No | Yes | **Ungrounded success**: answered from prior knowledge | Dangerous: it will invent answers too. Tighten grounding |

Retrieval failures have sub-types worth logging separately: the passage was never indexed, chunking split it, it was filtered out, or it was found but ranked below k (check recall@50 versus recall@5).

### The oracle run

Run the generation step twice on the same questions: once with retrieved chunks, once with the **labelled relevant chunks** (the oracle). Then:

- **Oracle accuracy** is your generation ceiling. If it's 92%, no retrieval work gets you past 92%.
- **The gap** between oracle and end-to-end accuracy is what retrieval is costing you.

A worked example: end-to-end accuracy 78%, oracle 92%, recall@5 84%. Most of the loss is retrieval: improve recall before touching the prompt. If instead oracle accuracy were 80%, the prompt or model is the bottleneck, and better search won't move the number much.

## Practice prompts (original, in the style of a deep dive)

1. "You changed chunk size from 800 to 300 tokens and recall@5 went from 0.81 to 0.84 on 150 queries. Ship it?"
2. "Users say the assistant is wrong about 20% of the time. Walk me through finding out why."
3. "How would you build an evaluation set for a search product that launched last week?"

For the first, a strong answer says the difference is within noise at that sample size, asks for a per-query win/loss count and the categories that changed, and checks cost (smaller chunks may mean raising k).

> **Key takeaways**
> - Set k in recall@k to the number of chunks you actually send to the model; that's the metric that bounds answer quality.
> - MRR rewards the first relevant hit; nDCG scores the whole ordering with graded relevance.
> - Build the query set from real traffic, pool candidates from several retrievers, label passages rather than chunk ids, and keep unanswerable questions.
> - With a few hundred queries, differences of a few points are noise. Compare systems per query.
> - Split failures with the right-chunk/right-answer table and an oracle run before you change the prompt or the retriever.
