---
title: "Lab 2 Report: Retrieval Eval"
type: written
minutes: 20
sections:
  - key: results
    label: 1. Results
    prompt: "Paste your results table: recall@1, @3 and @5 as hits out of 20 (plus your own queries) for the baseline, the rewrite variant (two runs if you did them) and the chunk-size variants, with MRR, cost and added latency."
    words: [60, 300]
  - key: misses
    label: 2. Why retrieval missed
    prompt: "Pick two misses and explain why lexical search failed, in your own words. Which queries did the rewrite fix, and which did it break?"
    words: [80, 300]
  - key: decision
    label: 3. Ship the rewrite step?
    prompt: "Would you add the rewrite step in production? Use your numbers: the recall change, its interval, the added cost and latency per query, and how the rewrite variant varied between runs."
    words: [80, 300]
rubric:
  - name: Numbers with counts and intervals
    points: 25
    lookFor: "Recall reported as hits out of n at each k for each variant, with an interval or a note that one query is 5 points. Cost and added latency for the rewrite variant from the results file."
  - name: Understanding of the misses
    points: 30
    lookFor: "Explains real misses by vocabulary mismatch, chunking or ambiguity, with the specific query and article. Names which queries the rewrite fixed and broke."
  - name: Variance and determinism
    points: 15
    lookFor: "Notes that the BM25 baseline is deterministic and the rewrite variant is not, and reports or discusses run-to-run change."
  - name: A decision grounded in trade-offs
    points: 30
    lookFor: "A clear ship or don't-ship call weighing recall gain against cost, latency and variance, with what more evidence would change the decision (more queries, chunk-level labels, a hybrid index)."
passScore: 70
graderNotes: "If recall is given only as a percentage with no counts, cap 'Numbers with counts and intervals' at 12. If the learner claims the rewrite is better from a one-query difference without mentioning noise, cap 'A decision grounded in trade-offs' at 15. Reward learners who added their own queries and noticed they behaved differently from the provided set. If the learner couldn't run the paid variant, the baseline is free: expect baseline numbers at least, and cap the total near 55 if only the baseline was run."
anchors:
  - label: weak
    expect: [0, 45]
    answer: "Results: the rewrite was better. Misses: some queries didn't match. Decision: yes, ship it, AI makes search better."
  - label: strong
    expect: [75, 100]
    answer: "Results: baseline BM25 at 120 words: recall@1 9/20, @3 14/20 (Wilson 48% to 86%), @5 15/20, MRR 0.59, free. Rewrite with claude-haiku-5-5 low: run 1 @3 18/20 (Wilson 70% to 97%), run 2 17/20; MRR 0.74; $0.004 for 20 queries; added p50 1.1 s, p95 2.3 s. 40 words: @3 14/20; 200 words: @3 13/20. My five queries: baseline 2/5 at @3, rewrite 4/5. Misses: q02 'my pen showed up broken' missed because the article says 'damage' and 'cracked', never 'broken'; q14 'remove all my personal information' missed because the article says 'deleting your account and data'. The rewrite fixed q02, q05, q09 and q14 in run 1 and broke none; in run 2 it lost q11 (Toronto), because the keywords never said Canada. Decision: not as a separate call on every query. The gain is about 3 to 4 queries out of 20, which is real but inside overlapping intervals; it adds about a second and makes retrieval non-deterministic. I'd first try a hybrid index (BM25 plus embeddings) and synonym expansion in the index, measure on 60 queries with chunk-level labels, and only add the rewrite call if it still wins by more than the run-to-run spread."
---

Paste your lab 2 results here. The lab lives in `capstone-kit/labs/lab2_retrieval_eval/`. The baseline costs nothing; the rewrite variant makes about 20 cheap calls on your own key.

Retrieval is measured on its own, before any answer is written. If the right article never reaches the model, no prompt can fix the answer. That's the point you're showing here.
