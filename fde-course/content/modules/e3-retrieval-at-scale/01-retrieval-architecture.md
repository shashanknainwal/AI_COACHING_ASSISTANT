---
title: "Retrieval Architecture Choices"
type: reading
minutes: 22
---

> **By the end of this lesson** you'll be able to decide between long context and retrieval with real cost numbers, pick a chunking strategy and defend it, explain lexical, dense and hybrid search and when each fails, place a reranker and metadata filters correctly, and talk through all of it in a design round.

## How this shows up in interviews

Retrieval is one of the most reliable topics in applied AI loops:

- Anthropic's Applied AI Engineer postings list retrieval next to prompting and agents as core skills (**Official**, from the job posting).
- LLM system design rounds are reported at every lab this course covers, and "design a document Q&A service" or "add search to this assistant" is a natural prompt (**Reported**).
- Perplexity's AI system design round is reported to focus on RAG, serving under latency limits and caching (**Reported**).

Interviewers rarely want a vendor list. They probe whether you know **why** each stage exists, what it costs, and how it fails. The practice prompts in this lesson are original, written in the style of those rounds.

If you took the FDE track, its lesson "Retrieval-Augmented Generation (RAG)" covers the basic pipeline. This lesson assumes it and goes deeper on the decisions.

## Decision 0: do you need retrieval at all?

Current Claude models have a 1M-token context window. Many corpora fit. The question is cost, latency, freshness and access control, not "can it fit".

### Worked numbers

A help center of 300 articles, about **400K tokens**. **10,000 questions a day**. Claude Sonnet 5.5: $2 per million input tokens, $10 per million output, cache reads $0.20 per million, cache writes about 1.25x input ($2.50).

| Approach | Input per question | Cost per question | Per day |
|---|---|---|---|
| Whole corpus in the prompt, no caching | 400K tokens | $0.80 | about $8,000 |
| Whole corpus, prompt-cached (steady traffic keeps the cache warm) | 400K cache-read tokens | about $0.08 | about $800 |
| RAG: 8 chunks of 500 tokens plus 1K of instructions | about 5K tokens | about $0.01 | about $100 + search infrastructure |

Output (say 300 tokens, $0.003 per answer) is the same in every row, so it doesn't change the decision.

Caching changes the math by 10x, which is why "just use long context" is a real option now. But caching only works while the prefix is byte-identical. Edit one article and the next request pays a full cache write.

### When long context wins

- The corpus is small or medium (well under the window) and changes rarely.
- Questions need **synthesis across many documents** ("summarise every change to the refund policy this year"). Top-k retrieval can't see the whole picture.
- You need a **quality baseline fast**. Long context has no retrieval misses, so it tells you the best answer quality you can expect. Build it first, then see if RAG matches it for less.

### When retrieval wins

- The corpus is larger than the window, or grows without bound (tickets, logs, contracts).
- **Freshness:** documents change hourly. Re-indexing one chunk is cheap; rebuilding and re-caching a 400K-token prompt is not.
- **Access control:** each user may see a different subset. A shared cached prompt can't hold per-user permissions; a filtered retrieval can.
- **Latency:** time to first token grows with prompt length. Caching cuts much of that, but a 400K-token prompt is still slower than a 5K one. Measure on your own traffic.
- **Attention:** research on earlier models ("Lost in the Middle", Liu et al., 2023) found facts placed mid-context were used less reliably. Newer models handle long context much better, but test it on your data rather than assuming.

**Interview line:** "I'd start with the corpus in a cached prompt as a baseline, measure quality and cost, and move to retrieval when the corpus, its update rate or its permission model makes the prompt approach expensive or unsafe."

## Chunking

You retrieve chunks, not documents. Chunking decides what a search hit can contain, so it caps everything downstream.

