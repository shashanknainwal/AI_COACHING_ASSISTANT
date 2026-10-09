---
title: "Round 1: A Prompt-Template Registry"
type: drill
minutes: 90
timeLimit: 90
levels:
  - "Versions and rendering"
  - "Tags, search and usage"
  - "A/B splits"
  - "Rollback and history"
hints:
  - "Level 4 asks which version a user got at any past time. That depends on two things that change over time: the active version and the split. Keep a per-template list of (time, active_version, split) entries from Level 1, and append one on every change."
  - "Write one regex for placeholders, r\"\\{\\{([A-Za-z0-9_]+)\\}\\}\", and use it for render, get_variables and the missing-variable check. re.sub with a function fills every occurrence."
  - "For a split, sort the version numbers, walk them while adding up percentages, and return the first version whose running total is greater than the user's bucket."
  - "Factor the version choice into one helper that takes (active, split, user_id). assign calls it with the current config; version_at calls it with the config found in history."
---

Round 1 of your mock loop. Leo Martins hands you the problem the way a screen would: "Every team at our customer keeps prompts in string constants. Build them a registry: versioned templates, A/B splits, and an answer to the question every incident review asks, 'what prompt did this user actually get?'"

This is an original problem in the progressive format candidates describe for practical coding screens (**Reported**; see module C3). One class, four levels, 90 minutes. No AI help, no tutor, no searching for solutions: the round only tells you something if you run it the way the real one runs.

## The rules

- Implement a class called `TemplateRegistry`. Every method takes `timestamp` (an integer) as its first argument, and timestamps only ever increase from one call to the next.
- Press **Submit** to run the checks for the levels you can see. When every check for a level passes, the next level opens.
- Write down the time when you clear each level. Lesson 06 uses those times for your scorecard.
- If the clock runs out, note which level you were on, then keep going. Finishing late is still practice, but it scores lower.

## Level 1: Versions and rendering

A template is a named prompt with numbered versions. Versions are never edited or deleted.

- `add_version(timestamp, name, body)`: add a new version of the template `name`, creating the template if it doesn't exist. Return the new version number: `1` for a template's first version, then `2`, `3`, and so on, counted per template. The newest version becomes the **active** version.
- A placeholder is `{{` + a variable name + `}}`, where the name is one or more letters, digits or underscores, with no spaces. Anything else (`{ x }`, `{{ x }}`) is plain text.
- `render(timestamp, name, variables, version=None)`: fill every placeholder in the given version (or the active version when `version` is `None`) with `str(variables[var])`. Extra keys in `variables` are ignored. Return the rendered string.
  - Return `None` if the template or the version doesn't exist.
  - If any placeholder has no value, return `"error: missing "` followed by the missing names, sorted, without duplicates, joined by commas: `"error: missing alpha,zeta"`.
- `get_variables(timestamp, name, version=None)`: return the sorted list of distinct variable names in the given (or active) version, or `None` if the template or version doesn't exist.

Example:

```python
r = TemplateRegistry()
r.add_version(1, "greet", "Hi {{name}}, welcome to {{product}}.")   # 1
r.render(2, "greet", {"name": "Ada", "product": "Atlas"})          # "Hi Ada, welcome to Atlas."
r.render(3, "greet", {"name": "Ada"})                               # "error: missing product"
```

## Level 2: Tags, search and usage

Teams want to find prompts and see which ones matter.

- `tag(timestamp, name, tags)`: add each string in the list `tags` to the template. Tags belong to the template, not to a version. Adding a tag it already has is fine. Return `True`, or `False` if the template doesn't exist.
- `search(timestamp, tag, text)`: return the names of templates that have the tag `tag` **and** whose active version's body contains `text`, case-insensitively. An empty `tag` matches every template; an empty `text` matches every body. Sort the names.
- `top_used(timestamp, n)`: return up to `n` templates ranked by uses, highest first, ties broken by name, each formatted as `"name(count)"`. Leave out templates with no uses.
- A **use** is a call to `render` that returns rendered text. Calls that return `None` or a missing-variable error don't count.

## Level 3: A/B splits

The customer wants to test a new prompt on part of their traffic, and each user must see the same version every time.

- A user's **bucket** is `sum(ord(c) for c in user_id) % 100`. For example, `"alice"` is in bucket 10 and `"carol"` in bucket 29.
- `set_split(timestamp, name, split)`: `split` maps version numbers to whole percentages, for example `{1: 20, 2: 80}`. Sort the versions in ascending order and give each one a range of buckets in turn: here version 1 gets buckets 0 to 19 and version 2 gets 20 to 99. A version may get 0%. Return `True`, or `False` (changing nothing) if the template doesn't exist, the split is empty, any version doesn't exist, or the percentages don't add up to exactly 100. A new split replaces the old one.
- `assign(timestamp, name, user_id)`: return the version this user gets: from the split if one is set, otherwise the active version. Return `None` if the template doesn't exist.
- `render_for(timestamp, name, user_id, variables)`: render the version `assign` picks for this user. It returns what `render` would, and a successful call counts as a use.
- `clear_split(timestamp, name)`: remove the split, so everyone gets the active version again. Return `True`, or `False` if the template doesn't exist or has no split.
- `render` without a version still renders the active version; it ignores the split.
- `add_version` while a split is running makes the new version active but doesn't change the split.

## Level 4: Rollback and history

A customer reports a bad answer from last Tuesday. The first question in the incident review is which prompt that user got.

- `rollback(timestamp, name, version)`: make `version` the active version **and** clear any split, so every user gets it. Return `True`, or `False` if the template or version doesn't exist. A rollback is a new change recorded at `timestamp`; earlier history stays as it was, and version numbers keep counting up afterwards.
- `version_at(timestamp, name, user_id, at)`: return the version `assign` would have returned for this user at time `at`, using the active version and split that applied then. A change made at exactly `at` counts. Return `None` if the template didn't exist at `at`.

## After the round

Record three things before you look at the solution: the level you reached, the minute you cleared each level, and the one decision that cost you the most time. Lesson 06 turns these into your round score.
