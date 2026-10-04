---
title: "Exercise: Claude-Suggested Schema Mapping with Validation"
type: exercise
minutes: 30
hints:
  - "`MAPPING_SCHEMA`: the item object has `source` (string), `target` (string with `\"enum\": TARGET_NAMES`), `transform` (string with `\"enum\": TRANSFORMS`) and `confidence` (number). Every object needs `additionalProperties: False` and a full `required` list."
  - "`build_prompt`: `json.dumps(samples, indent=2)` and a bullet line per target field, `f\"- {name}: {description}\"`, under clear headings."
  - "`suggest_mappings` is the extraction pattern from Module 2: call with `output_config`, check `stop_reason`, find the text block, `json.loads`."
  - "In `review`, sort suggestions with `sorted(items, key=lambda m: -m[\"confidence\"])` so the most confident claim on a target wins."
  - "Check in order: unknown source → rejected; target already used → rejected; confidence < threshold → needs_review; else accepted. Add the target to `used` for both accepted and needs_review."
  - "`missing_required` = required target names not used by any accepted or needs_review mapping, in `TARGET_FIELDS` order."
---

The retailer just signed a second carrier, **Polar Express**, whose API looks nothing like Northwind's. Instead of hand-mapping every field, you'll have Claude propose a mapping, then validate it in code and route anything uncertain to a human. The output is a reviewed mapping you'd commit as config, not something Claude applies to live data.

## Your task

**1. `MAPPING_SCHEMA`** for this shape:

```python
{"mappings": [{"source": "trk_no", "target": "external_id", "transform": "none", "confidence": 0.97}, ...]}
```

`target` uses `"enum": TARGET_NAMES`, `transform` uses `"enum": TRANSFORMS`, `confidence` is a `"number"`. All objects need `"additionalProperties": False` and all properties required.

**2. `build_prompt(samples)`** returns a prompt containing the sample records as JSON and every target field with its description (one line each, `"- name: description"`).

**3. `suggest_mappings(client, samples)`** calls Claude (`model=MODEL`, `max_tokens` ≥ 4096, `system=SYSTEM_PROMPT`, one user message with `build_prompt(samples)`, structured outputs with `MAPPING_SCHEMA`). Raise `ValueError("truncated")` or `ValueError("refused")` for those stop reasons; otherwise return the parsed dict.

**4. `review(suggestions, samples, threshold=0.8)`** validates `suggestions["mappings"]` and returns:

```python
{
    "accepted": [...],         # valid and confidence >= threshold
    "needs_review": [...],     # valid but confidence < threshold
    "rejected": [(mapping, "unknown source field"), (mapping, "duplicate target"), ...],
    "missing_required": ["weight_kg", ...],
}
```

- Process mappings from **highest confidence to lowest**.
- A mapping whose `source` isn't a key in the sample records is rejected with `"unknown source field"`.
- A mapping whose `target` was already claimed by an earlier (more confident) accepted or needs-review mapping is rejected with `"duplicate target"`.
- `missing_required` lists required target fields (in `TARGET_FIELDS` order) that no accepted or needs-review mapping covers.

Press **Run** to get Claude's suggestions for Polar Express and see your review queue, then **Submit**.
