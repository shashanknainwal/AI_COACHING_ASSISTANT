---
title: "Claude as an Integration Assistant"
type: reading
minutes: 14
---

> **By the end of this lesson you will be able to:**
> - Identify the integration tasks where Claude saves hours, and the ones where it shouldn't be in the loop
> - Use Claude at *design time* to propose mappings that become reviewed, deterministic code
> - Share the minimum data needed, and validate every suggestion before it's used
> - Recognize when an integration should call Claude at *run time*

## Design time vs. run time

There are two very different ways to use Claude in integration work:

| | Design time | Run time |
|---|---|---|
| When | While you build the integration | On every record, every sync |
| Example | "Propose a field mapping between these two schemas" | "Read this carrier email and extract the delivery date" |
| Output | Code or config that a human reviews and commits | Data that flows straight into the target |
| Cost | A few cents, once | Per record, forever |
| Risk | Low: a human checks it | Higher: needs validation, monitoring, fallbacks |

**Prefer design time whenever the problem is deterministic.** If a field mapping is fixed (`status_code: DL → delivered`), have Claude help you write it once, review it, test it, and run plain code forever. It's cheaper, faster, reproducible, and easier to debug. Use Claude at run time only for inputs that genuinely need reading comprehension, like free-text emails, PDFs, or wildly inconsistent partner data.

## Where Claude saves real time

- **Reading API docs:** paste the relevant section and ask for a client function with pagination and error handling. Then review it as carefully as you'd review a colleague's code.
- **Proposing field mappings:** given both schemas and a few sample records, Claude is very good at suggesting which field maps to which, including transformations (units, code lookups, date formats).
- **Explaining unfamiliar formats:** EDI segments, SOAP envelopes, legacy fixed-width files.
- **Generating test fixtures:** "Give me 10 realistic edge-case records for this schema: missing fields, unusual units, unknown codes."
- **Decoding errors:** a cryptic 422 body from an ERP, explained in plain English with likely causes.

## The mapping workflow

Onboarding a new carrier means mapping their schema onto the ERP's, again. With dozens of fields, it's tedious and error-prone. A good workflow:

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

Three things make this safe:

1. **Structured outputs with an enum of target fields.** Claude can only suggest targets that exist.
2. **Validation in code.** Reject suggestions that reference source fields that don't exist, or map two sources to the same target.
3. **A confidence threshold and a human.** Low-confidence suggestions are routed to review; *all* of them get human sign-off before the mapping is committed.

Claude's confidence numbers aren't calibrated probabilities. Treat them as a useful *ranking* ("look at these first"), not as a guarantee. The validation rules and the human review are what make the result trustworthy.

## Share the minimum data

When you send customer data to any external service, including an LLM API, follow the customer's data policies and send only what's needed:

- For mapping, **field names, types, and 2-3 sample values** are usually enough. You rarely need real customer names or addresses; redact or fake them.
- **Never send secrets** (API keys, tokens) in prompts.
- Check whether the customer requires specific data-handling terms for AI services, and confirm before sending production data. This is a conversation to have in discovery, with the security team you mapped in Module 2.

## When run time is the right call

Some integrations genuinely need Claude per record:

- A carrier sends delivery exceptions as free-text emails.
- Partner invoices arrive as PDFs in 40 different layouts.
- Product descriptions from suppliers must be categorized into the retailer's taxonomy.

For these, apply everything from Modules 2 and 3: structured outputs, rules first, batching, validation, fallbacks for failures, cost estimates, and an evaluation set before go-live. And in Module 7, you'll go one step further: giving Claude **tools** (like your integration's `get_shipment` function) so it can look things up itself while answering questions.

> **Key takeaways**
> - Prefer design-time use: Claude helps you write mappings and code that a human reviews and commits.
> - Constrain suggestions with structured outputs, validate them in code, and route low-confidence ones to review.
> - Confidence scores are a ranking, not a guarantee; human sign-off makes mappings trustworthy.
> - Send the minimum data, never secrets, and follow the customer's data policies.
