---
title: "The Messages API in Depth"
type: reading
minutes: 7
---

> **By the end of this lesson you will be able to:**
> - Explain the key parameters of a `messages.create` request
> - Choose a model and effort level and justify the cost
> - Build multi-turn conversations correctly
> - Read a response: content blocks, stop reasons, usage, request IDs

Priya Desai, Head of Digital Support at **Harbor Bank**, wants a Claude assistant her support agents can chat with during customer calls. Before you promise her anything on accuracy or cost, know exactly what goes in and what comes back.

## Anatomy of a request

```python
import anthropic

client = anthropic.Anthropic()          # reads ANTHROPIC_API_KEY from the environment

response = client.messages.create(
    model="claude-opus-5-5",            # which model
    max_tokens=16000,                   # hard cap on output tokens
    system="You are Harbor Bank's support assistant. ...",   # role, context, rules
    messages=[                          # the conversation so far
        {"role": "user", "content": "How do I dispute a card charge?"},
    ],
    output_config={"effort": "low"},    # how much reasoning effort to spend
)
```

Don't lowball `max_tokens`: about 16,000 for normal calls, and stream for larger values. `messages` alternate user/assistant turns, starting with `user`.

## Choosing a model

Prices per million tokens (input / output):

| Model | ID | Price | Typical use |
|---|---|---|---|
| Claude Opus 5.5 | `claude-opus-5-5` | $4 / $20 | Default: complex reasoning, agents, customer-facing work that must be right |
| Claude Sonnet 5.5 | `claude-sonnet-5-5` | $2 / $10 | High-volume production work |
| Claude Haiku 5.5 | `claude-haiku-5-5` | $0.10 / $0.50 (prompts up to 100K tokens) | Fast, cheap classification, routing, extraction |
| Claude Haiku 4.5 | `claude-haiku-4-5` | $1 / $5 | Previous Haiku, still served; no `effort` parameter, 200K context |

The method: **start with the most capable model** and get the task working against an evaluation set (Module 8); **then try lower effort, then a cheaper model**, re-running the evaluation each time; **keep the cheapest option that meets the bar**. Lower effort on the top model often matches a smaller model with fewer surprises.

## Effort and thinking

Claude Opus 5.5 always thinks before answering (adaptive thinking); it can't be turned off. Effort controls how much:

| Effort | Use for |
|---|---|
| `low` | Chat, simple classification, routing, high volume |
| `medium` | Default on Opus 5.5: everyday tasks |
| `high` / `xhigh` | Hard analysis, coding, multi-step agents |
| `max` | Correctness far outweighs cost and latency |

Higher effort means more billed output tokens and latency. Thinking arrives as `thinking` blocks you must handle, even if you don't show them.

## Reading a response

```python
response.content        # list of blocks: thinking, text (and tool_use, in Module 7)
response.stop_reason    # why generation ended
response.usage          # token counts, including cache usage
response._request_id    # Anthropic's ID for this request; log it
```

```python
answer = "".join(b.text for b in response.content if b.type == "text")
```

**Check `stop_reason` first.** `end_turn` is normal; `max_tokens` means truncated; `refusal` means declined (`response.stop_details.category` may say why); `tool_use` means Claude wants a tool. **Log the request ID** (`response._request_id`, or `e.request_id` on errors): it's what Anthropic support needs.

## Multi-turn conversations

The API is **stateless**: send the whole history every time.

```python
history = [{"role": "user", "content": "What's the fee for an international wire?"}]
first = client.messages.create(model="claude-opus-5-5", max_tokens=16000, system=SYSTEM, messages=history)

history.append({"role": "assistant", "content": first.content})   # the full content list
history.append({"role": "user", "content": "And for a domestic one?"})
second = client.messages.create(model="claude-opus-5-5", max_tokens=16000, system=SYSTEM, messages=history)
```

**Append the assistant's full `content` list**, thinking blocks included, unchanged. **Never edit earlier turns**; append new ones. Because history grows, so do cost and latency: trim old turns (complete pairs, still starting with `user`), summarize them, or use prompt caching (lesson 7).

Content can also be a list of blocks that includes images (`{"type": "image", ...}` next to a text block).

> **Key takeaways**
> - A request is model + max_tokens + system + messages (+ effort).
> - Start with the most capable model, then step down effort or model against an evaluation.
> - Check `stop_reason` first and log request IDs.
> - The API is stateless: append the full content list; never edit earlier turns.
