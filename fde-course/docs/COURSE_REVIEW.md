# FDE Playbook: course review (October 2026)

Five independent reviewers read the whole course, each acting as a senior hiring-side engineer at a frontier lab:

1. Foundations (C1–C5)
2. Applied AI Engineer (E1–E7)
3. Applied AI Architect (A1–A7)
4. Forward Deployed Engineer (modules 01–11)
5. Platform and market fit: the app itself, plus competitors

Between them they read all 241 lessons, every rubric, persona brief and quiz, and the exercise code. They checked API and platform facts against the live docs at platform.claude.com and the claude-api skill, recomputed about 60 worked numbers, and drove the app with Playwright at desktop and phone widths. Nobody edited anything during the review.

---

## 1. Verdict

**For its niche (role-specific prep for Applied AI Engineer, Architect and FDE roles), this is already one of the strongest products available.** No competitor found combines graded in-browser coding against a Claude SDK simulator, timed progressive drills, rubric-graded written answers, hidden-fact customer role-plays, three full mock loops and confidence labels on every hiring claim.

**It is not yet best-in-market.** Five gaps hold it back, in this order:

| # | Gap | In one line |
|---|-----|-------------|
| 1 | **The modern agent stack is missing** | No hands-on MCP server, sub-agents, Agent Skills, Agent SDK, Managed Agents, Claude Code or context engineering, though the Anthropic FDE posting names the first three. |
| 2 | **Nothing real to show** | Every model call is canned, and no track ends with a portfolio project on the real API, yet every deep-dive round assumes you have one. |
| 3 | **Mock rounds don't feel like real rounds** | Everything is typed and turn-based. Design rounds are one-shot essays with no follow-up questions or whiteboard. |
| 4 | **No memory of progress** | Restart and Submit again overwrite scores. There is no attempt history, no readiness dashboard and no personalised plan. |
| 5 | **Missing first and last mile** | No model-level ML literacy (transformers, tokenization, RLHF and Constitutional AI, hallucination). No career mechanics (resume, referrals, levels, compensation, negotiation). |

There are also **about 30 factual or consistency errors to fix before launch**. Most are small; four could cost a learner points in a real interview (section 3).

### Scorecard by track

| Track | Strongest part | Biggest gap | Reviewer's grade |
|---|---|---|---|
| Foundations | C4 essays framework, C5 values, evidence labels | How LLMs work; career mechanics; only 2 of 5 promised C3 drills | Honest and well sourced; light on reps |
| Engineer | API accuracy (best in market), E4 statistics | Agent stack; real-model practice; capstone | Mid-level difficulty, narrow scope |
| Architect | A2 platform facts, A1/03 discovery role-play, arithmetic | Live whiteboard; demo building; governance; commercial | Near best-in-market on the core loop |
| FDE | Hidden-fact role-plays, mock loop, evals module | MCP, sub-agents, Skills; TypeScript; portfolio capstone | Strong for consulting-style FDE, not yet the lab FDE |
| Platform | One practice type per round; grading secrets stay on the server | Voice, interactive design, attempt history, humans | Polished, works on phones |

---

## 2. Where it shines (keep and market these)

- **Honest evidence labels.** Official, Reported and Anecdotal labels with "last checked" dates run through every track ("the recruiter wins"). SEO guides and question banks have nothing like it. It is a trust advantage worth putting on the home page.
- **Current, precise API facts.** Every reviewer independently found the Claude 5.5-era details correct. Examples:
  - prefill and forced `tool_choice` return a 400;
  - default effort levels;
  - `output_config.format`;
  - the 512-token cache minimum;
  - `fallbacks="default"` doesn't cover 429s;
  - pre-warming with `max_tokens: 0`;
  - mid-conversation `system` messages.

  The Engineer reviewer called it "better than anything I know of on the market" on API accuracy.
