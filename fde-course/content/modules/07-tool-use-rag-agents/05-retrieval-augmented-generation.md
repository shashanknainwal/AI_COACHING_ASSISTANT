---
title: "Retrieval-Augmented Generation (RAG)"
type: reading
minutes: 3
---

> **By the end of this lesson you will be able to:**
> - Decide when RAG is needed and when a long prompt is simpler
> - Design chunking, retrieval, prompting and citing
> - Make answers verifiable with checked citations and an honest "I don't know"

Jordan's agents answer *"Can I return a sofa?"* a dozen times a day. That isn't a database lookup; it's a paragraph in Brightway's returns policy. **Retrieval-augmented generation** finds the relevant passages, puts them in the prompt, and asks Claude to answer **from those passages only**.

## First: do you need retrieval at all?

Claude Opus 5.5 has a 1M-token context window, and Brightway's whole help center is about 1,000 tokens. **Put it all in a cached system prompt** (Module 6). Search can't miss the right article, and it's the quality baseline for any later RAG system.

Use retrieval when the corpus is too big (or too slow and costly to send every time), changes often, or differs by user permissions.

## The pipeline

<div data-diagram="rag-pipeline"></div>

### 1. Chunking

| Strategy | Good for | Watch out for |
|---|---|---|
| One chunk per paragraph | Help centers, FAQs, policies | Very short paragraphs lose context |
| Fixed size (300-500 tokens) with overlap | Long unstructured text | Splits mid-sentence; duplicates text |
| By structure (headings, clauses) | Manuals, contracts | Needs a parser per format |

Give every chunk a **stable ID** (`KB-01#2`) and metadata (title, URL, updated date, who may see it). IDs make citations possible.

*"Gold members receive a $25 store credit instead"* means nothing alone: instead of what? Include the **title** when indexing and prompting (you'll do this in the exercise), or use **contextual retrieval**, an Anthropic technique where Claude writes a one-sentence context for each chunk before indexing. It measurably reduces failed retrievals, and caching keeps it cheap.

### 2. Retrieval

| Method | Strength | Weakness |
|---|---|---|
| **Keyword** (TF-IDF, BM25) | Fast, explainable, exact terms like product codes | Misses synonyms: "refund my couch" won't match "return a sofa" |
| **Embeddings** | Catches paraphrases | Needs an embedding provider (Anthropic has none; teams often use Voyage AI) and a vector store such as pgvector |
| **Hybrid** | Both; the usual production choice | Often adds a **reranker** over the top 20-50 |

You'll build keyword search with IDF weighting, the core of BM25, where every score is explainable.

### 3. Prompting

Documents **first**, question **last**, each document tagged with its ID:

```
<documents>
<document id="KB-01#2" title="Returns policy">
Large furniture such as sofas and tables can be returned within 14 days, and a $49 pickup fee applies.
</document>
</documents>

<question>
Can I return a sofa?
</question>
```

System prompt: answer only from the documents; if they don't answer it, say so (an `answerable: false` field makes this checkable); list the IDs used. Retrieved text is **untrusted data**: tell Claude documents are reference material, not instructions, and never let retrieved text alone trigger a write.

### 4. Citations you check in code

- Drop any cited ID that wasn't in the retrieved set.
- If no valid citation remains, don't show the answer; fall back to "I couldn't find that; a teammate will follow up."

The API also has a built-in **citations feature** (`document` blocks with `"citations": {"enabled": true}`) that returns the exact quoted passages. Use it when you need sentence-level quotes.

### 5. Nothing found? Skip the call

If retrieval returns nothing relevant, return the fallback without calling Claude, and log the question (it shows which articles are missing).

Measure retrieval (is the right chunk in the top k?) and generation (correct, grounded, cited?) separately. Module 8 builds both.

> **Key takeaways**
> - If the corpus fits in the prompt, use a cached system prompt instead of retrieval.
> - Chunk with stable IDs and titles or contextual summaries.
> - Keyword is exact and explainable, embeddings catch paraphrases, hybrid gets both.
> - Documents first, question last; validate every citation; skip the call when nothing is found.
