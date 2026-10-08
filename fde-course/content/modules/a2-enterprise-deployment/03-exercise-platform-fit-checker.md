---
title: "Exercise: Requirements-to-Platform Checker"
type: exercise
minutes: 30
hints:
  - "Start `check_platform` with three empty lists: `reasons`, `gaps`, `open_items`. Use `requirements.get(...)` so a missing key means 'not required'."
  - "Run the checks in the fixed order: procurement, processor, geo, each feature, zdr (then conflicts), private_network. Appending as you go gives you the right gap order for free."
  - "ZDR and private networking share one rule: 'yes' adds a reason, 'confirm' adds an open item, anything else adds a gap. A small helper keeps both checks identical."
  - "The ZDR conflict check loops over the required features again and adds `conflict: <feature> ...` for each one in `non_zdr_features`, whatever the platform supports."
  - "In `shortlist`, sort eligible results with `key=lambda r: (len(r[\"open_items\"]), r[\"platform\"])`, and build `blocked` as `{r[\"platform\"]: r[\"gaps\"] ...}` for the ineligible ones."
---

Grace Liu here. Tomorrow we're in front of **Granite Mutual Bank** (fictional), and their platform team keeps changing the requirements list. Every time they do, someone rebuilds the platform comparison in a spreadsheet by hand and gets a cell wrong.

I want a small checker instead. Feed it the customer's requirements and a capability table, and it tells us which platforms are eligible, why, what blocks the rest, and what we still have to confirm. The capability table is passed in, never hard-coded, because it changes every few weeks and a real review re-checks it against the docs. The one loaded for you as `PLATFORMS` is **illustrative**: a simplified snapshot of lesson 01, not a source of truth.

## The data

`PLATFORMS` maps a platform name to its capabilities:

```python
"claude_platform_aws": {
    "label": "Claude Platform on AWS",
    "procurement": ["aws"],             # how it can be bought
    "processor": "anthropic",           # "anthropic" or "cloud_provider"
    "geos": ["global", "us"],           # where inference can be pinned
    "features": ["prompt_caching", "batches", ...],
    "zdr": "yes",                       # "yes" | "confirm" | "no"
    "private_network": "yes",           # "yes" | "confirm" | "no"
}
```

`NON_ZDR_FEATURES` lists features that aren't eligible for zero data retention (from Anthropic's data retention page): `batches`, `files_api`, `code_execution`, `agent_skills`, `mcp_connector`, `managed_agents`.

A customer's requirements look like this. Every key is optional; a missing key, `None`, `False` or an empty list means "not required":

```python
{"procurement": "aws", "processor": "anthropic", "geo": "us",
 "features": ["prompt_caching", "batches"], "zdr": True, "private_network": True}
```

## Your task

**1. `check_platform(name, platform, requirements, non_zdr_features)`** returns:

```python
{"platform": name, "eligible": bool, "reasons": [...], "gaps": [...], "open_items": [...]}
```

Run these checks in this order. Every string starts with its code and a colon, for example `"geo: needs eu, platform offers global, us"`.

| Check (code) | Runs when | Pass | Fail |
|---|---|---|---|
| `procurement` | requirement set | reason | gap naming what's needed |
| `processor` | requirement set | reason | gap naming what's needed |
| `geo` | requirement set | reason | gap naming the geo |
| `feature` | once per required feature, in order | reason | gap naming the feature |
| `zdr` | `zdr` is true | `"yes"`: reason | `"confirm"`: **open item**; `"no"`: gap |
| `conflict` | `zdr` is true; once per required feature that's in `non_zdr_features` | | gap naming the feature |
| `network` | `private_network` is true | `"yes"`: reason | `"confirm"`: **open item**; `"no"`: gap |

A platform is **eligible** when it has no gaps. Open items don't block; they're the questions you take to the call.

The `conflict` rule is deliberate. Under ZDR the API doesn't block non-eligible features, so a design that "needs ZDR" and "uses Batches" contradicts itself on every platform. The checker must say so instead of quietly passing.

**2. `shortlist(platforms, requirements, non_zdr_features)`** returns:

```python
{"eligible": ["best", "next", ...], "blocked": {"name": [gaps], ...}}
```

Sort eligible platforms by number of open items (fewest first), then by name. Don't modify the table.

## Example

```python
req = {"procurement": "aws", "geo": "us", "features": ["prompt_caching", "batches"], "private_network": True}
shortlist(PLATFORMS, req, NON_ZDR_FEATURES)
# {"eligible": ["claude_platform_aws"],
#  "blocked": {"claude_api": ["procurement: needs aws, ..."],
#              "bedrock": ["feature: batches not available"], ...}}
```

Now add `"zdr": True` and run it again. Nothing is eligible, because Batches isn't ZDR-eligible. That's the most useful output this tool can produce: it tells you to go back to the customer and ask which requirement gives way, for example moving the overnight job to standard Messages calls.

> **Architect tip:** Present the output, not the code. "Two platforms are eligible; here's why; here are three things we must confirm by Friday" is the sentence that moves a deal forward.
