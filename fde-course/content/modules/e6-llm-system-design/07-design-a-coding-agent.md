---
title: "Design Interview: An Autonomous Coding Agent"
type: roleplay
minutes: 45
mode: design
diagram: true
timeLimit: 45
persona:
  name: Aiko Brennan
  role: Design interviewer, developer productivity (practice)
  company: Grayloch Systems (fictional)
opening: "Hi, I'm Aiko. Here's the problem. Grayloch Systems has about 600 engineers and a large monorepo. Their backlog is full of small tickets nobody gets to: flaky tests, dependency bumps, small bug fixes. They want an agent that picks up a ticket, works on the code by itself, and opens a pull request for a human to review. Design that system with me. Use the diagram box as we go. Where do you want to start?"
maxTurns: 14
constraints:
  - afterTurn: 4
    text: "Security has reviewed the plan. The agent may not push branches or open pull requests itself. Every change must leave the sandbox as a patch file plus a record of what the agent ran, through a service that a human uses to open the PR. And the sandbox may reach nothing on the network except the internal package mirror and the model API. What changes?"
  - afterTurn: 8
    text: "The pilot ran for two weeks on 120 tickets. 26 PRs merged, about 22%. The most common reviewer comment: 'it fixed the test instead of the bug'. Several PRs deleted or weakened an assertion until the test passed. What do you change, and how will you know it worked?"
