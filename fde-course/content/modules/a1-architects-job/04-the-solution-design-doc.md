---
title: The Solution Design Doc
type: reading
minutes: 20
---

> **By the end of this lesson** you'll be able to structure a solution design doc for an AI project, write each section so it survives a CTO, a CISO and a sceptical engineer, and recognise a good one from a worked example with real numbers.

## What the doc is for

A solution design doc turns discovery into a decision. It's the artifact your customer's architects review, their CISO marks up, and their executive skims before approving a proof of concept or a build. It does three jobs:

1. **Records what you agreed**: the problem, the metrics, the constraints. When someone changes their mind later, the doc is how you notice.
2. **Shows the design and why**: the architecture, the alternatives you rejected, and the reasons.
3. **Makes risk and cost visible** before anyone has spent money.

Write it for three readers at once. The **executive** reads the first half page and decides whether to keep going. The **customer's architect** reads the architecture and data flow line by line. The **CISO's team** reads the security section and the data-flow diagram and nothing else. If each reader can find their part in under a minute, the structure is working.

## The structure

| Section | What it answers | Typical length | Common mistake |
|---|---|---|---|
| 1. Context | What's the problem today, in numbers? | 1 paragraph | Restating the customer's ask instead of the need |
| 2. Goals and non-goals | What will this do, and what won't it do? | 3–5 bullets each | No non-goals, so scope grows silently |
| 3. Success criteria | Which numbers move, from what baseline, to what target? | A small table | "Improve efficiency"; targets with no baseline |
| 4. Architecture | What are the components and how does a request flow? | Diagram + 1 paragraph per component | A box diagram with no reasons; no alternatives considered |
| 5. Data flow | What data goes where, when, and who can see it? | Diagram or numbered steps | Forgetting logs, caches and eval data |
| 6. Security and data handling | Classification, access control, retention, residency, injection risk | Short table | Claims about vendor terms nobody has checked |
| 7. Evals | How will we know it works before launch and keep knowing after? | Golden set, metrics, launch gate | Only "user feedback" |
| 8. Rollout | Phases, who's in each, what has to be true to move on, how to roll back | 3–4 phases | Big-bang launch; no kill criteria |
| 9. Risks | What could go wrong, how likely, how we'd notice, what we'd do | Table | Risks with no mitigation or owner |
| 10. Costs | Model spend per unit and per month, build and run effort | Arithmetic shown | A number with no assumptions |
| 11. Open questions | What we don't know yet, who will find out, by when | List with owners and dates | Hiding unknowns to look certain |

**Length.** For a proof of concept, aim for two to four pages. Grace's rule: if a section is longer than the decision it supports, cut it. The written exercise in the next lesson asks for a **one-page** version: the same sections, compressed to the decisions.

## Writing each section well

**Goals and non-goals.** Non-goals are the most underrated lines in any design doc. "Will not send messages to customers without human approval in phase 1" prevents a month of argument. Each non-goal should be something a reasonable stakeholder might otherwise assume is included.

**Architecture with alternatives.** For each major decision, write one line on the alternative and why you rejected it: prompting versus fine-tuning, retrieval versus putting everything in a long context, one agent versus a fixed pipeline, a larger model versus a smaller one. Reviewers trust a design more when they can see what else you considered. Module A3 goes deep on choosing the approach.

**Security.** State facts about the customer's own controls (SSO, network, logging) plainly. For anything about a vendor's or cloud platform's data handling, cite the current document or write "to confirm against current terms" and put it in open questions. A wrong claim in this section can cost you the CISO's trust for the rest of the deal.

**Evals.** Name the golden set (where it comes from, how many items, who labels it), the metrics and thresholds, and the **launch gate**: the result that has to be true before real users see it. Include something for cases the system should decline.

**Costs.** Show tokens per request, price per million tokens, requests per month, and the product. Say which numbers are assumptions you'll replace with measurements in the proof of concept.

## A worked example: Varga Industrial

The following is a condensed design doc for a fictional customer. Read it as a model of tone and density, not as the answer to every problem.

---

**Varga Industrial: field-service assistant. Solution design v0.3 (draft for proof of concept)**