- **Correct arithmetic everywhere.** About 60 worked numbers were recomputed (TCO tables, Wilson intervals, kappa, cost per question, E6 vector sizing) and none was wrong.
- **Hidden-fact role-plays.** Leah's two-cause integration incident (04/11), Whitlock discovery with a hidden contract clause (A1/03), Marcus's single pushback (E7/04) and Ines's live re-scope (11/04). Grader-note caps make them hard to game with keywords.
- **Three honest mock loops.** Readiness is judged by the weakest round, not the average, and each weak rubric line maps to the module that fixes it (E7/06, A7, module 11).
- **Statistics that interviewers respect.** E4, A4 and module 08 cover Wilson intervals, Cohen's kappa, position bias, sign tests, pass@k vs pass^k, and "missing cases count as errors".
- **Code-enforced controls over prompt wording.** Fail-closed approvals keyed on the `tool_use` id, permission filters inside retrieval, never pasting `str(exc)` into a tool result. This is exactly what staff interviewers probe.
- **A faithful simulator with zero setup.** It rejects what the real API rejects, starts responses with thinking blocks, and has a Trace tab. Learners are coding in seconds with no key.
- **Grading integrity basics.** Rubrics, grader notes and persona briefs never reach the browser (confirmed by curl). Grades use structured output and are clamped per criterion.
- **Polished UI** that holds at 390px with no overflow and no page errors.

---

## 3. Errors to fix before launch

**Do not change:** Sonnet 5.5 cache reads at **$0.10/MTok** are confirmed against the live pricing page. The claude-api skill's `models.md` ($0.20) is the stale source. One reviewer flagged it; two others confirmed $0.10.

### 3a. High impact: could cost a learner points in a real interview

| # | Where | Problem | Fix |
|---|---|---|---|
| 1 | `a7-*/04` Aldermoor rubric | Rewards "Azure for the EU". Per the Foundry docs, Foundry offers only Global Standard and US Data Zone, with no EU zone, so the rubric punishes the candidate who spots this. | Rewrite the rubric line and grader notes: EU needs Bedrock (EU profile or in-region) or Vertex `eu`, which means a cross-cloud conversation. Make it a deliberate trap. |
| 2 | E-track cost and latency examples (e5/03, e6/02, e2/01, e4/03) and some A-track estimates | Thinking tokens are left out. Sonnet 5.5 defaults to effort `high`, Opus and Haiku 5.5 to `medium`. Output-token and TTFT figures are about 2× too optimistic. | Set `effort` explicitly in each example, or add a thinking-token row and an "output 3×" sensitivity line. |
| 3 | `06/01`, `06/02` (FDE) | Teaches rolling history trimming. On Opus 5.5, preserved thinking binds signatures to earlier turns, so trimming returns a 400 by default and misses the cache. | Teach append-only history plus compaction or context editing, or strip thinking from the turns you keep. |
| 4 | `06/10`, `08/09`, quizzes `06/12`, `08/12` (FDE) | Uses Haiku 4.5 ($1/$5) as the cheap tier. Haiku 5.5 is $0.10/$0.50 and supports `effort`. "2–4× between tiers" is really 20–40×, which changes the lesson's conclusion. | Switch to Haiku 5.5 and redo the tables. Fix the hint "Haiku rejects effort". |

### 3b. Factual errors

