---
title: "Vendor-Neutral Vocabulary: Speak Every Lab's Language"
type: reading
minutes: 12
---

> **By the end of this lesson** you'll be able to translate between vendors' names for the same idea (function calling and tool use, Responses-style and Messages-style APIs, structured outputs, logprobs, seeds, embeddings) and answer a fundamentals question without tying it to one provider.

## Why it matters

Interviewers at different labs use their own vocabulary, and customers often run more than one provider. If an OpenAI or Perplexity interviewer asks about "function calling" and you answer only in Claude terms, you sound narrow. If an Anthropic interviewer asks about tool use and you know the general pattern, you sound like someone who has shipped. Candidates report vendor-neutral fundamentals questions across these labs' applied loops (**Anecdotal**).

A rule for this lesson: the Claude column is checked against Anthropic's documentation. The other columns describe general patterns, and APIs change often. **Check each vendor's current docs** before relying on a specific parameter name.

## The core ideas, named

| Idea | General description | On Claude (Messages API) | Elsewhere (check each vendor's docs) |
|---|---|---|---|
| **Letting the model call your code** | The model returns a structured request to run a function; your code runs it and sends back the result | **Tool use**: `tools` with `input_schema`; the response has `stop_reason: "tool_use"` and `tool_use` blocks; you reply with `tool_result` blocks | Often called **function calling**; same loop: model proposes, your code executes, you return the result |
| **Request style** | How conversation state is managed | **Messages-style**: stateless; you send the full `messages` list (with `system` separate) every time | Some vendors offer a **Responses-style** API that can keep conversation state server-side and reference a previous response, alongside a chat-style endpoint. The trade-off: less to resend versus less control over exactly what's in context |
| **Guaranteed output shape** | The output must match a JSON schema | **Structured outputs**: `output_config.format` with a JSON schema; `strict: true` on tools for schema-exact arguments | Most major vendors have a JSON-schema mode under a similar name |
| **Reasoning control** | How much the model thinks before answering | Adaptive thinking; **`effort`** (`low` to `max`) in `output_config`; thinking billed as output | Vendors expose reasoning effort or budget controls under different names |
| **Sampling knobs** | Temperature, top-p, top-k | Rejected on the newest models (on Claude Opus 5.5 all three return a 400) | Commonly supported, often with model-specific limits on reasoning models |
| **Logprobs** | Per-token log probabilities | Not returned by the Messages API at the time of writing | Some vendors return them for some models |
| **Seeds** | Fix the sampler's randomness for reproducibility | No seed parameter | Some vendors offer a best-effort seed (lesson 05 explains why it's best-effort) |
| **Embeddings** | Text to vectors for retrieval | Not offered by Anthropic; its docs point to third-party embedding providers | Several LLM vendors sell embedding models; specialist providers exist too |
| **Prompt caching** | Reuse prefill work for a repeated prefix | Opt-in: top-level `cache_control` or block breakpoints; reads 0.05x input on Opus 5.5 and Sonnet 5.5, 0.1x on most other models | Some vendors cache automatically, some opt-in; discounts differ |
| **Batch processing** | Cheaper asynchronous jobs | **Message Batches**: 50% of standard price; not available on Bedrock, Vertex AI or Foundry | Most vendors offer a batch endpoint at a discount |
| **Grounded web answers** | Answers with live search and citations | Server-side web search tool (check the current docs for platform availability) | Perplexity's API is built around search-grounded answers with citations; others offer search tools |
| **Where you buy it** | Hosting and billing | Anthropic API, Claude Platform on AWS, Amazon Bedrock, Google Vertex AI, Microsoft Foundry | Most vendors sell direct and through one or more clouds |

## Answering vendor-neutrally

A pattern that works for most "how does X work" questions:

1. **Describe the mechanism generally.** "The model can't run code. It emits a structured request naming a function and arguments; my code validates and runs it, then returns the result as the next message."
2. **Name the vendor terms you know, accurately.** "Anthropic calls it tool use, with `tool_use` and `tool_result` blocks. Other vendors call it function calling; the loop is the same."
3. **Say what you'd check.** "The parameter names and whether parallel calls are supported differ, so I'd check the docs for the model we pick."

Don't invent a parameter name to sound fluent. "I'd check their docs for the exact field" is a strong answer; a confident wrong field name is a weak one.

## Practice (say it out loud)

- "Explain function calling to me. Now explain what changes if the API keeps conversation state for you."
- "A customer wants to switch providers for cost. What breaks in their code, and what doesn't?" (Hint: message format, tool schemas, structured-output syntax, sampling parameters, caching behaviour, token counts.)

> **Key takeaways**
>
> - Function calling and tool use are the same loop: the model proposes a call, your code runs it, you return the result.
> - Messages-style APIs are stateless; Responses-style APIs can hold state server-side. Know the trade-off.
> - Structured outputs, reasoning effort, caching and batch exist across vendors under different names; logprobs, seeds and sampling knobs vary most.
> - Describe the mechanism, name the terms you know accurately, and say you'd check each vendor's docs for the rest.
