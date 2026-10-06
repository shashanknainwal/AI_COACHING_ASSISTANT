# FDE Playbook: project handoff

Read this first when resuming. It records what exists, what's live, the decisions behind it, how to verify changes, and what's next. Last updated: 2026-10-06.

## 1. The product

- **What:** a browser-based course on Forward Deployed Engineering (FDE), sold at **$149 one-time**. Brand: **FDE Playbook**. Domain: **https://fdeplaybook.dev** (Cloudflare Registrar, DNS pointed at Vercel).
- **Layout:** DataCamp-style split view: lesson on the left, Monaco code editor + console on the right. Python only, run in the browser with Pyodide and graded by hidden tests.
- **Content:** 10 modules, 107 lessons, 48 graded exercises, 10 module quizzes + a 20-question final assessment, about 39.5 hours. Module 1 is free.
- **Owner/instructor:** "Who I am" section (first person, no name yet): seasoned AI architect, worked at Amazon, now FDE Architect at an AI startup, works in the FDE model, has shipped AI solutions to enterprise customers. The owner may later add name, photo and LinkedIn.
- **Owner's email:** hybridboy11@gmail.com (to go in `FREE_ACCESS_EMAILS` in Vercel, not in code).

## 2. Where everything lives

- **Repo:** `shashanknainwal/AI_COACHING_ASSISTANT`. Everything is in `fde-course/`; the root `README.md` is the owner's original file and must not be changed.
- **Branch workflow:** develop on `claude/fde-course-platform-gf06sa`, open a PR to `main`, and the owner merges it. Vercel deploys `main` to production and every other branch to a preview URL. PR #1 (platform + modules) and PR #2 (redesign, trace viewer, diagrams, access controls) are **merged**. After a merge, restart the branch from `main` before new work.
- **Vercel:** team `jev-a8de`, project `ai-coaching-assistant`, Root Directory `fde-course`, production branch `main`.

### Code map (inside `fde-course/`)