| Where | Problem | Fix |
|---|---|---|
| `c2-*/03` effort table | Implies only Opus 5.5 defaults to `medium`. Haiku 5.5 does too. | "Opus 5.5 and Haiku 5.5 default to medium; Sonnet 5.5 and most others to high." |
| `04/01` | Calls PATCH "usually" safe to retry. It isn't idempotent (RFC 5789). | Group it with POST: safe only with an idempotency key. |
| `e4-*/01` | "50 cases × 2 runs ≈ 100 × 1." Wrong: runs of the same case are correlated, so 50×2 behaves much closer to n=50. | Cases narrow the interval; repeats measure flakiness. Mention clustered standard errors. |
| `a4-*/01` | "±10 at 100 cases, ±5 at 400" in a 95%-target context. That holds only near p=50%, and contradicts A4/03's own table. | Use Wilson figures near 95% (about −6/+3 at 100, ±2–3 at 400). |
| `a2-*/01` residency table | Lists Vertex regional endpoints without the caveat that single-region endpoints serve only Sonnet 4.6 and earlier. "Inference in Germany only" has no documented option for current models. | Add the caveat; teach the sharper Germany answer. |
| `a2-*/01` Foundry | Missing three facts: Sonnet 5.5 is Global Standard only, Fable 5.1 is Hosted on Anthropic only, and Anthropic is an "independent processor for Microsoft". | Add all three; they change the CISO role-play answers. |
| `a2-*/01`, `a6-*/05`, `a6-*/02`, `a7-*/04` | Structured outputs on Bedrock shown as a "source conflict". It is a version split: the new Messages-API page lists it as not supported. | Explain the split. Add a `structured_outputs_platform` flag to the A6/05 matcher (the Ostrava Re case). |
| `a2-*/02` | Misses the docs' wording that conversation content is not retained by default, except for Covered Models (30 days). | Quote the current wording with its caveats. |
| `a2-*/05` Larkspur rubric | Treats a P&C insurer's claim medical bills as HIPAA PHI. P&C insurers generally aren't covered entities. | Reward "confirm with privacy counsel; treat as sensitive regardless". |
| `a1-*/06` quiz Q9 | The answer says "several times more"; the lesson says "nearly twice". | Align them. |
| `09/01`, `11/02`, `a5-*/02`, `a5-*/04`, `a5-*/06`, `a7-*/02`, `a7-*/04` | Platform lists omit **Claude Platform on AWS**, though AWS-first customers are the norm in these cases. | Add it everywhere. |
| `03/09`, `08/09` | Recommend Message Batches without noting that Batches isn't available on Bedrock, Vertex or Foundry. | Add the availability caveat and link the A2 platform checker. |
| `e2-*/03` | "The `tool_use` id is a natural key" overstates it: a re-issued call or regenerated turn gets a new id. | Say the id dedupes replays; re-issued calls need a natural-key check. |
| `e5-*/01` sample | Haiku 5.5 with `max_tokens=256` and default thinking, so it will hit `max_tokens`. | Add `effort: "low"` or disable thinking. |
| E-track code samples | No `cache_control` anywhere, yet the comments imply a stable prefix caches by itself. | Add the marker. |
| `01/07` | "A token ≈ 4 characters" ignores the newer tokenizers, which count about 30% more tokens. | Teach `count_tokens`. |
| `06/07`, `08/09` | "~95% off" caching is true only on Opus 5.5. | State the model each time. |
| `public/py/anthropic/_sim.py` | `CACHE_MIN_TOKENS = 1024`; the course says 512. | Set it to 512 (keep 4,096 for Haiku 4.5). |
| `components/TracksHome.tsx` FAQ | "your code works against the real API unchanged" overclaims: no `client.beta`, `messages.parse`, async client or batches. | "Uses the same calls as the real SDK for the features taught." |
| `components/AiPractice.tsx` | "Passed · interview-ready" contradicts the rubric disclaimer. | "Passed this rubric." |
| Hero illustration (`LoopComposition`) | Shows a loop tracker with per-round times that doesn't exist. | Change the art or build the dashboard (roadmap item 5). |

### 3c. Consistency and grading problems

- **Values-round labels break the course's own rules.**
  - "The values round fails the most candidates" is labelled Reported but rests on guides. It is repeated about 7 times across C1, C4 and C5.
  - "Run by a nominated employee" rests on one Axios newsletter.
  - Relabel both Anecdotal and cut the repetition.
- **Contradictory rule on a `reasoning` field.**
  - e1/03 and the e1/05 rubric penalise a `reasoning` field; e4/03 and e4/04 teach one.
  - Pick one rule (for example a short `rationale`) and soften the Larkspur grader note.
- **e6/02 validates a judge on raw agreement**, which e4/03 calls easy to fool. Use kappa.
- **e4/05 gate** blocks on a single flipped case in small categories, contradicting its own "send one-case drops to review" prose. Add a minimum flip count.
- **Quiz answer bias.**
  - `04/12`: 13 of 13 answers are B; `06/12`: 12 of 13; `05/12`: 9 of 13; `03/14`: 8 of 13. Modules 1–6 never use D.
  - The correct option is usually the longest, across tracks.
  - Rebalance, and add a validator check for both.
- **Missing grader notes and caps** on `07/09` (automatic refunds) and `08/11` (eval readout).
- **Promises not kept:**
  - E2 promises "sub-agents" in `course.json`;
  - TRACKS_PLAN promises "six" E6 design prompts (three exist) and five C3 drills (two exist);
  - the architect modules' `customer` metadata is placeholder text.
- **Company names collide:** Halvorsen ×2, Larchmont ×3, Corvane ×2, Varga ×2, Larkspur/Larkfield.
- **Drills can't be restarted,** yet E7/06 and C1/05 tell learners to redo them on the clock. Drill state is also stored only in the browser.
- **Role-play timing:** labelled 30 minutes, but 8–10 short turns take about 10–15 minutes. A7/03's Sofia says "I will interrupt you", which a turn-based chat can't do.

