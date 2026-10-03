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
- **AI tutor:** `app/api/tutor/route.ts` calls Claude through the Anthropic TypeScript SDK to give hints without giving away the answer.
- **Progress:** stored in `localStorage` for now (`lib/progress.ts`).

## Not built yet

- Accounts (Supabase), the $99 Stripe paywall, server-side progress, and certificates
- Modules 2–10 content (the syllabus is in `content/course.json`)
- Deployment to Vercel and a custom domain
