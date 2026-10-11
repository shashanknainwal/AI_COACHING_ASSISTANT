---
title: "Embeddings Internals: Why Dense Retrieval Misses, and What to Do About It"
type: reading
minutes: 16
---

> **By the end of this lesson** you'll be able to explain how embedding models are trained, choose between cosine and dot product, use Matryoshka truncation and quantisation without breaking recall, describe how approximate indexes like IVF trade recall for speed, and plan a re-embedding migration.

## The follow-up you will get

E3 taught you to combine BM25 and dense retrieval and to measure recall. In a design round or deep dive, the next question is often "why did dense retrieval miss this document?" or "what happens when you change embedding models?" Candidates who know what's inside the vector answer these well. This lesson gives you that.

## Where embeddings come from on a Claude project

The skill reference we use for the Claude API has no embeddings endpoint. Anthropic's documentation has pointed customers to Voyage AI for embeddings, and teams also use open-weight embedding models or their cloud's own. Check the current Anthropic docs before you recommend a provider to a customer. Everything below applies to any embedding model.

## How an embedding model is trained

Most modern text embedders are **bi-encoders**. One transformer turns a text into one vector, and query and document are encoded separately. That's why you can embed a corpus ahead of time and search it fast.

They are trained with a **contrastive** objective:

1. Take pairs that should match, such as a question and the passage that answers it, or a title and its article.
2. Encode a batch of pairs. For each query, its own passage is the positive. Every other passage in the batch is a negative ("in-batch negatives").
3. Adjust the model so the positive scores higher than the negatives. A common loss for this is InfoNCE, a softmax over similarities with a temperature.
4. Add **hard negatives**: passages that look relevant but aren't. They teach the fine distinctions.

What this explains:

- **Dense retrieval learns "what tends to be paired", not exact words.** It finds paraphrases well. It can miss rare identifiers, part numbers, names and exact phrases, which BM25 catches. That's the main reason hybrid retrieval wins.
- **Domain shift hurts.** A model trained mostly on web question-and-answer pairs may not know that two of your product codes mean the same thing. Measure recall on your own golden set before you trust a leaderboard.
- **Queries and documents can differ in shape.** Some models expect a prefix or a separate mode for queries and documents. Use the mode the model card says to, or recall drops quietly.

A **cross-encoder** reads the query and the document together and outputs one relevance score. It's more accurate and much slower, because nothing can be precomputed. That's why it's used as a reranker on the top 50 to 200 candidates, not for first-stage search.

## Cosine, dot product and normalisation

| Measure | Formula | Notes |
|---|---|---|
| Dot product | sum of a_i x b_i | Rewards longer vectors as well as direction |
| Cosine | dot(a, b) / (norm(a) x norm(b)) | Direction only |
| Euclidean (L2) | distance between the points | For unit vectors, ranks exactly like cosine |

If vectors are **normalised to length 1**, cosine and dot product give the same number, and L2 distance gives the same ranking. Normalise once at write time, then use the fastest operation your vector store has (usually the dot product).

When they differ, follow the model card. A model trained with dot product may encode something useful in the vector's length, and normalising throws that away. A model trained with cosine has meaningless lengths, so an unnormalised dot product adds noise. Mixing them up is a silent recall bug.

## Dimensions, Matryoshka truncation and quantisation

Storage and search cost grow with dimensions times documents. 10 million documents at 1,024 dimensions in 32-bit floats is about 41 GB of raw vectors before any index overhead.

**Matryoshka representation learning** trains a model so that the first 256 (or 512, ...) numbers of its vector are a usable embedding on their own. You can store shorter vectors and lose a little recall. Two rules:

1. Only truncate models trained this way. Truncating an ordinary embedding throws away information at random.
2. **Re-normalise after truncating.** The shortened vector no longer has length 1.

**Quantisation** shrinks each number:

- **int8 (scalar) quantisation**: 4x smaller than 32-bit floats, usually a small recall loss.
- **Binary quantisation**: one bit per dimension, 32x smaller. Recall drops more, so search with the binary vectors first, then **rescore** the top candidates with the full vectors.
- **Product quantisation**: splits the vector into chunks and replaces each chunk with a codebook id. Common inside ANN indexes.

Every one of these is a recall-for-cost trade. Decide with numbers from your golden set, not intuition.

## Approximate nearest neighbour search

Brute force compares the query with every vector. It's exact, and fine up to roughly a few hundred thousand vectors on one machine, but cost grows linearly. Approximate nearest neighbour (ANN) indexes search a fraction of the corpus.

**IVF (inverted file index).**

1. Cluster the vectors with k-means into `n_lists` clusters. Each cluster has a centroid.
2. At query time, find the `n_probe` nearest centroids.
3. Search only the vectors in those clusters.

With 1,000 lists and `n_probe` = 10, you compare against about 1% of the corpus plus 1,000 centroids. Recall drops when a true neighbour sits in a cluster you didn't probe, which happens most for points near cluster borders. Raise `n_probe` and recall goes up, and so does latency. You'll measure that curve in the next exercise.

**HNSW** builds a layered graph of neighbours and walks it greedily. It usually gives high recall at low latency, uses more memory, and is slower to build and update. Most vector stores offer one or both. The knobs (`n_probe`, `ef_search`) are the recall-latency dial you tune per workload.

The metric to report is **recall@k against brute force** on your real queries, at a stated latency percentile. "We use HNSW" is not an answer. "Recall@10 of 0.97 against exact search at 12 ms p95, with `ef_search` = 64" is.

## Re-embedding migrations

Vectors from different models live in different spaces, and even two versions of the same model differ. **You can't compare a query embedded with model B against documents embedded with model A.** Changing models means re-embedding the whole corpus.

A safe migration:

1. **Evaluate first.** Run the golden set through both models: recall@k, and end-to-end answer quality if you have it.
2. **Backfill a second index** with the new model while the old one serves. Budget the embedding cost and the time (10 million chunks at a few thousand per second takes hours).
3. **Dual-write.** New and updated documents go to both indexes during the backfill.
4. **Shadow-read.** Send a share of live queries to both and compare overlap and quality.
5. **Cut over**, keep the old index for rollback, then delete it.

Store the embedding model's name and version with every vector. It turns "which index is this?" into a query instead of an incident.

> **Key takeaways**
> - Bi-encoders trained contrastively find paraphrases well and miss exact identifiers. That's why hybrid retrieval wins. Domain shift is real, so measure on your own set.
> - Normalise once. Then cosine and dot product agree. Otherwise follow the model card.
> - Matryoshka truncation and quantisation trade recall for cost. Re-normalise after truncation, and rescore binary results.
> - IVF searches only the clusters nearest the query. `n_probe` is the recall-latency dial. Report recall against brute force at a latency percentile.
> - A new embedding model means re-embedding everything: evaluate, backfill, dual-write, shadow-read, cut over.
> - For a Claude project, check Anthropic's current docs for the recommended embedding provider (they have pointed to Voyage AI).
