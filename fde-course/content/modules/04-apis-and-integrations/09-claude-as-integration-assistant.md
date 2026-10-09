---
title: "Claude as an Integration Assistant"
type: reading
minutes: 3
---

> **By the end of this lesson you will be able to:**
> - Use Claude at design time to propose mappings that become reviewed code
> - Validate every suggestion and share the minimum data
> - Recognize when an integration should call Claude at run time

Northwind is onboarding a new carrier partner, and Leah's team has to map yet another schema onto the ERP: dozens of fields, tedious and error-prone. Claude can do the first pass in minutes, if you keep it out of places it doesn't belong.

## Design time vs. run time

| | Design time | Run time |
|---|---|---|
| Example | "Propose a field mapping between these schemas" | "Extract the delivery date from this carrier email" |
| Output | Code or config a human reviews and commits | Data flowing straight into the target |
| Cost | A few cents, once | Per record, forever |
| Risk | Low: a human checks it | Needs validation, monitoring, fallbacks |

**Prefer design time when the problem is deterministic.** Have Claude help write `DL → delivered` once, review it, test it, and run plain code forever. Also useful at design time: drafting a client from API docs (review it like a colleague's code), explaining EDI or SOAP formats, generating edge-case fixtures, and decoding a cryptic 422 body.

## The mapping workflow

```
source samples + target schema ──► Claude (structured output)
                                        │
                                        ▼
                               suggested mappings + confidence
                                        │
                        ┌───────────────┼────────────────┐
                        ▼               ▼                ▼
                   accepted        needs review       rejected
                (high confidence)  (human decides)  (invalid: unknown
                                                     field, duplicate)
                        └───────► reviewed mapping config ──► committed, tested code
```

1. **Structured outputs with an enum of target fields**, so Claude can only suggest targets that exist.
2. **Validation in code**: reject unknown source fields (a hallucinated `amount` when samples have `amt_usd`) and two sources mapped to one target; flag required targets left uncovered.
3. **A confidence threshold and a human**: low confidence goes to review, and *every* mapping gets sign-off before commit.

Claude's confidence numbers aren't calibrated probabilities. Use them to rank what to review first; validation and review make the result trustworthy.

## Share the minimum data

- Field names, types and 2–3 sample values are usually enough; redact or fake real names and addresses.
- **Never send secrets** in prompts.
- Confirm the customer's data-handling requirements for AI services before sending production data (a discovery question for the security team).

## When run time is right

Free-text exception emails, invoice PDFs in 40 layouts, supplier descriptions to categorize: these need Claude per record. Apply Modules 2 and 3: structured outputs, rules first, batching, validation, fallbacks, cost estimates and an evaluation set. Module 7 adds tools, like your `get_shipment` function.

> **Key takeaways**
> - Prefer design time: Claude drafts, a human reviews, plain code runs.
> - Constrain with an enum, validate in code, route low confidence to review.
> - Confidence is a ranking, not a guarantee.
> - Send the minimum data and never secrets.
