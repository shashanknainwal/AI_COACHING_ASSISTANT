---
title: Module 6 Quiz
type: quiz
minutes: 10
questions:
- q: "You're starting a new Claude feature for a customer. Which approach to model choice is best?"
  options:
  - Start with the cheapest model and upgrade if users complain
  - "Start with the most capable model, build an evaluation, then try lower effort or cheaper models and keep them only if quality holds"
  - Always use the newest model at max effort
  - Let each developer pick
  answer: 1
  explain: "Get it working well first, measure, then step down deliberately."
- q: What should you append to the conversation history after an assistant turn?
  options:
  - "The assistant's full content list, including thinking blocks, unchanged"
  - Only the text of the reply; thinking blocks are for display and can be dropped
  - A summary of the reply
  - Nothing; the API remembers
  answer: 0
  explain: "The API is stateless. Append response.content as-is, and never edit earlier turns."
- q: "A refusal comes back during a chat. What's the cleanest way to keep the conversation history valid?"
  options:
  - Append the refusal as an assistant turn with empty text so the roles still alternate
  - Retry the same request in a loop
  - Delete the whole history
  - Remove the refused user turn and show the user a polite message
  answer: 3
  explain: Keep a clean user/assistant alternation and handle refusals as a normal outcome.
- q: "Why wrap customer text in tags like <ticket> and escape < and > inside it?"
  options:
  - It makes responses faster
  - "Claude can't read plain text"
  - It separates data from instructions and stops customers from closing the tag to inject fake instructions
  - "It's required by the API"
  answer: 2
  explain: Tagging plus escaping is one layer of prompt-injection defense.
- q: Which layer limits the damage of a successful prompt injection in a ticket classifier?
  options:
  - "Structured outputs with an enum of categories, plus routing risky categories to humans"
  - A longer system prompt
  - Higher effort
  - Using a smaller model
  answer: 0
  explain: "If the output can only be one of a few categories, an injection can't make the system take other actions."
- q: Why stream responses?
  options:
  - It makes generation cheaper
  - "Users see text sooner, and long outputs avoid request timeouts"
  - "It's required for structured outputs and for any request that uses tools"
  - It disables thinking
  answer: 1
  explain: Streaming improves perceived speed and makes large max_tokens practical.
- q: "After iterating stream.text_stream, how do you check whether the output was truncated?"
  options:
  - Count the characters
  - Look for a period at the end
  - "You can't: streamed responses don't report a stop_reason until you call create()"
  - Call stream.get_final_message() and check stop_reason
  answer: 3
  explain: "The final message has stop_reason and usage, exactly like create()."
- q: The SDK client is created with max_retries=3. A request gets four 429 responses in a row. What happens?
  options:
  - The SDK retries forever
  - It returns an empty message
  - "The SDK makes 4 attempts (waiting between them), then raises RateLimitError"
  - It falls back to a less busy model automatically after the third 429 in a row
  answer: 2
  explain: "The SDK retries with backoff and honors retry-after, then raises the typed error."
- q: Why must except anthropic.RateLimitError come before except anthropic.APIStatusError?
  options:
  - "RateLimitError is a subclass of APIStatusError, so the general handler would catch it first"
  - Alphabetical order
  - RateLimitError is more common
  - "It doesn't matter"
  answer: 0
  explain: "Catch most specific first, and never match on error message text."
- q: "You added cache_control to a long system prompt, but cache_read_input_tokens stays at 0 on every request. Most likely cause?"
  options:
  - Caching is broken
  - The output is too long
  - You need higher effort
  - "Something in the prefix changes between requests, like a timestamp at the top of the system prompt"
  answer: 3
  explain: "Caching is a prefix match: any change before the cache point means a miss. Keep volatile content last."
- q: "On Claude Opus 5.5, cache reads cost $0.20 per million tokens versus $4.00 for uncached input. A 10,000-token system prompt is reused on 1,000 requests. What happens to its cost after the first request?"
  options:
  - It stays the same
  - Each later request pays about 1/20 of the uncached price for that prefix
  - It doubles
  - "It becomes free, because cached tokens aren't billed after the first write"
  answer: 1
  explain: The first request writes the cache (1.25x); later hits read it at a fraction of the price.
- q: Your router sends high-volume ticket classification to Claude Haiku 5.5. How do you keep its thinking spend under control?
  options:
  - "Leave effort out, since Haiku 5.5 doesn't think unless you ask it to"
  - "Set temperature to 0, which turns thinking off on smaller models like Haiku 5.5"
  - "Set output_config={'effort': 'low'} and leave max_tokens room for thinking"
  - Lower max_tokens to 64 so the model has no room to think at all
  answer: 2
  explain: "Haiku 5.5 thinks by default (effort defaults to medium) and supports effort, so set it explicitly. Thinking is billed as output and counts toward max_tokens. Only the legacy Haiku 4.5 rejects the effort parameter."
- q: "Opus is overloaded after the SDK's retries. When is falling back to Sonnet the right call?"
  options:
  - "Decide per task: fine for chat, maybe not for compliance; log the serving model"
  - "Always, since any answer beats an error message for the user"
  - "Never, because answers from a different model aren't comparable"
  - "Only when the fallback model scored within a point of Opus on last month's evals"
  answer: 0
  explain: Fallbacks trade quality for availability; make that choice deliberately per task.
- q: "A support chat on Claude Opus 5.5 has grown to 80 turns and is getting slow and expensive. What's the safest way to stop it growing forever?"
  options:
  - "Drop the oldest turns and resend the newer ones unchanged, thinking blocks included"
  - "Compact: get a summary, then start a fresh history whose first turn carries it"
  - Rewrite the system prompt each turn so it holds a running summary
  - Raise max_tokens so the model can read the longer history
  answer: 1
  explain: "Opus 5.5 binds each thinking block to everything before it, so trimming or rewriting earlier turns breaks that binding (a 400 or lost reasoning) and misses the cache. Server-side compaction, context editing, or a summary in a fresh history keeps the history append-only."
---

Thirteen questions on the Messages API, production prompting, streaming, errors and caching, and model routing. You need **11 out of 13** to pass. You can retry as many times as you like.
