---
title: "Embeddings and Retrieval 101"
type: reading
minutes: 15
---

> **By the end of this lesson** you'll be able to explain embeddings and cosine similarity, choose a chunking approach, say why hybrid search and reranking help, and argue when to use long context instead of retrieval.

## Why it's in the shared core

Almost every design round for applied roles has a "the model needs our documents" moment (**Reported**). You need the vocabulary and the trade-offs before you can draw the box labelled "retrieval". E3 builds production retrieval; this lesson is the foundation. Examples are original.

## Embeddings

An **embedding model** maps a piece of text to a vector of a few hundred to a few thousand numbers, so that texts with similar meaning land close together. "How do I get my money back?" and "refund policy" end up near each other even though they share no words.

Facts to state precisely:

- **Embeddings come from a separate model**, not from the chat model you call for answers. Vectors from different embedding models (or versions) aren't comparable: change the model and you re-embed everything.
- **Providers differ.** Some LLM vendors sell embedding models; others don't. Anthropic doesn't offer its own embedding model through the Claude API, and its docs point to third-party embedding providers. Check each vendor's current docs.
- **Query and document can be embedded differently.** Some models want an "input type" (query versus document). Follow the model's instructions.

## Cosine similarity

To compare two vectors, use **cosine similarity**: the cosine of the angle between them.

```text
cos(a, b) = (a · b) / (|a| · |b|)      1 = same direction, 0 = unrelated, −1 = opposite
```

It ignores vector length, so a long document isn't "more similar" just because its vector is bigger. If vectors are normalized to length 1, cosine is just the dot product, which is why vector databases often normalize on insert.

**Brute-force search** (compare the query with every vector, sort, take the top k) is exact and fine up to tens or hundreds of thousands of vectors. Beyond that, vector databases use **approximate nearest neighbour** indexes (for example graph-based HNSW) that trade a little recall for a lot of speed. You'll write the brute-force version in the next exercise; in an interview, say when you'd switch.

## Chunking

You don't embed a 200-page manual as one vector. You split it into **chunks** and embed each.

| Choice | Trade-off |
|---|---|
| **Chunk size** | Small chunks match precisely but lose context; large chunks keep context but dilute the match and cost more tokens when retrieved. A few hundred tokens is a common start |
| **Overlap** | Repeating some words between neighbouring chunks keeps a sentence that straddles a boundary findable |
| **Structure-aware splits** | Split on headings, sections, functions or table rows instead of every N words |
| **Context on the chunk** | Prepend the document title or a one-line summary of the section, so "it increases 4%" still says what "it" is |

## Hybrid search and reranking

Embeddings are good at meaning and bad at exact tokens: product codes, error numbers, names, rare terms. **Keyword search** (BM25) is the opposite. **Hybrid search** runs both and merges the lists, commonly with reciprocal rank fusion. It's a strong default for enterprise documents.

A **reranker** then rescores the top 20–100 candidates with a slower, more accurate model that reads the query and each chunk together, and you keep the best handful. Retrieve wide and cheap, then rerank narrow and expensive.

## Long context or RAG?

With 1M-token windows, "just put everything in the prompt" is sometimes right. Say the trade-off both ways:

| Long context wins when | Retrieval wins when |
|---|---|
| The corpus is small (fits comfortably) and stable | The corpus is large, growing or changes often |
| Questions need the whole document (summarize, compare sections) | Questions need a few facts from many documents |
| The prefix can be cached and reused across many questions | Each request would pay to read mostly irrelevant tokens |
| Building a retrieval pipeline isn't worth it for the volume | You need access control per document, or citations to specific chunks |

Lesson 01's cost and context-rot points apply: every token is billed and adds prefill time, and quality can degrade as irrelevant text grows. Prompt caching changes the maths for a stable corpus. Measure both approaches on the same eval when it's close.

## Practice (say it out loud)

- "Users search our parts catalogue by part number and by description. Design retrieval."
- "Our documents total 300K tokens and change monthly. 5,000 questions a day. Long context or RAG? Show your reasoning."

> **Key takeaways**
>
> - Embeddings map text to vectors where similar meaning is close. They come from a separate model; vectors from different models don't mix.
> - Cosine similarity compares direction, not length. Brute force is exact and fine at small scale; approximate indexes trade recall for speed.
> - Chunk by structure with some overlap, and add context to chunks.
> - Hybrid search covers exact terms and meaning; a reranker sharpens the top results.
> - Long context suits small, stable, cacheable corpora and whole-document questions; retrieval suits large, changing corpora and fact lookups. Measure when it's close.
