---
title: "Before Round 3: Your Six-Line Project Summary"
type: written
minutes: 15
sections:
  - key: system
    label: 1. The system and your part
    prompt: "One sentence on what the LLM system did and who used it, with one number for scale. Then what you personally built or decided, in the first person."
    words: [30, 120]
  - key: evals
    label: 2. Evals
    prompt: "What was in the eval set, how big it was, where the cases came from, and how outputs were graded. If there were no evals, say so."
    words: [20, 100]
  - key: failure
    label: 3. A failure
    prompt: "One thing that broke in front of users: what broke, how you noticed, what you changed."
    words: [20, 100]
  - key: numbers
    label: 4. Cost and latency
    prompt: "Rough cost per request and response time, and where those numbers come from (usage logs, a dashboard, an estimate)."
    words: [15, 80]
  - key: decision
    label: 5. The decision you'd defend
    prompt: "Your most important design decision, the option you rejected, and why. Include the number or test that convinced you, if there was one."
    words: [20, 120]
rubric:
  - name: A real system with a clear part
    points: 25
    lookFor: "Says what the system did, for whom and at what scale, and separates what the candidate did from what the team did."
  - name: Evals described concretely
    points: 25
    lookFor: "Where the cases came from, how many, what 'correct' meant and how grading worked. An honest 'we had none' with a specific plan scores well; vague claims of testing do not."
  - name: A specific failure
    points: 20
    lookFor: "One failure in front of users with how it was detected and what changed."
  - name: Numbers with sources
    points: 15
    lookFor: "Cost and latency given with their source or arithmetic. 'I didn't measure' is acceptable if stated plainly."
  - name: A decision with evidence
    points: 15
    lookFor: "Names the decision, the rejected alternative and the reason, ideally with the measurement behind it."
passScore: 70
graderNotes: "This is preparation for a deep dive, so grade honestly but kindly: the point is to expose gaps before Marcus does. Mark down 'we' throughout with no personal part, any precise number with no source, and an eval line that says only 'we tested it'. Do not penalise a candidate who says plainly they are using a course or portfolio project; cap 'A specific failure' at 12 if the project never had real users. If the summary includes what looks like a real customer's confidential details, say so and cap 'A real system with a clear part' at 10."
anchors:
  - label: weak
    expect: [0, 45]
    answer: "System: we built an AI chatbot for customers using RAG and GPT/Claude. Evals: we tested it a lot and it worked well. Failure: sometimes it hallucinated. Cost: cheap. Decision: we used RAG because it's best practice."
  - label: strong
    expect: [75, 100]
    answer: "System: an internal assistant answering HR policy questions for about 1,200 employees, around 300 questions a day. I built the retrieval pipeline and the eval harness; a teammate built the chat UI. Evals: 180 questions from real search logs, labelled by two HR specialists; correctness graded by a Claude judge checked against their labels (kappa 0.71 on 100 cases). Failure: after a policy update, answers cited the old version for two days; a user reported it. I added version filtering at index time and a freshness check to the eval. Numbers: about $0.011 per question from usage logs on Sonnet 5.5 at low effort; p95 2.8 s to first token from our tracing. Decision: 500-token chunks instead of 1,000; recall@8 on the eval set went from 78% to 86%, measured once, which I'd now repeat on a larger set."
---

Marcus reads this before Round 3. Write it the way you'd brief an interviewer the night before a deep dive: short, specific, honest. He uses it to skip the basics and drill straight into one decision, three or four questions deep, so every number you write here is a number he'll ask about: where it came from, who measured it, and what it looked like before.

Pick **one** LLM system you actually built or contributed to substantially. Anthropic's [candidate AI guidance](https://www.anthropic.com/candidate-ai-guidance) draws the line at inventing experience (**Official**). If you haven't shipped an LLM system yet, use the portfolio capstone from the Foundations track (a real project, built against the real API in your own repository) and say so. Keep customer names and confidential details out.

Write it yourself, without AI help: it's the raw material for a round where you can't use any.

Marcus Feld is a fictional practice interviewer played by Claude.
