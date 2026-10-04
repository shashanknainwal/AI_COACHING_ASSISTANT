---
title: "Module 6 Quiz"
type: quiz
minutes: 10
questions:
  - q: "You're starting a new Claude feature for a customer. Which approach to model choice is best?"
    options:
      - "Start with the cheapest model and upgrade if users complain"
      - "Start with the most capable model, build an evaluation, then try lower effort or cheaper models and keep them only if quality holds"
      - "Always use the newest model at max effort"
      - "Let each developer pick"
    answer: 1
    explain: "Get it working well first, measure, then step down deliberately."
  - q: "What should you append to the conversation history after an assistant turn?"
    options:
      - "Only the text of the reply"
      - "The assistant's full content list, including thinking blocks, unchanged"
      - "A summary of the reply"
      - "Nothing; the API remembers"
    answer: 1
    explain: "The API is stateless. Append response.content as-is, and never edit earlier turns."
  - q: "A refusal comes back during a chat. What's the cleanest way to keep the conversation history valid?"
    options:
      - "Append the refusal as an assistant turn with empty text"
      - "Remove the refused user turn and show the user a polite message"
      - "Retry the same request in a loop"
      - "Delete the whole history"
    answer: 1
    explain: "Keep a clean user/assistant alternation and handle refusals as a normal outcome."
  - q: "Why wrap customer text in tags like <ticket> and escape < and > inside it?"
    options:
      - "It makes responses faster"
      - "It separates data from instructions and stops customers from closing the tag to inject fake instructions"
      - "Claude can't read plain text"
      - "It's required by the API"
    answer: 1
    explain: "Tagging plus escaping is one layer of prompt-injection defense."
  - q: "Which layer limits the damage of a successful prompt injection in a ticket classifier?"
    options:
      - "A longer system prompt"
      - "Structured outputs with an enum of categories, plus routing risky categories to humans"
      - "Higher effort"
      - "Using a smaller model"
    answer: 1
    explain: "If the output can only be one of a few categories, an injection can't make the system take other actions."
  - q: "Why stream responses?"
    options:
      - "It makes generation cheaper"
      - "Users see text sooner, and long outputs avoid request timeouts"
      - "It's required for structured outputs"
      - "It disables thinking"
    answer: 1
    explain: "Streaming improves perceived speed and makes large max_tokens practical."
  - q: "After iterating stream.text_stream, how do you check whether the output was truncated?"
    options:
      - "Count the characters"
      - "Call stream.get_final_message() and check stop_reason"
      - "Look for a period at the end"
      - "You can't when streaming"
    answer: 1
    explain: "The final message has stop_reason and usage, exactly like create()."
  - q: "The SDK client is created with max_retries=3. A request gets four 429 responses in a row. What happens?"
    options:
      - "The SDK retries forever"
      - "The SDK makes 4 attempts (waiting between them), then raises RateLimitError"
      - "It returns an empty message"
      - "It switches models automatically"
    answer: 1
    explain: "The SDK retries with backoff and honors retry-after, then raises the typed error."
  - q: "Why must except anthropic.RateLimitError come before except anthropic.APIStatusError?"
    options:
      - "Alphabetical order"
      - "RateLimitError is a subclass of APIStatusError, so the general handler would catch it first"
      - "RateLimitError is more common"
      - "It doesn't matter"
    answer: 1
    explain: "Catch most specific first, and never match on error message text."
  - q: "You added cache_control to a long system prompt, but cache_read_input_tokens stays at 0 on every request. Most likely cause?"
    options:
      - "Caching is broken"
      - "Something in the prefix changes between requests, like a timestamp at the top of the system prompt"
      - "The output is too long"
      - "You need higher effort"
    answer: 1
    explain: "Caching is a prefix match: any change before the cache point means a miss. Keep volatile content last."
  - q: "On Claude Opus 5.5, cache reads cost $0.20 per million tokens versus $4.00 for uncached input. A 10,000-token system prompt is reused on 1,000 requests. What happens to its cost after the first request?"
    options:
      - "It stays the same"
      - "Each later request pays about 1/20 of the uncached price for that prefix"
      - "It doubles"
      - "It becomes free"
    answer: 1
    explain: "The first request writes the cache (1.25x); later hits read it at a fraction of the price."
  - q: "Your router sends a classification to Claude Haiku 4.5 with output_config={'effort': 'low'} and gets a 400. Why?"
    options:
      - "Haiku is overloaded"
      - "The effort parameter isn't supported on that model; build parameters per model"
      - "max_tokens is too low"
      - "Haiku requires streaming"
    answer: 1
    explain: "Models aren't interchangeable: supported parameters and context windows differ."
  - q: "Opus is overloaded after the SDK's retries. When is falling back to Sonnet the right call?"
    options:
      - "Always"
      - "Never"
      - "Decide per task: often fine for chat; for some tasks (like compliance analysis) queueing may be better. Record which model served the request"
      - "Only on weekends"
    answer: 2
    explain: "Fallbacks trade quality for availability; make that choice deliberately per task."
---

Thirteen questions on the Messages API, production prompting, streaming, errors and caching, and model routing. You need **11 out of 13** to pass. You can retry as many times as you like.