| Area | Files |
|---|---|
| Syllabus and personas | `content/course.json` (modules, summaries, outcomes, `customer` persona per module) |
| Lessons | `content/modules/<NN-module>/<NN-lesson>.md`; exercises have a folder with `starter.py`, `solution.py`, `tests.py`, optional `setup.py` |
| Content loading | `lib/content.ts` (splits an exercise's intro into `briefHtml`, tags objectives/takeaways callouts, `PRICE_USD` from config) |
| Config | `lib/config.ts`: `PRICE_USD = 149`, `SITE_NAME`, `SITE_URL`, `FREE_MODULES`, `freeAccessEmails()`, `previewUnlocked()`, `appMode()` |
| Access | `lib/access.ts` (`getViewer`, `canAccessModule`); every gate goes through `getViewer` |
| Payments | `app/buy/route.ts`, `app/api/stripe/webhook/route.ts`, `lib/purchases.ts`, `app/purchase/success/page.tsx` |
| Auth | `lib/supabase/{server,client}.ts`, `proxy.ts`, `app/login/*`, `app/auth/{callback,signout}` |
| Database | `supabase/migrations/0001_init.sql` (`purchases`, `lesson_progress`, row-level security) |
| Pages | `app/page.tsx` (home), `app/learn/page.tsx` (engagement map), `app/learn/[module]/[lesson]/page.tsx` (lesson or paywall) |
| UI components | `components/LessonWorkspace.tsx`, `CourseMap.tsx`, `TraceView.tsx`, `Diagrams.tsx`, `Playbook.tsx` (Avatar, Mark, Ring), `Quiz.tsx`, `TutorPanel.tsx`, `CodeEditor.tsx` |
| Design tokens | `app/globals.css` (paper/graphite/forest/vermilion/console colours, `.playbook-prose`, callouts, animations); fonts Fraunces/Inter/JetBrains Mono via Google Fonts link in `app/layout.tsx` |
| Python runtime | `public/pyodide-worker.mjs`, `lib/python-runner.ts` (20 s timeout, `RunResult` incl. `trace`) |
| Python support code | `public/py/fde_harness.py` (runs code + tests, builds the agent trace), `public/py/anthropic/` (simulated SDK; records responses for traces), `public/py/requests/` (simulated HTTP), `public/py/fde_clock.py` (instant sleep), `public/py/fde_datasets/` (pinecrest, brightway, incident, northstar, northstar_sim, northstar_agent) |
| AI tutor | `app/api/tutor/route.ts` (Claude via the TypeScript SDK; needs `ANTHROPIC_API_KEY`) |
| Scripts | `scripts/prepare-runtime.mjs` (copies Pyodide + Monaco into `public/`, writes `public/py/manifest.json`; runs on postinstall/predev/prebuild), `scripts/validate-content.mjs` |

## 3. Modes and environment variables

`appMode()`: **dev** (local `next dev` without Supabase, or a Vercel preview with `PREVIEW_UNLOCK_ALL=true`) unlocks everything; **unconfigured** (production without Supabase) shows Module 1 free and nothing for sale; **live** (Supabase keys set) enables logins and the paywall.

| Variable | Purpose | Status |
|---|---|---|
| `NEXT_PUBLIC_SITE_URL` | `https://fdeplaybook.dev` | Set in Vercel |
| `PREVIEW_UNLOCK_ALL` | `true` on the **Preview** environment only; ignored on production | Set in Vercel (Preview) |
| `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` (or `NEXT_PUBLIC_SUPABASE_ANON_KEY`), `SUPABASE_SECRET_KEY` (or `SUPABASE_SERVICE_ROLE_KEY`) | Logins, progress sync, purchases | Added by the Vercel–Supabase integration, which points to Supabase project `etoeogxzkanrtntudvnp`. Use that project (run the migration and URL configuration there). A second project, `xmhqjgqraxrfiyddoouf`, was created by hand and is unused. |
| `FREE_ACCESS_EMAILS` | Comma-separated emails with full access without paying | **Not set yet** (owner's email) |
| `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRICE_ID` (optional) | Payments ($149) | **Not set yet** |
| `ANTHROPIC_API_KEY` | AI tutor | **Not set yet** |

## 4. Status

| Phase | Status |
|---|---|
| 1. Platform (editor, runtime, grading, tutor) | Done |
| 2. Logins and payments (code) | Done; accounts not connected |
| 3. All 10 modules of content | Done |
| UI redesign "The Playbook" (look B) + features 1–5 | Done and merged (PR #2) |
| 4. Deployment | Live on Vercel + fdeplaybook.dev; Supabase, Stripe, Anthropic key still to connect |

### Design decisions (look B, "The Playbook")

Paper reading pages with serif headings; dark "mission console" for code. Features: (1) case-file briefings from each module's customer contact, (2) animated checks panel + customer reply on pass, (3) engagement-map dashboard, (4) agent trace viewer (Trace tab), (5) interactive diagrams in five readings (`<div data-diagram="tool-cycle|agent-loop|rag-pipeline|prompt-caching|circuit-breaker"></div>` in markdown).

Customer personas (fictional), per module: 1 Brightline Health / Dana Ruiz (VP Operations); 2 Lumen Insurance / Marisol Grant (VP Claims); 3 Cobalt Supply / Owen Bradley (CFO); 4 Northwind Freight / Leah Park (Head of Integrations); 5 Pinecrest Fitness / Tom Haddad (COO); 6 Harbor Bank / Priya Desai (Head of Digital Support); 7–9 Brightway Retail / Jordan Lee (VP of Customer Support); 10 NorthStar Logistics / Dana Whitfield (VP Operations).

## 5. Next steps, in order

1. **Supabase (logins):**
   1. In the Supabase SQL Editor, run `supabase/migrations/0001_init.sql`.
   2. Under Authentication → URL Configuration, set the Site URL to `https://fdeplaybook.dev` and add the redirect URLs `https://fdeplaybook.dev/auth/callback` and `https://*-jev-a8de.vercel.app/**`.
   3. Copy the Project URL, the publishable key and the secret key into Vercel. Add `FREE_ACCESS_EMAILS=hybridboy11@gmail.com` too.
   4. Redeploy, then test a magic-link login.
2. **Stripe (payments):**
   1. Copy the secret key from the Stripe dashboard.
   2. Add a webhook at `https://fdeplaybook.dev/api/stripe/webhook` with the events `checkout.session.completed`, `checkout.session.async_payment_succeeded` and `charge.refunded`, then copy its signing secret.
   3. Optionally create a $149 Price and put its ID in `STRIPE_PRICE_ID`.
   4. Test with card 4242 4242 4242 4242, then switch to live keys.
3. **Anthropic API key** for the tutor. Before launch, consider a per-user tutor rate limit, which isn't built yet.
4. **Production email:** Supabase's built-in email sender is rate-limited. Before launch, set up custom SMTP (for example Resend or Postmark).
5. **Nice to have:** certificates of completion; instructor name, photo and LinkedIn; a refund policy line (a refund already removes access).

## 6. How to verify a change (do this before every push)

```bash
cd fde-course
node scripts/validate-content.mjs     # all 107 lessons: solutions pass, starters fail, quizzes well-formed
npx tsc --noEmit
npm run build
```

For UI changes:
1. Run `node scripts/prepare-runtime.mjs`. `npx next dev` skips predev, so the Python file manifest won't include new files without this step.
2. Start `npx next dev -p 3100`.
3. Drive it with Playwright from `/opt/node22/lib/node_modules/playwright`. Check that every starter fails, every solution passes, there are no page errors and no CDN requests, and there's no horizontal overflow at 390 px.
4. Stop dev servers by walking `/proc` (skip `$$`). `pkill` kills the shell.

## 7. Content and code conventions

- **Readings:**
  - Start with a "By the end of this lesson you will be able to:" blockquote and end with a "Key takeaways" blockquote. Both are styled automatically.
- **Exercises:**
  - The intro paragraphs before the first `## ` heading become the case file.
  - Hints go in the frontmatter.
  - `starter.py` ends with a "# --- Try it out (not graded) ---" demo that must not crash on stubs.
  - Tests are `def test_*` with asserts; each docstring's first line is the check's label.
  - Tests reset simulator state with `_sim.calls.clear(); _sim._queue.clear()`.
- **Quizzes:** pass mark is ceil(0.8 × N); vary which option position is correct.
- **Facts about Claude models and the API:** check them with the `claude-api` skill, never from memory.
  - Current models and prices: claude-opus-5-5 at $4/$20 per million tokens, claude-sonnet-5-5 at $2/$10, claude-haiku-4-5 at $1/$5 (no effort parameter).
  - Opus 5.5 rejects forced `tool_choice` and assistant prefill.
  - Structured outputs use `output_config.format`.
- **Commits:** end with the `Co-Authored-By` and `Claude-Session` lines. Open a PR only when the owner asks.

## 8. Working with the owner

The owner has ADHD and prefers this format:
- Lead with the next action.
- Use numbered steps, at most 5 items per list.
- Restate where things stand.
- Give specific time estimates.
- Make wins visible.
- No preamble or closing pleasantries.
- End with one concrete next action.

They reply with short commands (for example "pr", "B", "4-5", "supabase ready").