### 3d. Platform hardening (needed before any certificate or leaderboard)

- **Tutor endpoint is an open Opus proxy.** `app/api/tutor` has no lesson or purchase check and accepts client-supplied instructions with `max_tokens: 16000`.
  - Check `canAccessLesson`.
  - Load instructions on the server.
  - Cap `max_tokens` at about 2k.
- **Usage counter fails open.** `takeAiCall` allows every call if the RPC errors. Make it fail closed and add a global daily spend breaker.
- **Grader prompt injection.** Learner text sits inside unescaped XML-like tags, so an answer can fake `<grader_notes>`.
  - Escape the text or use random per-request delimiters.
  - Tell the grader to treat learner content as data.
- **Forgeable persona turns.** The client sends the whole transcript and the server trusts it. Sign each persona line server-side.
- **Fragile criterion matching.** Criteria fall back to matching by position. Enforce exact names.
- **Prompt caching is a no-op.** The system prompt is under 512 tokens and the stable rubric sits uncached in the user turn. Move the task, rubric and notes into the system prompt behind a breakpoint, and cache the role-play transcript.
- **No grader calibration.**
  - Build an anchor-answer eval set (weak, borderline, strong per graded lesson) and run it in CI.
  - Take the median of two runs near the pass mark.
  - Show the previous score.
  - The course teaches judge calibration in E4 but doesn't apply it to itself.
- **Cost exposure.** Lifetime access with 60 Opus calls a day has no cap; about $0.01–0.03 per role-play turn is realistic. Measure Sonnet 5.5 or Haiku 5.5 for persona turns.
- **Accessibility:**
  - `graphite-3` meta text at 4.3:1, `gray-500` on the console at 3.9:1, placeholders at 2.3:1;
  - no `aria-live` on chat or grades;
  - the pane splitter is mouse-only;
  - lock icons have no label;
  - no extended-time option for drills.

---

## 4. Weak spots (cross-track themes)

1. **Spec-transcription exercises.** Exact strings, very explicit specs, and hints that are nearly the solution (e1/02, e3/02, e4/02, 07/04, 10/05). A staff candidate finishes them without making a design decision. There is no hard mode, no write-your-own-tests, no multi-file repos and no open-ended design exercises.
2. **No real model.** Prompt quality never affects a grade. Learners never see variance, refusals, real latency or real cost. E1 "production prompting" is the clearest casualty.
3. **Design rounds are static.** E6, E7/03, A7/04, A6/06 and the FDE track's missing design round are all one-shot essays with the requirements handed over up front. There are no clarifying questions, constraint changes or diagram.
4. **Too few reps.** There are 4 timed drills in the whole course, and E7/06 reuses the C3 drills as "fresh" material, so a third loop has nothing new. Personas unlock their hidden facts on the same three questions (security, past attempts, approvers), so the pattern is learnable.
5. **Personas are cooperative and memoryless.**
   - No multi-stakeholder meetings, hostile or silent personas, or internal pressure (your own account executive).
   - Jordan appears in four FDE modules and starts fresh each time.
   - Personas never see the learner's earlier work (case prep, project summary, design).
   - Marcus surveys four areas instead of drilling three levels into one.
6. **Narrow scenario mix.** About 7 insurers and 5 banks. No public sector, digital natives or startups, telco or pharma. All E6 prompts are RAG-shaped (no agentic, multimodal or infrastructure designs).
7. **Practice prompts without answers.** The "Practice (say it out loud)" prompts in C2 have no model answers or self-check rubric.

---

## 5. What's missing (the full list)

