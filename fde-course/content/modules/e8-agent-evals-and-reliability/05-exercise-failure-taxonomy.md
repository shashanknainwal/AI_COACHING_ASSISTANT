---
title: "Exercise: From 60 Failures to a Ranked Taxonomy"
type: exercise
minutes: 40
hints:
  - "`normalize`: replace the curly apostrophes first, then use one regular expression that deletes every character that is not a lowercase letter, digit, apostrophe, hyphen or space. Finish with `' '.join(text.split())`."
  - "`categorize`: dicts keep insertion order, so a plain loop over `CODEBOOK.items()` gives you 'first match wins'."
  - "`root_cause`: sort the notes by step, categorize each one, and drop the `None`s. The first category left is the root cause, and the rest are downstream. If nothing is left, the failure is uncategorized."
  - "`rank`: skip `uncategorized`, compute `impact = count * cost`, sort with the key `(-impact, category)`, then walk the sorted list once with a running total for the cumulative share."
  - "`analyze`: the uncategorized share is computed over all failures, including the uncategorized ones. `most_frequent` is a separate sort by count, kept so you can see that it differs from the top of the impact ranking."
---

Teodora Kessler (Gannet Home Energy, fictional) has done the step most teams skip. "We sampled 400 production conversations last week and three reviewers read every one. Sixty failed. Each reviewer wrote a quick note at the step where things went wrong, and after the first thirty traces we agreed a codebook. Now turn the notes into a taxonomy I can take to the steering group: what fails, how often, what it costs, and the two fixes we do first, each with the eval that proves it worked."

`FAILURES`, `CODEBOOK`, `COST_PER_FAILURE` and `FIX_LIBRARY` are loaded for you.

## Background: error analysis before metrics

You can't write a useful eval for a failure you haven't seen. The working method is short:

1. **Sample and read.** Pull a random sample of real traces (here 400), plus the ones users complained about. Read whole traces, not just final answers.
2. **Open coding.** Write a short free-text note at the **first** step where the agent went wrong. Don't force categories yet.
3. **Axial coding.** After 20 to 40 failures, group the notes into categories with definitions and keywords: the codebook. Keep coding new traces and add categories until new traces stop producing them. If more than about one note in ten fits no category, the codebook isn't finished.
4. **Attribute to the root cause.** An early mistake causes later ones. A wrong account ID at step 3 produces a false "done" at step 6. Count the failure once, under the earliest category, or the downstream symptom looks bigger than it is and you fix the wrong thing.
5. **Rank by frequency × cost.** A rare failure that costs $220 (a vulnerable customer not passed to a human) can matter more than a common one that costs a repeat contact. Agree the per-failure costs with the people who pay them.
6. **Fix and measure.** Each top category gets a fix at the right layer (tool code, tool results, prompt, retrieval) and an eval that would have caught it. The traces you read become the first cases in that eval.

## Your task

**1. `normalize(note)`**: lowercase, curly apostrophes (`‘`, `’`) become `'`, delete every character that isn't `a-z`, `0-9`, `'`, `-` or a space, and collapse runs of whitespace into single spaces.

**2. `categorize(note)`**: the first `CODEBOOK` category (in dict order) with a keyword that appears in the normalized note, or `None`.

**3. `root_cause(failure)`**: sort `failure["notes"]` by `step` (they come in a random order), categorize each, and drop notes that match nothing. Return `(root, downstream)`: the first category, and the list of later categories. With no categorized note, return `("uncategorized", [])`.

**4. `build_taxonomy(failures)`** returns `{"by_root": {category: [ids in FAILURES order]}, "downstream": {category: count}}`.

**5. `rank(taxonomy, costs, total)`** returns one row per category except `uncategorized`: `{"category", "count", "share", "cost_each", "impact", "cumulative_impact_share"}`. `share` is `count / total`, `impact` is `count * cost_each`, and rows are sorted by impact (highest first, ties by name). `cumulative_impact_share` is the running impact total over the sum of all impacts. Round shares to 3 decimals.

**6. `propose_fixes(ranked, taxonomy, top=2)`**: for each of the top rows, `{"category", "impact", "layer", "fix", "eval", "examples"}`. The layer, fix and eval come from `FIX_LIBRARY`, and `examples` is the first three ids in that category.

**7. `analyze(failures, max_uncategorized=0.10)`** returns `ranked`, `most_frequent` (highest count, ties by name), `uncategorized` (ids), `uncategorized_share` (3 decimals), `codebook_saturated` (share at most the threshold), `downstream` (sorted by category) and `fixes`.

## Example

```python
>>> categorize("Didn’t verify identity before changing tariff")
'identity_skipped'
>>> analyze(FAILURES)["most_frequent"]
'false_completion'
```

Press **Run** to see the table, then **Submit**.

## What to notice

- **The most frequent failure is third on impact.** False completions are 14 of 60, but missed escalations and skipped verification cost more in total. A frequency chart would have sent the team to the wrong fix first.
- **Counting every note inflates the symptoms.** Four false completions and three wrong credits were caused by earlier mistakes. Counting them would make false completions 18 and hide that tool-argument errors cause some of them.
- **The top two fixes are both in code, not in the prompt.** One layer of each fix is a control the model can't talk its way past, which is the theme of lesson 10.
- **Two failures fit nothing.** At 3% the codebook is good enough. If you sampled another week and it rose above 10%, you'd read those traces and extend the codebook before trusting the ranking.

Write the two fixes into a short note for Teodora: the category, its share and impact, the fix and its layer, and the eval you would add, seeded with the example traces.
