---
title: "Reference Architecture: Enterprise Knowledge Assistant"
type: reading
minutes: 18
---

> **By the end of this lesson** you'll be able to design an enterprise knowledge assistant around the three things that decide whether it survives a security review and a month of real use: permissions-aware retrieval, freshness, and citations. You'll also know when long context beats retrieval, and when the customer should buy instead of build.

## What the customer asks for, and what they mean

"We want ChatGPT for our documents" is the most common enterprise AI request. Underneath it are three requirements the customer may not say out loud:

1. **Nobody sees an answer built from a document they can't open.** This is what the CISO will test first.
2. **Answers reflect the current version.** An assistant that quotes last year's travel policy loses trust in a week.
3. **Every answer shows where it came from.** Employees need to check, and legal wants an audit trail.

If you design for those three, the rest is standard retrieval engineering. The Applied AI Engineer track's worked example "An Internal Knowledge Assistant" (E6) walks through the full design interview; this lesson focuses on the architect's decisions and the conversation with the customer.

## When it fits

| Signal | Why it matters |
|---|---|
| Thousands of employees asking repetitive questions (HR, IT, policy, product, engineering docs) | Volume and repetition make answers valuable and evaluable |
| Content spread across several systems with poor search | The assistant's first value is finding things |
| Content is mostly current and owned | Garbage in, confident garbage out |
| Source systems expose permissions and change feeds | Without them you can't do permissions or freshness properly |
| Read-only is acceptable for v1 | Taking actions is a different pattern with different risks |

## Components and data flow

Fictional customer: **Halvorsen Industrial**, a manufacturer with 12,000 employees, content in a wiki, shared drives, an HR policy portal and a quality-management system with restricted procedures.

**Offline path (indexing):**

1. **Connectors** pull each source through its change feed: new and edited documents, deletes, and permission changes. A nightly reconciliation compares the index to each source and fixes anything a feed missed.
2. **Normalise and chunk** by structure: split on headings, keep the title and section path on every chunk, never split a table from its header.
3. **Store metadata with every chunk:** document ID, version, owner, last-modified time, and the access-control list (the groups that can read it).
4. **Index** for hybrid search: keyword search for part numbers, procedure IDs and acronyms, vector search for meaning.

**Online path (per question):**

5. **Identity.** The gateway takes the user's identity from single sign-on and expands their group memberships from the identity provider, cached for a short time (say 15 minutes).
6. **Query rewrite.** A small model turns a follow-up ("and for contractors?") into a standalone question.
7. **Retrieve with the permission filter inside the search query,** so restricted chunks are never retrieved, ranked or shown to the model. Then rerank to the best 8.
8. **Answer with citations.** A mid-tier model answers only from the retrieved chunks and cites them. Claude's API supports this directly: documents or search-result content blocks with citations enabled return answer text linked to the exact source passages. Both features are listed as available on the Claude API, Bedrock, Vertex AI and Foundry in Anthropic's platform availability table.
9. **Post-check.** Every citation must point to a retrieved chunk. If nothing relevant was found, say so and show the search results instead of guessing.
10. **Feedback loop.** Thumbs up or down, citation clicks and "couldn't find this" topics go to content owners every week. The assistant is also a map of where the documentation is missing.

Two design notes that come up in customer reviews:

- **Filtering after generation is too late.** If the model read a restricted chunk, it may paraphrase it. The filter belongs in retrieval.
- **Citations and structured outputs don't mix in one request.** Claude's API returns a 400 if you combine them. If the UI needs a structured payload (answer, sources, follow-up suggestions), build it from the citation blocks in your code rather than asking for a JSON schema.

## Freshness is a contract, not a feature

Agree a freshness target per source with the customer, write it down, and monitor it.

| Source | Freshness target | How |
|---|---|---|
| HR policy portal | Within 1 hour of publication | Change feed; only the current version is indexed |
| Wiki | Within 15 minutes | Change feed |
| Shared drives | Within 4 hours | Polling, plus nightly reconciliation |
| Permission changes | Within 15 minutes | Group cache TTL; immediate for named sensitive groups |

Monitor each source with a simple check: the newest document in the index from that source should be no older than the target. A connector that fails silently is the most common way knowledge assistants rot.

Show users each source's last-updated date next to the citation. It costs nothing and lets people judge for themselves.

## Model choices

| Step | Model | Reason |
|---|---|---|
| Query rewrite | Claude Haiku 5.5 at low `effort` | Small input, small output, on the critical path |
| Answer | Claude Sonnet 5.5 | Good synthesis over several sources at a moderate price |
| Hard questions (optional) | Claude Opus 5.5 | Only if the golden set shows a slice Sonnet gets wrong |

Embeddings and the vector store are separate line items from separate vendors. Price them with whichever provider the customer picks.

## Long context or retrieval?

All current Claude models except Haiku 4.5 have a 1M-token context window, and on Sonnet 5.5 the full window is billed at the standard per-token rate. For a small, stable corpus you can skip the retrieval pipeline and put the whole corpus in a cached prompt.

