---
title: "Claude in the FDE Toolkit: Your First API Call"
type: reading
minutes: 15
---

Large language models changed FDE work in two ways. First, they're a **tool you use** every day: summarizing call notes, drafting briefs, writing data-cleaning scripts, reading unfamiliar code. Second, they're very often **what you deploy**: support assistants, document extraction, triage agents, internal search. This course teaches both, using Claude and the official **Anthropic Python SDK**.

This lesson covers the mental model and your first API call. Module 6 goes much deeper.

## The Messages API in one picture

Everything goes through one endpoint, `messages.create`. You send a list of messages; Claude sends back one assistant message.

```
your code ──► client.messages.create(
                  model="claude-opus-5-5",
                  max_tokens=1024,
                  system="You are ...",            # who Claude is, rules to follow
                  messages=[{"role": "user", "content": "..."}],
              )
          ◄── Message(
                  content=[ThinkingBlock(...), TextBlock(text="...")],
                  stop_reason="end_turn",
                  usage=Usage(input_tokens=..., output_tokens=...),
              )
```

Key ideas:

- **The API is stateless.** Claude doesn't remember previous calls. To have a conversation, you send the whole history every time.
- **`system`** sets the role, context, and rules. It's where most of your prompt engineering lives.
- **`messages`** alternate between `"user"` and `"assistant"`. The first message must be from the user.
- **`max_tokens`** is a hard cap on the *output* length. If Claude hits it, the response is cut off and `stop_reason` is `"max_tokens"`.

## Your first call

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

## The response is a list of blocks, not a string

This is the number-one beginner mistake. `response.content` is a **list of content blocks**, and each block has a `type`:

| Block type | What it is |
|---|---|
| `"text"` | The text answer. Read it from `block.text`. |
| `"thinking"` | Claude's reasoning step. Current models like Claude Opus 5.5 think adaptively, so responses often *start* with a thinking block. Its text is empty by default. |
| `"tool_use"` | Claude asking to call one of your tools (Module 7). |

So this common snippet is **fragile**:

```python
answer = response.content[0].text   # breaks when content[0] is a thinking block
```

Do this instead:

```python
answer = "".join(b.text for b in response.content if b.type == "text")
```

## Check why Claude stopped

`response.stop_reason` tells you why generation ended. Always check it before trusting the output:

| `stop_reason` | Meaning | What to do |
|---|---|---|
| `"end_turn"` | Claude finished normally | Use the answer |
| `"max_tokens"` | Hit your `max_tokens` cap; output is truncated | Raise `max_tokens` or ask for a shorter answer |
| `"tool_use"` | Claude wants to call a tool | Run the tool and send back the result (Module 7) |
| `"refusal"` | The request was declined by safety systems | Don't treat the content as an answer; handle it gracefully |

## Tokens and cost

You pay per **token** (roughly 4 characters of English text), with separate prices for input and output. `response.usage` tells you exactly how many tokens a call used:

```python
print(response.usage.input_tokens, response.usage.output_tokens)
```

Claude Opus 5.5, which this course uses by default, costs **$4 per million input tokens** and **$20 per million output tokens**. So a call with 2,000 input tokens and 500 output tokens costs:

```
2,000 / 1,000,000 × $4  = $0.008
  500 / 1,000,000 × $20 = $0.010
                  total = $0.018
```

Small per call, but a customer workflow running 50,000 times a day changes the math. FDEs are expected to know the unit economics of what they deploy. You'll build a cost calculator in the next exercise.

## About the simulator

In this course, `import anthropic` loads an offline simulator with the same interface as the real SDK. It returns realistic responses (including thinking blocks, `stop_reason`, and `usage`), raises the same error classes, and even rejects invalid requests the way the real API does, for example a first message that isn't from the user. To run your code for real later:

```bash
pip install anthropic
export ANTHROPIC_API_KEY=sk-ant-...
python main.py
```

**Try it:** the scratchpad on the right has the first-call example ready to run. Try printing `response.content` to see the blocks, then change the first message's role to `"assistant"` and see the error you get.
