---
title: "Exercise: Label the Claims"
type: exercise
minutes: 20
hints:
  - "In `label_claim`, check for a `company` source first and return `\"official\"` straight away. Nothing else matters once the company has said it."
  - "Only the kinds `candidate`, `guide` and `news` count as independent. Ignore every other kind, including ones you've never seen."
  - "Collect the ids in a set so duplicates disappear: `{s[\"independent_id\"] for s in sources if s[\"kind\"] in (\"candidate\", \"guide\", \"news\")}`. Then look at its length."
  - "In `prep_priorities`, map each label to a number (official 0, reported 1, anecdotal 2), skip unsupported claims, and sort by that number. Python's `sorted()` is stable, so ties keep their original order for free."
---

You've been collecting interview notes for three weeks: forum threads, a couple of prep blogs, a news piece, a line from a careers page, and something your cousin heard from a friend. Your interview coach, Nadia Okafor, looks at the pile and asks one question: **"Which of these would you bet your prep time on?"**

You don't know, because the notes don't say where each claim came from or how many people agree. So you've rewritten every note as a claim with its sources. Now you'll write the code that labels each claim the way this course does (official, reported, anecdotal) and turns the pile into a prep plan you can trust.

## The data

Each claim is a dictionary with its text and a list of sources:

```python
{
    "text": "The online assessment is one problem with about four levels",
    "sources": [
        {"kind": "candidate", "independent_id": "forum-post-a"},
        {"kind": "guide",     "independent_id": "prep-blog-b"},
        {"kind": "candidate", "independent_id": "forum-post-c"},
    ],
}
```

- `kind` is `"company"` (the lab itself: careers page, job posting, official guidance), `"candidate"` (a first-hand account), `"guide"` (a prep site or career-centre article) or `"news"`. Your notes may contain other kinds, such as `"friend"`. Those don't count as evidence.
- `independent_id` names the original source. Two entries with the same id are the same source, even if they arrived by different routes (for example, two blogs quoting the same forum post were both given that post's id).

## Your task

Write two functions.

**1. `label_claim(claim)`** returns one string:

| Return | When |
|---|---|
| `"official"` | Any source has kind `"company"`. |
| `"reported"` | Otherwise, at least **3 distinct** `independent_id` values among sources of kind `"candidate"`, `"guide"` or `"news"`. |
| `"anecdotal"` | Otherwise, 1 or 2 distinct ids among those kinds. |
| `"unsupported"` | No sources of those kinds at all (including an empty list). |

**2. `prep_priorities(claims)`** returns a list of claim **texts** to prepare for:

1. Official claims first, then reported, then anecdotal.
2. Drop unsupported claims entirely.
3. Claims with the same label keep their original order.
4. Don't modify the input list.

## Example

```python
notes = [
    {"text": "Live interviews are AI-free unless they say otherwise",
     "sources": [{"kind": "company", "independent_id": "careers-page"}]},
    {"text": "The online assessment is one problem with about four levels",
     "sources": [{"kind": "candidate", "independent_id": "forum-post-a"},
                 {"kind": "guide", "independent_id": "prep-blog-b"},
                 {"kind": "candidate", "independent_id": "forum-post-c"}]},
    {"text": "Interviewers like hearing about a favourite paper",
     "sources": [{"kind": "guide", "independent_id": "prep-blog-b"},
                 {"kind": "guide", "independent_id": "prep-blog-b"}]},   # one source, twice
    {"text": "You must memorise the lab's essays",
     "sources": [{"kind": "friend", "independent_id": "my-cousin"}]},    # not evidence
]

[label_claim(n) for n in notes]
# -> ["official", "reported", "anecdotal", "unsupported"]

prep_priorities(notes)
# -> ["Live interviews are AI-free unless they say otherwise",
#     "The online assessment is one problem with about four levels",
#     "Interviewers like hearing about a favourite paper"]
```

The example notes are practice data for this exercise, not research findings. Press **Run** to try your code on them, then **Submit** to grade it.

> **Coach's tip:** The distinct-id rule is the one that matters in real life. A claim repeated by ten prep sites that all copied one forum post is still one account. Before you trust a "fact", trace it back to where it started.
