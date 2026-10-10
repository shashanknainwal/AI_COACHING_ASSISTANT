---
title: "Module Quiz: Retrieval at Scale"
type: quiz
minutes: 10
questions:
  - q: "A 400K-token help center sits in a prompt-cached system prompt on Claude Sonnet 5.5 (cache reads $0.10 per million tokens). Roughly what does the cached corpus cost per question once the cache is warm?"
    options:
      - "$0.004"
      - "$0.04"
      - "$0.80"
      - "$8.00"
    answer: 1
    explain: "0.4M tokens x $0.10 per million = $0.04. Uncached it would be 0.4M x $2 = $0.80. Caching makes long context a real option, but only while the prefix stays byte-identical."
  - q: "In BM25, what does the k1 parameter control?"
    options:
      - "How many results the search returns for each query"
      - "How much long chunks are penalised relative to short ones"
      - "How fast repeated mentions of a term stop adding score"
      - "The weight of the title compared with the body text"
    answer: 2
    explain: "k1 controls term-frequency saturation: the tenth mention of a word adds far less than the first. Length normalisation is b. Neither sets the number of results."
  - q: "Users search for exact error codes such as E4012. Which first-stage retriever is most likely to rank the right article first?"
    options:
      - "Lexical search (BM25)"
      - "Dense embeddings on their own"
      - "A reranker with no first-stage retriever"
      - "Long context with no retrieval step at all"
    answer: 0
    explain: "Exact identifiers are lexical search's strength. Embeddings often treat rare codes as noise. That's one reason hybrid search is the safe default for user-facing systems."
  - q: "Why does reciprocal rank fusion combine ranks instead of adding raw scores from BM25 and the vector index?"
    options:
      - "Ranks are much cheaper to compute than similarity scores"
      - "Raw scores are kept private inside each separate index"
      - "Adding scores would require retrieving every document"
      - "The score scales differ, so one retriever would dominate"
    answer: 3
    explain: "BM25 scores are unbounded while cosine similarities sit in a narrow band. RRF uses only positions, so it needs no normalisation and has a single constant, k (60 in the original paper)."
  - q: "You fuse keyword and vector results, keep the top 5, then drop documents the user isn't allowed to see. What goes wrong?"
    options:
      - "Nothing; the result is identical to filtering first"
      - "Fewer than 5 results, though allowed ones ranked lower"
      - "RRF scores can turn negative once documents are removed"
      - "The filter leaks the hidden documents' titles to the user"
    answer: 1
    explain: "Post-filtering a small top-k can starve the result list. Filter each candidate list first (pre-filter), and enforce permissions in retrieval, never only in the prompt."
  - q: "Recall@50 is 0.95 but recall@5 is 0.62. What is the most targeted next step?"
    options:
      - "Increase the chunk overlap so fewer facts are split"
      - "Switch to a larger generation model for the answers"
      - "Add a reranker over the top 50 candidates"
      - "Remove the vector index and rely on lexical search"
    answer: 2
    explain: "The right chunk is being found but ranked too low. A reranker reorders a few dozen candidates accurately. If recall@50 were also low, a reranker couldn't help."
  - q: "A query has exactly one relevant chunk (grade 1), and your system ranks it 2nd. What is nDCG@5?"
    options:
      - "About 0.63"
      - "0.5"
      - "1.0"
      - "About 0.32"
    answer: 0
    explain: "DCG = 1 / log2(3) = 0.631. The ideal ordering puts it first: IDCG = 1 / log2(2) = 1. nDCG = 0.631. MRR for the same query would be 0.5."
  - q: "You build a retrieval eval set by labelling only the top 10 results from your current BM25 system. What's the main risk?"
    options:
      - "The set will grow too large for anyone to label by hand"
      - "BM25 results can't be graded on a relevance scale"
      - "Recall will always come out as exactly zero for BM25"
      - "Chunks BM25 never surfaces are never labelled at all"
    answer: 3
    explain: "Pool candidates from several retrievers (BM25, dense, hybrid) and label the union, so a new system that finds what BM25 missed gets credit for it."
  - q: "End-to-end accuracy is 70%. With the labelled relevant chunks supplied instead of retrieved ones (an oracle run), accuracy is 91%. Recall@5 is 74%. Where should you work first?"
    options:
      - "The prompt, because 91% shows the model itself is weak"
      - "The embedding model's dimension, which caps the recall"
      - "Retrieval: the gap mostly closes with the right chunks"
      - "Nowhere, because a 70% score is within the noise"
    answer: 2
    explain: "The oracle run bounds generation quality at 91%. The 21-point gap is what retrieval costs you, and recall@5 of 74% agrees. Fix retrieval before touching the prompt."
  - q: "Your code verifies that every cited document id in Claude's answer was actually retrieved. What does that check NOT prove?"
    options:
      - "That the cited document supports the sentence"
      - "That the answer cites only documents you retrieved"
      - "That no invented document ids ever reach the user"
      - "That every sentence has a citation, given an uncited check"
    answer: 0
    explain: "An id check catches invented sources and missing citations. Whether the document supports the claim needs a groundedness check: an LLM judge calibrated against humans, or human review on a sample."
---

Ten questions on the decisions in this module. You need 8 correct to pass.
