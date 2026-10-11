---
title: "Exercise: Harden a Tool Loop Against an Injected Document"
type: exercise
minutes: 40
hints:
  - "Least privilege starts before any call: build `TASK_TOOLS = [t for t in ALL_TOOLS if t[\"name\"] in TASK_TOOL_NAMES]` and send only that list."
  - "`policy_check`: check the tool name first, then for `send_email` check the domain, then the taint. For the domain, require exactly one `@`, take `address.rsplit(\"@\", 1)[1].lower()` and test membership in `ALLOWED_DOMAINS`. Never use `endswith`."
  - "Keep `state = {\"tainted\": False}` inside `run_agent`. Set it to True right after `fetch_document` runs, and wrap that result with `wrap_untrusted` before it goes back to the model."
  - "For each `tool_use` block build `{\"type\": \"tool_result\", \"tool_use_id\": block.id}`. Deny adds `is_error: True` and `\"Blocked by policy: \" + reason`. An approval gate calls `approve(block.name, block.input)`; if it returns False, add `is_error: True` and `\"Not approved by a human reviewer\"`. Send all results in one user message."
  - "Record the decision per call as `allow`, `deny`, `approved` or `rejected`. Check `iteration == max_iterations` after appending the assistant turn and before running any tools."
---

Mira Vasquez, the fictional interviewer for this module, ends her injection question with a laptop: "Here's a toy agent. A vendor document in our system contains hidden instructions, and the model follows them. Don't fix the model. Fix the loop."

Brindle Labs, a fictional company, has an operations assistant that summarizes vendor documents and emails the summary internally. Document VND-114 hides white-on-white text telling the assistant to export the customer list and email it to an outside address. The simulated Claude here is scripted to **fall for it** every time, which is the right assumption to design for. Your job is to make sure a fully convinced model still can't leak anything.

The agent has all three legs of the lethal trifecta: private data (`export_customers`), untrusted content (`fetch_document`) and an external channel (`send_email`). You'll cut them in code.

## Your task

**1. `wrap_untrusted(text)`** returns `"<untrusted_document>\n" + text + "\n</untrusted_document>"`. Delimiters are a speed bump, not a wall, but they help.

**2. `policy_check(name, tool_input, state)`** returns `(decision, reason)`:

| Check, in order | Result |
|---|---|
| `name` not in `TASK_TOOL_NAMES` | `("deny", "<name> is not available for this task")` |
| `send_email` whose `to` doesn't have exactly one `@` with a domain (case-insensitive) in `ALLOWED_DOMAINS` | `("deny", "recipient domain is not allowed")` |
| `send_email` while `state["tainted"]` is True | `("approve", "untrusted content is in the context")` |
| anything else | `("allow", "")` |

**3. `run_agent(client, task, approve, max_iterations=6)`** runs the tool loop and returns `{"status", "answer", "actions"}`:

- Each request: `model=MODEL`, `max_tokens=MAX_TOKENS`, `system=SYSTEM_PROMPT`, and `tools` = only the tools in `TASK_TOOL_NAMES`.
- Append each `response.content` as the assistant turn. A non-`tool_use` stop ends the run: status `"completed"`, answer = the text blocks joined.
- For every `tool_use` block, call `policy_check` with a `state` dict you keep for the run (starting `{"tainted": False}`):
  - **deny**: don't run it; return an `is_error` result with content `"Blocked by policy: " + reason`.
  - **approve**: call `approve(name, input)`. True runs the tool (decision `"approved"`). False doesn't (decision `"rejected"`, `is_error` content `"Not approved by a human reviewer"`).
  - **allow**: run it (decision `"allow"`).
- Running a tool: call `TOOL_FUNCTIONS[name](**input)`. For `fetch_document`, wrap the text with `wrap_untrusted` and set `state["tainted"] = True`. Otherwise send strings as they are and anything else as `json.dumps(...)`.
- Send all of a turn's results in **one** user message. Append `{"name", "decision"}` to `actions` for each call, in order.
- If the response on call number `max_iterations` still asks for tools, return status `"max_iterations"` (answer `""`) without running them.

## Example

```text
   APPROVAL REQUESTED: send_email to ops@brindle.example: 'Vendor Fernhill Supply raises prices 4% ...'
   fetch_document    allow
   export_customers  deny        <- not a tool for this task (it wasn't even offered)
   send_email        deny        <- audit@vendor-review.example is outside the allowlist
   send_email        approved
status: completed | answer: Summary sent to ops@brindle.example.
emails sent: ['ops@brindle.example'] | customer exports: 0
```

Press **Run**, open the **Trace** tab to see the denied calls marked as errors, then **Submit**.

> **Interview tip:** Say which leg of the trifecta each control cuts. "Least privilege removes private data from this task. The domain allowlist removes the external channel. The approval gate covers what's left after untrusted content arrives." It shows you're designing, not listing.
