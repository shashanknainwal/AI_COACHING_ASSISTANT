# FDE Course

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
- **Simulated Anthropic SDK:** `public/py/anthropic/` mirrors the real `anthropic` Python SDK (`messages.create`, content blocks, `stop_reason`, `usage`, typed errors, retries). Exercises script replies through `anthropic._sim` in `setup.py`. Learner code works unchanged against the real API.
- **Simulated `requests` library:** `public/py/requests/` mirrors `requests` (`get`/`post`, `Session`, `Response`, `raise_for_status`, timeouts, exception classes). Exercises define fake APIs with `requests._sim.route(...)`, including `flaky(...)` failures and `rate_limited(...)` endpoints.
- **Fake clock:** `public/py/fde_clock.py` makes `time.sleep` instant and recorded, so retry/backoff exercises run immediately and tests can check exact delays.
- Packages the course simulates are never downloaded from the Pyodide CDN, even when learner code imports them.
- **AI tutor:** `app/api/tutor/route.ts` calls Claude through the Anthropic TypeScript SDK to give hints without giving away the answer.
- **Progress:** cached in `localStorage`, and synced to Supabase when signed in (`lib/progress.ts`, `app/api/progress`).

## Accounts and payments

The app picks a mode from environment variables:

| Mode | When | Behavior |
|---|---|---|
| Dev preview | `npm run dev`, no Supabase keys | Every module unlocked, "Dev preview" badge |
| Unconfigured | Production build, no Supabase keys | Module 1 free, paid modules locked, nothing for sale |
| Live | Supabase keys set | Email magic-link login, Module 1 free, Modules 2–10 need the $99 purchase, progress syncs to the account |

Paid lesson content is rendered on the server only for learners who bought the course, so it never reaches the browser otherwise.

### Going live

1. **Supabase** (free tier): create a project, then run `supabase/migrations/0001_init.sql` in the SQL editor. Under Authentication → URL Configuration, set the Site URL to your domain and add `https://YOUR_DOMAIN/auth/callback` to the redirect URLs.
2. **Stripe**: copy the secret key. Add a webhook endpoint at `https://YOUR_DOMAIN/api/stripe/webhook` with the events `checkout.session.completed`, `checkout.session.async_payment_succeeded` and `charge.refunded`, then copy its signing secret.
3. **Environment variables**: fill in everything in `.env.example` (locally in `.env.local`, in production in your host's settings).
4. **Test a purchase** in Stripe test mode with card `4242 4242 4242 4242`.

Purchase flow: `/buy` → login if needed → Stripe Checkout → `/purchase/success`. The success page records the purchase immediately, and the webhook records it too as a backup (writes are idempotent). A full refund removes access.

## Not built yet

- Modules 5–10 content (the syllabus is in `content/course.json`)
- Certificates of completion
- Per-user rate limit on the AI tutor
- Deployment to Vercel and a custom domain
