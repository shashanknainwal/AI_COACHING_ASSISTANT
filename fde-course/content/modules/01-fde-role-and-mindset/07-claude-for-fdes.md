---
title: "Claude in the FDE Toolkit: Your First API Call"
type: reading
minutes: 7
---

> **By the end of this lesson** you will be able to make a Messages API call, read the response blocks safely, check `stop_reason`, count tokens and work out the cost of a call.

Dana Ruiz wants a summary of every Brightline steering meeting to forward to her CEO. You'll have Claude draft it, so you need the API basics.

## The Messages API

One endpoint, `messages.create`: you send a list of messages, Claude returns one assistant message.

```python
import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment

response = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=16000,                 # covers thinking and the answer
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
- **`max_tokens`** caps the *output*, thinking included. Hit it and the response is cut off. About 16,000 is a sensible default.

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

`response.usage` reports a call's input and output tokens. To know the input size **before** you send, count it with the model you'll use:

```python
count = client.messages.count_tokens(
    model="claude-opus-5-5",
    system="You are a concise assistant for a forward deployed engineer.",
    messages=[{"role": "user", "content": meeting_notes}],
)
print(count.input_tokens)
```

Don't estimate with a characters-per-token constant. Token counts depend on the model's tokenizer: the newer tokenizers (Sonnet 5 and 5.5, Haiku 5.5) count roughly 30% more tokens than Sonnet 4.6 for the same text, and other vendors' tokenizers (such as `tiktoken`) undercount Claude tokens. A rule of thumb that was fine last year can be off by a third today.

Claude Opus 5.5 costs **$4 per million input tokens** and **$20 per million output tokens**. Output includes thinking: Opus 5.5 always thinks (at `medium` effort by default), those tokens are billed as output, and `max_tokens` has to leave room for them. For a 2,000-token prompt and 500 output tokens (say 350 thinking plus 150 of answer):

```
2,000 / 1,000,000 × $4  = $0.008   input (from count_tokens)
  500 / 1,000,000 × $20 = $0.010   output, thinking included
                  total = $0.018
```

Lower effort (`output_config={"effort": "low"}`) cuts the thinking part. Measure real `usage` on a sample before you quote a number.

At 50,000 calls a day that's real money. Know your unit economics.

**Try it:** the simulator behaves like the real SDK, errors included. Run the scratchpad, print `response.content`, then change the first message's role to `"assistant"` and read the error.

> **Key takeaways**
> - `response.content` is a list of typed blocks; filter for `"text"`.
> - Check `stop_reason` before trusting output.
> - Cost = tokens × price per million, input and output priced separately; output includes thinking.
> - Count input tokens with `count_tokens` for the model you'll use, not a characters-per-token rule.
