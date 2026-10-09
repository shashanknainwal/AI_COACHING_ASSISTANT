---
title: "Reference Architecture: Coding Assistants and Developer Productivity"
type: reading
minutes: 20
---

> **By the end of this lesson** you'll be able to separate the three developer-productivity patterns (PR review, code search and Q&A, agentic coding), design each with the security and governance controls an enterprise will ask for, and estimate their cost, including why agentic coding costs grow faster than you expect without caching.

## Three patterns, not one

"We want AI for our developers" can mean three different systems with different risks:

| Pattern | What it does | Risk level | Typical buyer concern |
|---|---|---|---|
| **PR review** | Comments on pull requests: bugs, security issues, style, missing tests | Low: it only comments | Noise. Developers mute bots that cry wolf |
| **Code search and Q&A** | Answers "where is X handled?" and "how does Y work?" over the codebase | Low to medium: read-only, but code is sensitive | Where the code goes and who can see what |
| **Agentic coding** | Plans and makes changes, runs tests, opens PRs | Medium to high: it writes and executes | What it can touch, and who approves its work |

Most enterprises should start with the first two and add the third with guardrails. Your job is to separate them early, because a security team that hears "an agent that writes code" will review all three at the strictest level.

## When it fits

| Signal | Why it matters |
|---|---|
| Hundreds of engineers, steady PR flow | Volume makes per-PR savings add up |
| CI with meaningful tests | Agentic work needs a checker; reviews need a baseline |
| Code review is a bottleneck (PRs wait a day or more) | A first-pass review shortens the wait |
| Branch protection and required human review already exist | The governance to contain an agent is already in place |
| A clear policy on where source code may be processed | Without it, the project stalls in security review |

## Buy or build

For agentic coding, start from an existing tool before proposing a custom build. Anthropic's [Claude Code page](https://claude.com/product/claude-code) (checked 2026-10-08) describes a tool that runs in the terminal, in VS Code and JetBrains IDEs, on the web and desktop, works with GitHub and GitLab to read issues and open pull requests, asks permission before changing files or running commands, and runs locally talking directly to the model API "without requiring a backend server or remote code index". It also lists self-hosted environments in public beta and Team and Enterprise plans.

Build custom when the customer needs something a tool doesn't do: a PR reviewer that enforces their internal security standards, review comments routed into their own ticketing, or a code Q&A bot inside an internal developer portal. Those are straightforward on the Messages API. For admin controls, plan features and deployment options of any product, confirm with the vendor's current docs before you promise anything.

## Components and data flow

Fictional customer: **Larkfield Bank**, 1,500 engineers, 600 merged PRs a day, a strict change-management policy.

### PR review bot

1. **Trigger.** A webhook on PR open and on each new push.
2. **Pre-filter in code.** Skip generated files, lockfiles and vendored code. Run a secret scanner on the diff; if it finds a credential, block the review call and alert, so secrets never enter a prompt.
3. **Assemble context.** The diff, the full content of changed files, the files they import or that call them (one hop), and the team's review guidelines. Guidelines and instructions go first so they cache.
4. **Review.** The model returns structured findings: file, line, severity, category, explanation, suggested fix.
5. **Filter findings in code.** Drop low-severity style comments if linters already cover them; cap comments per PR (say 5); never repeat a comment the developer already resolved.
6. **Post** as review comments, clearly labelled as automated. The bot never approves and never blocks merging on its own.
7. **Measure** which comments developers resolve with a code change versus dismiss.

On later pushes, review only the new commits plus context, not the whole PR again. That's the biggest cost lever for this pattern.

### Code search and Q&A

This is the knowledge-assistant pattern (previous lesson) applied to code: index repositories by symbol and file structure, enforce repository permissions in retrieval (an engineer sees answers only from repos they can read), and cite file paths and line ranges. Keyword search matters more than usual, because identifiers are exact strings.

### Agentic coding

