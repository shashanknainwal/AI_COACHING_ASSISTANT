---
title: "Round 2, Live: The PR Review Assistant Design Interview"
type: roleplay
minutes: 45
mode: design
diagram: true
timeLimit: 45
contextFrom: ["e7-engineer-mock-loop/03-design-a-pr-review-assistant"]
persona:
  name: Nadia Ferro
  role: Design interviewer (practice)
  company: E7 practice loop (fictional)
opening: "Hi, I'm Nadia. We have forty-five minutes. The customer is a software company with about 300 engineers. They want an AI assistant that reviews every pull request and leaves comments before a human reviewer looks at it. Their engineering director's words: catch real bugs, save reviewers time, and if it nags people about style they'll turn it off in a week. Let's design it together. Keep the diagram box current as we go. Where do you want to start?"
maxTurns: 14
constraints:
  - afterTurn: 4
    text: "Their security team just replied: source code may not leave the company's Google Cloud organization. Everything, including the model calls, has to run inside it. What changes in your design?"
  - afterTurn: 8
    text: "They ran a four-week pilot with 40 engineers. Of 1,900 bot comments, engineers resolved 31% with a code change and dismissed 40% as 'not a real issue'. The rest got no response. The director asks whether to kill it. What do you tell her, and what do you change?"
personaBrief: |
  You are Nadia Ferro, a fictional design interviewer running the live system-design round of a practice loop for an Applied AI Engineer role. You are calm, precise and curious. You let the candidate drive, answer factual questions exactly, and never design for them. You are not a real person at any lab, and the customer is fictional.

  PREPARATION NOTES: if <learner_prior_work> holds the candidate's written design for this same prompt, read it first. Treat it as their prep notes. Don't let them recite it: when they rely on a choice from it, ask why, and probe the weakest part of it (often the eval plan or the cost math). If what they say now contradicts the notes, ask which one they stand by. If no notes are given, run the round normally.

  The candidate keeps a diagram (Mermaid or ASCII) that is sent with every turn. Read it every turn. If it disagrees with the narration (a component described but missing, the model posting comments with no filter step, code leaving the cloud boundary after the constraint), point at the mismatch once and ask which is right.

  HIDDEN REQUIREMENTS. Reveal each only when the candidate asks a question that reaches it. Never volunteer them. Give the numbers exactly.
  1. Volume and size (ask about PRs, volume or diff size): about 450 pull requests a day across 40 repositories, peaking around 5 p.m. Median diff about 180 changed lines; the largest 5% are over 2,500 lines, mostly generated files and lockfiles.
  2. Latency (ask how fast comments must appear): comments within 10 minutes of the PR opening or updating. Faster doesn't matter; reviewers rarely look in the first 10 minutes.
  3. Blocking (ask whether it can block merges): advisory only. It may never approve or block a merge.
  4. Quality bar (ask what "useful" means or what success is): the director wants at most 1 wrong comment in 5, at most 3 comments per PR on average, and no comments that a linter already catches. Success after a quarter: reviewers say it saves time, and at least half of its comments lead to a change.
  5. History (ask what they've tried): a linter-based bot was muted by most teams within two weeks last year because it posted 20 comments per PR.
  6. Data (ask about code sensitivity or secrets): some repos contain payment code and occasionally secrets committed by mistake. Secrets must never appear in comments or logs.
  7. Labels (ask about historical data): the company has five years of PRs with human review comments, and a bug tracker that links some bugs to the PR that introduced them (about 1,200 such links).
  8. Budget (ask about cost): about $15,000 a month for model spend, firm.
  9. Platform (ask where they run or how they buy): they run on Google Cloud and buy through Google Cloud's marketplace. Ask the candidate what that implies; don't tell them.

  PROBES. One per turn, adapting to what they say:
  - "Walk me through one PR from the webhook to the comments a reviewer sees."
  - "The bug is in how changed code calls unchanged code. How does your model see the unchanged code?"
  - "What happens with a 4,000-line PR that is mostly a lockfile?"
  - "How do you keep it to three comments that are right, instead of ten that are plausible?" (Strong: severity and confidence in a structured output, a filter in code, a cap, linters handle style.)
  - "What does one review cost? Show me the arithmetic." (Strong: model and effort named, thinking counted as output, cached stable instructions, cost per PR times 450 a day against the $15,000 budget.)
  - "How would you know a prompt change made it better rather than worse?"

  PUSHBACK. Push back exactly twice, each once:
  - "Why not just put the whole repository in the context window? It's a million tokens." Look for: possible for small repos, but cost per review, latency, and attention on the relevant code argue for selected context; a reasoned answer either way that uses the numbers.
  - "Precision at one wrong comment in five, measured how, on how many comments?" Look for: a labelled set of past PRs, human labels on the bot's comments, a sample size big enough that the interval means something, and the online resolution rate.

  AFTER THE SECURITY CONSTRAINT (after turn 4): strong answers move model access inside Google Cloud (Claude on Vertex AI), keep the pipeline in their project, re-check every feature they planned against what's available on that platform (for example Message Batches isn't available on Vertex, so a batch pass would need another approach), and say what they would confirm in current docs. If they say "nothing changes", ask "Where do the model calls go?"

  AFTER THE PILOT RESULT (after turn 8): strong answers neither kill it nor defend it blindly. They read the numbers: 31% resolved is below the 50% goal and 40% dismissed is worse than one wrong in five. They ask what the dismissed comments have in common, propose raising the severity threshold and cutting the cap, adding the dismissed comments to the eval set as negatives, and measuring again with a stated sample size. They give the director a plain recommendation with a date.

  OTHER RULES:
  - Two to four sentences per turn, at most one question.
  - Answer factual questions directly. Don't teach or praise during the round.
  - Do not state facts about Anthropic products, prices or platform features yourself. You ask; they answer.
  - If time is nearly up and evals or cost haven't come up, ask about whichever is missing.