**1. Context.** Varga Industrial makes industrial air compressors. 450 field technicians service about 60 product models at customer sites. Technicians look up procedures and specifications in 38,000 pages of manuals (PDF) and call a 12-person remote-expert desk when stuck. Measured over the last quarter: technicians spend a median of 25 minutes per complex job searching manuals; the expert desk answers about 1,100 calls a month with a median wait of 35 minutes; 18% of jobs need a second visit, and Varga's finance team puts the cost of a repeat visit at about $650.

**2. Goals.** (a) Answer technicians' procedure and specification questions in under 10 seconds, with citations to the manual page. (b) Reduce second visits caused by wrong procedure or wrong part. (c) Reduce routine calls to the expert desk.
**Non-goals (phase 1).** No parts ordering. No customer-facing use. No diagnosis from photos. Not a replacement for the expert desk, which stays the escalation path.

**3. Success criteria.**

| Metric | Baseline | Target (pilot) | Measured by |
|---|---|---|---|
| Second-visit rate, pilot region | 18% | 14% or lower | Work-order system, pilot vs. matched control region |
| Routine expert-desk calls, pilot region | ~170/month | 30% fewer | Desk call log, tagged by category |
| Answer correctness on golden set | n/a | 85% or higher | Senior technicians grading, see section 7 |
| Exact match on numeric specifications | n/a | 100% on the 80 spec questions | Automated check against source |

**4. Architecture.** Technicians ask in the existing field-service mobile app. The app calls a new assistant service in Varga's Google Cloud project. The service (1) filters manuals by the equipment's model and serial number, (2) runs hybrid retrieval (keyword plus vector search) over manual chunks, (3) can call one read-only tool, `get_service_history(serial)`, against the work-order system, and (4) calls Claude Sonnet 5.5 through Google Cloud Vertex AI, because Varga buys through its Google Cloud agreement. The prompt requires a citation for every claim and quotes numeric specifications verbatim from the cited page; if the manuals don't contain the answer, the assistant says so and offers the expert desk.
*Alternatives considered.* **Fine-tuning on the manuals:** rejected, because manuals change monthly, fine-tuned answers can't cite pages, and we have no eval yet showing prompting plus retrieval falls short. **Whole corpus in context:** 38,000 pages is roughly 19 million tokens, far beyond a 1M-token context. One model's manual set (about 800 pages, roughly 400,000 tokens) would fit, but even read from cache at $0.10 per million tokens on Sonnet 5.5 that's about $0.04 per question in input alone, nearly twice the whole retrieval design, and slower. Kept as a fallback if retrieval recall misses the target. **Claude Opus 5.5:** about twice the per-question cost; we'll run it in the bake-off and switch only if it clears a quality gap Sonnet 5.5 doesn't.

**5. Data flow.** Question text and equipment serial go from the app to the assistant service; the service sends the question, retrieved manual passages and service history for that serial to the model; the answer and citations return to the app. Questions, retrieved chunk IDs, answers and ratings are logged in Varga's project for 90 days for evaluation. Manuals are re-indexed nightly from the document store.

**6. Security and data handling.** Data classes: internal technical documentation, customer site names and equipment history (business data, no consumer personal data). Access through Varga's SSO; the service uses a dedicated account with read-only access to the work-order API. Prompt-injection exposure is low (sources are Varga's own manuals and technician notes) and the only tool is read-only. Vertex AI data-handling and retention terms: to confirm against current Google Cloud and Anthropic documentation before the CISO review (open question 2).

**7. Evals.** Golden set: 350 real questions from the last 12 months of expert-desk tickets, each with the correct answer and source page labelled by four senior technicians (two per item, disagreements resolved by the desk lead). It includes 80 numeric-specification questions and 40 questions the manuals can't answer. Metrics: answer correctness graded by senior technicians on a sample plus an LLM judge checked against their grades; citation supports the answer; exact numeric match; correct "not in the manuals" on the 40 unanswerable items (target 90%); retrieval recall at 8 chunks (target 90%); p95 latency under 10 seconds with streaming. **Launch gate for the pilot:** correctness at least 85%, numeric exact match 100%, no safety-procedure answer without a citation.