1. **Task intake.** An issue or a developer's request, with a scope ("in this repo, behind this feature flag").
2. **Sandboxed workspace.** A fresh checkout in an isolated environment. No production credentials, network egress limited to the package mirror and the model API.
3. **Agent loop.** The model reads code, edits files and runs tests in the sandbox. Tool permissions are an allowlist: build and test commands yes, deploy commands no.
4. **Checks.** CI runs the full suite, linters, dependency and licence policy, and secret scanning on the branch.
5. **Pull request.** The agent opens a PR with a summary of what changed and why. Branch protection requires human review; the agent can never merge.
6. **Audit.** Each run's prompt, tool calls, commands and diff are logged and linked from the PR.

## Security and governance questions you'll get

| Question from the bank's security team | Your answer's shape |
|---|---|
| "Will our code be used to train models?" | Anthropic's [commercial terms](https://www.anthropic.com/legal/commercial-terms) state Anthropic "may not train models on Customer Content from Services". Point them to the terms rather than paraphrasing. |
| "Where is the code processed?" | Depends on the deployment: Claude API, Amazon Bedrock, Google Vertex AI or Microsoft Foundry. Confirm region and data-residency options in each platform's current docs. |
| "What stops the agent running something destructive?" | Sandbox with no production credentials, command allowlist, egress limits, and permission prompts or policy for anything else. |
| "Who is accountable for agent-written code?" | The human reviewer who approves the PR, exactly as today. Branch protection makes that enforceable. |
| "What about secrets in the repo?" | Secret scanning before any content is sent, plus rotation of anything found. |
| "Can a malicious issue or code comment hijack the agent?" | Treat issue text, comments and fetched pages as untrusted data. The sandbox and the human PR review limit the blast radius even if it happens. |
| "Can we see what it did?" | Full run log per PR: prompts, tool calls, commands, diffs. |

## Model choices

| Use | Model | Reason |
|---|---|---|
| PR review | Claude Sonnet 5.5; Opus 5.5 for security-sensitive repos | Sonnet for volume; Opus where a missed bug is expensive. Decide with the seeded-bug eval below |
| Code Q&A answers | Claude Sonnet 5.5 | Synthesis over retrieved code at moderate cost |
| Agentic coding | Claude Opus 5.5, `effort` tuned per task class | Long multi-step work benefits most from the strongest model; lower effort for routine tasks |

Remember that output tokens include the model's thinking on current models, so effort settings show up directly in output cost.

## Evals and launch gate

**PR review:**

- **Seeded-bug set:** 200 historical PRs where a bug was later found and fixed. Did the bot flag the line?
- **Clean set:** 200 PRs with no later fixes. How many comments did it make that a senior engineer would call noise?
- **Gate (example):** catches at least 40% of seeded bugs, at most 1 noise comment per clean PR on average. Then a two-team pilot where at least half of bot comments are resolved with a change.

**Agentic coding:**

- **Task suite:** 100 past issues from the bank's own repos with the tests that verified the real fix.
- **Metrics:** pass rate on hidden tests, reviewer edits needed before merge, cost per solved task, and policy violations in the sandbox log (target zero).

## Failure modes

| Failure | How you notice | What you design in |
|---|---|---|
| Review noise, developers mute the bot | Dismiss rate per repo | Comment cap, severity filter, no style comments linters cover |
| Confident but wrong security finding | Pilot feedback; dismiss reasons | Require a concrete line and explanation; route security findings to a human security reviewer first |
| Agent "fixes" tests instead of code | Diff review; test-file change alert | Flag PRs that modify tests and code together; reviewers check them |
| Agent adds a risky dependency | Dependency policy check in CI | Allowlist of registries and licences |
| Prompt injection via issue text | Red-team issues in a test repo | Untrusted-data handling, sandbox, no secrets in the environment |
| Cost spike from long agent runs | Cost per task dashboard | Turn caps, task scoping, caching verified in usage logs |

## Cost drivers and a worked estimate

Prices from Anthropic's [pricing page](https://platform.claude.com/docs/en/about-claude/pricing) (checked 2026-10-08), per million tokens: Sonnet 5.5 $2 input, $10 output; Opus 5.5 $4 input, $20 output, $0.20 cache read, $5 for a 5-minute cache write.

