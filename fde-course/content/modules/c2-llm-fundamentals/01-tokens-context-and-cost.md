---
title: Tokens, Context Windows and What They Cost
type: reading
minutes: 26
---

> **By the end of this lesson** you'll be able to explain what a token is, why input and output are priced differently, why a big context window is not free memory, and run a back-of-envelope cost estimate out loud in a design round.

## How this comes up in an interview

Applied AI loops lean on system design, and candidates report that the design round is often about LLM systems (Reported, for both Anthropic and OpenAI applied roles). In those rounds, cost and scale questions are a natural follow-up to any design: "How much would this cost per month?" or "What happens to your bill if traffic grows 10x?"

You don't need exact numbers. You need a method you can run in your head, say clearly, and correct when the interviewer changes an assumption. This lesson gives you that method. The practice questions below are original, written in the style of these rounds, not real questions from any lab.

## Tokens, not words

Models read and write **tokens**: chunks of text produced by a tokenizer. A token can be a whole word, part of a word, punctuation or whitespace. Three things to say precisely:

- **Billing and limits are in tokens.** Prices are quoted per million tokens. Context windows and `max_tokens` are token counts.
- **Token counts are model-specific.** Different model generations use different tokenizers. The same prompt can produce a different count on a newer model, so re-measure when you migrate. A concrete case: the tokenizer used by the Sonnet 5 line (Sonnet 5 and 5.5) counts the same text as about 30% more tokens than Sonnet 4.6 did, and Haiku 5.5's newer tokenizer does the same against Haiku 4.5. A migration can raise your token count, and so your bill and your context use, before you change a single prompt.
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

The Haiku 5.5 price applies to prompts up to 100K tokens; longer prompts are priced higher. Claude is also sold through Claude Platform on AWS, Amazon Bedrock, Google Vertex AI and Microsoft Foundry; Bedrock and Vertex AI publish their own pricing. Prices change, so in an interview say "at current list prices" and show your arithmetic, not just a total.

Architects get asked about data residency, and it changes the price:

- **On the Claude API** (and Claude Platform on AWS), setting `inference_geo: "us"` to keep inference in the US applies a **1.1x multiplier** to every token category on Claude 4.6 and later models. The default, `"global"`, is standard price.
- **On Bedrock and Google Cloud**, regional and multi-region endpoints carry a **10% premium** over global endpoints for Claude 4.5 models and later.

