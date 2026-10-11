---
title: "Written: An Eval Plan for a New Agent Product"
type: written
minutes: 45
sections:
  - key: success
    label: 1. What success means
    prompt: "The three to five numbers that decide launch, with thresholds, and who agreed them. Include at least one reliability number (pass^k or similar), one safety number and one cost or turn number."
    words: [80, 250]
  - key: data
    label: 2. Cases, sources and splits
    prompt: "Where the cases come from with no traffic yet, how many, how they are varied and labelled, how you split them, and what you keep frozen."
    words: [100, 300]
  - key: grading
    label: 3. How each case is graded
    prompt: "End-state checks, trajectory rules (and why each one is a policy), simulated users, and any judge. Say what runs in a sandbox and what the sandbox contains."
    words: [100, 300]
  - key: reliability
    label: 4. Reliability and statistics
    prompt: "Trials per task, how you report pass^k, how you compute intervals when runs are correlated, how errors and flaky cases are handled, and what the case count can and can't show."
    words: [80, 250]
  - key: gates
    label: 5. Gates, adversarial suite and after launch
    prompt: "The CI gate and the release gate, the injection suite and its gate, and what happens after launch: sampling, error analysis cadence, and how new failures become cases."
    words: [80, 300]
rubric:
  - name: Success defined in numbers
    points: 15
    lookFor: "Three to five launch numbers with thresholds, agreed with named roles at Gannet. Includes a reliability metric (pass^k or per-task consistency), a safety metric (attack success rate or critical-action violations) and a cost or turns metric with the model and effort named."
  - name: Credible data without traffic
    points: 20
    lookFor: "Seeds from real sources (the existing support queue, expert-written edge cases, policy documents). Synthetic variation along stated axes with labels checked, deduplication, and decontamination against a frozen test set. Hash-based dev, validation and test splits, with seed families kept in one split. A realistic count (for example 80 to 200 tasks) and a plan to replace synthetic cases with real traffic."
  - name: Grading matched to an agent
    points: 20
    lookFor: "End-state grading in a fresh sandbox comparing the whole state, so side effects count. Trajectory rules limited to policies such as identity before writes and authority limits. Simulated users with hidden facts and patience, success scored from the sandbox rather than the conversation, and false claims of completion counted. Any judge is calibrated (E4)."
  - name: Honest statistics
    points: 20
    lookFor: "Several trials per task (k of at least 3), pass^k from C(c,k)/C(n,k), intervals clustered by task or computed over tasks, errors excluded and rerun, flaky cases quarantined with a rerun policy, and a clear statement of what the sample size can and can't show."
  - name: Gates and the loop after launch
    points: 25
    lookFor: "A CI gate on paired regressions (E4) plus case-level rules for critical categories. An injection and red-team suite graded in code (executed tool calls, URL hosts, canary) with zero tolerance for irreversible harm and an ASR bound, plus a benign utility check. A frozen test set read once per release. After launch: shadow mode or a staged rollout, weekly trace sampling and error analysis, new failures added as versioned cases."
passScore: 70
graderNotes: "Grade the plan as something a head of AI quality could run. If the plan grades success from the agent's own messages or a judge reading the transcript, with no end-state check, cap 'Grading matched to an agent' at 8. If it reports a single pass rate from one run per task, cap 'Honest statistics' at 8. If it tunes prompts on the same cases it reports, with no held-out set, deduct 8 from 'Credible data without traffic'. If there is no adversarial suite, cap 'Gates and the loop after launch' at 12. If cost is mentioned without thinking tokens or without naming a model, deduct 3 from 'Success defined in numbers'. Do not reward length; reward specific numbers, named mechanisms and stated limits."
anchors:
  - label: weak
    expect: [0, 45]
    answer: "Success: the agent should be accurate and customers should be happy. Data: we will ask Claude to generate 50 test conversations about moving home. Grading: an LLM judge reads each conversation and rates it 1 to 10; above 7 is a pass. Reliability: we will run the tests and check the accuracy is above 90%. Gates: we will run the tests before each release and monitor customer satisfaction after launch."
  - label: strong
    expect: [75, 100]
    answer: "Success (agreed with Teodora, the ops lead and compliance): pass^3 of at least 80% over tasks, zero critical violations (writes before verification, credits over the limit, missed vulnerability escalations), attack success rate upper bound under 10% with no executed money-moving attacks, and median cost per successful task under $0.08 on Sonnet 5.5 at effort medium, thinking tokens included. Data: 40 seeds from the current Home Move email queue, anonymized, plus 20 policy edge cases from the compliance team. 6 variants per seed along slot, tone, channel and noise axes, with slot values checked against labels, near-duplicates dropped and lookalikes of test cases removed: about 280 tasks. Split by hashed seed ID 60/20/20, with the test set fingerprinted and run once per release. Grading: each task runs in a fresh sandbox (accounts, meter bookings, a payments mock). We compare the whole final state and apply three trajectory rules, each a written policy. A scripted simulated customer with hidden facts and a patience limit drives 60 multi-turn scenarios, and a model-driven simulator runs nightly for variety. Success comes from the sandbox, and claimed-but-failed is counted. A tone judge is calibrated against 100 human labels (kappa at least 0.7). Statistics: 5 trials per task, pass^3 via C(c,3)/C(5,3), intervals over tasks with t, errors excluded and rerun, flaky tasks quarantined after a 5x rerun. 280 tasks give roughly ±5 points. Rare categories get floors, not rates. Gates: the paired CI gate from E4 plus case-level blocking for vulnerable and credit categories. A 60-attack injection suite graded on executed calls, URL hosts and a canary, plus 30 benign lookalikes. Launch is two weeks in shadow mode, then 10% of traffic. Weekly we sample 200 traces, run error analysis, and add new failures as golden-v2."
---

Teodora Kessler, Head of AI Quality at Gannet Home Energy (a fictional company), asks you for a plan she can take to her steering group. Gannet is building a **Home Move agent**. Customers moving house will use it to give final meter readings, close the old account, open one at the new address, book a meter engineer and get any credit balance refunded. It can write to accounts and trigger refunds of up to $150. It launches in eight weeks and has **no traffic yet**.

Write the eval plan. It's a design exercise in the style of an applied AI system design round, and it draws on every lesson in this module and on module E4. Name mechanisms and numbers. "We'll monitor quality" doesn't count as a plan.

## What a strong plan has

- Launch numbers that someone signed up to, including reliability, safety and cost.
- Cases from real seeds, varied deliberately, with a frozen test set.
- End-state grading in a sandbox, a few trajectory rules that are policies, and simulated users.
- Statistics that survive the follow-up "how sure are you?"
- Gates in CI and at release, an adversarial suite, and a loop that turns production failures into new cases.

Keep it to the word limits. A reviewer should be able to run this plan, not just agree with it.
