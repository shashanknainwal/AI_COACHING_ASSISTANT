---
title: "Exercise: Reconcile Billing Against the CRM"
type: exercise
minutes: 30
hints:
  - "`normalize_key`: uppercase, then remove whitespace and hyphens with `re.sub(r\"[\\s-]\", \"\", ...)`. Then `m = re.fullmatch(r\"([A-Z]+)0*(\\d+)\", key)`; if it matches, return `m.group(1) + m.group(2)`."
  - "You don't need a special case for keys like `A-000`: the regex must keep at least one digit for `(\\d+)`, so it normalizes to `A0`."
  - "`index_by_key`: loop over rows, normalize the key, and `raise ValueError(f\"duplicate key: {key}\")` if it's already in your dict."
  - "Use set operations on the dict keys: `crm.keys() & billing.keys()` for matched, `-` for each side's leftovers. Wrap each in `sorted(...)`."
  - "For each matched key (sorted), loop over `FIELD_MAP`. Compare plans with `.strip().lower()`. Compare money with `abs(float(a) - float(b)) > tolerance`."
  - "A mismatch entry stores the **original** values: `{\"key\": k, \"field\": crm_field, \"crm\": crm_value, \"billing\": billing_value}`."
---

Cobalt's CFO wants to know, before the new system goes live, whether the CRM and billing agree. You've got both exports. Build the reconciliation.

## The data

```python
# CRM export
{"account_id": "A-1004", "name": "acme corporation", "plan": "Pro", "mrr": "1200.00"}

# Billing export
{"customer_ref": "a1004", "customer_name": "ACME CORP", "plan": "basic", "monthly_amount": "1200"}
```

Field pairs to compare are listed in `FIELD_MAP` in the starter: `("plan", "plan")` and `("mrr", "monthly_amount")`. Names are **not** compared.

## Your task

**1. `normalize_key(key)`**: uppercase, remove all whitespace and hyphens, and drop leading zeros from the number part when the key is letters followed by digits. So `"a-01003 "` → `"A1003"`, and `"A-1001"` → `"A1001"`. Keys that don't fit the letters-then-digits pattern are returned uppercased with whitespace and hyphens removed.

**2. `index_by_key(rows, key_field)`** returns a dictionary from normalized key to row. If two rows normalize to the same key, raise `ValueError("duplicate key: <key>")`. That's the fan-out guard from the lesson.

**3. `reconcile(crm_rows, billing_rows, tolerance=0.01)`** returns:

```python
{
    "matched": ["A1001", "A1003", ...],     # keys in both, sorted
    "only_crm": ["A1009", ...],             # sorted
    "only_billing": ["A1020"],              # sorted
    "mismatches": [
        {"key": "A1004", "field": "plan", "crm": "Pro", "billing": "basic"},
        ...
    ],
}
```

- Plans match if they're equal after `strip().lower()`.
- Money matches if the absolute difference is at most `tolerance`.
- Mismatches are ordered by key, then by the order of `FIELD_MAP`. Store the **original** (uncleaned) values.

**4. `summary(result)`** returns one line, for example:

```
"10 matched, 2 only in CRM, 1 only in billing, 3 field mismatches"
```

Press **Run** to reconcile Cobalt's exports, then **Submit**.

> **In real life** you'd send this to the CFO with the field-ownership table from the lesson: "Billing is the source of truth for plan and amount, so these 3 CRM records need correcting."
