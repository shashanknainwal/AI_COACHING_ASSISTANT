# FDE Playbook

A browser-based course on Forward Deployed Engineering. Learners read lessons on the left and write Python on the right. Code runs in the browser (Pyodide) and is graded instantly by hidden tests.

## Run it locally

```bash
cd fde-course
npm install          # also copies Pyodide + Monaco into public/
npm run dev          # http://localhost:3000
```

Optional: copy `.env.example` to `.env.local` and set `ANTHROPIC_API_KEY` to turn on the AI tutor.

## Commands

| Command | What it does |
|---|---|
| `npm run dev` | Dev server |
| `npm run build` | Production build |
| `npm run typecheck` | TypeScript check |
| `npm run validate-content` | Runs every exercise: solution must pass, starter must fail, quizzes must be well-formed |

## How it works

- **Lesson content:** `content/course.json` (syllabus) plus `content/modules/<module>/<NN-lesson>.md`. Frontmatter sets `title`, `type` (`reading` | `exercise` | `quiz`), `minutes`, `hints`, and `questions`.
- **Exercises:** a folder next to the lesson's `.md` with the same name, containing `starter.py`, `solution.py`, `tests.py`, and an optional hidden `setup.py`. Tests are plain `def test_*()` functions using `assert`. The first line of each docstring is shown to the learner. `solution.py` is never sent to the browser.
- **Python runtime:** `public/pyodide-worker.mjs` runs Pyodide in a Web Worker. Runs that take longer than 20 seconds are stopped.
- **Simulated Anthropic SDK:** `public/py/anthropic/` mirrors the real `anthropic` Python SDK (`messages.create`, `messages.stream`, content blocks, `stop_reason`, `usage` with prompt-cache accounting, typed errors with request IDs, retries that honor `retry-after`). Exercises script replies through `anthropic._sim` in `setup.py`. Learner code works unchanged against the real API.
- **Simulated `requests` library:** `public/py/requests/` mirrors `requests` (`get`/`post`, `Session`, `Response`, `raise_for_status`, timeouts, exception classes). Exercises define fake APIs with `requests._sim.route(...)`, including `flaky(...)` failures and `rate_limited(...)` endpoints.
- **Datasets:** `public/py/fde_datasets/` holds shared practice databases (for example `pinecrest.connect()`, an in-memory SQLite gym-chain database), generated deterministically so results match in every browser.
- **Fake clock:** `public/py/fde_clock.py` makes `time.sleep` instant and recorded, so retry/backoff exercises run immediately and tests can check exact delays.
- Packages the course simulates are never downloaded from the Pyodide CDN, even when learner code imports them.
- **AI tutor:** `app/api/tutor/route.ts` calls Claude through the Anthropic TypeScript SDK to give hints without giving away the answer.
- **AI grading and role-play:** `app/api/coach/route.ts` grades written answers and role-play sessions against each lesson's rubric, and plays role-play personas.
- **Progress:** cached in `localStorage`, and synced to Supabase when signed in (`lib/progress.ts`, `app/api/progress`).

## Accounts and payments

The app picks a mode from environment variables:

| Mode | When | Behavior |
|---|---|---|
| Dev preview | `npm run dev`, no Supabase keys | Every module unlocked, "Dev preview" badge |
| Unconfigured | Production build, no Supabase keys | Module 1 free, paid modules locked, nothing for sale |
| Live | Supabase keys set | Email magic-link login, Module 1 free, paid lessons need the purchase ($149 for the FDE course; $249 for all tracks once `TRACKS_LIVE=true`), progress syncs to the account |

Paid lesson content is rendered on the server only for learners who bought the course, so it never reaches the browser otherwise.

### Going live on fdeplaybook.dev

1. **Vercel** (free tier): import the GitHub repo, set **Root Directory** to `fde-course`, and deploy. The framework is detected as Next.js; `npm run build` copies the Python runtime and editor into `public/` automatically.
2. **Domain (Cloudflare)**: in Vercel → Project → Settings → Domains, add `fdeplaybook.dev` and `www.fdeplaybook.dev`. Vercel shows the DNS records to create (usually an `A` record for the root and a `CNAME` for `www`). Add them in Cloudflare → DNS and set each record to **DNS only** (grey cloud), so Vercel can issue the HTTPS certificate. `.dev` domains only work over HTTPS, which Vercel handles.
3. **Supabase** (free tier): create a project, then run `supabase/migrations/0001_init.sql` in the SQL editor. Under Authentication → URL Configuration, set the Site URL to `https://fdeplaybook.dev` and add `https://fdeplaybook.dev/auth/callback` to the redirect URLs.
4. **Stripe**: copy the secret key. Add a webhook endpoint at `https://fdeplaybook.dev/api/stripe/webhook` with the events `checkout.session.completed`, `checkout.session.async_payment_succeeded` and `charge.refunded`, then copy its signing secret. Optionally create a one-time Price matching the current price and put its ID in `STRIPE_PRICE_ID`.
5. **Environment variables**: fill in everything in `.env.example` in Vercel → Settings → Environment Variables (and in `.env.local` for local testing), then redeploy.
6. **Free access for yourself**: set `FREE_ACCESS_EMAILS` to your email (comma-separate several). After you log in with that email, every module is unlocked without paying.
7. **Test the whole course on a preview link**: in Vercel → Settings → Environment Variables, add `PREVIEW_UNLOCK_ALL` = `true` for the **Preview** environment only. Preview deployments (any branch other than `main`) then have every module unlocked; production is never affected.
8. **Test a purchase** in Stripe test mode with card `4242 4242 4242 4242`, then switch Stripe to live keys.

The price is set in one place: `priceUsd()` in `lib/config.ts` ($149 for the FDE-only course, $249 once `TRACKS_LIVE=true`). If you use `STRIPE_PRICE_ID`, keep that Stripe Price at the same amount, or leave it unset so checkout charges `priceUsd()` inline.

Purchase flow: `/buy` → login if needed → Stripe Checkout → `/purchase/success`. The success page records the purchase immediately, and the webhook records it too as a backup (writes are idempotent). A full refund removes access.

## Three tracks (in progress)

The course is growing into a shared core plus three tracks (Applied AI Engineer, Applied AI Architect, FDE). The plan, owner decisions and build log are in `docs/TRACKS_PLAN.md`. The tracks show in dev and on unlocked previews; production shows them once `TRACKS_LIVE=true`.

New lesson types: `drill` (timed, multi-level Python), `written` (graded by Claude against a rubric) and `roleplay` (a conversation with a Claude persona, then a scored debrief). Each Claude-backed action counts against a per-learner daily limit (`AI_DAILY_LIMIT`, table in `supabase/migrations/0002_ai_usage.sql`).

## Not built yet

- Certificates of completion