Compare per question on Sonnet 5.5 (prices per million: input $2, output $10, cache read $0.10, 5-minute cache write $2.50, from the [pricing page](https://platform.claude.com/docs/en/about-claude/pricing), checked 2026-10-08):

| Approach | Per question | Notes |
|---|---|---|
| Whole 300K-token handbook in a cached prefix | 300,000 x $0.10/M + 400 output x $10/M = about $0.034 | Each cache write costs 300,000 x $2.50/M = $0.75 when the cache has expired |
| Retrieval of 8 chunks (see below) | about $0.016 | Plus indexing, connectors and vector store |

The long-context option costs about twice as much per question but deletes a whole subsystem. It fits a single handbook or a product manual set under a few hundred thousand tokens, with one permission level. It doesn't fit Halvorsen: millions of documents, per-document permissions, constant change.

## Evals and launch gate

- **Golden set:** 300 questions from search logs and subject experts, by question type, with known-good source documents.
- **Unanswerable questions:** about 10%, where the right answer is "I couldn't find this".
- **Permission traps:** about 5%, asked as a test user who lacks access to the document that holds the answer.
- **Stale-version traps:** questions whose answer changed in the latest policy version.

| Metric | Graded by | Launch gate (example) |
|---|---|---|
| Retrieval recall at 8 | Code | At least 85% |
| Answer correctness | LLM judge with rubric, checked against human labels | At least 85% |
| Citation support | LLM judge per claim | At least 95% |
| Permission leaks | Code | Zero |
| Stale answers on version traps | Code | Zero |

## Failure modes

| Failure | How you notice | What you design in |
|---|---|---|
| Permission leak via stale group cache | Permission traps in every eval run; audit log of chunks shown per user | Short TTL; immediate refresh for sensitive groups; reconciliation |
| Connector stops syncing | Freshness monitor per source | Alert on breach of the agreed target |
| Two versions of a policy disagree | Version traps; judge flags conflicts | Index current versions only; show last-updated dates |
| Instructions planted in a wiki page | Red-team pages in a test space | Chunks marked as data; the assistant has no write tools |
| Low adoption | Weekly active users, repeat use | Put it where people already work (chat tool, intranet), not a new portal |

## Cost drivers and a worked estimate

Cost drivers:

1. **Retrieved context per question,** the biggest fresh-token cost.
2. **Questions per day,** which depends on adoption, not head count.
3. **Conversation history** carried into each follow-up.
4. **Output length.** Short answers with citations are cheaper and better liked.

Halvorsen assumptions: 25% of 12,000 employees active daily (3,000), 5 questions each, so 15,000 questions a day over 22 working days a month.

Per question:

| Part | Tokens | Rate per million | Cost |
|---|---|---|---|
| Query rewrite on Haiku 5.5 | 800 in, 60 out | $0.10 / $0.50 | $0.00011 |
| Cached prefix on Sonnet 5.5 (rules, format) | 3,000 | $0.10 | $0.0003 |
| Fresh input (8 chunks, history, question) | 6,000 | $2.00 | $0.0120 |
| Output | 400 | $10.00 | $0.0040 |
| **Total** | | | **about $0.0164** |

15,000 questions a day is about **$246 a day**, about **$5,400 a month**, or **45 cents per employee per month**. Fresh retrieved context is about three quarters of the cost, so "retrieve 5 chunks instead of 8" is the first lever, if recall on the golden set holds.

## Buy, build, or both

Before designing anything, ask what the customer already owns. Many enterprise search, intranet and productivity suites now include an assistant, and Anthropic sells its own apps for teams and enterprises alongside the API. Confirm current capabilities, connectors and admin controls in each vendor's current documentation. A fair recommendation often looks like this: buy for general employee Q&A, build where a workflow needs custom permissions, a specialised corpus, or integration into an internal tool. Recommending the cheaper option when it fits is part of being a trusted advisor.

## When this pattern doesn't fit

- **Small, stable, single-permission corpus:** use long context with caching.
- **Questions need live transactional data** ("what's the status of PO 4471?"): that's a tool-using agent, not retrieval over documents.
- **Content is wrong or unowned:** fix ownership first; the assistant will amplify whatever is there.
- **Exhaustive search is required** (legal discovery, regulatory audits): top-8 retrieval is built for answers, not for "find every document that mentions X".
- **No permission metadata available from the sources:** either restrict v1 to content everyone can read or make permission sync the first project.

## How this shows up in interviews

The Solutions Architect, Applied AI posting describes fitting Claude into the customer's stack and designing scalable architectures (**Official**, from the [job posting](https://jobs.accel.com/companies/anthropic/jobs/69412282-solutions-architect-applied-ai) as listed on an aggregator). A knowledge assistant is a likely case because almost every enterprise asks for one.

Original practice prompts:

- "The CISO says: 'Prove to me that a contractor can never get an answer from an HR compensation document.' What do you show them?"
- "The pilot's thumbs-down rate is 30%. How do you find out why?" (Split by retrieval misses, wrong answers from good sources, and missing content.)
- "Their corpus is one 250-page operations manual. Do you still build retrieval?"

> **Key takeaways**
> - Design for permissions, freshness and citations first; they decide whether the assistant survives review and real use.
> - Enforce permissions inside the search query. Filtering after generation is too late.
> - Freshness is a per-source contract with a monitor, not a hope.
> - Claude's citations work on every platform but can't be combined with structured outputs in one request.
> - At Halvorsen's volume the assistant costs about 45 cents per employee per month. For a small single-permission corpus, long context with caching can replace retrieval entirely.