### A. Technical depth: model literacy (shared core)
- **How LLMs work:** attention as a weighted lookup, KV cache, prefill vs decode (time to first token vs generation), why cost scales with context, context rot and lost-in-the-middle.
- **Tokenization:** a toy BPE exercise; why costs differ across languages and code.
- **Sampling:** logits, softmax, temperature, and why temperature 0 isn't deterministic (the vendor-neutral answer OpenAI and Perplexity interviewers expect).
- **Training pipeline:** pretraining, SFT, RLHF, Constitutional AI and RLAIF, sycophancy, reward hacking.
- **Hallucination:** causes, detection, mitigation, plus a citation-grounding checker exercise.
- **Prompt injection fundamentals:** direct vs indirect, the lethal trifecta, least privilege, approval gates.
- **Evals 101 and embeddings 101** in the shared core, before any track's design round.
- **Vendor-neutral vocabulary:** function calling vs tool use, Responses-style APIs, logprobs, seeds.
- **Inference and serving basics**, plus an LLM-infrastructure design prompt (a multi-tenant gateway). Reported as a frequent Anthropic design-round topic.
- **Fine-tuning and distillation:** when you would, and what data and evals it needs.

### B. The modern agent stack (Engineer and FDE)
- **Building an MCP server:** tools, resources and prompts; stdio vs streamable HTTP; OAuth; a JSON-RPC handler exercise; wiring it to the MCP connector and Claude Code; a CISO brief. In Python, then TypeScript.
- **Sub-agents:** orchestrator-workers, context isolation, cheaper workers, budgets, failure isolation, a cost-vs-quality eval against a single agent.
- **Agent Skills:** `SKILL.md` and progressive disclosure; package a customer playbook as a Skill with a trigger eval.
- **Agent SDK vs Managed Agents vs tool runner vs manual loop:** build-or-buy, with hooks as approval gates.
- **Claude Code:** as the FDE's own tool in a customer repo, and as something to roll out to a customer's engineering org.
- **Context engineering:** compaction, context editing, the memory tool, tool search, programmatic tool calling, append-only histories under preserved thinking.
- **Computer use:** when GUI automation beats an API, sandboxing, on-screen injection risk.
- **Multimodal:** PDF and image blocks, the Files API, the native Citations API with `page_location`. Three of the course's own customers need it.
- **Streaming:** event parsing, mid-stream refusal, cancellation, eager tool input.
- **Async and batch:** `AsyncAnthropic` with a semaphore, a full Batches job (noting platform availability).
- **Deeper agent evals:** end state vs trajectory, simulated users, pass^k, error-analysis taxonomies, hill-climbing without overfitting, synthetic and adversarial suites, a hands-on layered injection defence.
- **TypeScript:** `@anthropic-ai/sdk` streaming to a Next.js route, a tool loop, an MCP server, one timed drill. The FDE posting asks for Python plus one other language.

### C. Proof of skill
- **A portfolio capstone on the real API** for every track (bring your own key, or a metered proxy).
  - The learner picks the domain.
  - It ships with a golden set, calibrated judge, CI gate, cost and latency table, decision record, and Dockerfile plus IaC.
  - Personas (Marcus, Theo, Sofia) then load its README as context for the deep dive.
- **Real-model labs:** 3–4 existing exercises (E1, E3, E4, 06/04) get an optional real-API mode, so variance and refusals become real.
- **A higher coding bar:**
  - hard mode with hints hidden;
  - behavioural tests;
  - write-the-tests exercises graded by mutation testing;
  - multi-file customer repos;
  - a debug-a-broken-harness exercise;
  - a 30-minute war-room debugging drill;
  - 3 more C3 drills and 3–4 more FDE drills;
  - an AI-allowed drill.
- **An onsite live-coding role-play:** requirements change mid-problem while the learner narrates.
- **A take-home plus walk-through panel:** OpenAI's reported format.

