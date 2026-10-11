---
title: Module 8 Quiz
type: quiz
minutes: 12
questions:
- q: A customer asks how you know the triage system works. Which answer is strongest?
  options:
  - We tested it in the demo and it handled every example correctly
  - Claude is a very capable model
  - "On 400 labeled tickets from your queue it routes 93% correctly, 98% of safety tickets are marked urgent, and here are the failures"
  - "We'll monitor complaints after launch"
  answer: 2
  explain: "Real data, agreed metrics, critical slices and visible failures. Demos only sample the cases you thought of."
- q: "Which grader should you reach for first when the output is {\"category\": ..., \"urgency\": ...}?"
  options:
  - "Code: compare each field with the label"
  - An LLM-as-judge with a detailed rubric
  - A human reviewer for every case
  - Ask the model to grade itself
  answer: 0
  explain: "Prefer the cheapest, most reliable grader. Structured outputs make code grading trivial."
- q: Why ask the judge for its reasoning before the verdict in the structured output?
  options:
  - It makes responses shorter
  - The API requires a reasoning field to come before any enum field in a structured-output schema
  - It hides the verdict from users
  - "The verdict then follows from the reasoning, and the reasoning shows why a case failed"
  answer: 3
  explain: Reasoning first produces more consistent verdicts and makes disagreements easy to diagnose.
- q: "A judge says \"pass\" to every answer. 90% of answers really are good. What are its accuracy and Cohen's kappa?"
  options:
  - "Accuracy 90%, kappa 0.9"
  - "Accuracy 90%, kappa 0"
  - "Accuracy 100%, kappa 1"
  - "Accuracy 50%, kappa 0.5"
  answer: 1
  explain: Kappa corrects for chance. A judge with no skill scores 0 however high its raw accuracy.
- q: "During calibration, which kind of judge error is usually most dangerous for a customer-facing system?"
  options:
  - "False fails: good answers marked as failures"
  - "False passes: bad answers marked as good"
  - Both are equally harmless
  - "Neither matters if accuracy is above 80%"
  answer: 1
  explain: "A lenient judge hides real failures, so your eval says the system works when it doesn't."
- q: "Your judge passes long, friendly answers that contain the wrong refund window. What is this?"
  options:
  - "Position bias, because the judge favours whichever answer it reads first; shuffle the order"
  - Self-preference
  - A tokenizer bug
  - Verbosity bias; fix it with rubric wording and long wrong answers in the calibration set
  answer: 3
  explain: "Judges tend to favor longer, confident text. Say length doesn't matter, and calibrate with cases that test it."
- q: "An agent's answer to \"my order is late, make it right\" is correct, but its trace shows it issued credit without tracking the shipment. What catches this?"
  options:
  - A trajectory check that required tools appear in order
  - An exact-match check on the final answer against the labeled reference reply
  - A higher max_tokens
  - Nothing; the answer was correct
  answer: 0
  explain: Agents can reach the right answer the wrong way. Grade the process as well as the reply.
- q: "A RAG system gives a wrong answer. Retrieval recall@3 for that question is 0. Where should you look first?"
  options:
  - "The answer prompt's wording: Claude should have inferred the policy from the other chunks it saw"
  - "The judge's rubric"
  - "Retrieval: chunking, search method or the query's wording; Claude never saw the relevant chunk"
  - "The model's temperature"
  answer: 2
  explain: Measure retrieval and generation separately. No prompt can fix a fact that was never retrieved.
- q: The current prompt scores 14/20 and a new one scores 15/20. What can you conclude?
  options:
  - The new prompt is 5 points better; ship it
  - The new prompt is worse
  - The eval is broken
  - "Very little: the Wilson intervals overlap almost completely. Look at the case-by-case regressions and fixes, and add cases"
  answer: 3
  explain: "With 20 cases, one case is 5 points. Use intervals and paired comparisons before deciding."
- q: A candidate has a higher overall pass rate but breaks a fraud-report case that passed before. What should a good release gate do?
  options:
  - "Block it: a regression in a critical slice or a must-pass case fails the gate regardless of the average"
  - "Ship it, since the average went up"
  - Ship it to half the users
  - Ignore fraud cases in the eval
  answer: 0
  explain: "Averages hide what matters. Gates combine must-pass cases, critical-slice rules and a tolerance on the overall rate."
- q: "An agent passes a case 4 times out of 5 trials. For customer-facing automation, which metric reflects this risk?"
  options:
  - "pass@5 (passed at least once)"
  - pass^5 (passed every time)
  - The average output length
  - The number of tools
  answer: 1
  explain: "pass^k measures reliability: an agent that fails 1 time in 5 fails one customer in five. A gap between pass@k and pass^k means flakiness."
- q: "Your system prompt is marked for caching, but cache_read_input_tokens is always 0. Which is a likely cause?"
  options:
  - Caching only works on Fridays
  - Output tokens are too high
  - "The prefix is under the minimum cacheable length, or it changes between requests"
  - "The Message Batches API is disabled on the account, which also turns off prompt caching"
  answer: 2
  explain: "Short prefixes are silently not cached, and any change in the prefix (like a timestamp) breaks the match. Always verify with usage."
- q: "Evals show: Opus 5.5 at medium effort 95% ($1,518/mo), Sonnet 5.5 at low effort 93% ($339/mo), Haiku 5.5 at low effort 89% ($18/mo). The agreed bar is 92%. What do you recommend?"
  options:
  - Sonnet at low effort; run one more Haiku 5.5 prompt round and switch only if it passes
  - "Haiku 5.5, because a 95% saving outweighs missing the bar by three points"
  - "Opus at medium effort, because the top score is always worth the extra cost to a customer"
  - "Average the Haiku and Sonnet answers so the blend clears the 92% bar"
  answer: 0
  explain: "Sonnet is the cheapest configuration that clears the bar. Haiku 5.5 fails it, but at about a twentieth of Sonnet's cost one more prompt iteration is worth trying; switch only if it clears the bar and the critical slices. Present Opus as an option with its extra cost."
---

Thirteen questions on eval sets, graders and LLM judges, agent and RAG evals, release gates and cost modeling. You need **11 out of 13** to pass. You can retry as many times as you like.
