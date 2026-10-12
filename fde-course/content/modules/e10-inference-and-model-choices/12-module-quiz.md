---
title: "Module Quiz: Inference, Embeddings and Model Choices"
type: quiz
minutes: 12
questions:
  - q: "A customer's prompt grew from 5,000 to 150,000 tokens. Streaming speed after the first token barely changed, but time to first token jumped. Which phase explains this?"
    options:
      - "Prefill, which processes the whole prompt before any output"
      - "Decode, which slows down steadily as each output token is produced"
      - "Network transfer of the larger response body to the client"
      - "Tokenisation, which runs on the client before the request"
    answer: 0
    explain: "Prefill reads the whole prompt before the first output token and grows with prompt length. Decode speed depends mostly on batch size and memory bandwidth, so streaming speed stays about the same."
  - q: "An open-weight model's KV cache takes 128 KiB per token. Why does that number matter most when sizing a serving fleet?"
    options:
      - "It sets how fast each output token is computed on the GPU"
      - "It bounds how many tokens, and so requests, fit in GPU memory at once"
      - "It decides the price per token the provider will charge"
      - "It determines the maximum prompt length the tokenizer accepts"
    answer: 1
    explain: "KV-cache memory grows with every token in flight. After the weights, it's usually what caps concurrent requests per GPU."
  - q: "A team raised decode batch size from 32 to 64 on their own GPUs. Total tokens per second went up. What should they check before celebrating?"
    options:
      - "Whether the model's context window shrank as a side effect of batching"
      - "Whether prompt caching was disabled by the larger batch"
      - "Whether per-stream speed and p95 latency still meet the target"
      - "Whether the tokenizer now counts the same text differently"
    answer: 2
    explain: "Bigger batches trade per-stream speed for throughput. Goodput, the share of requests that meet the latency targets, is the number that matters."
  - q: "Your Sonnet 5.5 chat route doesn't set effort. Users say the first token is slow on simple questions. What's the first change to test?"
    options:
      - "Add 'answer quickly and don't think first' to the system prompt"
      - "Switch to the Message Batches API for lower cost"
      - "Raise max_tokens so the answer has more room to finish"
      - "Set output_config.effort to low and measure quality and TTFT"
    answer: 3
    explain: "Sonnet 5.5 defaults to high effort and thinks before answering, and thinking sits inside time to first token. Lowering effort reduces thinking more reliably than prompting does. Batches don't serve live chat."
  - q: "In your gateway's token bucket, why reserve input_tokens plus max_tokens at admission and refund later?"
    options:
      - "Because the API bills max_tokens whether or not they are used"
      - "Because output length isn't known until the call ends, and the worst case keeps the limit honest"
      - "Because cache reads must be reserved twice, once for each layer"
      - "Because the upstream rate limit counts only requests, not tokens"
    answer: 1
    explain: "Output length, thinking included, is only known at the end. Reserving the worst case prevents overspending, and the refund in complete() gives back what wasn't used. You're billed for actual usage."
  - q: "Your embedding model's card says it was trained with cosine similarity, and your vectors are normalised at write time. Which statement is true?"
    options:
      - "Dot product will rank results differently and is noticeably less accurate"
      - "You must store vector lengths to recover cosine at query time"
      - "Dot product and cosine give the same scores, so use the faster one"
      - "Euclidean distance becomes meaningless for unit-length vectors"
    answer: 2
    explain: "For unit vectors, dot product equals cosine, and Euclidean distance gives the same ranking."
  - q: "You truncate a Matryoshka-trained embedding from 1,024 to 256 dimensions. What must you do next?"
    options:
      - "Re-normalise the shortened vector before comparing it"
      - "Retrain the index with binary quantisation on the result"
      - "Pad the vector back to 1,024 with zeros before storing it"
      - "Re-embed the queries with a different, smaller model"
    answer: 0
    explain: "The first 256 numbers no longer have length 1. Re-normalise so cosine and dot product agree again."
  - q: "An IVF index with 1,000 lists runs at n_probe = 1 and misses an obvious related article. What is the most likely cause?"
    options:
      - "The query was not tokenised with the same model as the documents"
      - "The k-means centroids were computed with too many iterations"
      - "IVF indexes cannot return more than one result per list"
      - "The true neighbour sits in a nearby cluster that wasn't probed"
    answer: 3
    explain: "IVF only scores vectors in the probed lists. Neighbours near cluster borders land in adjacent lists. Raise n_probe and measure recall against brute force."
  - q: "A team switches embedding models. What's the safe plan?"
    options:
      - "Embed new documents with the new model and keep old vectors as they are"
      - "Re-embed the corpus into a second index, dual-write, shadow-read, then cut over"
      - "Average the old and new vectors so both models' queries still match"
      - "Keep the old model for queries and the new one for documents"
    answer: 1
    explain: "Vectors from different models live in different spaces and can't be compared. Backfill a new index, dual-write during the backfill, compare on live queries, and keep the old index for rollback."
  - q: "When does fine-tuning a model make most sense?"
    options:
      - "When the knowledge the model needs changes every week"
      - "When prompting hasn't been tried yet but the deadline is close"
      - "For a narrow, stable, high-volume task where prompting has plateaued on a trusted eval"
      - "When the team has no labelled data but wants a more on-brand style"
    answer: 2
    explain: "Fine-tuning teaches behaviour on a stable task. Facts that change belong in retrieval, and without trusted data and an eval you can't tell whether the tune helped."
  - q: "A Claude Opus 5 integration sends tool_choice {type: tool} and temperature 0. What happens after switching the model ID to claude-opus-5-5?"
    options:
      - "Both parameters are silently ignored and the call succeeds"
      - "Only the temperature is rejected; forced tool choice still works"
      - "Only tool_choice is rejected; temperature 0 is still accepted"
      - "The request returns a 400; both need to change"
    answer: 3
    explain: "Opus 5.5 rejects forced tool_choice (any or tool) and sampling parameters. Use auto with strict tools and a prompt instruction, or structured outputs, and remove temperature."
  - q: "In OpenTelemetry's GenAI conventions, a Claude response reports input_tokens 1,000, cache_read_input_tokens 6,000 and cache_creation_input_tokens 0. What is gen_ai.usage.input_tokens?"
    options:
      - "7,000, because the convention's total includes cached tokens"
      - "1,000, because only uncached tokens count as input in the convention"
      - "6,000, because cache reads replace the uncached input"
      - "It is left unset whenever caching was used on the call"
    answer: 0
    explain: "The convention's input total includes cache reads and writes, which are also reported in their own attributes. Claude's input_tokens field counts only uncached tokens."
---

Twelve questions on serving, rate limits, embeddings, fine-tuning, observability and model migration. You need 10 correct to pass.
