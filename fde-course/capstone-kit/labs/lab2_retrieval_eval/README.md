# Lab 2: Retrieval eval with recall@k

**Mirrors:** the retrieval exercises in E3 (retrieval at scale) and module 07. **Paste results into:** C8 lesson "Lab 2 Report: Retrieval Eval".
**Time:** 45 minutes. **Cost:** the baseline is free (no API calls). The rewrite variant makes 20 Claude Haiku 5.5 calls at effort low: well under $0.05.

You measure retrieval on its own, before any answer is generated. If the right article never reaches the model, no prompt can save the answer.

## Steps

1. Run the free baseline first and read every miss:
   ```bash
   python -m labs.lab2_retrieval_eval.run --variant baseline
   ```
   For each miss at k=3, open `queries.jsonl` and the article in `app/data/kb/`. Why did lexical search miss? (Usually: the customer's words are not the article's words, such as "broken" vs "damage".)
2. Run both variants:
   ```bash
   python -m labs.lab2_retrieval_eval.run
   ```
   The rewrite variant asks Haiku 5.5 for search keywords, then runs the same BM25. Note which queries it fixed and which it broke.
3. Try one chunking change with `--max-words 40` and `--max-words 200`. Record recall@3 for each.
4. Add five queries of your own to `queries.jsonl`, written the way a real customer would, with the article you think is relevant. Re-run. Did your queries behave like the provided ones?
5. Decide: would you ship the rewrite step? It adds a model call (cost and latency) to every query. Use your numbers.

## What to notice

- With 20 queries, one query is 5 points. Report hits out of 20 and the interval, not just a percentage.
- The baseline is deterministic: running it twice gives the same numbers. The rewrite variant is not. Run it twice and see whether recall moves.
- Recall here is document-level. Your capstone may need chunk-level relevance labels, which take longer to write and are worth it.

See `RESULTS_TEMPLATE.md`.
