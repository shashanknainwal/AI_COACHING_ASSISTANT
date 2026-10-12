---
title: "Module E6 Quiz"
type: quiz
minutes: 14
questions:
  - q: "What should you produce in the first five minutes of an LLM system design round?"
    options:
      - "A complete component diagram with every service labelled"
      - "A model choice for each step and the full system prompt"
      - "Clarifying questions and numbers written on the board"
      - "A list of the vector databases you have used before"
    answer: 2
    explain: "Scope and numbers come first: users, volume, latency target, quality bar, scope. Every later decision should point back to them, and interviewers listen for the questions that change the design."
  - q: "The prompt says 'p95 under 2 seconds'. What is the strongest first move?"
    options:
      - "Pin down whether it means first token or full answer"
      - "Pick the fastest model available and move straight on"
      - "Promise to cache every answer so latency stops mattering"
      - "Say that latency can be tuned later, after the launch"
    answer: 0
    explain: "First token and full answer lead to very different designs. Pin the definition and where it's measured, then build a per-step budget that adds up to it."
  - q: "In an internal knowledge assistant, where should document permissions be enforced?"
    options:
      - "In the system prompt, listing the documents the user may see"
      - "After generation, by scanning answers for restricted content"
      - "Only in the user interface, by hiding restricted source links"
      - "At retrieval, filtering chunks by the user's groups"
    answer: 3
    explain: "If a restricted chunk reaches the model, the model has already read it. Filter in the search query so it is never retrieved, ranked or shown."
  - q: "An answer step on Claude Sonnet 5.5 at effort low uses 2,500 cached tokens, 4,900 fresh input tokens, 350 answer tokens and about 300 thinking tokens ($2 / $10 per million, cache reads $0.10). Roughly what does one question cost?"
    options:
      - "About $0.0017"
      - "About $0.017"
      - "About $0.17"
      - "About $1.70"
    answer: 1
    explain: "2,500 x $0.10/M = $0.00025; 4,900 x $2/M = $0.0098; (350 + 300) x $10/M = $0.0065. Total about $0.0166. Thinking is billed as output, which is why the effort setting belongs in the estimate."
  - q: "Your prompt puts today's date and the user's name at the very start, before a 3,000-token block of fixed rules. What happens to prompt caching?"
    options:
      - "Nothing, because caching ignores small changes in a prompt"
      - "Only the date and the name are re-processed on each call"
      - "The fixed rules miss too, since the changed bytes come first"
      - "The API reorders the prompt so the stable part comes first"
    answer: 2
    explain: "Caching matches the prefix in order: tools, system, messages. Any change early invalidates everything after it, so put stable content first (and opt in with cache_control)."
  - q: "Two prompt versions score 86% and 85% on a 300-case golden set. What's the right reading?"
    options:
      - "Version A is better by a point, so it should ship"
      - "It's within noise; compare case by case and look at flips"
      - "The golden set must be broken if the scores are so close"
      - "Rerun the suite until version A wins by a wider margin"
    answer: 1
    explain: "At 85% on 300 cases, the standard error is about 2 points, so the 95% interval is roughly plus or minus 4. A one-point gap is not evidence of a real difference."
  - q: "Your judge agrees with human labels 86% of the time on 100 cases, and humans pass 85% of answers. What should you check before trusting it?"
    options:
      - "Nothing more; 86% agreement already clears an 85% bar"
      - "Whether it gives the same scores on repeated identical runs"
      - "Whether a more capable judge model gets a higher number"
      - "Cohen's kappa and the false passes, not raw agreement"
    answer: 3
    explain: "A judge that passes everything would agree 85% of the time here with no skill. Kappa corrects for chance agreement, and false passes are the dangerous direction. On 100 cases, kappa still has a wide interval."
  - q: "Which work is the best fit for the Message Batches API at half price?"
    options:
      - "Nightly eval runs that nobody is waiting on"
      - "Live chat answers that have a 2-second target"
      - "Streaming responses straight to a user's browser"
      - "A tool loop that reacts to each tool result at once"
    answer: 0
    explain: "Batches are asynchronous and single-shot, and not available on Bedrock, Vertex or Foundry. Evals, backfills and scheduled jobs fit; anything interactive or mid-tool-loop doesn't."
  - q: "In a multi-tenant LLM gateway, how should a token bucket admit a request whose output length isn't known yet?"
    options:
      - "Admit everything and bill each team at the end of the month"
      - "Reserve worst-case tokens, then reconcile from usage"
      - "Count only input tokens, since output can't be known ahead"
      - "Reject requests whose max_tokens is above a fixed number"
    answer: 1
    explain: "Reserve against max_tokens (which covers thinking) or a calibrated estimate at admission, then refund the difference when usage arrives. Counting only input lets output-heavy teams blow through the limit."
  - q: "A team's cache hit rate falls to almost zero the day its traffic moves behind your new gateway, with no errors. Which check comes first?"
    options:
      - "Switch the team's prompt to the 1-hour cache TTL"
      - "Move the team to a model with a bigger context window"
      - "Diff the forwarded bytes and cache_control markers"
      - "Ask the team to shorten its system prompt by half"
    answer: 2
    explain: "A gateway that injects a request id or timestamp into the system prompt, reorders tools, strips cache_control or spreads one team across keys or workspaces breaks the prefix match silently. Verify with cache_read_input_tokens on two identical requests."
  - q: "A customs intake design needs typed fields and a traceable source for every value. What's a sound approach?"
    options:
      - "Citations plus output_config.format in the same request"
      - "Free-text answers parsed later with regular expressions"
      - "Typed fields with a source_page field, checked in code"
      - "OCR every page first and drop the original documents"
    answer: 2
    explain: "Citations can't be combined with structured outputs in one request. A page reference per field, validated in code against the document, keeps both the types and the trace; a second citations call is another option."
  - q: "A candidate opens with 'We'll fine-tune a model on the company's documents.' What would a strong candidate do instead?"
    options:
      - "Fine-tune a smaller model to save on cost"
      - "Train an embedding model from scratch first"
      - "Avoid mentioning fine-tuning at any point"
      - "Start with retrieval, prompts and evals"
    answer: 3
    explain: "Fine-tuning as a first move skips the cheaper, easier-to-update options. Strong answers start simple and name the eval result that would justify fine-tuning later."
---

Twelve questions on the design framework, the worked example and the design prompts. You need 10 correct to pass.
