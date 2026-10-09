---
title: Joining and Reconciling Systems of Record
type: reading
minutes: 6
---

> **By the end of this lesson you will be able to:**
> - Normalize keys so two systems match, and avoid the join bug that doubles revenue
> - Produce a reconciliation: matched, missing on each side, field mismatches
> - Decide which system "wins" for each field

Owen wants Claude to answer "what does this customer pay us?" But Cobalt's CRM (owned by Sales) and billing system (owned by Finance) were never connected: some accounts exist in only one, and where both exist, plan and monthly amount don't always agree. Before anything answers that question, you need to know which answer is right.

## Normalize the key, conservatively

| CRM | Billing | Same account? |
|---|---|---|
| `A-1001` | `a1001` | Yes: case and hyphen differ |
| `A-1003` | `A-01003` | Yes: leading zero added by billing |
| `A-1006` | ` A-1006 ` | Yes: whitespace |

Write one key-normalization function and apply it to both sides. Normalize only differences you've seen and confirmed; over-eager normalization merges records that aren't the same.

## The fan-out bug

If a key appears twice on one side, a join produces every combination of matching rows:

```
CRM (one row)           Billing (two rows for A-1003, a duplicate)
A-1003  Cobalt Rigging  A-1003  $850
                        A-1003  $850

Joined: two rows for A-1003 → revenue counted twice
```

Nothing errors; the totals are just wrong, on an executive's slide. Check key uniqueness on each side first and **fail loudly**: raise when building the lookup, or use `validate="one_to_one"` in a pandas `merge`.

## Reconcile with dictionaries and sets

A reconciliation is a full outer join split into pieces:

```python
crm = {normalize_key(r["account_id"]): r for r in crm_rows}
billing = {normalize_key(r["customer_ref"]): r for r in billing_rows}

matched = crm.keys() & billing.keys()
only_crm = crm.keys() - billing.keys()
only_billing = billing.keys() - crm.keys()
```

For matched keys, compare fields fairly:
- **Map field names** explicitly (CRM `mrr` = billing `monthly_amount`).
- **Normalize before comparing** (`"Pro"` vs `"pro "`).
- **Use a one-cent tolerance for money.**
- **Skip fields expected to differ**, like typed account names; they bury real issues.

In pandas: `merge(..., how="outer", indicator=True, validate="one_to_one")`, then split on `_merge` (`left_only`, `right_only`, `both`).

## A report someone can act on

```
Reconciliation: CRM vs Billing (Mar 10)
  10 matched
   2 only in CRM       → never billed? (A-1009, A-1013)
   1 only in billing   → missing from CRM (A-1020)
   3 field mismatches
       A-1004  plan  CRM=pro   Billing=basic
       A-1006  mrr   CRM=2450  Billing=2405
```

Each line implies an owner: Finance checks unbilled accounts, Sales adds the missing one.

## Who wins? Agree per field

| Field | Source of truth | Why |
|---|---|---|
| Monthly amount | Billing | It's what's invoiced |
| Plan | Billing | It drives the invoice |
| Account owner | CRM | Sales manages territories there |
| Industry | CRM | Entered during qualification |

Agree this with the customer once and write it down. It turns future arguments into a lookup.

> **Key takeaways**
> - Normalize keys on both sides, only for differences you've confirmed.
> - Check uniqueness before joining; duplicates silently double totals.
> - Reconciliation = matched + only in A + only in B + field mismatches (money tolerance).
> - Agree per field which system is the source of truth.
