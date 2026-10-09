---
title: "Module E6 Quiz"
type: quiz
minutes: 10
questions:
  - q: "What should you produce in the first five minutes of an LLM system design round?"
    options:
      - "A complete component diagram"
      - "A model choice and the system prompt"
      - "Clarifying questions and written numbers: users, volume, latency target, quality bar, scope"
      - "A list of vector databases you've used"
    answer: 2
    explain: "Scope and numbers come first. Every later decision should point back to them, and interviewers listen for the questions that change the design."
  - q: "The prompt says 'p95 under 2 seconds'. What is the strongest first move?"
    options:
      - "Ask or state whether 2 seconds means first streamed token or the complete answer, and where it's measured"
      - "Pick the fastest model and move on"
      - "Promise to cache every answer"
      - "Say latency can be tuned after launch"
    answer: 0
    explain: "First token and full answer lead to very different designs. Pin the definition, then build a per-step budget that adds up to it."
  - q: "In an internal knowledge assistant, where should document permissions be enforced?"
    options:
      - "In the system prompt, by telling the model which documents the user may see"
      - "After generation, by scanning the answer for restricted content"
      - "Only in the user interface"
      - "At retrieval time, filtering chunks by the user's groups before ranking"
    answer: 3
    explain: "If a restricted chunk reaches the model, the model has already read it. Filter in the search query so it is never retrieved, ranked or shown."
  - q: "An answer step uses 2,500 cached tokens, 4,900 fresh input tokens and 350 output tokens on Claude Sonnet 5.5 ($2 / $10 per million, cache reads $0.10). Roughly what does one question cost?"
    options:
      - "About $0.0014"
      - "About $0.014"
      - "About $0.14"
      - "About $1.40"
    answer: 1
    explain: "2,500 x $0.10/M = $0.00025; 4,900 x $2/M = $0.0098; 350 x $10/M = $0.0035. Total about $0.0136, so about $0.014."
  - q: "Your prompt puts today's date and the user's name at the very start, before a 3,000-token block of fixed rules. What happens to prompt caching?"
    options:
      - "Nothing; caching ignores small changes"
      - "Only the date and name are re-processed"
      - "The cache misses on the fixed rules too, because caching is a prefix match and the changed bytes come first"
      - "The API reorders the prompt automatically"
    answer: 2
    explain: "Caching matches the prefix in order: tools, system, messages. Any change early invalidates everything after it, so put stable content first."
  - q: "Two prompt versions score 86% and 85% on a 300-case golden set. What's the right reading?"
    options:
      - "Version A is better; ship it"
      - "The difference is within noise at this size (about plus or minus 4 points); compare on the same cases and look at which ones flipped"
      - "The golden set is broken"
      - "Rerun until A wins by more"
    answer: 1
    explain: "At 85% on 300 cases, the standard error is about 2 points, so the 95% interval is roughly plus or minus 4. A one-point gap is not evidence of a real difference."
  - q: "How should you decide whether to trust an LLM judge in your eval suite?"
    options:
      - "Use the most capable model and assume it's right"
      - "Ask the judge to rate its own confidence"
      - "Trust it once it gives consistent scores on repeated runs"
      - "Compare its verdicts with human labels on a sample and require an agreement threshold before relying on it"
    answer: 3
    explain: "A judge is a measuring instrument. Check it against people, and re-check whenever the judge prompt or model changes."
  - q: "Which work is the best fit for the Message Batches API at half price?"
    options:
      - "Nightly eval runs that nobody waits on in real time"
      - "Live chat answers with a 2-second target"
      - "Streaming responses to a browser"
      - "A tool loop that must react to each tool result immediately"
    answer: 0
    explain: "Batches are asynchronous and single-shot. Evals, backfills and scheduled jobs fit; anything interactive or mid-tool-loop doesn't."
  - q: "A candidate opens with 'We'll fine-tune a model on the company's documents.' What would a strong candidate do instead?"
    options:
      - "Fine-tune a smaller model to save cost"
      - "Start with retrieval, prompting and evals, and name the eval result that would justify fine-tuning later"
      - "Avoid mentioning fine-tuning at all"
      - "Train an embedding model from scratch first"
    answer: 1
    explain: "Fine-tuning as a first move skips the cheaper, easier-to-update options. Strong answers say what evidence would make it worth it."
  - q: "Which statement about LLM system design rounds can this course label as Reported?"
    options:
      - "Anthropic publishes its design questions in advance"
      - "Every lab uses the same design prompt"
      - "Perplexity onsites include AI system design covering retrieval, serving under latency limits and caching"
      - "Design rounds at frontier labs never discuss cost"
    answer: 2
    explain: "Several candidate accounts describe Perplexity's AI system design round this way. No lab publishes its design questions, and practice prompts in this course are original."
---

Ten questions on the design framework, the worked example and the three design prompts. You need 8 correct to pass.
