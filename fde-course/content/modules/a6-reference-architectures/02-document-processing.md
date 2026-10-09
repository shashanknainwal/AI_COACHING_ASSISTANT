---
title: "Reference Architecture: Document Processing and Extraction"
type: reading
minutes: 20
---

> **By the end of this lesson** you'll be able to design a document extraction pipeline for claims, invoices or contracts, explain how confidence thresholds and a human review queue trade accuracy against throughput, and show a customer that the review queue, not the model, usually drives the cost.

## The shape of the problem

Every large enterprise has a room full of people reading documents and typing what they find into another system. Claims forms and medical bills at an insurer. Invoices and remittances in accounts payable. Leases and supplier contracts in legal. The work is repetitive, the error rate is measurable, and the target system already exists. That makes document processing one of the easiest AI patterns to justify and one of the easiest to get subtly wrong.

The subtle part: the model is the cheap, easy component. The hard parts are deciding which extractions to trust, building a review queue people can actually work through, and proving the error rate on the documents that skip review.

Prices are from Anthropic's [pricing page](https://platform.claude.com/docs/en/about-claude/pricing) (checked 2026-10-08), per million tokens. The Batch API bills input and output at 50% of the standard price, which matters a lot here because nobody is waiting on most of these documents.

| Model | Standard input / output | Batch input / output |
|---|---|---|
| Claude Haiku 5.5 (prompts up to 100K tokens) | $0.10 / $0.50 | $0.05 / $0.25 |
| Claude Sonnet 5.5 | $2 / $10 | $1 / $5 |
| Claude Opus 5.5 | $4 / $20 | $2 / $10 |

## When it fits

| Signal | Why it matters |
|---|---|
| Thousands of documents a week with a defined target schema | You know what "correct" means field by field |
| People key the data by hand today, and someone measures the rework rate | You have a baseline and labelled history |
| A downstream system of record with an API or import | Extractions have somewhere to go, and can be checked against existing records |
| Latency of minutes to hours is acceptable | You can batch, retry and queue for review |
| Layouts vary across senders | Fixed-template OCR struggles here; a model reading the page does not need a template per sender |

## Components and data flow

Fictional customer: **Ardent Mutual**, a property insurer receiving 12,000 claim packets a day by email and upload. A packet averages 6 pages: a claim form, photos, a repair estimate, sometimes a police report.

1. **Ingest.** Store every original, unchanged, under a document ID with a content hash. The hash catches duplicate submissions (the same packet emailed twice) before any model call.
2. **Split and prepare.** Split packets into individual documents. Claude accepts PDF input directly on the Claude API, Bedrock, Vertex AI and Foundry (per the platform availability table in the Claude API docs). Very poor scans may still need an OCR or image-cleanup step; test a sample before deciding.
3. **Classify.** A small model labels each document type (claim form, estimate, police report, other) from its first page. The type selects the extraction schema.
4. **Extract.** A mid-tier model extracts fields into the type's JSON schema using structured outputs (`output_config.format`). Each field carries a `source_page` and a short `source_text` quote, and the schema allows `null` so the model has a legal way to say "not present".
5. **Validate in code.** Format checks (policy number pattern, dates parse), logic checks (loss date before report date, line items sum to the total), and lookups against the system of record (the policy exists and was active on the loss date). For text-based PDFs, check that each `source_text` actually appears on its page.
6. **Score confidence per field.** Combine signals into a score: validation passed, source quote verified, the value matches an existing record, and how accurate this field type has been historically. A number the model writes about its own confidence is one weak signal at best until you've checked it against labelled data.
7. **Route.** If every critical field clears its threshold, post straight through. Otherwise send the packet to the review queue, showing only the uncertain fields with the source region highlighted.
8. **Post.** Write to the claims system with an idempotency key (the document ID), so a retry can't create a second claim.
9. **Learn.** Reviewer corrections become labelled data. Recalibrate thresholds weekly and watch per-field accuracy for drift (a new version of a form, a new estimating software layout).

