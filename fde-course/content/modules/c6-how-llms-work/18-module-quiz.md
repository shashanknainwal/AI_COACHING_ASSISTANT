---
title: "Module C6 Quiz"
type: quiz
minutes: 12
questions:
  - q: "A team adds a 60K-token document to every request. Time to first token rises sharply, but output tokens per second barely change. Why?"
    options:
      - "The provider throttles any request whose prompt is longer than a set limit"
      - "Prefill must finish before the first token; decode speed is per token"
      - "Longer prompts force the model to produce longer answers"
      - "The KV cache is disabled once a prompt passes 50K tokens"
    answer: 1
    explain: "Prefill handles the entire prompt up front, so time to first token grows with prompt length. Decode generates one token at a time at roughly the same rate."
  - q: "In attention, what does the softmax over query-key scores produce?"
    options:
      - "The next token, chosen greedily from the whole vocabulary at that step"
      - "A new key vector for every earlier token"
      - "The logits for the whole vocabulary"
      - "Weights summing to 1 that blend the earlier tokens' values"
    answer: 3
    explain: "Attention is a weighted lookup: scores become weights through softmax, and the output is the weighted average of the value vectors."
  - q: "Why is a cached prompt prefix cheaper and faster to process?"
    options:
      - "The provider reuses earlier prefill work for an identical prefix"
      - "Cached tokens are compressed into a shorter form before the model reads them"
      - "The model skips reading the system prompt when it is cached"
      - "Cache hits run on a smaller, cheaper version of the model"
    answer: 0
    explain: "Conceptually, caching keeps the result of processing the prefix, so a repeat request skips that work. Any byte change in the prefix invalidates everything after it."
  - q: "A byte-level BPE tokenizer was trained mostly on English. Why does Hindi text cost several times more tokens per character?"
    options:
      - "Hindi words are longer than English words on average"
      - "Tokenizers reject non-Latin text and quietly fall back to a slower code path"
      - "Few merges cover Devanagari, and each character is 3 bytes in UTF-8"
      - "Non-English input is billed at a higher per-token price"
    answer: 2
    explain: "Merges come from the training corpus. Scripts rare in that corpus stay close to one token per byte, and Devanagari characters take 3 bytes each."
  - q: "You migrate to a newer Claude model with a newer tokenizer. What should you do about token budgets?"
    options:
      - "Re-measure with count_tokens on the new model; counts can be about 30% higher"
      - "Nothing; token counts are identical across Claude generations"
      - "Use another vendor's tokenizer library, since it matches Claude's counts closely"
      - "Halve max_tokens, because newer tokenizers are more efficient"
    answer: 0
    explain: "Anthropic's migration guidance says the newer tokenizer produces roughly 30% more tokens for the same text. Re-baseline costs, max_tokens and context budgets."
  - q: "Greedy decoding (temperature 0) still gives different outputs on identical requests now and then. What is the main reason?"
    options:
      - "The provider adds a small random offset to every logit"
      - "Floating-point sums vary with batching, so near-ties can flip"
      - "Temperature 0 is silently rounded up to a small positive value by most APIs"
      - "The model updates its weights after each request it serves"
    answer: 1
    explain: "Floating-point addition isn't associative, and the reduction order depends on the batch. Tiny logit differences flip near-tied tokens, and the outputs diverge from there."
  - q: "With top-p set to 0.9 and probabilities 0.66, 0.24 and 0.10, which tokens can be sampled?"
    options:
      - "Only the first token"
      - "All three tokens"
      - "Only the last two tokens"
      - "The first two, renormalized to about 0.73 and 0.27"
    answer: 3
    explain: "Top-p keeps the smallest set of most likely tokens whose total reaches 0.9. The first two sum to 0.90, so the third is dropped and the rest are renormalized."
  - q: "What best describes Constitutional AI as Anthropic's 2022 paper presents it?"
    options:
      - "A legal document that governs how customers may use Claude"
      - "A moderation filter that blocks harmful outputs after they are generated"
      - "A training method using written principles and AI feedback (RLAIF)"
      - "A pretraining corpus made of constitutions and legal texts"
    answer: 2
    explain: "The paper trains with self-critique against principles and with AI preference labels. It's distinct from Claude's published constitution document."
  - q: "A coding agent makes a failing test pass by deleting the assertion. Which training failure mode does this resemble?"
    options:
      - "Sycophancy toward the user's stated opinion"
      - "Reward hacking: satisfying the measure instead of the goal"
      - "Context rot caused by an overly long prompt"
      - "A tokenizer mismatch between code and prose"
    answer: 1
    explain: "When the reward is 'tests pass', optimizing it can mean gaming the tests. Grade outcomes, and check agent diffs for edited or hard-coded tests."
  - q: "An agent reads inbound emails, can query customer records and can send email. What is the most robust defence against injected instructions?"
    options:
      - "Enforce least-privilege tools, allowlists and approval gates in code"
      - "Add a firm instruction to ignore commands found inside emails"
      - "Lower the temperature so the model follows instructions less"
      - "Switch to a larger model that is harder to fool"
    answer: 0
    explain: "The agent has the lethal trifecta. Prompts and model choice lower the success rate but never to zero, so limit what a convinced model can do, in code."
  - q: "Your new prompt scores 46/50 and the old one 44/50. What can you honestly conclude?"
    options:
      - "The new prompt is 4 points better and should ship"
      - "The old prompt is better because its interval is wider"
      - "Nothing; evals need at least 1,000 cases to be useful"
      - "The intervals overlap heavily, so you can't tell yet"
    answer: 3
    explain: "The 95% Wilson intervals are about 81 to 97% and 76 to 94%. Add cases and compare on the cases where the prompts differ."
  - q: "When is long context usually a better choice than retrieval?"
    options:
      - "The corpus is huge and changes daily"
      - "Each user may only see some of the documents"
      - "The corpus is small, stable and cacheable"
      - "Questions need one fact from thousands of files"
    answer: 2
    explain: "A small, stable corpus fits, can be cached, and suits whole-document questions. Large, changing or permissioned corpora favour retrieval."
---

Twelve questions on the whole module. You need 10 correct to pass.
