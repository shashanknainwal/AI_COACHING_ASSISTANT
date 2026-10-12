---
title: "Exercise: Find the Byte That Breaks the Cache"
type: exercise
minutes: 35
hints:
  - "`strip_cache_control`: recurse. A dict becomes a new dict without the `cache_control` key (with its values stripped too), a list becomes a new list of stripped items, anything else is returned as is."
  - "`segments`: strip first, then serialize. Use `json.dumps(x, ensure_ascii=False, separators=(\",\", \":\"))` and never `sort_keys=True`: sorting would hide exactly the key-order bug you're hunting."
  - "`first_divergence`: compare the model first. Then `zip` the two segment lists. The first pair whose path or text differs is the break; find the first differing character with a simple loop. If the texts match but one list is longer, only a longer `a` is a break."
  - "`diagnose` for the tools section: compare the tool names. Different sets mean a tool was added or removed; the same names in a different order mean `tool_order`; the same names in the same order mean the bytes inside a definition moved: `key_order`."
---

Leo here. Tallowmere's order-desk agent runs on Claude Sonnet 5.5 with a long, stable system prompt and three tools. You covered the basics of caching in E5: `cache_control`, prefix matching, reading `cache_read_input_tokens`. Their usage shows that cache reads collapsed after a refactor last week. Every request writes the whole prefix again, and nothing errors. Their engineer swears the system prompt "didn't change".

When usage says the prefix broke but not where, the docs' method is to log consecutive request bodies and diff them in cache order, **tools, then system, then messages**. Strip `cache_control` markers first (a marker that moves between requests isn't a break). The first difference inside the shared region is the break. Everything after it is billed as fresh input.

On the Claude API there's also a server-side cache diagnostics feature (beta) that reports where two requests diverged; it's first-party only and its request shape is in the current docs. The payload diff below works everywhere, including Bedrock, Vertex and behind a customer's gateway.

## Given

`PAIRS`: eight `(request_n, request_n_plus_1)` pairs of logged request bodies (`model`, `max_tokens`, `output_config`, `tools`, `system`, `messages`), plus `TOOLS` and `SYSTEM_TEXT`.

## Your task

**1. `strip_cache_control(obj)`** returns a copy of `obj` with every `cache_control` key removed at any depth. Don't modify the input.

**2. `segments(body)`** strips markers and returns a list of `(path, serialized)` pairs in cache order:

- each tool: `("tools[i]", ...)`
- the system prompt: one `("system", ...)` if it's a string, or `("system[j]", ...)` per block if it's a list
- each message: `("messages[k]", ...)`

Serialize with `json.dumps(x, ensure_ascii=False, separators=(",", ":"))`, keeping keys in the order they were sent.

**3. `first_divergence(a, b)`** returns `None` when `b` keeps all of `a`'s prefix, otherwise a dict `{"section", "path", "offset", "a", "b"}`:

- Models differ: `{"section": "model", "path": "model", "offset": 0, "a": a_model, "b": b_model}`.
- Otherwise walk both segment lists together. At the first position where the paths or texts differ: `path` is `a`'s path, `section` is the part before `[` (`"tools"`, `"system"` or `"messages"`), `offset` is the index of the first differing character (0 if the paths differ), and `"a"` and `"b"` are the 20 characters of each text starting at `offset`.
- If every shared segment matches and `b` has more segments, that's a growing conversation: return `None`. If `a` has more, report `a`'s next segment with offset 0 and `"b": ""`.

**4. `diagnose(a, b)`** names the cause:

| Divergence | Cause |
|---|---|
| None | `"none"` |
| model | `"model_switch"` |
| tools, different set of tool names | `"tools_changed"` |
| tools, same names in a different order | `"tool_order"` |
| tools, same names in the same order | `"key_order"` |
| system | `"system_changed"` |
| messages | `"history_edited"` |

## The usual suspects (and their fixes)

- **A timestamp in the system prompt.** One `datetime.now()` makes every request's prefix unique. Move volatile values into the latest user turn, or round them to the day.
- **Tool order.** Building `tools` from a set or a dict of registered plugins can reorder them between processes. Sort tools by name once, at startup.
- **Key order.** Python says the two `key_order` bodies are equal (`a == b` is `True`), but the bytes on the wire differ because a library rebuilt one schema with its keys in a different order. Comparing bytes, not objects, is the whole point of this exercise.
- **A trimmed tool result.** Someone shortened an old tool result to save tokens. Every message after it is rewritten. On Claude Opus 5.5, editing earlier turns can also fail outright, because thinking-block signatures bind to the earlier messages; the fix there is append-only history plus compaction or context editing (C7 covers those).
- **A model switch.** Caches are per model. A turn routed to Haiku 5.5 to save money can't read the Sonnet 5.5 cache and pays to write its own. Keep one conversation on one model, and send cheap side tasks to a separate call.

## Example

```python
>>> first_divergence(*PAIRS["timestamp"])
{'section': 'system', 'path': 'system[0]', 'offset': 931, 'a': '03Z"}', 'b': '41Z"}'}
>>> diagnose(*PAIRS["growing"]), diagnose(*PAIRS["key_order"])
('none', 'key_order')
```

Press **Run** to diagnose all eight pairs, then **Submit**.
