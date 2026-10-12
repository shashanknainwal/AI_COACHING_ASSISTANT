---
title: "Exercise: Port Audit for a Locked-Down Platform"
type: exercise
minutes: 30
hints:
  - "`features_used` and `files_using` are one set comprehension each, wrapped in `sorted(...)`."
  - "In `audit_platform`, loop over `features_used(call_sites)` and look each one up with `matrix[name].get(feature, \"unknown\")`. Handle `yes`, then beta with `allow_beta`, then `no` or beta without it, then `partial`, then anything else."
  - "A blocker is `{\"feature\": f, \"files\": files_using(call_sites, f), \"workaround\": workarounds.get(f)}`. `.get` gives you `None` when there is no workaround."
  - "Work out the verdict from worst to best: any blocker whose workaround is `None` gives `blocked`; any blockers gives `rework`; any open items gives `confirm`; any beta gives `ready_with_beta`; otherwise `ready`. Check residency before you decide, because it can add an open item."
  - "In `port_report`, sort with `key=lambda a: (VERDICT_ORDER.index(a[\"verdict\"]), len(a[\"rework_files\"]), a[\"platform\"])`."
---

Sana Iqbal here, Platform Engineering at Quarrybank. Your team built the support-triage prototype on the Claude API from your own sandbox. It works. Now it has to move into our AWS account, and our cloud security group's first instinct is Amazon Bedrock because we already use it.

Before I take that to the architecture board I need to know what breaks, in which files, on each option, and what you would do instead. Not a feature list from a slide. An audit of the code you actually wrote.

## The data

`QUARRYBANK_PROTOTYPE` is an inventory of call sites: one entry per file and API feature it uses. In a real engagement you'd build it by searching the repository for `batches.create`, `mcp_servers`, `container`, `fallbacks` and so on.

```python
{"file": "jobs/nightly_backfill.py", "feature": "batches"}
```

`PLATFORM_FEATURES` maps each platform to a status per feature: `"yes"`, `"beta"`, `"partial"` (only on some deployments, for example Foundry features that need an Anthropic-hosted deployment) or `"no"`. It is an **illustrative snapshot** of the platform availability table from October 2026, passed in as an argument because it changes. Re-check every row against the current docs in a real audit. `WORKAROUNDS` maps a feature to what you'd do on a platform that lacks it.

## Your task

**1. `features_used(call_sites)`** returns the distinct features, sorted.

**2. `files_using(call_sites, feature)`** returns the distinct files that use one feature, sorted.

**3. `audit_platform(name, matrix, call_sites, requirements, workarounds)`** returns:

```python
{"platform": name, "verdict": "...", "blockers": [...], "beta": [...],
 "open_items": [...], "residency": None | "inference_geo" | "confirm", "rework_files": [...]}
```

For each feature used, in sorted order, look up its status (a feature missing from the platform's dict is `"unknown"`):

| Status | Result |
|---|---|
| `yes` | Nothing |
| `beta` and `requirements["allow_beta"]` is true | Add the feature to `beta` |
| `no`, or `beta` without `allow_beta` | Add a blocker: `{"feature", "files": files_using(...), "workaround": workarounds.get(feature)}` |
| `partial` | Add an open item starting `"<feature>:"` |
| unknown | Add an open item starting `"<feature>:"` |

**Residency.** If `requirements["residency"]` is set (for example `"us"`): when the platform's `inference_geo` status is `"yes"`, set `residency` to `"inference_geo"`. Otherwise set it to `"confirm"` and add an open item starting `"residency:"` that names the requested geography. On those platforms the region or deployment type decides where inference runs. If residency isn't required, `residency` is `None`.

**Verdict**, worst first: `"blocked"` if any blocker has no workaround, `"rework"` if there are blockers, `"confirm"` if there are open items, `"ready_with_beta"` if there are beta features, else `"ready"`.

`rework_files` is the sorted, distinct list of files across all blockers.

**4. `port_report(matrix, call_sites, requirements, workarounds)`** audits every platform in the matrix and sorts the results by verdict (in `VERDICT_ORDER`), then by number of rework files, then by name. Don't modify the matrix.

## Example

```python
port_report(PLATFORM_FEATURES, QUARRYBANK_PROTOTYPE, {"residency": "us", "allow_beta": True}, WORKAROUNDS)
# claude_api           ready_with_beta
# claude_platform_aws  ready_with_beta
# foundry              rework    (batches, server_fallbacks; code_execution to confirm)
# bedrock              rework    (5 files)
# vertex               rework    (5 files)
```

Press **Run** to see the report with and without beta features allowed.

## What you'd tell Sana

The code tells you Bedrock means rewriting five files, including the nightly backfill, which loses the Batches discount. Claude Platform on AWS keeps the code as it is, with IAM and AWS billing, but Anthropic becomes the data processor, which is a legal question rather than an engineering one. That is the trade the board decides. Your job is to put the cost of each side in numbers: files, days and dollars.

> **FDE tip:** Run this audit before the prototype gets popular, not after. The day a stakeholder demos the prototype to their CIO is the day "just move it to Bedrock" becomes a deadline.
