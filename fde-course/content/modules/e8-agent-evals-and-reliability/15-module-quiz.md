---
title: "Module E8 Quiz"
type: quiz
minutes: 12
questions:
  - q: "An agent run ends with the right tariff on the account, but it changed the tariff before verifying the caller's identity. How should a well-designed eval grade it?"
    options:
      - "Pass, because the end state matches the target"
      - "Fail, because a trajectory rule encodes the identity policy"
      - "Pass, but lower its score for taking a longer, riskier route"
      - "Error, because the run order was unexpected"
    answer: 1
    explain: "Identity before writes is a policy about the path, so it belongs in a trajectory rule. The end state can be right while the process is a compliance breach."
  - q: "Every task in your suite passes 80% of the time, independently. What is pass^3?"
    options:
      - "About 99%"
      - "80%"
      - "About 64%"
      - "About 51%"
    answer: 3
    explain: "pass^3 is the chance that all three trials pass: 0.8 cubed is 0.512. A single per-run rate hides how often a customer meets a failure."
  - q: "A task ran 5 times and passed 4. What is the unbiased estimate of its pass^3?"
    options:
      - "0.4"
      - "0.512"
      - "0.8"
      - "0.6"
    answer: 0
    explain: "C(4,3)/C(5,3) = 4/10 = 0.4. Cubing the observed rate gives 0.512, which is biased with this few trials."
  - q: "Your 30 runs come from 10 tasks with 3 trials each, and the failures sit in two hard tasks. Why is the naive standard error on the per-run rate too small?"
    options:
      - "The naive formula ignores errored runs"
      - "Wilson intervals should replace it for agents"
      - "Runs of one task are correlated, so they carry less information"
      - "Three trials per task is below the minimum the naive formula needs"
    answer: 2
    explain: "Trials of the same task fail together. Cluster the standard error by task. More tasks, not more trials, narrow the interval."
  - q: "In a simulated-user episode the agent says 'Done: you're on Fixed 24' and the simulated customer ends satisfied, but the sandbox shows the old tariff. How is the episode scored?"
    options:
      - "Success, because the customer was satisfied"
      - "Failure, counted as claimed but failed"
      - "Error, because the simulator and sandbox disagree"
      - "Excluded, because the simulator misread the reply"
    answer: 1
    explain: "Success comes from the end state, never from the conversation. A false claim of completion is the most damaging failure, because nobody follows up."
  - q: "Error analysis finds 14 false completions at $35 each and 5 missed escalations at $220 each. Which should the team fix first, and why?"
    options:
      - "Missed escalations, with $1,100 of impact against $490"
      - "False completions, because they are the most frequent"
      - "Both together, because they share the same root cause"
      - "Neither, until the codebook covers every single trace in the sample"
    answer: 0
    explain: "Rank by frequency times cost. The rarer failure has more than twice the impact. Frequency alone would send the team to the wrong fix."
  - q: "A prompt change raises dev accuracy by 20 points and lowers validation accuracy by 8. What does the frozen-test protocol say?"
    options:
      - "Accept it, because the dev gain is much bigger"
      - "Run it on the test set to break the tie"
      - "Average dev and validation and accept if positive"
      - "Treat it as overfit and revert it"
    answer: 3
    explain: "Validation decides whether a change generalizes. A dev win with a validation loss is the signature of overfitting. Looking at the test set to decide would leak it."
  - q: "Why should a synthetic variant that nearly matches a frozen test case be dropped?"
    options:
      - "Near-duplicates make the generator less deterministic"
      - "Synthetic cases may never share wording with real ones"
      - "Tuning on it would leak the test case, inflating the score"
      - "It lowers the share of terse and angry variants"
    answer: 2
    explain: "If you tune on a lookalike of a test case, the final score partly measures memory. Decontaminate synthetic sets against the frozen test set."
  - q: "An injection suite has 24 attacks and none succeed. What can you honestly claim?"
    options:
      - "The attack success rate is likely under about 14%"
      - "The attack success rate is exactly zero"
      - "The agent is immune to prompt injection"
      - "The rate is under 1% with 95% confidence"
    answer: 0
    explain: "The Wilson upper bound for 0 of 24 is about 0.14. Small suites can't prove tiny rates, which is why irreversible harms also get zero-tolerance rules."
  - q: "A harness appends each tool_result in its own user message when the model calls two tools in one turn. What happens?"
    options:
      - "Both results are used, at a somewhat higher token cost overall"
      - "The request is rejected, so the case looks like an error"
      - "The second result is silently ignored"
      - "The prompt cache resets but the run succeeds"
    answer: 1
    explain: "Every tool_result for a turn must be in the next user message, so the split is a 400. The harness then logs an error, and a harness bug looks like an agent failure."
---

Ten questions on agent evals and reliability. You need 8 correct to pass.
