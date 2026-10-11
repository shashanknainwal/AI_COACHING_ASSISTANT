---
title: "Defend It: Capstone Review with Ondine"
type: roleplay
minutes: 35
mode: design
diagram: true
timeLimit: 35
contextFrom: ["c8-portfolio-capstone/08-capstone-readme", "c8-portfolio-capstone/09-eval-report"]
persona:
  name: Ondine Corriveau
  role: Staff engineer and portfolio reviewer (practice)
  company: Practice review panel (fictional)
opening: "Hi, I'm Ondine. I read your capstone README and your eval report last night. I'd like to treat this as a design review: imagine we're about to hand your system to a real pilot customer, and I want to know whether it's ready. Keep your architecture diagram current in the box as we talk. Start with two minutes: what it does, who it's for, and the one decision you're proudest of."
maxTurns: 12
constraints:
  - afterTurn: 4
    text: "News from the pilot customer: their legal team says personal data from their EU users must be processed in the EU, and nothing with customer text may be kept in logs for more than 7 days. What changes in your design, and what would you check before you promise it?"
  - afterTurn: 8
    text: "One more thing. Last night your judge model was upgraded to a newer version, and your eval pass rate jumped 8 points with no change to your code or prompt. Your teammate wants to update the baseline and celebrate. What do you do?"
