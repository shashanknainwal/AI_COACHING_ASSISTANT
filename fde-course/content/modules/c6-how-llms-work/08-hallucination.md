---
title: "Hallucination: Causes, Detection and Mitigation"
type: reading
minutes: 16
---

> **By the end of this lesson** you'll be able to explain why models make things up, name the ways to detect it, choose mitigations in the right order, and give a calm, structured answer when a customer says "it makes things up".

## Why it comes up

It's the most common complaint about LLM products, and a staple of design and customer rounds. Candidates report design prompts that include a grounding or accuracy requirement (**Reported**, across applied loops). The scenarios here are original.

## What a hallucination is

A **hallucination** is fluent output that isn't supported by the model's sources or by the world: an invented citation, a wrong number, a policy that doesn't exist, a function the library never had. Two kinds are worth separating, because the fixes differ:

- **Unfaithful to the context.** The answer contradicts or goes beyond the documents you supplied. You can check this mechanically.
- **Factually wrong without context.** The model answered from its weights and was wrong. You fix this by giving it sources, not by asking it to try harder.

## Why it happens

Connect each cause to the training lesson:

1. **Next-token prediction rewards plausibility.** A plausible-sounding citation is a likely continuation even when no such paper exists.
2. **Training can reward answering over abstaining.** If graders score a confident guess higher than "I don't know", the model learns to guess.
3. **Knowledge gaps.** Facts after the training cutoff, internal company facts, rare facts seen few times.
4. **Context problems.** The right passage wasn't retrieved, was cut off, or was lost in the middle of a long prompt (lesson 01).
5. **Ambiguous prompts.** The model fills gaps with assumptions instead of asking.
6. **Pressure to comply.** Instructions like "always give an answer" or a required field in a schema with no way to say "unknown".

## Detection

| Method | How | Catches | Cost |
|---|---|---|---|
| **Citation checking** | Require a citation per claim; verify each claim against the cited span | Unfaithful answers, fake citations | Cheap, deterministic (next exercise) |
| **LLM-as-judge for faithfulness** | A second model call grades "is every claim supported by these passages?" | Paraphrased unsupported claims that word overlap misses | One extra call; calibrate the judge against human labels |
| **Self-consistency** | Ask several times; disagreement signals low confidence | Guesses on facts the model doesn't know | N times the cost |
| **Validators in code** | Check IDs, dates, totals and enums against your systems | Invented order numbers, wrong sums | Cheapest of all |
| **Evals and production sampling** | Labelled set with known answers, including unanswerable questions; review a sample of live traffic | Regressions and the rate over time | Ongoing effort |

## Mitigation, in order

Say them in this order: the early items fix the cause, the later ones contain it.

1. **Ground it.** Retrieve the relevant documents and put them in the context. Most "it makes things up" complaints are retrieval problems.
2. **Permit "I don't know".** Say explicitly that "the documents don't cover this" is a correct answer, and make the output schema allow it (a nullable field or an `unknown` enum value).
3. **Require citations.** Ask for quotes or citations per claim. Claude's API also has a citations feature for supplied documents; check the current docs for its response shape.
4. **Verify in code.** Check citations, IDs and numbers against the sources before the user sees the answer. Block or flag what fails.
5. **Narrow the task.** Extraction and classification hallucinate less than open generation. Use tools for lookups and arithmetic.
6. **Measure.** An eval with unanswerable questions measures false answers, not just correct ones. Track a faithfulness rate in production.
7. **Design the UX for residual error.** Show sources, let users report errors, route high-stakes answers to a human.

## Model answer: "The customer says it makes things up"

In a customer round, the trap is either to promise it'll never happen or to blame the model. A strong answer has four moves:

"First, I'd get three or four concrete examples, with the question, the answer and what was wrong, and the request IDs so I can see exactly what the model was given. Second, I'd classify each one: did retrieval miss the right document, did the model ignore a document it had, or did it answer something the documents don't cover at all? Those have different fixes. Third, the fixes: improve retrieval if documents were missing; require citations and verify them in code before the answer is shown; tell the model that 'not covered' is a valid answer and allow it in the output format. Fourth, I'd build a test set from their real questions, including ones the documents can't answer, and report two numbers each week: how often answers are fully supported, and how often it answers when it should have said it didn't know. I won't promise zero, but I'll promise we measure it and drive it down, and that unsupported answers get flagged instead of shown as fact."

## Practice (say it out loud)

- "Your RAG assistant cites a real document but the claim isn't in it. Which detection method catches this, and which misses it?"
- "A legal customer needs zero fabricated case citations. What would you build?"

> **Key takeaways**
>
> - Hallucination is fluent output unsupported by sources or reality. Separate unfaithful-to-context from wrong-from-memory.
> - Causes: plausibility-trained generation, rewards for guessing, knowledge gaps, poor context, ambiguity and pressure to answer.
> - Detect with citation checks, validators, faithfulness judges, self-consistency and evals that include unanswerable questions.
> - Mitigate in order: ground, permit "I don't know", cite, verify in code, narrow, measure, design the UX for what's left.
