---
title: "Claude in the FDE Toolkit: Your First API Call"
type: reading
minutes: 5
---

> **By the end of this lesson** you will be able to make a Messages API call, read the response blocks safely, check `stop_reason`, and work out the cost of a call.

Dana Ruiz wants a summary of every Brightline steering meeting to forward to her CEO. You'll have Claude draft it, so you need the API basics.

## The Messages API

One endpoint, `messages.create`: you send a list of messages, Claude returns one assistant message.

```python
import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment

response = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=1024,
    system="You are a concise assistant for a forward deployed engineer.",
    messages=[
        {"role": "user", "content": "Give me three questions to ask in a discovery call."}
    ],
)

for block in response.content:
    if block.type == "text":
        print(block.text)
```

- **Stateless:** Claude doesn't remember earlier calls. Send the full history each time.
- **`system`** holds role, context and rules.
- **`messages`** alternate `"user"` and `"assistant"`; the first must be `"user"`.
- **`max_tokens`** caps the *output*. Hit it and the response is cut off.

## The response is a list of blocks

| Block type | What it is |
|---|---|
| `"text"` | The answer, in `block.text` |
| `"thinking"` | Claude's reasoning. Claude Opus 5.5 thinks adaptively, so responses often *start* with one (text empty by default) |
| `"tool_use"` | A request to call your tool (Module 7) |

So `response.content[0].text` is fragile: `content[0]` may be a thinking block. Use:

```python
answer = "".join(b.text for b in response.content if b.type == "text")
```

## Check `stop_reason`

| `stop_reason` | Meaning | Do |
|---|---|---|
| `"end_turn"` | Finished normally | Use the answer |
| `"max_tokens"` | Output truncated at your cap | Raise `max_tokens` or ask for less |
| `"tool_use"` | Wants a tool | Run it, send the result (Module 7) |
| `"refusal"` | Declined by safety systems | Don't treat it as an answer |

## Tokens and cost

A token is about 4 characters of English; `response.usage` reports a call's input and output tokens. Claude Opus 5.5 costs **$4 per million input tokens** and **$20 per million output tokens**:

```
2,000 / 1,000,000 × $4  = $0.008
  500 / 1,000,000 × $20 = $0.010
                  total = $0.018
```

At 50,000 calls a day that's real money. Know your unit economics.

**Try it:** the simulator behaves like the real SDK, errors included. Run the scratchpad, print `response.content`, then change the first message's role to `"assistant"` and read the error.

> **Key takeaways**
> - `response.content` is a list of typed blocks; filter for `"text"`.
> - Check `stop_reason` before trusting output.
> - Cost = tokens × price per million, input and output priced separately.
