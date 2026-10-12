"""Lab 2: retrieval eval with recall@k, baseline vs model-rewritten queries.

    python -m labs.lab2_retrieval_eval.run                       # both variants
    python -m labs.lab2_retrieval_eval.run --variant baseline    # no API calls, free
    python -m labs.lab2_retrieval_eval.run --max-words 60        # try another chunk size

Baseline: BM25 over the help-centre articles with the raw query.
Rewrite: Claude Haiku 5.5 (effort low) turns the query into search keywords
first (structured output), then the same BM25. Recall is measured at the
document level: a query counts as a hit at k if a relevant article is in the
top k distinct articles.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from app import config
from app.costs import CostMeter
from app.retrieval import BM25Index, load_corpus, recall_at_k, reciprocal_rank, unique_docs
from evals.stats import wilson_interval
from labs.common import ROOT, latency_cost_summary, load_jsonl, pct, write_json

HERE = Path(__file__).parent
KS = (1, 3, 5)

REWRITE_SYSTEM = """You turn a customer's question into keywords for a lexical search over a stationery shop's help centre.
The help centre has articles on: returns and refunds, damaged or wrong items, shipping options and international delivery, order tracking and late orders, engraving, billing and invoices, accounts and privacy, the Inkwell Rewards loyalty programme, wholesale accounts, and product care.
Return 4 to 8 lowercase keywords that are likely to appear in the right article. Include synonyms the article might use for the customer's words. Do not answer the question."""

REWRITE_SCHEMA = {
    "type": "object",
    "properties": {"keywords": {"type": "array", "items": {"type": "string"}}},
    "required": ["keywords"],
    "additionalProperties": False,
}


def evaluate(index: BM25Index, queries: list[dict], query_text: dict[str, str]) -> dict:
    rows, hits = [], {k: 0 for k in KS}
    rr_total = 0.0
    for q in queries:
        chunks = index.search(query_text[q["id"]], k=20)
        docs = unique_docs([c.id for c, _ in chunks])
        row = {"id": q["id"], "query": query_text[q["id"]], "top_docs": docs[:5], "relevant": q["relevant"]}
        for k in KS:
            r = recall_at_k(docs, q["relevant"], k)
            row[f"recall@{k}"] = r
            hits[k] += r == 1.0
        row["rr"] = reciprocal_rank(docs, q["relevant"])
        rr_total += row["rr"]
        rows.append(row)
    n = len(queries)
    summary = {f"recall@{k}": {"hits": hits[k], "n": n, "rate": hits[k] / n,
                               "wilson_95": [round(x, 4) for x in wilson_interval(hits[k], n)]} for k in KS}
    summary["mrr"] = rr_total / n
    return {"summary": summary, "rows": rows}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", choices=["baseline", "rewrite", "both"], default="both")
    ap.add_argument("--max-words", type=int, default=120)
    ap.add_argument("--model", default=config.HAIKU)
    ap.add_argument("--effort", default="low")
    args = ap.parse_args()

    corpus = load_corpus(ROOT / "app" / "data" / "kb", max_words=args.max_words)
    index = BM25Index(corpus)
    queries = load_jsonl(HERE / "queries.jsonl")
    print(f"{len(corpus)} chunks from {len({c.doc_id for c in corpus})} articles, chunk size {args.max_words} words")
    out: dict = {"max_words": args.max_words, "chunks": len(corpus)}

    variants = ["baseline", "rewrite"] if args.variant == "both" else [args.variant]
    for variant in variants:
        if variant == "baseline":
            texts = {q["id"]: q["query"] for q in queries}
        else:
            from app.llm import call, get_client

            client, meter, results, texts = get_client(), CostMeter(), [], {}
            for q in queries:
                res = call(client, system=REWRITE_SYSTEM, user=q["query"], model=args.model, effort=args.effort,
                           max_tokens=2048, schema=REWRITE_SCHEMA, meter=meter)
                results.append(res)
                kws = res.parsed.get("keywords", []) if res.ok and isinstance(res.parsed, dict) else []
                # Fall back to the raw query on any error, and keep the raw words too.
                texts[q["id"]] = q["query"] + " " + " ".join(kws)
            out["rewrite_usage"] = latency_cost_summary(results)
        result = evaluate(index, queries, texts)
        out[variant] = result
        s = result["summary"]
        print(f"\n{variant}:")
        for k in KS:
            r = s[f"recall@{k}"]
            print(f"  recall@{k}: {r['hits']}/{r['n']} = {pct(r['rate'])} (95% Wilson {pct(r['wilson_95'][0])} to {pct(r['wilson_95'][1])})")
        print(f"  MRR {s['mrr']:.3f}")
        misses = [row["id"] for row in result["rows"] if row["recall@3"] < 1.0]
        print(f"  misses at k=3: {misses or 'none'}")
        if variant == "rewrite":
            u = out["rewrite_usage"]
            print(f"  rewrite cost ${u['total_usd']:.4f} for {u['calls']} queries; p50 {u['p50_latency_s']}s, "
                  f"p95 {u['p95_latency_s']}s added per query; errors {u['errors']}")

    if "baseline" in out and "rewrite" in out:
        b = {r["id"]: r["recall@3"] for r in out["baseline"]["rows"]}
        w = {r["id"]: r["recall@3"] for r in out["rewrite"]["rows"]}
        print(f"\nat k=3, rewrite fixed {[i for i in b if b[i] < 1 <= w[i]]} and broke {[i for i in b if w[i] < 1 <= b[i]]}")
    path = Path("results") / f"lab2_retrieval_{args.max_words}w.json"
    write_json(path, out)
    print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