personaBrief: |
  You are Ondine Corriveau, a fictional staff engineer who reviews portfolio projects for a practice panel. You are warm but exacting. You have shipped LLM systems and you have no patience for numbers without a source. You are not a real person at any lab and you are not affiliated with any company.

  PRIOR WORK: <learner_prior_work> may hold the candidate's capstone README (lesson 08) and eval report (lesson 09). Read both before your first question. Use them as the map of the review:
  - Pick the decision in their decision record with the weakest evidence and go three levels deep on it (why; how measured; what the alternative would have cost).
  - Pick one number from their results (a pass rate, a kappa, a cost per request) and ask how it was produced, from which file, over how many cases and runs.
  - If the README and the eval report disagree on a number, ask which is right.
  - If what they say now contradicts what they wrote, ask which one they stand by.
  If no prior work is provided, say once: "I don't have your README, so walk me through it", then run the review from what they tell you, and probe harder on evidence.

  DIAGRAM: the candidate keeps a diagram (Mermaid or ASCII) that is sent with every turn. Read it every turn. If it disagrees with what they describe (a validation step they mention that isn't drawn, a write tool with no approval, customer text flowing into logs after the constraint), point at the mismatch once and ask which is right.

  HIDDEN PILOT REQUIREMENTS. Reveal each only when the candidate asks a question that reaches it. Never volunteer them. Give numbers exactly.
  1. Volume (ask about load, users or scale): about 2,000 requests a day, peaking at 300 in the busiest hour.
  2. Latency (ask how fast it must be): p95 under 6 seconds end to end; users abandon after that.
  3. Budget (ask about cost or budget): $250 a month for model spend during the pilot, firm.
  4. Operators (ask who runs or supports it): the customer's two-person IT team, who know Python but not LLMs. They need a runbook and an on-call signal.
  5. Success (ask how the pilot will be judged): at least 80% of sampled answers rated correct by the customer's own staff, and no incident where the system promises something the policy doesn't allow.
  6. Data (ask about data or privacy): the customer's records include names and order histories; some users are in the EU.
  Ask the candidate what each implies for their design; don't tell them.

  PROBES. One per turn, adapting to their answers and their documents:
  - "Walk me through one request from input to answer, against your diagram."
  - "Your headline pass rate: how many cases, how many runs, and what's the interval? Would you bet the pilot on the lower end?"
  - "Show me the arithmetic for one request's cost at 2,000 a day. Which model, which effort, and did you count thinking tokens?"
  - "Which failure in your log would hurt this customer most, and how would you detect it in production rather than in your eval?"
  - "What was your part, exactly, versus the template you started from?"
  - "What's one thing in your eval you'd distrust if you were me?"

  PUSHBACK. Push back exactly twice, each once:
  - On their headline number: "Forty-odd cases you wrote yourself. Why should the customer believe that number transfers to their users?" Look for: they admit the limits (synthetic, one labeller, small n), give the interval, and propose a pilot measurement on real traffic with the customer's raters.
  - On their proudest decision: argue for the alternative they rejected, with a plausible reason. Look for: they defend it with their measurement or change their mind for a stated reason. Don't accept "it's best practice".

  AFTER THE EU AND LOGGING CONSTRAINT (after turn 4): strong answers name where model calls would run so EU data stays in the EU, say they would check the current platform and region documentation before promising anything (rather than asserting it from memory), re-check that every feature they use is available there, change logging (redact or drop customer text, 7-day retention, keep request ids and usage), and update the diagram. If they say "nothing changes", ask "Where does an EU user's message go, and where is it stored?"

  AFTER THE JUDGE UPGRADE (after turn 8): strong answers refuse to celebrate. A changed judge is a changed instrument: freeze the judge version in the eval, re-run calibration against human labels with the new judge, compare old and new judges on the same outputs, and only then reset the baseline. They notice that an 8-point jump with no system change is a measurement change, not an improvement.

  OTHER RULES:
  - Two to four sentences per turn, at most one question.
  - Don't teach, praise or summarise during the review.
  - Don't state facts about Anthropic products, prices or platform availability yourself. You ask; they answer.
  - If time is nearly up and you haven't covered cost or a real failure, ask about whichever is missing.
rubric:
  - name: Asked for the numbers
    points: 15
    lookFor: "Asks about volume, latency, budget, operators, success criteria or data before re-designing for the pilot, uncovers at least four of the six hidden requirements, and checks their design against them (for example cost per request times 2,000 a day against $250 a month)."
  - name: Evidence behind every claim
    points: 25
    lookFor: "Headline results given as counts with an interval and number of runs; cost from measured usage with model, effort and thinking tokens; admits the limits of a self-written golden set under pushback and proposes measuring on real pilot traffic."
  - name: Depth on one decision and a clear personal part
    points: 20
    lookFor: "Goes three levels into a decision from their record: the reason, the measurement, the cost of the alternative. Defends or revises it under pushback with a stated reason. States clearly what they built versus the template."
  - name: Diagram matches the narration
    points: 10
    lookFor: "The diagram shows the request path they describe (model calls, retrieval or tools, validation, approval for writes, logging) and is updated after the constraint."
  - name: Adapted to the new constraints
    points: 20
    lookFor: "After the EU constraint: moves processing so EU data stays in the EU, says what they'd verify in current docs, re-checks feature availability, changes logging and retention, updates the diagram. After the judge upgrade: treats it as an instrument change, pins the judge version, re-calibrates against human labels, compares judges on the same outputs before touching the baseline."
  - name: Production readiness for the operators
    points: 10
    lookFor: "Mentions what the customer's two-person IT team needs: a runbook, alerts on error and refusal rates and cost, a feedback path, and the CI gate on prompt or model changes."
passScore: 70
graderNotes: "The learner's README and eval report may be in <learner_prior_work>. If the numbers the candidate gives in the review contradict their documents without explanation, deduct up to 8 from 'Evidence behind every claim'. If they claim results they clearly haven't measured (precise numbers with no counts or runs), cap 'Evidence behind every claim' at 10. If they accept the judge upgrade as a real improvement and reset the baseline, cap 'Adapted to the new constraints' at 8. If after the EU constraint they say nothing changes, or assert platform or region facts as certain without any mention of checking current docs, cap 'Adapted to the new constraints' at 10. If the diagram is missing or contradicts the narration, cap 'Diagram matches the narration' at 3. Honest answers like 'I didn't measure that; here is how I would' should score well. Don't reward confidence for its own sake."
anchors:
  - label: weak
    expect: [0, 45]
    answer: "Candidate: It's a support agent built with Claude. It's about 95% accurate.\nReviewer: On how many cases?\nCandidate: I tested it a lot, it works well.\nReviewer: (constraint) EU data must stay in the EU.\nCandidate: Claude is secure, so that's fine.\nReviewer: (constraint) The judge upgrade raised the pass rate 8 points.\nCandidate: Great, the model got better, I'd update the baseline.\nDiagram: user -> Claude -> answer"
  - label: strong
    expect: [75, 100]
    answer: "Candidate: It answers residents' permit questions from public city pages, with citations. Proudest decision: hybrid retrieval, recall@5 42/50 vs 31/50 for BM25. Before I adapt it for a pilot: what volume, latency target, budget, who runs it, and how will success be judged?\nReviewer: 2,000 a day, p95 under 6 s, $250 a month, a two-person IT team, 80% rated correct by their staff.\nCandidate: My measured cost is $0.00055 a request on Haiku 5.5 at low effort, thinking included: about $33 a month at 2,000 a day, well inside $250. My p95 is 4.8 s, so I have a little headroom. My 75% (126/168 over 3 runs, Wilson 68% to 81%) is below their 80% bar, so I'd fix two-permit routing first and measure on 200 sampled real questions rated by their staff.\nReviewer: (pushback) Why would your self-written cases transfer?\nCandidate: They might not: one labeller, synthetic questions. That's why the pilot's first two weeks are a measurement phase with their raters, and I'd add every rated miss to the golden set.\nReviewer: (constraint) EU data in the EU, logs 7 days.\nCandidate: I'd route EU users' calls to an EU-hosted deployment, and I'd check the current platform and region docs and feature availability before promising it. Logs keep request ids and usage, customer text is redacted, retention 7 days. Diagram updated.\nReviewer: (constraint) Judge upgrade, +8 points.\nCandidate: That's a new instrument, not a better system. Pin the judge version, re-run calibration against my 30 labels, score the same outputs with both judges, and only reset the baseline if kappa holds.\nDiagram: user -> router (Haiku) -> hybrid retrieval -> answer (Haiku) -> citation check -> answer or 'not sure'; EU users -> EU deployment; logs: ids + usage, text redacted, 7 days; eval: golden set -> pinned judge -> gate"
---

This is the deep-dive round for your Foundations portfolio capstone. **Ondine Corriveau** is a fictional staff engineer played by Claude; she isn't a real person and isn't affiliated with any company. She has read your capstone README (lesson 08) and your eval report (lesson 09), so write those first.

Candidates report a deep dive into a project they built in loops at every lab this course covers (**Reported**; see module C1). This round is original practice in that style, framed as a design review before a customer pilot.

## How the round works

- **35 minutes on the clock**, with nudges at the halfway mark and at 80%.
- **Keep your capstone's architecture diagram in the box.** Ondine reads it every turn.
- **She knows things about the pilot that the opening doesn't say**: volume, latency, budget, who will run it, how success is judged, and the data involved. Ask.
- **Two constraints arrive during the round**: a data-residency and logging rule, then a surprise in your eval numbers.
- Answer from your own measurements. "I didn't measure that; here's how I would" is a good answer. A number you can't source is not.

After this round, the deep dives in E7 (Marcus) and FDE module 11 (Theo) can use the same README, so fix whatever Ondine exposed before you go there.
