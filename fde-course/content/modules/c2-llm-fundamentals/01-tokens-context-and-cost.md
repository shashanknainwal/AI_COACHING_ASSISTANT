---
title: Tokens, Context Windows and What They Cost
type: reading
minutes: 20
---

> **By the end of this lesson** you'll be able to explain what a token is, why input and output are priced differently, why a big context window is not free memory, and run a back-of-envelope cost estimate out loud in a design round.

## How this comes up in an interview

Applied AI loops lean on system design, and candidates report that the design round is often about LLM systems (Reported, for both Anthropic and OpenAI applied roles). In those rounds, cost and scale questions are a natural follow-up to any design: "How much would this cost per month?" or "What happens to your bill if traffic grows 10x?"

You don't need exact numbers. You need a method you can run in your head, say clearly, and correct when the interviewer changes an assumption. This lesson gives you that method. The practice questions below are original, written in the style of these rounds, not real questions from any lab.

## Tokens, not words

Models read and write **tokens**: chunks of text produced by a tokenizer. A token can be a whole word, part of a word, punctuation or whitespace. Three things to say precisely:

- **Billing and limits are in tokens.** Prices are quoted per million tokens. Context windows and `max_tokens` are token counts.
- **Token counts are model-specific.** Different model generations use different tokenizers. The same prompt can produce a different count on a newer model, so re-measure when you migrate.
- **Measure, don't guess.** The Claude API has a token-counting endpoint (`POST /v1/messages/count_tokens`) that takes the same model ID you'll use. Other vendors' tokenizer libraries give the wrong answer for Claude, often by a lot on code and non-English text.

In an interview, it's fine to use a rough words-to-tokens ratio for a quick estimate, as long as you say it's a rough ratio and that you'd confirm it with the token-counting endpoint on real data.

## Input and output are priced differently

Every request has **input tokens** (system prompt, tool definitions, the conversation so far, any documents) and **output tokens** (what the model writes back, including any thinking it does). Output costs more per token than input. On the current Claude models, output is 5x the input price.

Current list prices on the Anthropic API, in dollars per million tokens:

| Model | Input | Output | Context window |
|---|---:|---:|---|
| Claude Opus 5.5 | $4.00 | $20.00 | 1M tokens |
| Claude Sonnet 5.5 | $2.00 | $10.00 | 1M tokens |
| Claude Haiku 5.5 | $0.10 | $0.50 | 1M tokens |
| Claude Fable 5.1 | $10.00 | $50.00 | 1M tokens |

The Haiku 5.5 price applies to prompts up to 100K tokens; longer prompts are priced higher. Claude is also sold through Amazon Bedrock, Google Vertex AI and Microsoft Foundry; Bedrock and Vertex AI publish their own pricing. Prices change, so in an interview say "at current list prices" and show your arithmetic, not just a total.

Two consequences worth saying out loud:

- **Long outputs are expensive.** A task that writes a 2,000-token report costs more in output than one that reads a 10,000-token document and returns a label.
- **Thinking is output.** When the model reasons before answering, those tokens are billed. Lesson 3 covers how to control that.

## A context window is not free memory

The context window is the maximum number of tokens one request can hold: input plus output. A 1M-token window is a limit, not a store. Three points interviewers like to probe:

1. **The API is stateless.** The model does not remember your last request. In a chat, your code resends the whole conversation every turn. Turn 20 pays for turns 1 to 19 again as input.
2. **Every token you send is billed.** Stuffing a whole knowledge base into every request "because it fits" multiplies your input bill by however much you stuffed in.
3. **More input means more work before the answer starts.** Long prompts take longer to process, so time to first token goes up. Retrieval, summarization and caching exist partly to keep the per-request context small and stable.

A strong answer sounds like: "It fits in the window, but we'd be paying for 400K tokens on every call and waiting for them. I'd retrieve the 5–10 relevant chunks instead, and cache the stable system prompt."

## The estimate, step by step

Use the same four steps every time:

1. **Tokens per request.** Input (system + tools + history + documents + question) and output (answer + any thinking).
2. **Cost per request.** `input_tokens × input_price / 1,000,000 + output_tokens × output_price / 1,000,000`.
3. **Volume.** Requests per day × days per month.
4. **Sanity check and levers.** Is the total plausible for the business value? What would you change first: caching, a smaller model, shorter outputs, batching?

## Worked example: a ticket summarizer

An interviewer says: "Support agents get a one-paragraph summary of each ticket. 100,000 tickets a day. Estimate the monthly model cost."

Assume 3,000 input tokens (instructions plus the ticket thread) and 500 output tokens per request.

| Model | Input cost | Output cost | Per request | Per month (100K/day × 30) |
|---|---:|---:|---:|---:|
| Opus 5.5 | 3,000 × $4 / 1M = $0.012 | 500 × $20 / 1M = $0.010 | $0.022 | $66,000 |
| Sonnet 5.5 | 3,000 × $2 / 1M = $0.006 | 500 × $10 / 1M = $0.005 | $0.011 | $33,000 |
| Haiku 5.5 | 3,000 × $0.10 / 1M = $0.0003 | 500 × $0.50 / 1M = $0.00025 | $0.00055 | $1,650 |

Now say what the numbers mean, not just what they are:

- "A 40x spread between the largest and smallest model. Summaries are a well-defined task, so I'd run an eval on a few hundred real tickets and pick the cheapest model that meets the quality bar."
- "If the instructions are a large, fixed block, prompt caching cuts the input side further (Lesson 6)."
- "Nobody needs the summary in under a second if it's generated when the ticket closes. If it can wait, the Batch API charges 50% of the standard price."

Then invite the follow-up: "Want me to rerun it with thinking turned up, or with a longer output?" That shows you know which assumptions drive the total.

## Practice (say it out loud)

Original practice prompts in the style of a design round:

- "A legal team wants to ask questions over a 300-page contract. Each question sends the whole contract. Walk me through the cost of 2,000 questions a day, and what you'd change."
- "Your chat assistant's bill doubled with no change in traffic. What would you look at first?" (Hint: conversation length, output length, thinking, and whether a cache stopped hitting.)

> **Key takeaways**
>
> - Billing, limits and context are all in tokens, and token counts depend on the model. Measure with the token-counting endpoint.
> - Output costs more than input (5x on current Claude models), and thinking counts as output.
> - The context window is a per-request limit, not memory. Chat apps resend history every turn, and every token is billed and adds latency.
> - Estimate with four steps: tokens per request, cost per request, volume, then levers. Say your assumptions out loud.
