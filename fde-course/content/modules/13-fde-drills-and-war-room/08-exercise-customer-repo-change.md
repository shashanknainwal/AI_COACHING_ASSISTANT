---
title: "Exercise: Land a Change in a Customer's Repo"
type: exercise
minutes: 30
hints:
  - "Start with tree() and show('README.md'). Then read hooks.py and audit.py: the repo already tells you where customer rules go."
  - "Before writing a phone parser, look for one. Read tidewater/phone.py."
  - "A hook takes a record and returns it, or returns None to send the row to review. Register yours with @hook('your_name') in a new module."
  - "A hook module does nothing until settings.py lists it in HOOK_MODULES (so it is imported) and its hook name in ENABLED_HOOKS (so it runs). Append to both lists; keep audit_trail."
---

Tidewater Supply, a fictional distributor and one of Marram's clients, imports contacts from CSV exports. Their ops lead wants two rules: every saved phone number in E.164 form (`+1` and ten digits), and any row with no email sent to manual review. "Small change," he says. "The importer is right there."

The importer is shared by three customers. This exercise is about the FDE skill that matters most in an unfamiliar codebase: **find the integration point the code already offers, and land the smallest change that works.**

## The repo

Your editor isn't the repo. The repo is on disk at `/tmp/tidewater_repo` (the package `tidewater`), rebuilt fresh every time you press Run or Submit. Setup gives you helpers:

- `tree()` prints every file; `show("tidewater/hooks.py")` prints a file with line numbers.
- `write_file(path, text)` creates a file. `edit_file(path, old, new)` replaces one exact snippet in a file, like a one-hunk patch, and raises if the snippet isn't found exactly once.
- After editing, `from tidewater.importer import import_contacts` and `from tidewater.store import MemoryStore` let you try it: `import_contacts(csv_text, store)` returns counts, and the store has `saved` (by email) and `review`.

## The requirement

- A saved contact's `phone` is in E.164 form. A row whose phone is blank is saved with `phone` set to `None`. A row whose phone isn't a valid US number goes to review.
- A row with no email goes to review.
- Everything that worked before still works, including the existing audit hook.

## How it's checked

- The checks reload the package from disk and import a sample CSV, then check the behaviour above.
- They also check the **diff**: the shared files (`importer.py`, `hooks.py`, `phone.py`, `store.py`, `audit.py`, `legacy_sync.py`, the README) must be unchanged, `settings.py` may change only its hook lists, you may add at most one new file, and it must reuse the phone helper the repo already has.

## Why this matters in the job

On site, the customer's code is not yours. A change in the shared importer works today and breaks two other customers next month, and the reviewer who owns that file will reject it. Reading the README, finding the extension point, reusing the helper that exists, and keeping the diff small is how you earn commit access. Interviewers probe the same instinct when they hand you an unfamiliar repo: they watch where you look before you type.