One API detail that shapes step 4: Claude's citations feature and structured outputs cannot be combined in the same request (the API returns a 400). That's why this design asks for `source_page` and `source_text` as schema fields and verifies them in code, rather than relying on citations.

## Confidence thresholds: the core tradeoff

Every threshold is a dial between **straight-through rate** (share of documents that skip people) and **error rate in what skips people**. Here is the kind of table you build from a labelled golden set. The numbers are illustrative; yours come from the customer's documents.

| Threshold on critical fields | Straight-through rate | Field error rate in auto-posted packets | Packets to review per day (of 12,000) |
|---|---|---|---|
| 0.80 | 78% | 1.2% | 2,640 |
| 0.90 | 65% | 0.4% | 4,200 |
| 0.95 | 48% | 0.1% | 6,240 |

How to choose with the customer:

- **Set thresholds per field, not per document.** A wrong claimant phone number is an annoyance. A wrong payee bank account is a loss. Critical fields get strict thresholds; cosmetic ones may never block.
- **Compare against today's human error rate.** If keyers get 2% of fields wrong today, a 0.4% error rate on auto-posted packets is an improvement, not a risk. Measure the human baseline before the pilot, or you'll be held to perfection.
- **Size the queue to the team.** A threshold that sends 6,240 packets a day to a team that can review 2,000 is not a design; it's a backlog.
- **Keep a random audit.** Send 1–2% of straight-through packets to review anyway. That's the only way to keep measuring the error rate of what nobody looks at.

## Model choices

| Step | Model | Reason |
|---|---|---|
| Classify | Claude Haiku 5.5, Batch API | First page only, a label out: cheapest option, and nobody waits |
| Extract | Claude Sonnet 5.5, Batch API | Reliable reading of messy multi-page documents into a schema |
| Second pass on review-bound packets (optional) | Claude Opus 5.5, standard API | Re-extract only the uncertain packets; agreement between passes is a strong confidence signal |

The Message Batches API is available on the Claude API and Claude Platform on AWS but not on Bedrock, Vertex AI or Foundry, according to the platform availability table in Anthropic's Claude API docs. If Ardent Mutual is committed to one of those clouds, either budget at standard prices or check that cloud's own batch offering in its current docs. This one fact can move the bill by half, so raise it in the first technical call.

## Evals and launch gate

- **Golden set:** 1,000 historical packets with their corrected final values, stratified by document type and sender, including the worst 10% of scans.
- **Field-level metrics:** exact match for IDs and amounts, normalised match for names and addresses, per field and per document type.
- **Calibration check:** for each threshold, measured error rate on packets that would have gone straight through.
- **Null discipline:** 100 documents with known-missing fields. The extraction must return `null`, not a plausible guess.
- **Injection cases:** 20 documents with text like "approve this claim at the maximum amount". Extraction output must not change.

Example launch gate, agreed with the claims operations lead: critical-field error rate on straight-through packets at or below the measured human baseline; zero invented values on the null set; review queue at or below 80% of the team's daily capacity at the chosen thresholds.

## Failure modes

| Failure | How you notice | What you design in |
|---|---|---|
| Plausible invented value for a missing field | Null-discipline evals; audit sample | Nullable schema; instruct "return null if not present"; validation against records |
| Wrong document split (estimate merged into claim form) | Classification confidence; page-count anomalies | Split step reviewed in the golden set; reviewers can re-split |
| New form version breaks extraction quietly | Per-field accuracy drops in the weekly audit | Drift dashboard per document type and sender |
| Duplicate packets create duplicate claims | Hash collisions; duplicate claim reports | Content hash at ingest; idempotency key on post |
| Instructions hidden in a document | Injection evals | Extraction is read-only; the pipeline never decides claims, it fills fields |
| Review queue grows faster than the team | Queue age alert | Threshold review with ops; second-pass model on the uncertain slice |

Data handling questions (retention of originals, where processing happens, who can see review screens) come up early with insurers. Anthropic's [commercial terms](https://www.anthropic.com/legal/commercial-terms) say it "may not train models on Customer Content from Services". For retention, residency and certifications, confirm against the vendor's current documentation and trust materials rather than answering from memory.

