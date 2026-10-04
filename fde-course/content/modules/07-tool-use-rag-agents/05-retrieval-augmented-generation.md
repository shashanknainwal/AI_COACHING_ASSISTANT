---
title: "Retrieval-Augmented Generation (RAG)"
type: reading
minutes: 20
---

> **By the end of this lesson you will be able to:**
> - Explain when RAG is the right tool and when a long prompt is simpler
> - Design each stage of a RAG pipeline: chunking, indexing, retrieval, prompting and citing
> - Choose between keyword search, embeddings and hybrid retrieval
> - Make answers verifiable with citations and an honest "I don't know"

## The problem RAG solves

Tools give Claude live data from systems with clear lookups ("order B-1001"). But much of what customers ask is answered in **documents**: help-center articles, policy PDFs, contracts, runbooks. *"Can I return a sofa?"* isn't a database query; it's a paragraph in the returns policy.

**Retrieval-augmented generation** means: find the passages relevant to the question, put them in the prompt, and ask Claude to answer **from those passages only**. Claude provides language understanding; your documents provide the facts.

## First question: do you need retrieval at all?

Claude Opus 5.5 has a context window of 1M tokens. Brightway's whole help center is about 1,000 tokens. For a knowledge base this small, **put all of it in the system prompt** and turn on prompt caching (Module 6). There is nothing to retrieve, nothing to tune, and no way for search to miss the right article.

Use retrieval when:

- The corpus is **too big** for the context window, or big enough that sending it on every request is too slow or expensive even with caching.
- The documents **change often** and you want each answer to use the latest version without rebuilding a giant prompt.
- **Permissions** differ by user (each customer may see only their own contracts), so each request needs a different subset.

FDEs make this call constantly. "Just put it in the prompt" is often the right first version, and it gives you a quality baseline to compare a RAG pipeline against.

## The pipeline

```
Ingest → Chunk → Index → (per question) Retrieve → Prompt → Answer → Cite & check
```

### 1. Chunking

You retrieve **chunks**, not whole documents. A chunk should be big enough to make sense on its own and small enough to be specific.

| Strategy | Good for | Watch out for |
|---|---|---|
| One chunk per paragraph | Help centers, FAQs, policies | Very short paragraphs lose context |
| Fixed size (e.g. 300-500 tokens) with overlap | Long unstructured text | Splits mid-sentence; overlap duplicates text |
| By structure (headings, sections, clauses) | Manuals, contracts, docs with headings | Needs a parser per format |

Give every chunk a **stable ID** (`KB-01#2`) and keep its metadata: source title, URL, last-updated date, and who's allowed to see it. IDs make citations possible; metadata lets you filter and show sources.

A chunk like *"Gold members receive a $25 store credit instead."* is useless out of context: instead of what? Two fixes: include the **title** when indexing and prompting (you'll do this in the exercise), or use **contextual retrieval**, a technique Anthropic published in which Claude writes a one-sentence context for each chunk before indexing ("This chunk is from the late-shipments policy and describes the credit for gold members"). It measurably reduces failed retrievals, and prompt caching keeps it cheap.

### 2. Indexing and retrieval

Three families of search:

- **Keyword search** (TF-IDF, BM25): scores chunks by shared words, weighting rare words more. Fast, explainable, no extra services, great for exact terms like product codes and error messages. Misses synonyms: "expiring" won't match "expires" without stemming, and "refund my couch" won't match "return a sofa".
- **Embeddings** (semantic search): a model converts each chunk and the question into vectors; nearby vectors mean similar meaning. Catches paraphrases. Anthropic doesn't offer an embedding model; teams commonly use Voyage AI or another provider, and store vectors in a vector database or a Postgres extension like pgvector.
- **Hybrid**: run both and merge the results. This is the usual production choice, often followed by a **reranker** that rescores the top 20-50 candidates more carefully before you keep the best few.

You'll build keyword search with IDF weighting in the exercise. It's the foundation of BM25, it runs anywhere, and every score is explainable, which matters when a customer's IT team asks "why did it return that?"

### 3. Prompting with retrieved documents

Put the documents **first** and the question **last**, each document wrapped in tags with its ID:

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

And give grounding instructions in the system prompt:

- Answer **only** from the documents.
- If they don't answer the question, **say so** (an `answerable: false` field in a structured output makes this machine-checkable).
- List the IDs of the documents you used.

Retrieved text is **untrusted data**, just like user input. A document (or a web page, or an email) can contain "ignore your instructions". Keep the tag structure, tell Claude documents are reference material and not instructions, and never let retrieved text alone trigger a write action.

### 4. Citations you can check

Citations turn "trust me" into "here's the policy". Ask for document IDs in a structured output, then **validate them in code**:

- Drop any cited ID that wasn't in the retrieved set (an invented citation is a red flag).
- If no valid citation remains, don't show the answer. Fall back to "I couldn't find that; a teammate will follow up."

The Messages API also has a built-in **citations feature**: you send documents as `document` content blocks with `"citations": {"enabled": true}`, and Claude's response includes the exact quoted passages each sentence relies on. It's worth using when you need sentence-level quotes; the ID approach in this lesson works with any output format and is easy to test.

### 5. Skip the call when nothing is found

If retrieval returns nothing relevant, don't ask Claude anyway: it has nothing to ground an answer in, and you pay for the call. Return the fallback immediately. (In production you'd also log these questions; they're a list of articles the help center is missing.)

## Measuring a RAG system

Measure the two halves separately, because they fail differently:

- **Retrieval:** for a set of test questions with known correct chunks, how often is the right chunk in the top k (recall@k)? If retrieval misses, no prompt can save the answer.
- **Generation:** given the right chunks, is the answer correct, grounded, and properly cited? Does it say "I don't know" when it should?

Module 8 builds evaluation sets for exactly this.

> **Key takeaways**
> - If the whole corpus fits comfortably in the prompt, skip retrieval: use a cached system prompt.
> - Chunk with stable IDs and metadata; include titles or contextual summaries so chunks make sense alone.
> - Keyword search is explainable and exact; embeddings catch paraphrases; production systems usually combine them.
> - Put documents first, question last, require answers from the documents only, and validate every citation in code.
> - Measure retrieval and generation separately.
