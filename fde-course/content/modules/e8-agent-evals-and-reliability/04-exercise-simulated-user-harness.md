---
title: "Exercise: A Simulated-User Harness for a Support Agent"
type: exercise
minutes: 40
hints:
  - "`respond`: check the two endings before anything else, in this order: `Done:` first, then patience. Only then work out a reply, and count the turn only when you actually return one."
  - "Build `asked` by walking `FACT_KEYWORDS` in its own order and testing each keyword against the lowercased agent text. Reveal facts only if the persona holds every one asked for; otherwise it's an unknown question."
  - "`run_episode`: one loop. Call the API, append `response.content` unchanged as the assistant turn, let the simulator respond, then decide whether to stop. The simulator's reason for stopping wins over the turn cap."
  - "Catch `anthropic.APIError` around the call. The SDK has already retried by the time you see it, and an episode that never got an answer is an error, not a failed task."
  - "`run_suite`: `reset_db()` before each episode, because the agent's tools write to the shared sandbox. Success comes from `check_state`, never from the transcript."
---

Teodora Kessler at Gannet Home Energy (fictional) is back. "Single-turn cases don't tell me much about this agent. Real customers don't hand over their account number and postcode in the first message, they get impatient, and they don't know things. I want a harness where a scripted customer drives the agent through whole conversations, and the score comes from the account database, not from the agent saying it's done."

The agent runs behind the simulated Claude API (`client`), and its tools write to the sandbox `ACCOUNTS`. You write the user simulator, the episode loop and the scoring. This simulator is scripted, not a model, so the harness is deterministic. Lesson 03 covers when to use a model-driven simulator instead.

## Your task

**1. `UserSimulator(persona)`.** A persona has an `opening` message, a `patience` (the most user turns this customer will send) and hidden `facts`.

- `opening()` returns `persona["opening"]` and sets `turns` to 1.
- `respond(agent_text)` returns the next user message, or `None` when the customer stops. In order:

| # | Condition | Effect |
|---|---|---|
| 1 | `agent_text` starts with `"Done:"` | `ended = "satisfied"`, return `None` |
| 2 | `turns >= patience` | `ended = "gave_up"`, return `None` |
| 3 | The agent asked for facts (each `FACT_KEYWORDS` keyword found in the lowercased text) and the persona holds all of them | `"It's " + ", ".join(values) + "."`, values in `FACT_KEYWORDS` order |
| 4 | It asked for a fact the persona doesn't hold, or the text contains `"?"` | `"Sorry, I don't know that."` and `unknown_questions += 1` |
| 5 | Anything else | `"Is that sorted, then?"` |

After rules 3 to 5, add one to `turns`.

**2. `run_episode(client, persona, max_agent_turns=8)`** starts the conversation with the opening and loops:

- Call `client.messages.create(model=AGENT_MODEL, max_tokens=MAX_TOKENS, system=AGENT_SYSTEM, messages=messages)`. If it raises `anthropic.APIError`, stop with `ended = "error"`.
- Append `response.content` unchanged as the assistant turn. The agent's text is its text blocks joined.
- Ask the simulator to respond. If it returns `None`, stop with its `ended`. Otherwise, if this was agent turn `max_agent_turns`, stop with `"max_turns"`. Otherwise append the reply as a user turn.

Return `{"ended", "agent_turns", "transcript", "unknown_questions"}`, where `transcript` is a list of `(role, text)` tuples starting with `("user", opening)`.

**3. `check_state(expect)`** returns `True` when every `ACCOUNTS[account][field]` matches `expect`, a dict of `{account: {field: value}}`.

**4. `run_suite(client, scenarios)`** calls `reset_db()`, runs the episode and scores it, for each scenario. Each row is `{"id", "ended", "agent_turns", "success", "claimed_but_failed", "unknown_questions"}`. `success` is `None` for an error episode, otherwise `check_state(scenario["expect"])`. `claimed_but_failed` is true when the customer ended satisfied but the check failed.

**5. `summarize(rows)`** returns `episodes`, `errors`, `success_rate` (over scored episodes, 3 decimals), `mean_turns_success` (agent turns over successful episodes, 2 decimals), and three lists of ids in row order: `claimed_but_failed`, `gave_up`, and `check_simulator` (episodes where the simulator couldn't answer a question).

## Example

```python
>>> sim = UserSimulator(SCENARIOS[0]["persona"]); sim.opening()
'Hi, I need to submit a meter reading.'
>>> sim.respond("Can I take your account number, please?")
"It's GN-204117."
```

Press **Run** and read the table, then **Submit**.

## What to notice

- **S3 is the dangerous one.** The agent said "Done:" and the customer left happy, but the tariff never changed, because the customer typed the postcode without a space. A grader that read the transcript, or asked a judge "did the agent resolve it?", would pass it.
- **S5 says "check the simulator".** The agent asked for a date of birth that the persona doesn't have. That might be an agent problem (a requirement nobody told the customer about) or a simulator gap. Read the episode before blaming either one.
- **S7 is a patience failure, not a capability failure.** Three questions in a row lost an impatient customer. Turn count is a quality metric, which is why S2 (everything in one message) should take one turn.
- **S6 is an error.** It's excluded from the success rate and reported on its own line, exactly as in module E4.