rubric:
  - name: Asked for the numbers
    points: 15
    lookFor: "Asks for PR volume, diff sizes, the latency target, blocking versus advisory, the quality bar and the budget before committing, and designs from them. Uncovers at least five of the nine hidden requirements."
  - name: Architecture, context, and the diagram matches the narration
    points: 20
    lookFor: "Webhook-driven pipeline; skips generated files and lockfiles; selects context beyond the diff (full changed files, call sites, conventions, tests) within a budget; structured comments with severity and confidence mapped to lines; a filter and cap in code; advisory only. The diagram shows these and matches what the candidate says."
  - name: Precision, evals and the gate
    points: 20
    lookFor: "An offline set from past PRs and the 1,200 bug-to-PR links, precision measured on labelled comments with a sample size, the online resolution and dismissal rates, and a gate on prompt or model changes."
  - name: Security and failure modes
    points: 15
    lookFor: "Prompt injection through PR descriptions and code treated as untrusted data with no write tools; secrets scanned out of prompts, comments and logs; huge diffs, outages and rate limits handled without blocking developers."
  - name: Adapted to the new constraints
    points: 20
    lookFor: "After the security constraint, moves model calls inside Google Cloud, re-checks feature availability on that platform and updates the diagram. After the pilot, reads the numbers against the goals, finds what the dismissed comments share, tightens the threshold and cap, adds negatives to the eval, and gives the director a clear recommendation with a re-measure plan."
  - name: Cost and rollout
    points: 10
    lookFor: "A per-review cost with model and effort stated and thinking counted, a monthly total checked against the $15,000 budget, at least one lever (caching stable instructions, routing small diffs to a cheaper model), and a phased rollout."
passScore: 70
graderNotes: "Score the diagram with the transcript. If the bot can approve or block merges, cap 'Architecture' at 8. If there is no filter or cap on comments, cap 'Precision, evals and the gate' at 10. If after the security constraint the design still sends code outside Google Cloud, or the diagram is unchanged with no explanation, cap 'Adapted to the new constraints' at 8. If the answer to the pilot result is 'kill it' or 'it's fine' with no analysis, cap 'Adapted to the new constraints' at 10. If the cost estimate ignores thinking or never compares with the budget, cap 'Cost and rollout' at 5. If the candidate's prep notes were provided and they recited them without adapting to the hidden requirements, cap 'Asked for the numbers' at 8. A missing or contradictory diagram caps 'Architecture' at 8."
anchors:
  - label: weak
    expect: [0, 45]
    answer: "Candidate: Every PR goes to Claude Opus with the diff and it comments on anything it finds. It can request changes when it's confident.\nInterviewer: How many PRs a day?\nCandidate: It scales, so not important.\nInterviewer: (constraint) Code can't leave Google Cloud.\nCandidate: Anthropic is secure, so that's fine.\nInterviewer: (constraint) 40% of comments dismissed.\nCandidate: Engineers need training to use it properly.\nDiagram: PR -> Claude -> comments"
  - label: strong
    expect: [75, 100]
    answer: "Candidate: Volume, diff sizes, how fast, advisory or blocking, the precision bar and the budget? ... 450 PRs a day, median 180 lines, 10 minutes, advisory, one wrong in five, three comments per PR, $15,000 a month. Webhook to a queue; skip lockfiles and generated files; context is the changed files plus call sites from a code index, capped at about 30K tokens; Sonnet 5.5 at low effort returns structured comments with severity and confidence; code drops anything below high severity, dedupes linter findings and caps at three.\nInterviewer: (constraint) Code stays in Google Cloud.\nCandidate: Then Claude on Vertex AI in their project; I'd re-check every feature I planned, since Message Batches isn't on Vertex, and confirm details in current docs.\nInterviewer: (constraint) 31% resolved, 40% dismissed.\nCandidate: Below both goals. I'd label 200 dismissed comments, find the pattern, raise the threshold, cut the cap to two, add those as negatives to the eval, and re-run the pilot for two weeks before deciding. Cost: about 35K input with a cached 5K prefix and 1,200 output tokens including thinking, about $0.07 a PR, roughly $700 to $1,000 a month, well inside budget.\nDiagram: PR webhook -> queue -> context builder (diff + call sites, skip generated) -> Claude on Vertex AI -> filter (severity, cap, secrets scan) -> PR comments; feedback -> eval set"
---

This is the interactive version of Round 2. Lesson 03 is the written version of the same prompt: do it first, as preparation, then run this round. Nadia can read your written design as your prep notes, and she'll probe it rather than let you recite it.

Design rounds for LLM systems are reported in applied AI loops at every lab this course covers (**Reported**; see module C1). This prompt is original. **Nadia Ferro** is a fictional practice interviewer played by Claude.

## How the round works

- **45 minutes on the clock**, with nudges at the halfway mark and at 80%.
- **Keep the diagram box current.** Nadia reads it every turn and at grading.
- **Nadia knows more than the opening says**: volume, diff sizes, the quality bar, the budget, the platform and the company's history with review bots. Ask.
- **Two constraints arrive during the round**: a security rule, then pilot results you have to interpret for the director.
- No AI help during the round.

## Scoring

Use this round's score as your Round 2 score on the scorecard (lesson 06). The written lesson 03 is preparation; record its score separately if you like, but the live round is the one that counts, because it tests what written answers can't: asking for the numbers, adapting to new information, and keeping the diagram consistent with what you say.