| Strategy | How | Good for | Fails when |
|---|---|---|---|
| Fixed window + overlap | N tokens, slide by N minus overlap | Unstructured text, a quick baseline | Splits tables, code and sentences mid-way |
| Sentence / paragraph | Split on natural boundaries, merge small pieces | FAQs, policies, help articles | Very short paragraphs lose their context |
| Structure-aware | Split on headings, clauses, functions; keep tables whole | Manuals, contracts, code, API docs | Needs a parser per format |
| Parent-child ("small to big") | Search small chunks, send the larger parent section to the model | Precise matching plus enough context to answer | More tokens per answer; dedupe parents |
| Contextual headers | Prepend title and section path to every chunk before indexing | Chunks that say "it" or "this plan" | Almost never hurts; cheap |
| Contextual retrieval | A model writes a short context sentence per chunk before indexing | Large corpora where chunks are ambiguous alone | Indexing cost; re-run when documents change |

### Sizing

A common starting point is **200 to 800 tokens per chunk, with 10 to 20% overlap**. Treat that as a rule of thumb to test, not a law.

- **Smaller chunks** match precisely and cost fewer tokens per answer, but a fact that needs two sentences of setup arrives without them.
- **Larger chunks** carry context, but one embedding has to represent several topics, so similarity gets blurry. You also send more irrelevant text to the model.
- **Overlap** protects facts that straddle a boundary. It also duplicates text, grows the index, and can return near-duplicate hits that waste top-k slots.

Pick between two or three settings with a labelled query set and recall@k (lesson 4), not by feel.

### Contextual retrieval

