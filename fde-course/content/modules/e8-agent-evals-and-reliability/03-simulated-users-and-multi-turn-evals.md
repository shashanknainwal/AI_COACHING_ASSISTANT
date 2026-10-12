---
title: "Simulated Users and Multi-Turn Evals"
type: reading
minutes: 16
---

> **By the end of this lesson** you'll be able to explain why single-turn cases under-test conversational agents, design a user simulator with a persona, hidden facts, a goal and stopping rules, choose between scripted and model-driven simulators, validate the simulator itself, and score multi-turn episodes on task success, turns and false claims of success.

## The problem with single-turn cases

A golden case for a router is one message and one label. A support agent's job is a conversation. The customer starts vague ("I need to sort out my meter"), answers only what they're asked, gets some facts wrong, changes their mind and leaves when they lose patience. A single-turn case that puts the account number, postcode and reading in the first message tests the easiest version of the task.

Multi-turn behaviour has failure modes single-turn evals can't see:

- **Asking for too much, or in the wrong order**, so the customer leaves.
- **Asking for something the customer can't know**, such as an internal reference number.
- **Losing facts from earlier turns** and asking again.
- **Declaring success too early**, saying "done" before the write actually happened.
- **Drifting under pressure**, for example giving in to a third request for an over-limit refund.

You need something that plays the customer, turn after turn, without a human in the loop for every run. That's a **user simulator**.

## Anatomy of a simulator

| Part | What it holds | Example |
|---|---|---|
| Persona | Who they are and how they talk | "Impatient, short sentences, types postcodes without spaces" |
| Goal | What they want, in their words | "Switch to the fixed tariff" |
| Hidden facts | What they know, revealed only when asked | Account number, postcode, meter reading |
| Unknowns | What they don't know | Date of birth on the account, internal codes |
| Stopping rules | When they end the conversation | Satisfied, out of patience (N turns), or told to call back |
| Scoring hook | What success means, checked outside the conversation | The tariff field in the sandbox |

Two rules matter most. **Hidden facts stay hidden until asked.** A simulator that volunteers everything turns a hard task into an easy one. **Success is never judged by the simulator.** The simulated customer can be satisfied while the task failed, which is exactly the false-completion failure you need to catch. Score the end state, as in lesson 01.

## Scripted or model-driven?

| | Scripted simulator | Model-driven simulator |
|---|---|---|
| How it works | Rules: keyword triggers map to canned replies | A model plays the persona from a prompt with the goal, facts and rules |
| Strengths | Deterministic, free, exact control of what's revealed | Natural, varied language. Copes with questions you didn't script. |
| Weaknesses | Brittle phrasing. Misses anything you didn't anticipate. | Can break character, leak hidden facts, or go along with the agent. It costs tokens and adds noise. |
| Use for | Regression suites in CI, policy edge cases, and the exercise in this lesson | Breadth: realistic variety before launch, finding new failure modes |

Most teams use both: a scripted core that runs on every change, and a model-driven layer run nightly or before releases. If you use a model to play the user, prefer a different model from the agent under test, and keep its prompt in version control next to the suite.

## Validate the simulator

A simulator is a model of your customers, so it needs its own checks:

- **Read episodes.** Before trusting any score, read 20 full transcripts. Look for the simulator revealing facts it wasn't asked for, answering questions it shouldn't know, or agreeing too readily.
- **Track simulator failures separately.** When the simulator hits a question it can't answer, flag the episode. Then decide: was the agent's question unreasonable (an agent bug), or is the persona incomplete (a simulator bug)?
- **Compare with real conversations.** Turn counts, how often customers give up, and the distribution of first messages should look like production once you have production.
- **Pin it.** A changed simulator prompt changes every score. Version it like the golden set.

## Scoring an episode

| Metric | Definition | Why |
|---|---|---|
| Task success | End-state check after the episode, from a fresh sandbox | The only success that counts |
| Claimed but failed | The customer ended satisfied, but the check failed | The most damaging failure: nobody follows up |
| Gave up | The simulator ran out of patience | Too many questions, or questions in the wrong order |
| Turns to success | Agent turns in successful episodes | Effort and latency for the customer |
| Simulator unknowns | Questions the persona couldn't answer | Triage: agent problem or persona gap |
| Errors | API or sandbox failures | Excluded from rates, reported, rerun |

Run each scenario several times when the agent or the simulator is a model, and report pass^k over scenarios with the clustered intervals from lesson 01.

## Designing the scenario set

Cover the axes that change behaviour, not just intents:

- **Information order:** everything up front, drip-fed, or wrong at first and corrected later.
- **Patience:** a patient customer and one who leaves after two questions.
- **Format noise:** postcodes without spaces, lowercase account numbers, typos.
- **Pressure:** repeated demands for something the policy forbids.
- **Vulnerability signals:** a mention of a medical device or bereavement that should change the path.
- **Out of scope:** a request the agent should hand off rather than attempt.

Start each scenario from a real conversation where you can (lesson 08), and keep a held-out set of scenarios you don't tune against (lesson 06).

## Practice (say it out loud)

These are original prompts, in the style of agentic design and deep-dive rounds.

- "Your simulated-user eval says 90% task success, but production complaints went up. Give three ways the simulator could be lying to you."
- "Design the persona and stopping rules for a simulated customer who wants a refund the policy doesn't allow."
- "When would you use a model to play the user, and how would you stop it from making the task easier?"

> **Key takeaways**
>
> - Single-turn cases test the easiest version of a conversational task. Simulated users test asking, remembering, patience and pressure.
> - A simulator has a persona, a goal, hidden facts revealed only when asked, unknowns and stopping rules. It never judges success: the sandbox does.
> - Scripted simulators are deterministic regression tests. Model-driven ones add realism and breadth, but can break character or go along with the agent.
> - Validate the simulator by reading episodes, tracking questions it couldn't answer, comparing with real conversations and versioning it.
> - Score task success, claimed-but-failed, gave-up, turns to success and simulator unknowns, with errors kept out of the rates.
