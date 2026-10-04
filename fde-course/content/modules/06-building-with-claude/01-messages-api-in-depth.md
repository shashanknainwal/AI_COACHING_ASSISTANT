---
title: "The Messages API in Depth"
type: reading
minutes: 18
---

> **By the end of this lesson you will be able to:**
> - Explain every important parameter of a `messages.create` request
> - Choose a model and an effort level for a task, and justify the cost
> - Build multi-turn conversations correctly, including what to append to history
> - Read a response like an engineer: content blocks, stop reasons, usage, request IDs

## From first call to production

In Module 1 you made your first Claude call. Since then you've used Claude for extraction (Module 2), labeling (Module 3), mapping (Module 4), and SQL (Module 5). This module goes deep on the API itself: the parameters, behaviors, and failure modes you need to know to put Claude in front of a customer's users.

Our customer for this module is **Harbor Bank**, a regional bank piloting a Claude-powered assistant for its customer-support team.

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

| Parameter | What it does | Production guidance |
|---|---|---|
| `model` | Which Claude model runs the request | Start with Claude Opus 5.5; see below for when to choose others |
| `max_tokens` | Maximum output tokens; generation stops there | Don't lowball it. About 16,000 for normal calls; use streaming for larger values |
| `system` | Instructions that frame the whole conversation | Where most of your prompt engineering lives (next lessons) |
| `messages` | Alternating user/assistant turns; first must be `user` | You resend the whole history every time |
| `output_config.effort` | How much thinking and effort Claude spends | `low` for chat and simple tasks; higher for hard reasoning |

## Choosing a model

Current Claude models and their API prices (per million tokens):

| Model | ID | Input | Output | Typical use |
|---|---|---|---|---|
| Claude Opus 5.5 | `claude-opus-5-5` | $4 | $20 | Default: complex reasoning, agents, coding, anything customer-facing that must be right |
| Claude Sonnet 5.5 | `claude-sonnet-5-5` | $2 | $10 | High-volume production work where speed and cost matter |
| Claude Haiku 4.5 | `claude-haiku-4-5` | $1 | $5 | Simple, latency-critical tasks: short classifications, routing |

Choosing is an engineering decision, not a vibe:

1. **Start with the most capable model** and get the task working well, with an evaluation set (Module 8) that measures quality.
2. **Then try lowering effort,** and if needed **try a cheaper model,** and re-run the evaluation each time.
3. **Keep the cheapest option that still meets the quality bar.**

Often, lowering **effort** on the most capable model matches a smaller model at similar cost, with fewer surprises. Always measure on your own tasks.

## Effort and thinking

Claude Opus 5.5 always **thinks** before answering (adaptive thinking): it reasons internally, more on hard problems and less on easy ones. You control how much with `output_config={"effort": ...}`:

| Effort | Use for |
|---|---|
| `low` | Chat replies, simple classification, routing, high-volume work |
| `medium` | The default on Claude Opus 5.5: everyday tasks |
| `high` / `xhigh` | Hard analysis, coding, multi-step agent work |
| `max` | When correctness matters far more than cost or latency |

Higher effort means more (billed) output tokens and more latency. Thinking appears in the response as `thinking` blocks, whose text is empty by default. You don't need to display them, but you do need to handle them, which brings us to responses.

## Reading a response

```python
response.content        # list of blocks: thinking, text (and tool_use, in Module 7)
response.stop_reason    # why generation ended
response.usage          # token counts, including cache usage
response._request_id    # Anthropic's ID for this request; log it
```

**Content is a list of typed blocks.** Get the answer by collecting text blocks:

```python
answer = "".join(b.text for b in response.content if b.type == "text")
```

**Check `stop_reason` first.** `end_turn` is normal. `max_tokens` means truncated output. `refusal` means the request was declined; check `response.stop_details.category` for why. `tool_use` means Claude wants to call a tool (Module 7).

**Log the request ID.** When something goes wrong in production, `response._request_id` (or `e.request_id` on errors) is what Anthropic support needs to investigate.

## Multi-turn conversations

The API is **stateless**. To continue a conversation, send the whole history, alternating user and assistant turns:

```python
history = [{"role": "user", "content": "What's the fee for an international wire?"}]
first = client.messages.create(model="claude-opus-5-5", max_tokens=16000, system=SYSTEM, messages=history)

history.append({"role": "assistant", "content": first.content})   # the full content list
history.append({"role": "user", "content": "And for a domestic one?"})
second = client.messages.create(model="claude-opus-5-5", max_tokens=16000, system=SYSTEM, messages=history)
```

**Append the assistant's full `content` list, not just its text.** The list includes thinking blocks, which current models use to keep their reasoning consistent across turns; passing them back unchanged is the safe default. Never edit earlier turns of a conversation in place: append new turns instead.

### Long conversations

Every turn resends the whole history, so cost and latency grow with conversation length. Three tools manage this:

- **Trim** old turns once a conversation passes a limit (keep complete user/assistant pairs, and make sure the history still starts with a user turn).
- **Summarize** older turns into a short recap.
- **Prompt caching** (lesson 7) makes the unchanged prefix of the history much cheaper on each new turn.

## Images, briefly

Content can also be a list of blocks that includes images, for example a photo of a cheque or a screenshot of an error:

```python
{"role": "user", "content": [
    {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": png_b64}},
    {"type": "text", "text": "What error is shown in this screenshot?"},
]}
```

The same patterns apply: structured outputs for extraction, validation afterward, and a human for anything consequential.

> **Key takeaways**
> - A request is model + max_tokens + system + messages (+ effort); don't lowball max_tokens.
> - Start with the most capable model, get it working, then try lower effort or cheaper models against an evaluation.
> - Read responses by block type, check stop_reason first, and log request IDs.
> - The API is stateless: resend history, append the assistant's full content list, and never edit earlier turns.