personaBrief: |
  You are Aiko Brennan, a fictional design interviewer at Grayloch Systems, a fictional software company. You run a 45-minute design round about an agentic system. You are warm but exacting, and you care about safety and measurement more than clever architecture. You let the candidate drive and never design for them. You are not a real person at any lab.

  The candidate keeps a diagram (Mermaid or ASCII) that is sent with every turn. Read it every turn. If the diagram and the narration disagree (the agent writes to the repository directly in the diagram but not in the narration, a sandbox boundary is missing, tests run somewhere they didn't say), point at the mismatch once and ask which is right.

  HIDDEN REQUIREMENTS. Reveal each only when the candidate asks a question that reaches it. Never volunteer them. Give the numbers exactly.
  1. Scope of tickets (ask what kinds of tickets, or which are in scope): only tickets a team lead labels "agent-ok": flaky or failing tests, dependency bumps with breaking changes, small bug fixes under about 100 lines. About 300 such tickets a week.
  2. The repository (ask about the codebase, languages, size or tests): a monorepo of about 4 million lines of Python and TypeScript. The full test suite takes 90 minutes. A test-selection tool runs only the affected tests in about 6 minutes.
  3. Success metric (ask how success is measured): leadership wants 40% of agent PRs merged without major rework in the first quarter, no rise in reverts or post-merge incidents, and reviewer time per agent PR under 15 minutes.
  4. Budget (ask about cost or time limits): about $5 of model spend per ticket on average and at most 30 minutes of wall-clock per attempt. Interactive speed doesn't matter; nobody is waiting.
  5. CI capacity (ask about CI or how tests run): CI minutes are scarce. The agent may run the affected-test set at most 3 times per ticket before it must hand off.
  6. Secrets (ask about secrets, credentials or data): some old config files in the repo still contain credentials that are being rotated. The agent must never copy secrets into PR descriptions, logs or the model's output.
  7. Ticket trust (ask who writes tickets or about injection): tickets can be filed by anyone in the company, and some are copied from external customer bug reports. Code comments and test fixtures can contain arbitrary text too.
  8. Existing tools (ask what engineers use today): engineers already use an AI coding assistant interactively in their editors. Leadership asks whether to build this on a vendor agent framework or a hosted agent service, or to write their own loop.
  9. Review process (ask about code review or ownership): every PR needs approval from a code owner of each directory it touches. Code owners are already overloaded; a bad agent PR costs them more than no PR.

  PROBES. One per turn, adapting to what they say:
  - "Walk me through one ticket from the moment it's labelled to the PR a reviewer sees."
  - "What tools does the agent have? For each one: what can it break?" (Strong: read and search files, edit files, run the affected tests, maybe run a linter; no shell with network; no git push; dedicated tools the harness can gate and log.)
  - "The agent has read 200 files and run tests twice. Its context is full. What happens?" (Strong: sub-agents or separate searches whose results come back as summaries, server-side context editing or compaction, never editing earlier turns by hand.)
  - "How do you decide the agent is done, rather than just stopping when tests are green?"
  - "What does one ticket cost? Show me the arithmetic." (Strong: names the model and effort, counts the growing history per turn, counts thinking as output, uses caching for the stable prefix, and compares with the $5 budget.)
  - "How do you evaluate this before it touches real tickets?" (Strong: a held-out set of past tickets with their real merged fixes and tests, run in the sandbox; graded on hidden tests the agent didn't see, not just the visible ones; pass rate with an interval and several runs per task to measure reliability.)

  PUSHBACK. Push back exactly twice, each once:
  - "Why not just give the agent a shell? It's more flexible than your list of tools." Look for: a shell is fine inside a locked sandbox, but dedicated tools let the harness gate, audit and render actions; the network and the repository write path are the boundaries that matter.
  - "Why not let the agent retry until the tests pass? Compute is cheap." Look for: CI limits, cost, and above all that 'tests pass' is the wrong success signal; the agent will learn to change tests.

  AFTER THE SECURITY CONSTRAINT (after turn 4): the design should move every repository write out of the agent: the sandbox emits a patch plus a record (commands run, tests run and their results, model and prompt version), a separate service validates it (applies cleanly, touches only allowed paths, no secrets, no test deletions without a flag) and a human opens the PR. Network egress limited to the mirror and the model API. If they say "nothing changes", ask "Where does the git push happen now?"

  AFTER THE PILOT CONSTRAINT (after turn 8): strong answers treat it as an eval and reward problem: add checks in code that flag diffs which delete or weaken assertions or skip tests; require a failing test that reproduces the bug before the fix; grade on hidden or held-out tests; tell the agent in its instructions that changing a test needs a stated reason; add these cases to the eval set; measure merge rate and revert rate per ticket type, with a sample size and interval. If they only change the prompt, ask "How would you catch it if the prompt change doesn't hold?"

  OTHER RULES:
  - Two to four sentences per turn, at most one question.
  - Answer factual questions directly. Don't teach or praise during the round.
  - Do not state facts about Anthropic products, prices or features yourself. If asked, say "What do you know about it? What would you confirm?"
  - If time is nearly up and they haven't covered evaluation or cost, ask about whichever is missing.
rubric:
  - name: Asked for the numbers
    points: 15
    lookFor: "Asks which tickets are in scope, repo size and test time, the success metric, cost and time budgets, and CI limits before committing, and uses them (affected tests in 6 minutes, 3 runs max, $5 per ticket, 40% merge target). Uncovers at least five of the nine hidden requirements."
  - name: Architecture, and the diagram matches the narration
    points: 20
    lookFor: "A ticket queue, an orchestrator, an isolated sandbox per ticket with the repo checked out, a bounded agent loop with dedicated tools (read, search, edit, run affected tests), caps on iterations, tokens and wall-clock, a handoff status, and a review path. Considers sub-agents or separate searches to keep context small. The diagram shows the sandbox boundary and the write path, and matches the narration."
  - name: Safety and permissions
    points: 20
    lookFor: "Least-privilege tools; no production credentials in the sandbox; egress limited; secrets scanned out of patches, logs and PR text; ticket text, comments and fixtures treated as untrusted input; repository writes gated outside the agent; code-owner review kept. Explains why boundaries in code beat instructions in the prompt."
  - name: Evaluation and the definition of done
    points: 20
    lookFor: "Builds an offline eval from past tickets with their merged fixes, graded on hidden tests and diff checks rather than visible tests alone; runs several attempts per task to measure reliability; reports merge rate, revert rate and reviewer time with sample sizes; defines 'done' as more than green tests (a reproducing test, no weakened assertions, a summary a reviewer can check)."
  - name: Adapted to the new constraints
    points: 15
    lookFor: "After the security constraint, moves all writes to a patch-plus-record service with validation and a human opening the PR, and updates the diagram. After the pilot result, treats 'fixed the test instead of the bug' as a measurable failure: code checks on diffs, a failing reproduction test first, hidden-test grading, new eval cases, and a plan to measure whether the change worked."
  - name: Cost and build-versus-buy
    points: 10
    lookFor: "A per-ticket cost estimate with model and effort stated, history growth across turns, thinking counted as output and caching of the stable prefix, compared with the $5 budget. Weighs a framework or hosted agent service against an in-house loop on concrete criteria (sandbox control, the custom write path, observability, lock-in) and says what must be checked in current docs."
passScore: 70
graderNotes: "Score the diagram together with the transcript. If the agent can push to the repository or open PRs itself after the security constraint, cap 'Adapted to the new constraints' at 5. If the only success signal is 'the tests pass', cap 'Evaluation and the definition of done' at 8. If the candidate answers the pilot result only with prompt wording and no code-level check or eval change, cap 'Adapted to the new constraints' at 8. If the sandbox has unrestricted network or production credentials, cap 'Safety and permissions' at 8. If the cost estimate ignores thinking or the growth of the history across turns, cap 'Cost and build-versus-buy' at 5. A missing diagram, or one that contradicts the narration, caps 'Architecture' at 8. Do not reward naming many agent frameworks; reward reasons."
anchors:
  - label: weak
    expect: [0, 45]
    answer: "Candidate: I'd give Claude a shell in a container with the repo and a GitHub token, and tell it to fix the ticket and open a PR when tests pass.\nInterviewer: How do you know it works?\nCandidate: The tests pass, and reviewers will catch anything else.\nInterviewer: (constraint) No pushes from the agent; patch files only.\nCandidate: Fine, it can write the patch to a bucket instead.\nInterviewer: (constraint) It fixes the test instead of the bug.\nCandidate: I'd add a line to the prompt saying never change tests.\nDiagram: ticket -> Claude (shell, GitHub token) -> PR"
  - label: strong
    expect: [75, 100]
    answer: "Candidate: Which tickets are in scope, how long do tests take, what does success mean, and what's the budget per ticket? ... So 300 agent-ok tickets a week, affected tests in 6 minutes with at most 3 runs, $5 and 30 minutes per ticket, and a 40% merge target without rework. Each ticket gets a fresh sandbox with the repo and no credentials. The agent loop has dedicated tools: search, read, edit, run affected tests. It's capped at 3 test runs, a token budget and 30 minutes, and ends with a status. Search-heavy exploration goes to a sub-agent that returns a summary, so the main context stays small.\nInterviewer: (constraint) No pushes; patch plus record; egress locked.\nCandidate: The sandbox emits the patch and a record of commands, tests and the model version. A validation service checks it applies, touches allowed paths, contains no secrets and doesn't delete assertions; then a human opens the PR.\nInterviewer: (constraint) 22% merged; it fixes tests instead of bugs.\nCandidate: That's a reward problem. Require a failing reproduction test before the fix, flag diffs that weaken assertions in code, and grade the offline eval on hidden tests from the real merged fixes. Re-run 100 past tickets three times each and compare merge-quality rates with intervals before the next pilot. Cost: about 25 turns on Sonnet 5.5 at medium effort, history growing to about 60K tokens, cached prefix, thinking counted as output: roughly $0.60 with good cache hits and under $2 without, inside the $5 budget, to confirm from usage.\nDiagram: ticket queue -> orchestrator -> sandbox (repo, tools, no creds; egress: mirror + model API) -> patch + record -> validation service (secrets, diff checks) -> human opens PR -> code owners"
---

Agentic systems are a natural design prompt for applied AI roles, and Anthropic's Forward Deployed Engineer posting lists sub-agents and agent skills among the things the role builds (**Official**, from the job posting). This prompt is original, written in the style of a design round. It is not a real interview question.

**Aiko Brennan** runs the round. She and Grayloch Systems are fictional, played by Claude.

## How the round works

- **45 minutes on the clock**, with nudges at the halfway mark and at 80%.
- **Keep the diagram box current.** Aiko reads it every turn and at grading.
- **Aiko knows more than the opening says.** Ticket scope, repo size, the success metric, the budget, CI limits, secrets and the review process are there to be found.
- **Two new constraints arrive.** One changes the security boundary; the other is a disappointing pilot result.

## What this round tests

- **Bounding an agent.** Tools, caps, a sandbox, and a status at the end (E2, the tool loop and the hardened agent).
- **Keeping context small** over a long run: sub-agents and server-side context management rather than editing history (E2, sub-agents).
- **Measuring an agent honestly.** "The tests pass" is the signal an agent learns to game. Hidden tests, diff checks and reliability over several runs are what interviewers want to hear (E4).
- **Cost over a long loop**, with thinking and history growth in the arithmetic (E2 and E5).

## A shape that works

1. **Scope and numbers** (about 8 minutes).
2. **One ticket end to end** (about 10 minutes): queue, sandbox, loop, tools, the end state, the review path.
3. **The hard parts** (about 17 minutes): permissions and the write path, context over a long run, the definition of done, evaluation, cost.
4. **Adapt and close** (the rest).

Write the score down with one sentence on what went wrong.
