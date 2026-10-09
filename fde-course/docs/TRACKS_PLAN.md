# Three-track plan: syllabus draft for review

Status: **approved 2026-10-08. Phase 1 (platform) built**; phases 2–6 to go. See "Build log" at the end.

## Decisions already made (2026-10-08)

| # | Decision | Choice |
|---|---|---|
| 1 | Brand | Keep **FDE Playbook** and fdeplaybook.dev. Each track is a "Playbook". |
| 2 | Pricing | **$249 all-access**, one-time. The live site stays at $149 until the tracks launch, then `PRICE_USD` changes to 249. |
| 3 | Order | Research first, then this written syllabus, then build. |

## The goal

Teach what it takes to get hired into applied roles at frontier labs (Anthropic, OpenAI, Perplexity and similar). There are three tracks:

| Track | For | The job in one line |
|---|---|---|
| **Applied AI Engineer** | Backend or ML engineers | Build production LLM systems: agents, RAG, evals, latency, cost |
| **Applied AI Architect** | Senior engineers and solutions architects | Design the customer's solution, run the proof of concept, defend tradeoffs to executives |
| **Forward Deployed Engineer** | Engineers who like customers | Ship working AI inside a customer's messy systems |

Every track sits on a **shared core** and ends with a **mock interview loop**.

---

## 1. What the research says

Confidence labels:

- **Official:** the company says it.
- **Reported:** several independent candidate accounts agree.
- **Anecdotal:** one or two accounts.

The course uses these same labels so learners know what to trust.

### Anthropic