Anthropic published a technique called [contextual retrieval](https://www.anthropic.com/news/contextual-retrieval): before indexing, Claude writes a short context for each chunk ("This chunk is from the Q2 report's section on EMEA revenue"), and that context is indexed with the chunk for both embeddings and BM25. In Anthropic's tests, it cut the top-20 retrieval failure rate by 49%, and by 67% when combined with reranking. Prompt caching keeps the indexing pass cheap, because the full document is the shared prefix for every chunk's request.

## Lexical, dense and hybrid search

### Lexical (BM25)

BM25 scores a chunk by the query terms it contains, weighted by how rare each term is (IDF), with term frequency that saturates and a penalty for long chunks. You build it from scratch in the next exercise.

- **Strengths:** exact identifiers (`E4012`, SKUs, function names, people's names), no model to host, every score is explainable, cheap to update.
- **Weaknesses:** no synonyms or paraphrase. "Undo a bad deploy" doesn't match "roll back a release".

### Dense (embeddings)

An embedding model maps each chunk and each query to a vector; similar meaning lands nearby. At scale you use an **approximate nearest neighbour** (ANN) index, such as HNSW (a navigable graph) or IVF (clustered lists). Both trade a little recall for a lot of speed, with a knob to turn (search breadth, number of clusters probed).

- **Strengths:** paraphrase, synonyms, questions phrased nothing like the document, often cross-lingual.
- **Weaknesses:** exact codes and rare names, negation ("plans **without** a deductible" looks like "plans with a deductible"), domain jargon the embedding model never saw. Changing the embedding model means re-embedding everything.

Storage math you can do on a whiteboard: 1M chunks x 1,024 dimensions x 4 bytes (float32) is about **4 GB** of raw vectors before index overhead. Int8 quantisation cuts that to about 1 GB; binary to about 128 MB, at some cost in accuracy.

### Hybrid

Run both and fuse the ranked lists. **Reciprocal rank fusion** (RRF) is the usual default: each document scores `sum(1 / (k + rank))` across lists, with `k = 60` from the original paper. It uses ranks, not raw scores, so BM25's unbounded scores and cosine similarity's narrow band don't need normalising. You'll implement it in exercise 3.

| Query type | Lexical | Dense | Hybrid |
|---|---|---|---|
| Error code `E4012` | Strong | Weak | Strong |
| "my login keeps timing out" vs "session expiry" | Weak | Strong | Strong |
| Product name plus a paraphrased problem | Partial | Partial | Strong |

**Interview line:** "Hybrid is my default for anything user-facing, because real queries mix identifiers and natural language. I'd only drop one side if the eval set shows it adds nothing."

## Reranking

First-stage retrieval is built for speed over millions of chunks. A **reranker** is built for accuracy over a few dozen. It reads the query and each candidate together (a cross-encoder, or an LLM prompted to score relevance) and reorders them.

Typical shape: retrieve the top 50 to 100 with hybrid search, rerank, keep the top 5 to 10 for the prompt.

- **Why not rerank everything?** A cross-encoder runs a model per (query, chunk) pair. That's fine for 50 candidates and impossible for 5 million.
- **Cost of an LLM reranker:** 50 candidates x 300 tokens is 15K input tokens. On Claude Haiku 5.5 ($0.10 per million input tokens for prompts up to 100K) that is about **$0.0015 per query**. The bigger cost is latency: one more model call on the critical path.
- **When it pays:** when recall@50 is high but recall@5 is low. The right chunk is being found, just not ranked high enough. If recall@50 is also low, a reranker can't help; fix chunking or the first stage.

## Metadata filters

Every chunk should carry metadata: source, product, version, date, language, tenant, permissions.

- **Pre-filter** (restrict the search space, then rank) versus **post-filter** (rank, then drop). Post-filtering a top-5 can leave you with 1 result. Pre-filtering fills all 5 but can slow approximate indexes or reduce their recall under very selective filters. Know which one your vector store does.
- **Permissions are enforced in retrieval, never in the prompt.** "Don't reveal internal documents" is a request the model may not honour under adversarial input. A filter guarantees the model never sees the document.
- **Fail closed:** a chunk with missing permission metadata is invisible, not public.
- **Freshness:** filter or boost by date and version, so a v3 article doesn't answer a v5 question.

## Query-side techniques

You can also change the query rather than the index:

- **Query rewriting:** a small, fast model turns a chatty follow-up ("what about for contractors?") into a standalone search query using the conversation.
- **Multi-query:** generate 2 to 4 phrasings, retrieve for each, fuse with RRF.
- **Routing:** send "what's my order status" to a tool or database, not to document search.

Each adds a model call, so each must earn its latency on the eval set.

## A latency budget you can reason about

Orders of magnitude only. Measure your own stack.

| Stage | Typical range | Notes |
|---|---|---|
| Query rewrite (small model) | hundreds of ms | Skip it for single-turn search |
| Query embedding | tens of ms | Network call to the embedding provider |
| BM25 + ANN search | single to tens of ms | Grows with filters and index size |
| Rerank 50 candidates | about 100 ms to 1 s | Model and hardware dependent |
| Generation | seconds | Usually dominates; stream it |

The lesson for a design round: retrieval is rarely the latency problem. Generation is. Spend the budget on retrieval quality, and stream the answer.

## Practice prompts (original, in the style of a design round)

1. "A legal team wants Q&A over 2 million contracts, and each lawyer may only see their clients' contracts. Walk me through retrieval." Cover: chunking by clause, hybrid search, tenant and permission filters at retrieval time, reranking, citations, evals.
2. "Your RAG bot answers questions about product version 5 with version 3 docs. Diagnose it." Cover: version metadata and filters, freshness boosts, a labelled query set that includes version-specific questions.
3. "Why not just put all the docs in the prompt?" Cover: the cost table above, caching, freshness, permissions, and that it's a valid baseline.

> **Key takeaways**
> - Long context with prompt caching is a real option and a quality baseline; retrieval wins on scale, freshness, permissions and cost per query.
> - Chunking caps everything downstream. Start around 200 to 800 tokens with modest overlap, add titles or contextual headers, and choose with recall@k, not by feel.
> - Lexical search wins on exact identifiers, dense on paraphrase; hybrid with reciprocal rank fusion is the safe default.
> - Rerank the top 50 to 100 when the right chunk is found but ranked too low; a reranker can't fix a first stage that never finds it.
> - Enforce permissions with metadata filters in retrieval, fail closed, and know whether your store pre-filters or post-filters.