### D. Interview realism (platform)
- **Voice mode** for every role-play: a microphone, spoken persona replies, a per-answer timer, delivery criteria. The lessons say "talk out loud" about 121 times.
- **Interactive design interviews:** hidden requirements revealed only when asked, a constraint injected every few turns, an embedded whiteboard (Excalidraw or Mermaid) snapshotted to the grader, and a 45-minute clock.
- **Loop mode:** a "Start loop" button that locks the tutor and hints, records the first attempt as the score, and runs a session clock.
- **Harder personas:** multi-stakeholder meetings, a hostile or silent persona, internal pressure, a territorial customer engineer reviewing your PR, two escalations at once.
- **New rounds:**
  - an AI-graded technical depth round (replacing A7's self-scored recording);
  - a customer-engineer round in E7 ("our extraction broke after migrating to Opus 5.5");
  - a mandatory FDE system-design round in module 11;
  - a pre-sales experience deep dive in A7.

### E. Progress and personalisation
- **Attempt history:** a `grades` table storing every attempt. Restart and Submit again must stop destroying scores.
- **Loop dashboard:** auto-builds the E7/06 scorecard, rubric-line trends, per-level drill times and "next best module".
- **Diagnostic and plan:** a 25-minute diagnostic that produces a plan from the interview date and hours per week, with an interview-date countdown and email nudges.
- **Onboarding:** an after-signup step asking role, interview date and background.
- **Drill reset** and drill state synced to the account.
- **Spaced repetition:** C2 numbers (prices, cache minimums, effort levels) as 5-minute daily flashcards, built from one prices data file.

### F. Career mechanics (new module C6)
- Choosing your role, with a posting decoder and skills-gap self-assessment.
- Resume and LinkedIn bullets, graded against the posting.
- Referrals and outreach messages; reapplying after rejection.
- A "tell me about yourself" two-minute pitch, plus a recruiter-screen role-play and questions to ask.
- Levelling, equity basics, and a negotiation role-play with a competing offer; team matching.
- Name the reported online-assessment platform (CodeSignal) and practise in its environment.
- Broaden the lab coverage: Google DeepMind, plus FDE employers such as Palantir, Scale, Sierra and Harvey.

### G. Architect-specific
- **Live whiteboarding** with constraint injection, and diagram submission with data-class and residency labels on every arrow.
- **Demo building:** demo craft, plus a simulated-SDK demo-with-eval exercise and a "live demo goes wrong" role-play.
- **AI governance:**
  - bank model risk management (SR 11-7, PRA SS1/23);
  - EU AI Act tiers and deployer duties;
  - NIST AI RMF and ISO/IEC 42001;
  - a Head of Model Risk role-play.
- **Claude Enterprise, Claude Code and connectors rollout:** SSO/SCIM, MCP governance, Compliance API, a 90-day adoption plan.
- **Commercial and capacity:** rate-limit planning at peak, Priority Tier, commits, marketplace and private offers, seat vs usage.
- **Fair competitive positioning:** a CIO already on Azure OpenAI or Gemini.
- **RFP/RFI responses:** comply / partial / to confirm, with no roadmap promises.
- **Partners and SIs:** a three-party role-play.
- **Enterprise agent and MCP reference architecture.**
- **Digital-native model-migration consult.**
- **Workshop and enablement design.**

### H. FDE-specific
- **Locked-down enterprise deployment:**
  - TLS-inspecting proxies and custom CAs;
  - PrivateLink and IAM roles;
  - OIDC JWT validation mapped to tool permissions;
  - air-gapped installs;
  - a platform choice matrix that flags Batches, MCP and Skills gaps.
- **Writing reusable assets back to product:** a field report; refactoring two connectors into one MCP server or Skill.
- **Refusals in regulated domains:** `stop_details`, fallbacks, refusal rate as an eval metric. HIPAA and BAA realism at Brightline.
- **Data at scale:** pandas or DuckDB, the 50,000-ticket backfill done for real.
- **Field realities:** VDI without admin rights, access lead times, 25–50% travel, juggling customers.

### I. Trust, community and proof
- **A human layer:** a Discord or Slack community, peer-mock matching with shared persona scripts, an optional paid instructor mock.
- **Outcome evidence:**
  - instructor name and LinkedIn;
  - a refund line on pricing;
  - a sample graded answer with its full debrief on the home page;
  - a post-loop "did you get the offer?" survey and testimonials.
- **Verified certificate and portfolio page:** this needs server-side completion first, since `/api/progress` trusts the client today.
- **A better free taster:** show free first lessons as unlocked on the map; make one drill and one track role-play free.

---

## 6. Ranked must-haves to be best-in-market

Time estimates assume Claude builds with the owner reviewing, at the pace of phases 2–6 (one phase is roughly one working session of a few hours).

| Rank | Item | Why it's ranked here | Estimate |
|---|---|---|---|
| **P0-1** | **Fix the errors in section 3** (3a, 3b, 3c), plus a validator check for quiz answer position and length | Accuracy is the brand. Four errors could cost a learner points in a real interview. | 1 session (about 3–4 hours) |
| **P0-2** | **Platform hardening** (3d): tutor lock-down, fail-closed counter, spend breaker, grader injection defence, signed persona turns, caching fix | Cost and abuse exposure today; blocks any certificate | 1 session |
| **P1-3** | **Agents module** for Engineer and FDE: MCP server build, sub-agents, Skills, Agent SDK vs Managed Agents, context engineering, Claude Code. About 10–12 lessons, half exercises. | The #1 gap versus the Anthropic FDE posting; keeps the E2 promise | 2–3 sessions |
| **P1-4** | **Portfolio capstone on the real API** (repo template plus BYO key) and 3–4 real-model labs, with personas reading the learner's README | Every deep-dive round needs it; turns the course into proof of skill | 2 sessions (plus an owner decision on BYO key vs metered proxy) |
| **P1-5** | **Attempt history, drill reset and loop dashboard** (`grades` table, scorecard, trends, onboarding with interview date) | Makes progress visible; required by the course's own E7/06 method | 1–2 sessions |
| **P1-6** | **Interactive design interviews** (persona with hidden requirements, constraint injection, Mermaid or Excalidraw snapshot to the grader), used in E6, E7/03, A7/04 and a new FDE design round | Design rounds are reported at all three labs; the current essays miss the live part | 2 sessions |
| **P2-7** | **"How LLMs work" plus training and safety fundamentals** in C2: transformers, BPE exercise, sampling, RLHF and Constitutional AI, hallucination, injection | Fundamentals questions at OpenAI and Perplexity; a credible safety conversation at Anthropic | 1–2 sessions |
| **P2-8** | **Career module C6:** role choice, resume grading, referrals, recruiter-screen role-play, levels and negotiation | The first and last filters; no competitor in this niche covers it with graded practice | 1 session |
| **P2-9** | **More reps and a higher coding bar:** 3 C3 drills, 3–4 FDE drills, hard mode, mutation-graded tests, war-room debugging drill, more persona variants | Loops 2 and 3 need fresh material; staff-level difficulty | 2–3 sessions |
| **P2-10** | **Voice mode for role-plays** (browser speech recognition plus spoken replies, per-answer timer, delivery criteria) | Real rounds are spoken; the clearest gap versus AI-mock competitors | 1–2 sessions (browser-only version) |

**Next wave** (after the top 10):
- Architect expansion: governance, demo building, commercial and capacity, RFP, competitive positioning, partners, Claude Enterprise rollout. About 2–3 sessions.
- TypeScript module. About 1–2 sessions.
- Multimodal and Citations. About 1 session.
- Locked-down deployment lab. About 1 session.
- Spaced repetition.
- Community and peer mocks: mostly owner work.
- Verified certificate: after P0-2 and P1-5.

**Rough total for the top 10:** about 15–20 working sessions, or 3–4 weeks at one session a day.

---

## 7. Market position

| Option | Price (public, mostly third-party) | They have | They lack vs FDE Playbook |
|---|---|---|---|
| Exponent (FDE course beta plus membership) | about $79/mo or about $12/mo on an annual plan; free peer mocks | FDE-specific content, peer and expert mocks, coaches | Graded LLM coding against an SDK, customer personas, three role-specific loops |
| Hello Interview | expert mocks about $170–289 | Human mocks, system design brand | Applied AI, FDE and customer rounds |
| interviewing.io | about $179–339 per mock | Big-tech human mocks, AI interviewer | LLM-specific design and customer rounds |
| Maven cohorts (evals, AI engineering) | $1.2k–4.2k | Deep real-API building, live teaching, community | Interview-format practice and mock loops |
| Question-bank sites | free to subscription | Breadth of reported questions | Graded practice, honest labels |

**Positioning:** the edge is role-specific, graded and honestly labelled practice for a one-time $249. To be the clear best, it needs what competitors already sell (spoken mocks, interactive design, humans, visible progress) plus what nobody sells: real agent-stack building and a portfolio project the learner can defend.

---

## 8. Items the owner should verify

- **Yale SOM and Axios sources behind the values-round claims.** Reviewers couldn't reach them.
- **Essay details written from pasted text:** classifiers at "close to 5% of inference", the co-founders' 80% pledge, the SB 53 and RAISE Act thresholds.
- **Anthropic's published company values page.** A reviewer believes it exists (medium confidence), and mapping stories to it would be a cheap C5 win.
- **"IAM-authorized" Compliance API on Claude Platform on AWS (A2/02).** Unverified; mark it "confirm".
- **Competitor prices.** These come from third-party reviews; Exponent's site couldn't be reached.