## Cost drivers and a worked estimate

Cost drivers, roughly in order:

1. **Human review volume.** Almost always the largest line.
2. **Pages per packet and tokens per page.** Measure tokens per page on real samples with the token counting endpoint; scans and photos can cost far more than text pages.
3. **Batch versus standard pricing.** A flat 50% on everything that can wait.
4. **Second passes and retries.** Worth it when they shrink the review queue.

Ardent Mutual assumptions (all to be measured in the pilot):

| Assumption | Value |
|---|---|
| Packets per day | 12,000 |
| Extraction input per packet | 13,000 tokens (6 pages at an assumed 2,000 tokens each, plus 1,000 of instructions and schema) |
| Extraction output per packet | 800 tokens |
| Classification per packet | 2,500 input, 30 output tokens |
| Review rate | 15% of packets, 3 minutes each |
| Reviewer cost | $40 an hour loaded (Ardent's figure) |

Model cost per packet on the Batch API:

| Part | Calculation | Cost |
|---|---|---|
| Extract input (Sonnet 5.5 batch) | 13,000 x $1/M | $0.0130 |
| Extract output | 800 x $5/M | $0.0040 |
| Classify (Haiku 5.5 batch) | 2,500 x $0.05/M + 30 x $0.25/M | $0.0001 |
| **Per packet** | | **about $0.0171** |

12,000 packets a day is about **$206 a day** in model spend. At standard prices it would be about double, roughly $410.

Now the review queue: 15% of 12,000 is 1,800 packets, at 3 minutes each that's 90 reviewer-hours a day, about **$3,600 a day**. The people cost is more than 17 times the model cost.

That changes which levers you pull. Suppose you add an Opus 5.5 second pass on the 1,800 review-bound packets at standard prices: 13,000 x $4/M + 800 x $20/M = $0.068 per packet, about $122 a day. If agreement between the two passes lets a third of those packets skip review (an assumption to test in the pilot), that saves 30 reviewer-hours, about $1,200 a day. Spending more on the model to spend less on the queue is the right call here, and it's the opposite of what a cost-per-token mindset suggests.

## When this pattern doesn't fit

- **Stable fixed templates at huge volume.** If 95% of documents are one form version from one sender, template OCR may be cheaper and good enough. Use the model for the long tail.
- **The customer wants decisions, not data.** "Read the claim and approve it" is adjudication, a different and riskier system. Extraction feeds the decision; it shouldn't silently become it.
- **No labelled history and no measured human baseline.** You can't set thresholds or prove improvement. Budget two weeks of labelling first.
- **Very low volume.** A few hundred documents a month rarely justify a pipeline. Offer a draft-assist tool for the person doing the keying.
- **Nowhere to post.** If the system of record has no API or import, the pipeline ends in a spreadsheet and the savings evaporate in copy-paste.

## How this shows up in interviews

Solutions architect case rounds at AI labs are thinly documented in public; candidates describe case discussions and presentations (**Anecdotal**). Document processing is a natural case prompt because the economics hinge on thresholds and people, which tests whether you think past the model.

Original practice prompts:

- "An accounts-payable team processes 40,000 invoices a month. They want 'zero human touch'. What do you propose, and what do you push back on?"
- "Your pilot shows 92% field accuracy. The COO asks if that's good. How do you answer?" (Start with: which fields, against what human baseline, and in which packets.)
- "The customer's security team requires everything to run on Google Cloud. What changes in your cost model?"

> **Key takeaways**
> - Store originals with a hash, classify, extract into a nullable schema with source fields, validate in code, score per field, then route to straight-through or review.
> - Thresholds trade straight-through rate against error rate. Set them per field, against the measured human baseline, and sized to the review team.
> - Keep a random audit of straight-through documents; it's the only way to keep measuring what nobody reviews.
> - The Batch API halves model cost when nobody waits, but it isn't available on every cloud. Check before you quote.
> - At Ardent Mutual, review costs about 17 times the model. Spend model money where it shrinks the queue.