**8. Rollout.** Phase 0 (weeks 1–4): build, offline evals, bake-off. Phase 1 (weeks 5–6): shadow mode at the expert desk; desk staff see the assistant's draft before answering. Phase 2 (weeks 7–12): 40 technicians in one region, compared with a matched region. Phase 3: all technicians if pilot targets are met. **Rollback:** any wrong safety-critical specification found in the field pauses the pilot until the cause is fixed and added to the golden set.

**9. Risks.**

| Risk | Likelihood | Detection | Mitigation | Owner |
|---|---|---|---|---|
| Wrong torque or pressure value | Low, high impact | Numeric exact-match eval; field reports | Verbatim quotes with citation; 100% gate; rollback rule | Architect + desk lead |
| Manuals for older models are scanned images with poor text | Medium | Retrieval recall by model family | OCR pass on 6 legacy families; exclude if recall stays low | Varga engineering |
| Technicians don't adopt it | Medium | Weekly active users in pilot | Built into the existing app; desk promotes it | Field service manager |
| Labelling time from senior technicians | High | Golden set behind schedule | Two half-day labelling sessions booked now | Varga sponsor |

**10. Costs (model spend, estimate).** Assumptions to replace with measurements: 6 questions per technician per working day, 22 working days a month: 450 × 6 × 22 = **59,400 questions/month**. Per question: 4,000 tokens of system prompt and tool definitions read from cache, 7,000 fresh input tokens (retrieved passages, history, question), 800 output tokens including thinking. On Claude Sonnet 5.5 ($2 input, $0.10 cache read, $10 output per million tokens): 7,000 × $2/M = $0.0140; 4,000 × $0.10/M = $0.0004; 800 × $10/M = $0.0080. Total **about $0.022 per question, about $1,330 a month** before occasional cache writes. The 800 output tokens assume `effort: "medium"` set explicitly; Sonnet 5.5 defaults to `high`. **Thinking sensitivity:** if thinking triples output to 2,400 tokens, output costs $0.024 and the total is about $0.038 per question, about $2,280 a month, and time to first token rises too. We'll measure thinking tokens in the bake-off. The same traffic on Claude Opus 5.5 ($4 / $0.20 / $20, default `medium` effort) is about $0.045 per question, about $2,650 a month. For comparison, avoiding 10 repeat visits a month at $650 each is $6,500. Build effort: one Varga engineer for 12 weeks plus our team's support.

**11. Open questions.**
1. Which 6 legacy model families have scanned-only manuals? (Varga engineering, by week 2.)
2. Data-handling and retention terms for Claude on Vertex AI, confirmed for the CISO pack, and which endpoint we use: Vertex single-region endpoints serve only Sonnet 4.6 and earlier, so Sonnet 5.5 runs on the global or a multi-region endpoint. (Architect, by week 2.)
3. Can the work-order API be reached from the assistant's network without a new firewall rule? (Varga IT, by week 1.)
4. Who signs off on the pilot launch gate? (Varga sponsor, by week 3.)

---

Notice what the example does. Every goal maps to a metric with a baseline. The rejected alternatives have numbers. The security section separates what's known from what's still to confirm. The cost section shows its arithmetic and sets it against the value. And the open questions have owners and dates, so the doc drives the next two weeks of work.

## How this shows up in interviews

- Candidates describe a **customer scenario or case presentation** in solutions-architect loops: you get a situation and present a solution (**Anecdotal**). The structure above is the skeleton of that presentation: context, goals, success criteria, architecture with alternatives, risks, cost, next steps.
- In design rounds, interviewers reportedly probe **evals, failure modes and cost** after the architecture (**Reported** across labs; see module E6). Those are sections 7, 9 and 10 here.

**Practice prompt** (original): "Here's a one-paragraph brief from a retailer that wants to summarise product reviews for its merchandisers. You have 20 minutes to prepare and 10 to present a design." Practise compressing the eleven sections into five slides: problem and metrics, architecture and alternatives, evals and rollout, risks and cost, asks and next steps.

> **Key takeaways**
>
> - A solution design doc records agreements, justifies the design and makes risk and cost visible before money is spent.
> - Write for three readers: the executive (top half page), the customer's architect (architecture and data flow) and the CISO (security and data flow).
> - Non-goals and rejected alternatives build more trust than extra components.
> - Show cost arithmetic with stated assumptions and compare it with the value at stake.
> - Never assert vendor or platform data-handling terms you haven't checked; list them as open questions with an owner.
