---
title: "Exercise: Decode the Posting"
type: exercise
minutes: 30
hints:
  - "In `parse_posting`, walk the lines with `text.splitlines()`, strip each one, and keep a `section` variable. A line ending in `:` that isn't a bullet sets the section; look its lowercased name up in a dict like `{\"must have\": \"must\", \"nice to have\": \"nice\", \"logistics\": \"logistics\"}` so unknown headings give `None`."
  - "A bullet starts with `\"- \"` or `\"* \"`. Only keep it when `section` isn't `None`. For the tag, check `body.endswith(\"]\")`, find the last `[` with `body.rindex(\"[\")`, slice out the tag, lowercase it, and strip it off the text."
  - "`score_evidence`: start from `{\"work\": 2, \"project\": 1, \"course\": 1}.get(kind, 0)`. If that's 0, return 0. Add 1 for a project with a `link`, add 1 for a `metric`, then `min(points, 3)`."
  - "`gap_report`: handle logistics (`\"ask\"`) and untagged rows (`\"review\"`) first. Otherwise loop over evidence, compare tags lowercased (build a new list; don't change the input), and only replace the best item when the score is strictly greater, so the first one wins ties."
  - "`focus_list` is three passes over the report in posting order: (must, red), then (must, amber), then (nice, red). A nested list comprehension does it in one line."
---

Hana Ostrowski, your career coach at Ossian Careers (both fictional), has a rule: **no application goes out until you've decoded the posting.** Last week you sent her three postings and a page of notes about your experience. She sent back one line: *"Which of these jobs does your evidence actually support, and what would you fix first?"*

You did the green-amber-red exercise from module C1 by hand once. It took an hour and you'll want to do it for every posting you consider. So you'll write a small tool: it reads a posting, matches each requirement against your evidence list, scores the evidence, and prints a gap report plus a focus list.

## The data

**A posting** is plain text. Requirements are bullets (`- ` or `* `) under one of three headings: `Must have:`, `Nice to have:` and `Logistics:` (case-insensitive). Each bullet may end with a tag in square brackets that says what kind of evidence it needs:

```text
Must have:
- Built evaluation frameworks for LLM systems [evals]
- Explains technical tradeoffs to customers [customer]

Logistics:
- Travel up to 25% to customer sites
```

Real postings don't come with tags. Adding them is your first job when you copy a posting into your notes: it forces you to decide what each line is really asking for.

**Your evidence** is a list of dicts:

```python
{"claim": "Public eval harness repo for a support classifier",
 "tags": ["evals"], "kind": "project", "link": "github.com/you/evals", "metric": False}
```

`kind` is `"work"` (done in a job), `"project"` (done on your own), `"course"` (learned, not applied) or something else, which doesn't count. `link` and `metric` are optional.

## Your task

**1. `parse_posting(text)`** returns a list of `{"text", "tag", "priority"}` dicts, in posting order.

- `priority` is `"must"`, `"nice"` or `"logistics"` from the heading above the bullet.
- Bullets under any other heading, or before the first known heading, are ignored. So are lines that aren't bullets.
- `tag` is the text inside a trailing `[...]`, stripped and lowercased, or `None` if there isn't one. Remove it from `text`.

**2. `score_evidence(item)`** returns 0 to 3.

| Rule | Points |
|---|---|
| `kind` is `"work"` | 2 |
| `kind` is `"project"` or `"course"` | 1 |
| Any other kind | 0, and nothing else is added |
| A `"project"` with a non-empty `link` | +1 |
| A truthy `metric` | +1 |
| Cap | 3 |

**3. `gap_report(requirements, evidence)`** returns one row per requirement, in order: `{"requirement", "priority", "status", "best"}`.

| Status | When |
|---|---|
| `"ask"` | The requirement is logistics. You confirm these with the recruiter and decide; evidence doesn't apply. |
| `"review"` | The requirement has no tag. Go back and tag it. |
| `"green"` | The best matching evidence scores 3. |
| `"amber"` | It scores 1 or 2. |
| `"red"` | Nothing matches, or everything that matches scores 0. |

Evidence matches when the requirement's tag is in its `tags` (compare lowercased). `best` is the matching claim with the highest score; the earlier one wins a tie. It's `None` when nothing scores above 0. Don't modify the inputs.

**4. `focus_list(report)`** returns requirement texts to work on: must-have reds, then must-have ambers, then nice-to-have reds, each group in posting order.

## Example

With the practice posting and evidence in the starter code:

```text
green   must      4+ years in a technical role  <- 6 years backend engineering at a logistics SaaS
amber   must      Built evaluation frameworks for LLM systems  <- Public eval harness repo ...
green   must      Strong Python  <- 6 years backend engineering at a logistics SaaS
red     must      Explains technical tradeoffs to customers  <- None
red     nice      Retrieval or RAG systems in production  <- None
amber   nice      Experience with agents and tool use  <- Completed course module on agents
ask     logistics Travel up to 25% to customer sites  <- None

Focus: ['Explains technical tradeoffs to customers',
        'Built evaluation frameworks for LLM systems',
        'Retrieval or RAG systems in production']
```

The practice posting is fictional, written in the general shape of applied-AI postings. Copy a real one in its place when you use the tool for yourself, and read C1 lesson 1 for the live links.

> **Coach's note (Hana):** "A red on a must-have isn't a reason not to apply. A red you haven't noticed is. Know your reds before the recruiter does, and have one honest sentence ready for each."

The scoring weights are our judgement (**General**): a recruiter or hiring manager won't score you this way. The point is to make you look at each line and ask whether you have evidence you could talk about for five minutes.