| Stage | What happens | Confidence |
|---|---|---|
| Application | A written "Why Anthropic?" answer (reported as 200–400 words). Treat it as the first interview. | Reported |
| AI use | First drafts must be your own. Claude may refine them. No AI in take-homes or live interviews unless Anthropic says otherwise. Using Claude for interview prep is encouraged. | **Official** ([candidate AI guidance](https://www.anthropic.com/candidate-ai-guidance)) |
| Recruiter screen | About 30 minutes: background, motivation, level. | Reported |
| Online assessment | One progressive CodeSignal problem, about 90 minutes, about 4 levels. Each level extends the previous one. Practical code in Python, no algorithm puzzles. The best-known variants are an in-memory database (get/set, then filtering, then TTL, then time-travel lookups) and a banking system. | Reported (many accounts) |
| Onsite | Two loops on separate days. Loop 1: coding, system design (often LLM infrastructure), culture. Loop 2: experiences and goals, plus a project deep dive. Failing Loop 1 cancels Loop 2. | Reported |
| Culture / values | Several guides call it the round that fails the most candidates. It is run by a nominated employee. Reported prompts include mission versus share price, and "someone you respect but disagree with on values". | Reported (Axios plus career-center guides) |
| References and team match | Can add 2–4+ weeks. | Reported |

**Essays to know** (link to them; never copy them into the course):

- Dario Amodei, *Machines of Loving Grace* (Oct 2024)
- *The Urgency of Interpretability* (Apr 2025)
- *The Adolescence of Technology* (Jan 2026)
- Anthropic's Responsible Scaling Policy
- Claude's constitution
- Anthropic's engineering posts, e.g. *Building effective agents*

No public source confirms that interviewers ask about the essays directly. The course frames them as how to answer "Why Anthropic?" specifically and how to hold your own in the values round. It does not frame them as "they will quiz you on this".

**Applied roles at Anthropic** (from job postings):

- **Applied AI Engineer:** a customer-facing technical advisor from discovery through deployment. Builds eval frameworks, pairs with customer engineers, knows prompting, agents and retrieval. 4+ years in a technical role.
- **Solutions Architect, Applied AI:** pre-sales architecture for large enterprises. Fits Claude into their stack, builds evals, designs scalable architectures.
- **Forward Deployed Engineer, Applied AI:** builds production apps on Claude inside customer systems (MCP servers, sub-agents, agent skills), white-glove deployment, 25–50% travel. Python plus one more language.

### OpenAI (Forward Deployed Engineer)

- Recruiter screen, then two 60-minute screens or a take-home with a review call, then a virtual onsite of 4–6 interviews (reported).
- **Coding:** practical, production-style. One account describes an AI-enabled coding screen.
- **System design:** LLM deployment.
- **Project deep dive:** present and defend something you built.
- **Assessed on:** scoping ambiguous problems, building systems around models, proving them with evals, talking to non-technical stakeholders.
- One candidate reports a one-week take-home case study, then a panel walking through it from several angles (anecdotal).
- Solutions Architect loops are thinly documented. Plan for a case discussion plus a presentation, labelled anecdotal.

### Perplexity

- HR screen, then a project-style online assessment (caches, multi-part tasks with tests) or live coding, then a 4–5 round onsite (reported).
- **Coding:** domain-flavored, e.g. tokenization, streaming, beam search.
- **AI system design:** RAG, serving under latency limits, caching.
- **Hiring manager deep dive.**
- **Senior roles:** a technical founder interview.

### What this means for the course

1. **Practical, progressive coding is the common screen.** Build a timed, multi-level coding drill engine. Write **original** problems in that format, never reconstructions of reported questions.
2. **LLM system design shows up everywhere.** Each track needs a design module with rubrics.
3. **Values and mission is a real filter at Anthropic.** Treat it as a full module with practice, not a tips page.
4. **The project deep dive appears at every lab.** The capstone doubles as the learner's deep-dive project.
5. **No AI during assessments.** Timed drills run with the tutor turned off, mirroring the real rules.

---

## 2. Course structure

```
FDE Playbook
├── Shared core: Frontier Foundations (C1–C5)   ← everyone starts here
├── Applied AI Engineer Playbook (E1–E6 + Loop)
├── Applied AI Architect Playbook (A1–A6 + Loop)
└── Forward Deployed Engineer Playbook (F1–F6 + Loop)   ← reworked from today's 10 modules
```

Hours are estimates. Lesson counts include readings, exercises and quizzes.

### Shared core: Frontier Foundations (about 30 lessons, about 10 hours)

| # | Module | What the learner does | Reuses |
|---|---|---|---|
| C1 | **How frontier labs hire** | Maps the loop at Anthropic, OpenAI and Perplexity, with confidence labels. Covers levels, timelines and the AI-use rules. **Exercise:** draft your own "Why Anthropic?" answer; Claude grades it against a rubric (specificity, own experience, mission link). | New |
| C2 | **LLM fundamentals interviewers probe** | Tokens, context, sampling, tool use, caching, structured output, model choice and cost math. **Exercises:** a cost calculator, a token budgeter, picking a model for a scenario. | Module 6 (trimmed) |
| C3 | **Progressive coding drills** | Learns the multi-level format: data model first, extend without rewriting. Original drills: a key-value store with expiry and history, an event ledger, a rate limiter, a log aggregator, a job scheduler. **Timed mode, tutor off.** | New engine |
| C4 | **Reading the labs** | Learns a critique framework (steelman, assumptions, strongest counterargument, what would change your mind). Applies it to Amodei's essays, the RSP and the constitution, plus OpenAI's charter for contrast. **Exercise:** a written critique graded by Claude against a rubric. | New |
| C5 | **Values and behavioral** | Mission versus money, disagreement, failure, safety tradeoffs, STAR stories. **Exercise:** a mock values interview; Claude interviews you, then scores you. | New |

### Applied AI Engineer Playbook (about 40 lessons, about 14 hours)

| # | Module | Focus | Reuses |
|---|---|---|---|
| E1 | Production prompting and structured outputs | System prompts, JSON schemas, extraction reliability, prompt regression | Module 6 |
| E2 | Tool use and agents | Tool loops, MCP servers, sub-agents, failure handling, traces | Module 7 |
| E3 | Retrieval at scale | Chunking, hybrid search, reranking, retrieval evals, citations | Module 7 |
| E4 | Evals as engineering | Golden sets, LLM-as-judge calibration, regression gates in CI | Module 8 |
| E5 | Production concerns | Streaming, latency budgets, prompt caching, rate limits, fallbacks, observability, cost | Module 9 |
| E6 | **LLM system design interview** | Six design prompts (e.g. a support agent at 10k tickets/day, a doc-QA service at p95 < 2s), each graded against a rubric | New |
| Loop | **Mock loop** | Timed progressive coding, then system design, then project deep dive, then values | New |

### Applied AI Architect Playbook (about 38 lessons, about 13 hours)

| # | Module | Focus |
|---|---|---|
| A1 | The architect's job | Pre-sales to deployment, solution design docs, working with Sales and Product |
| A2 | Enterprise deployment of Claude | Direct API versus Bedrock, Vertex AI and Foundry; data handling, security reviews, SSO, compliance questions (facts verified against current docs before writing) |
| A3 | Choosing the approach | Prompting versus RAG versus agents versus fine-tuning; build versus buy; cost and total-cost-of-ownership models at scale |
| A4 | Proofs of concept that close | Success criteria, bake-offs, eval-driven proofs of concept, reading results honestly |
| A5 | Executive communication | Architecture one-pagers, objection handling. **Role-play:** a skeptical CTO and a cautious CISO, both played by Claude |
| A6 | Reference architectures | Support automation, document processing, knowledge assistant, coding assistant, each with tradeoffs |
| Loop | **Mock loop** | Case presentation, then architecture design, then customer role-play, then values |

### Forward Deployed Engineer Playbook (rework: about 45 lessons, about 15 hours, down from 39.5)

The fix for "boring": every lesson opens on a customer problem. Readings are about 40% shorter. Each module ends with a **field drill**, a timed customer scenario.

| # | Module | Built from today's |
|---|---|---|
| F1 | Discovery and scoping under ambiguity | Modules 1 and 2 |
| F2 | Messy data and SQL on customer systems | Modules 3 and 5 |
| F3 | Integrations that survive production | Module 4 |
| F4 | Shipping Claude inside customer systems (agents, MCP, evals) | Modules 7 and 8 |
| F5 | Production and handover | Module 9 |
| F6 | Capstone: NorthStar engagement (doubles as your deep-dive project) | Module 10 |
| Loop | **Mock loop** | Take-home case plus debrief, then practical coding, then customer role-play, then project deep dive |

**About 150 lessons in total**, about 70 of them reused or reworked. **About 52 hours.**

---

## 3. New platform features

| Feature | What it is | Notes |
|---|---|---|
| Tracks | `course.json` gains `tracks[]`. Each track lists its modules; shared modules appear in every track. A track picker sits on `/learn`. | Existing lesson URLs keep working |
| Timed progressive exercise | Levels unlock when the previous level's hidden tests pass; there is a countdown and the tutor is off | Runs in Pyodide like today, so it costs nothing |
| Written exercise | A text answer graded by Claude against a rubric on the server, returning a score per criterion | Uses the owner's API key, server-side only |
| Role-play | A chat with a Claude persona (interviewer, CTO, CISO), then a scored debrief | Same server route as written exercises |
| Design exercise | A structured answer form (requirements, components, tradeoffs, failure modes) graded against a rubric | Same |
| Per-user limits | A daily cap on Claude-graded attempts per learner | **Required before launch** |

**Cost of live grading:** grading and role-play run on Claude Opus 5.5 (the same model as the tutor): about $0.03–0.05 per grade and about $0.01 per role-play turn. At around 100 Claude-backed actions per learner, that is **about $2–4 per learner**, against $249 revenue. The model is one constant (`MODEL` in `app/api/coach/route.ts`) if cost ever needs cutting.

---

## 4. Guardrails

1. **No leaked or NDA-covered questions.** Every problem is original and written "in the style of" the publicly reported format.
2. **No implied affiliation.** Lab names appear only as factual references, with a disclaimer on the home page and in C1.
3. **Every claim about a hiring process carries a confidence label and a source,** plus a "last checked" date. Processes change, so plan a re-check every quarter.
4. **Essays are linked and summarized in our own words,** never reproduced.
5. **Timed drills mirror the real AI rules:** no tutor during the drill; the tutor is available for the debrief afterwards.

---

## 5. Build order

| Phase | Work | Estimate |
|---|---|---|
| 1 | Platform: tracks, track picker, the three new exercise types, grading route, per-user limits | 2 sessions |
| 2 | Shared core C1–C5 | 2–3 sessions |
| 3 | Applied AI Engineer track plus its loop | 3 sessions |
| 4 | Applied AI Architect track plus its loop | 3 sessions |
| 5 | FDE rework plus its loop | 2–3 sessions |
| 6 | Home page and pricing ($249), then launch | 1 session |

**About 13–15 sessions.** Each phase ships behind the preview unlock first, so the live site never breaks.

---

## 6. Owner answers (2026-10-08)

1. **Free preview:** yes. C1 is free, plus the first lesson of every track.
2. **Lab depth:** Anthropic in depth; OpenAI and Perplexity as comparison chapters.
3. **Live grading on the owner's Anthropic key:** yes.
4. **FDE customers:** keep the existing fictional customers in the rework.
5. **Owner's own stories:** yes. "From my loop" notes go in C1 and C5, **in the owner's words**. Still needed from the owner: 3–5 short true stories (the Amazon loop, an FDE engagement, a values moment). Never invent them.

## Sources (checked 2026-10-08)

- Anthropic candidate AI guidance: https://www.anthropic.com/candidate-ai-guidance
- Anthropic loop overviews (third-party): https://cdo.som.yale.edu/blog/2026/05/18/get-a-job-at-anthropic-interview-process-and-top-questions/ · https://www.educative.io/blog/anthropic-interview-process · https://www.designgurus.io/answers/detail/what-is-the-anthropic-interview-process-like-round-by-round
- Anthropic culture interview: https://www.axios.com/newsletters/axios-ai-plus-10f46cb9-9c35-4d55-b72c-498c853ea10b.html
- Anthropic online assessment reports: https://www.lodely.com/blog/anthropic-oa · https://deepsunai.substack.com/p/anthropics-codesignal-assessment · https://prachub.com/interview-experiences/anthropic-software-engineer-interview-experience-a-community-compiled-guide-to-the-oa-technical-and-values-rounds
- Anthropic role postings (aggregators): https://jobs.accel.com/companies/anthropic/jobs/81748657-applied-ai-engineer · https://jobs.accel.com/companies/anthropic/jobs/69412282-solutions-architect-applied-ai · https://jobs.generalcatalyst.com/companies/anthropic/jobs/89778489-forward-deployed-engineer
- Dario Amodei essays: https://darioamodei.com/post/the-urgency-of-interpretability · https://darioamodei.com/llms.txt
- OpenAI FDE: https://www.tryexponent.com/guides/openai-forward-deployed-engineer-interview · https://igotanoffer.com/en/advice/openai-forward-deployed-engineer-interview · https://www.tryexponent.com/experiences/openai-forward-deployed-engineer-interview-0b9c09
- OpenAI Solutions roles: https://dataford.io/interview-guides/openai/solutions-engineer · https://www.tryexponent.com/blog/openai-interview-process
- Perplexity: https://www.designgurus.io/answers/detail/what-is-the-perplexity-interview-process-like-round-by-round · https://www.interviewquery.com/prep-guides/perplexity-ai-software-engineer

## Build log

### Phase 1: platform (2026-10-08)

- **Tracks.** `content/course.json` has `tracks[]` (core, engineer, architect, fde); each module belongs to exactly one track and may have a `code` ("C1"). `/learn?track=...` shows a track picker plus that track's map. Lesson prev/next stays inside the track.
- **Feature flag.** `tracksEnabled()` in `lib/config.ts`: on in dev and on unlocked previews, off in production until `TRACKS_LIVE=true`. When off, only the FDE track exists (new modules 404) and the site is unchanged.
- **New lesson types** (`lib/content.ts`, `components/LessonWorkspace.tsx`, `components/AiPractice.tsx`):
  - `drill`: timed, multi-level Python. Frontmatter `timeLimit` and `levels`; body has one `## Level N: ...` section per level; tests are named `test_l<N>_...`. Hints and tutor are off while the clock runs.
  - `written`: Claude grades the answer against the lesson's `rubric` (frontmatter `sections`, `rubric`, `passScore`, optional hidden `graderNotes`). Design answers are written lessons with several sections.
  - `roleplay`: conversation with a Claude persona (`persona`, `opening`, `maxTurns`, hidden `personaBrief`, `rubric`), then a scored debrief.
- **Grading route** `app/api/coach/route.ts`: reads rubric, persona brief and grader notes from the lesson on the server; structured JSON output; checks login and lesson access.
- **Daily AI limit** `lib/ai-usage.ts`: tutor answers, grades and role-play turns count against `AI_DAILY_LIMIT` (default 60) per learner per day. Needs `supabase/migrations/0002_ai_usage.sql` (or `supabase/setup_ai_usage_single_statement.sql` for Vercel's Query tool). Emails in `FREE_ACCESS_EMAILS` are exempt. If the table is missing, calls are allowed and an error is logged.
- **Free access:** C1 plus the first lesson of every track (`canAccessLesson` in `lib/access.ts`).
- **Seed lessons:** C1 (round-by-round reading, "Why this lab?" written), C3 (format reading, feature-flag drill), C5 (values role-play), E6 (support-agent design). All other new modules show as "Coming soon".

### Phase 2: shared core content (2026-10-08)

- C1 How Frontier Labs Hire: 6 lessons (loop overview, "Why this lab?" written, preparing with Claude under the official AI rules, label-the-claims exercise, prep plan, quiz).
- C2 LLM Fundamentals: 7 lessons (tokens and cost, cost-calculator exercise, thinking and effort, tool use and structured outputs, pick-the-model exercise, prompt caching and latency, quiz).
- C3 Progressive Coding: 6 lessons (format, feature-flag drill, data models that survive Level 4, ranking warm-up, LLM gateway drill, quiz).
- C4 Reading the Labs: 6 lessons (critique framework, Machines of Loving Grace and The Adolescence of Technology study guides written from full texts the owner pasted, RSP and Claude's constitution, written critique, 12-question quiz). Optional later: The Urgency of Interpretability, and the OpenAI Charter contrast in 04 (needs openai.com access or pasted text). Never summarize essays from memory.
- C5 Values & Behavioral: 7 lessons (what the round tests, story bank, two STAR stories written, mission questions, values role-play, project deep-dive role-play, quiz).
- Verified: validator 138 lessons / 0 problems; every new exercise and drill passes in the browser with its solution and fails with its starter; no phone overflow.
- "From my loop" owner stories: 5 supplied 2026-10-08 and placed in C1/01, C1/05, C5/01, C5/02, C5/06 (styled as `callout-loop`). Numbers the owner wrote in [brackets] were used as given; confirm with the owner before launch.

### Phase 3: Applied AI Engineer track (2026-10-08)

- E1 Production Prompting (6): prompt anatomy, warranty-claim extractor (structured output + validation + retries), structured outputs and validation, prompt regression suite, "defend your prompt" written, quiz.
- E2 Tool Use & Agents (6): the tool loop in depth, hardened agent loop, designing tools (incl. MCP), approval pause-and-resume for risky actions, debugging from traces, quiz.
- E3 Retrieval at Scale (6): retrieval architecture, chunker + BM25, hybrid RRF fusion with filters, measuring retrieval, grounded answers with verified citations, quiz.
- E4 Evals as Engineering (6): evals are the job, golden-set runner with Wilson intervals, LLM-as-judge done right, pairwise judge calibration (kappa, position bias), CI regression gate (sign test), quiz.
- E5 Production Concerns (6): latency budgets, resilient client (retry-after, jitter, deadlines), cost at scale, router + daily budget, observability and graceful degradation, quiz.
- E6 LLM System Design (6): how the round works, worked example (knowledge assistant), three graded designs (support agent, doc Q&A at p95 < 2 s, eval platform), quiz.
- E7 Mock Loop (6): how to run it, 90-minute template-registry drill, PR-review assistant design, deep-dive role-play (Marcus Feld), experiences-and-goals role-play (Elena Sorokin), scorecard and fix plan.
- Verified: validator 181 lessons / 0 problems; all 12 new exercises pass with solutions and fail with starters in the browser; the E7 drill completes; no CDN requests; no phone overflow.

### Phase 4: Applied AI Architect track (2026-10-08)

- A1 The Architect's Job: the role (Anthropic now titles it "Applied AI Architect" on anthropic.com/jobs), technical discovery, discovery-call role-play (hidden constraints), the solution design doc, one-page design (written), quiz.
- A2 Enterprise Deployment: five deployment options compared, data handling and security reviews, platform-fit checker exercise, CISO role-play, security questionnaire (written), quiz. Facts only from platform.claude.com docs, the claude-api skill and Anthropic's commercial terms; certifications and default retention are deliberately not stated (trust/privacy sites unreachable from the build environment).
- A3 Choosing the Approach: decision ladder, build/buy/partner, 12-month TCO exercise, cost at enterprise scale, recommendation memo (written), quiz.
- A4 Proofs of Concept That Close: why POCs stall and the POC plan, scorecard exercise, fair bake-offs, bake-off scorer exercise, honest readout (written), quiz.
- A5 Executive Communication: how executives decide, CTO one-pager (written), objection handling, three role-plays (skeptical CTO, saying no to a sponsor, cautious CISO), quiz.
- A6 Reference Architectures: support automation, document processing, knowledge assistant, coding assistant, pattern-matcher exercise, adapt-a-pattern memo (written), quiz.
- A7 Mock Loop: how to run it, case prep (written), panel presentation role-play, claims-platform design (written), hospital COO role-play, scorecard.

### Pricing correction (2026-10-08)

The writer briefs said Sonnet 5.5 cache reads cost $0.20/MTok; Anthropic's pricing page says **$0.10** (0.05x, same multiplier as Opus 5.5's $0.20). Fixed everywhere, with derived numbers recomputed, including three FDE exercises and `public/py/fde_datasets/incident.py`. Always check prices against https://platform.claude.com/docs/en/about-claude/pricing (reachable from the build environment).

### Phase 5: FDE track rework (2026-10-09)

- Kept all 10 modules and their lesson slugs (learner progress and links survive) instead of merging into six; only quiz files moved up one number.
- Readings cut about 37–40% (e.g. module 2: 6,733 → 4,090 words) and each opens on the module's customer problem. Reading minutes re-estimated at about 100 words per minute (minimum 5): about 318 reading minutes across the track, down from about 720.
- One field-drill role-play per module with its customer: kickoff with Dana Ruiz, discovery call with Marisol Grant (now Head of Claims Operations, reporting to Joan Pierce, VP Claims, matching the exercises), data findings with Owen Bradley, integration incident with Leah Park, churn numbers with Tom Haddad, prototype demo with Priya Desai, auto-refund guardrails and eval readout with Jordan Lee, outage update with Jordan Lee, executive readout with Dana Whitfield.
- New module 11, FDE Mock Interview Loop: how to run it, Marlow & Pike take-home case (written), 75-minute ticket-router drill, customer call with Ines Carvalho, deep dive with Theo Brandt, scorecard.
- Fixes found during the rework: a wrong cost-per-100-tickets figure in module 8, a wrong prompt-caching minimum in module 6 (now 512 tokens on current models), and Haiku 5.5 added to the model table.
- Verified: validator 241 lessons / 0 problems; all 48 FDE exercises and the module 11 drill pass in the browser with solutions and fail with starters.

### Phase 6: launch preparation (2026-10-09)

- `priceUsd()` replaces `PRICE_USD`: $149 while only the FDE course is visible, $249 once `tracksEnabled()` (dev, unlocked previews, or `TRACKS_LIVE=true`). Checkout uses it inline unless `STRIPE_PRICE_ID` is set (which must then match).
- New four-track home page (`components/TracksHome.tsx`), shown when tracks are enabled; the original FDE home page is served otherwise. Site title and description switch the same way.
- Learn page, lock page and checkout copy adapt to tracks.
- Verified: with the flag off, production serves the FDE home at $149 and track lessons 404; with `TRACKS_LIVE=true`, the four-track home at $249, C1 open, paid lessons locked; no phone overflow.
- Owner launch steps (Vercel, production): run `supabase/setup_ai_usage_single_statement.sql`; set `ANTHROPIC_API_KEY`; set `TRACKS_LIVE=true`; remove or update `STRIPE_PRICE_ID`; redeploy; test a purchase with card 4242 4242 4242 4242.