### PR review at Larkfield

Assumptions: 600 PRs a day, 3 reviews per PR (open plus two pushes), 30,000 input tokens and 2,000 output tokens per review, mostly fresh (each diff is new).

| Model | Per review | Per day (1,800 reviews) | Per month (22 days) |
|---|---|---|---|
| Sonnet 5.5 | 30,000 x $2/M + 2,000 x $10/M = $0.08 | $144 | about $3,200 |
| Opus 5.5 | 30,000 x $4/M + 2,000 x $20/M = $0.16 | $288 | about $6,300 |

On Opus 5.5 that's about $4.20 per engineer per month. Reviewing only new commits on later pushes could cut input on those reviews by more than half.

### One agentic coding task

Agent loops resend the whole conversation every turn, so total input across a task grows roughly with the square of the turn count. Caching is what keeps this affordable. Assume a 40-turn task on Opus 5.5 that starts at 20,000 tokens of context and adds 2,000 tokens per turn (tool results, file contents), with 1,000 output tokens per turn:

| Part | Tokens | Rate | Cost |
|---|---|---|---|
| Cache reads (earlier context, re-read each turn) | about 2,400,000 | $0.20/M | $0.48 |
| Cache writes (new content each turn) | about 100,000 | $5/M | $0.50 |
| Output | 40,000 | $20/M | $0.80 |
| **With caching** | | | **about $1.78** |
| Same task with no caching | about 2,500,000 input at $4/M plus output | | **about $10.80** |

Caching makes the task about six times cheaper. Confirm it is working in production with `usage.cache_read_input_tokens`; one timestamp near the top of the prompt can silently break it.

At 1,500 engineers running 3 tasks a working day, that's about $8,000 a day, about $117 per engineer per month at 22 working days. Present it next to what an engineer-hour costs the bank and next to measured outcomes from the pilot (tasks merged, review time), not on its own. If the customer will use a seat-based product rather than the API, compare against that product's current pricing.

## When this pattern doesn't fit

- **No meaningful tests or CI.** An agent without a checker produces plausible code nobody can verify cheaply. Fix the test suite first, or limit the scope to review and Q&A.
- **No review capacity.** Agentic coding moves work from writing to reviewing. If reviewers are already the bottleneck, more PRs make it worse.
- **No approved path for code to leave the network,** and no deployment option the security team accepts. Settle that before any pilot.
- **A small team on a small codebase.** Off-the-shelf tools with default settings are enough; a custom architecture is overkill.
- **The goal is "replace engineers".** Reset expectations to throughput and cycle time, measured in a pilot. Promising headcount cuts from a demo ends badly.

## How this shows up in interviews

Applied AI postings at Anthropic mention fitting Claude into the customer's stack and building evals (**Official**, from the [Solutions Architect, Applied AI posting](https://jobs.accel.com/companies/anthropic/jobs/69412282-solutions-architect-applied-ai) as listed on an aggregator). Coding use cases are a common enterprise entry point, so expect them in case rounds. How a given interviewer frames them isn't publicly documented.

Original practice prompts:

- "A bank's CISO says no AI agent may ever run code on their network. Can you still help their developers? Design what you'd propose."
- "The PR bot's comments are dismissed 70% of the time. What do you change?"
- "Estimate the monthly model cost of agentic coding for 300 engineers, out loud, and tell me what assumption you're least sure of."

> **Key takeaways**
> - Split developer productivity into PR review, code Q&A and agentic coding. They carry different risks and should be reviewed separately.
> - Governance is architecture: secret scanning before prompts, sandboxes without production credentials, command allowlists, branch protection, and a run log per PR.
> - Prefer an existing tool for agentic coding; build where custom policy or integration is the point.
> - PR review on Opus 5.5 costs about $0.16 a review at Larkfield's sizes; agent tasks cost about $1.78 with caching and about $10.80 without.
> - Without tests, review capacity or an approved data path, agentic coding is the wrong first step.