So "the customer needs US-only processing" is roughly a 10% line on the bill. Say it before the customer's finance team finds it. (Source: Anthropic's [pricing page](https://platform.claude.com/docs/en/about-claude/pricing), checked 2026-10-10.)

Two consequences worth saying out loud:

- **Long outputs are expensive.** A task that writes a 2,000-token report costs more in output than one that reads a 10,000-token document and returns a label.
- **Thinking is output.** When the model reasons before answering, those tokens are billed. Lesson 3 covers how to control that.

## A context window is not free memory

The context window is the maximum number of tokens one request can hold: input plus output. A 1M-token window is a limit, not a store. Three points interviewers like to probe:

1. **The API is stateless.** The model does not remember your last request. In a chat, your code resends the whole conversation every turn. Turn 20 pays for turns 1 to 19 again as input.
2. **Every token you send is billed.** Stuffing a whole knowledge base into every request "because it fits" multiplies your input bill by however much you stuffed in.
3. **More input means more work before the answer starts.** Long prompts take longer to process, so time to first token goes up. Retrieval, summarization and caching exist partly to keep the per-request context small and stable.
4. **More input can mean worse answers.** This is the one candidates forget. As the context grows, a model's ability to find and use a specific fact in it tends to drop. Anthropic's own [context-engineering guidance](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) calls this **context rot** and describes it as a gradual decline across all models, not a cliff. A well-known 2023 research paper, [Lost in the Middle](https://arxiv.org/abs/2307.03172), found that the models it tested used information at the start and end of a long context better than information buried in the middle. Newer models handle long context better, so treat the exact shape as model-specific, but the direction holds: a fact surrounded by 400K tokens of noise is easier to miss than the same fact in a 5K-token prompt.

A strong answer gives the quality reason as well as the cost reason: "It fits in the window, but we'd be paying for 400K tokens on every call, waiting for them, and asking the model to find one clause in a haystack. I'd retrieve the 5–10 relevant chunks instead, put them close to the question, and cache the stable system prompt. Then I'd run an eval on both setups to check retrieval doesn't miss things the long-context version caught."

## The estimate, step by step

Use the same four steps every time:

1. **Tokens per request.** Input (system + tools + history + documents + question) and output (answer + any thinking).
2. **Cost per request.** `input_tokens × input_price / 1,000,000 + output_tokens × output_price / 1,000,000`.
3. **Volume.** Requests per day × days per month.
4. **Sanity check and levers.** Is the total plausible for the business value? What would you change first: caching, a smaller model, shorter outputs, batching?

## Worked example: a ticket summarizer

An interviewer says: "Support agents get a one-paragraph summary of each ticket. 100,000 tickets a day. Estimate the monthly model cost."

Assume 3,000 input tokens (instructions plus the ticket thread) and 500 output tokens per request. **Assume you set `output_config.effort` to `"low"`**, so thinking stays short and the 500 output tokens include it.

| Model | Input cost | Output cost | Per request | Per month (100K/day × 30) |
|---|---:|---:|---:|---:|
| Opus 5.5 | 3,000 × $4 / 1M = $0.012 | 500 × $20 / 1M = $0.010 | $0.022 | $66,000 |
| Sonnet 5.5 | 3,000 × $2 / 1M = $0.006 | 500 × $10 / 1M = $0.005 | $0.011 | $33,000 |
| Haiku 5.5 | 3,000 × $0.10 / 1M = $0.0003 | 500 × $0.50 / 1M = $0.00025 | $0.00055 | $1,650 |

Now say what the numbers mean, not just what they are:

- "A 40x spread between the largest and smallest model. Summaries are a well-defined task, so I'd run an eval on a few hundred real tickets and pick the cheapest model that meets the quality bar."
- "If the instructions are a large, fixed block, prompt caching cuts the input side further (Lesson 6)."
- "Nobody needs the summary in under a second if it's generated when the ticket closes. If it can wait, the Batch API charges 50% of the standard price."

**The thinking line.** Current models think by default, and thinking is billed as output. If you leave effort at the default (`medium` on Opus 5.5 and Haiku 5.5, `high` on Sonnet 5.5), output per request can easily be two or three times the visible summary. At 1,500 output tokens instead of 500, the Sonnet 5.5 row becomes 3,000 × $2/M + 1,500 × $10/M = $0.021 per request, or $63,000 a month: nearly double. That's why you set effort explicitly and measure `usage.output_tokens` on real traffic.

Then invite the follow-up: "Want me to rerun it with effort at the default, or with a longer output?" That shows you know which assumptions drive the total.

## Practice (say it out loud)

Original practice prompts in the style of a design round. Answer out loud first, with a timer running (aim for two to three minutes), then open the model answer and score yourself against the checklist.

**1.** "A legal team wants to ask questions over a 300-page contract. Each question sends the whole contract. Walk me through the cost of 2,000 questions a day, and what you'd change."

<details>
<summary>Model answer and self-check</summary>

"First the assumptions, out loud. A dense contract page is very roughly 500 tokens, so call the contract 150K tokens. I'd confirm that with the token-counting endpoint on the real file. Say a 200-token question and a 500-token answer, on Sonnet 5.5 at effort `low`.

Input: 150K × 2,000 = 300M tokens a day. At $2 per million that's about $600 a day, or $18,000 a month, for re-sending the same contract. Output is 1M tokens a day, about $10. So input is 98% of the bill.

What I'd change, in order:

1. **Cache the contract.** It's identical on every question, so put it first and mark it with `cache_control`. On Sonnet 5.5 a cache read is $0.10 per million, so 300M cached tokens is about $30 a day, plus a write each time the cache goes cold. That's roughly a 95% cut, and time to first token drops too.
2. **Ask whether every question needs the whole contract.** Retrieval of the 5–10 relevant clauses is cheaper still and helps quality, because of context rot: one clause in 150K tokens is easier to miss. I'd run an eval comparing the two on real questions before choosing.
3. **Set effort explicitly** and measure output tokens, because thinking counts as output.

Risks: if there are many contracts, each one has its own cache entry, so the saving depends on how many questions hit the same contract within the TTL."

Score yourself:
- [ ] Stated assumptions (tokens per page, question and answer size, model, effort) before any arithmetic.
- [ ] Got the input side within a factor of two and noticed it dominates.
- [ ] Named caching with a model-specific number, and retrieval as an alternative.
- [ ] Gave a quality reason (context rot), not only a cost reason.
- [ ] Mentioned measuring: the token-counting endpoint, an eval, or `usage`.

</details>

**2.** "Your chat assistant's bill doubled with no change in traffic. What would you look at first?"

<details>
<summary>Model answer and self-check</summary>

"Traffic is flat, so tokens per request or price per token changed. I'd pull the `usage` block for a sample of requests before and after the jump and compare four numbers per route.

1. **`cache_read_input_tokens`.** If it fell to zero, someone broke the cached prefix: a timestamp in the system prompt, a tool list that varies, unsorted JSON. This is the most common silent doubling.
2. **`input_tokens` per request.** If it grew, conversations got longer, someone added documents or tool output to the context, or we migrated to a model whose tokenizer counts more tokens.
3. **`output_tokens`.** If it grew, check effort and thinking. Changing model can change the default effort: Sonnet 5.5 defaults to `high`, Opus 5.5 and Haiku 5.5 to `medium`. A prompt change that asks for longer answers does it too.
4. **Request count per conversation.** Retries on errors, or an agent loop taking more turns, multiply cost without more users.

Then the price side: did the model change, or did someone turn on `inference_geo: "us"` (1.1x)? Once I find the cause, I'd add a monitor on these usage fields so it can't happen silently again."

Score yourself:
- [ ] Started from data (usage fields, before and after), not guesses.
- [ ] Checked caching first or near the top.
- [ ] Covered input growth, output and thinking growth, and extra requests.
- [ ] Mentioned a price-side cause (model change, data residency).
- [ ] Ended with a standing check, not just a one-off fix.

</details>

> **Key takeaways**
>
> - Billing, limits and context are all in tokens, and token counts depend on the model. Measure with the token-counting endpoint.
> - Output costs more than input (5x on current Claude models), and thinking counts as output.
> - The context window is a per-request limit, not memory. Chat apps resend history every turn, and every token is billed, adds latency and can lower answer quality (context rot).
> - Data residency costs extra: 1.1x for `inference_geo: "us"` on the Claude API, a 10% premium for regional endpoints on Bedrock and Google Cloud.
> - Estimate with four steps: tokens per request, cost per request, volume, then levers. Say your assumptions out loud.
