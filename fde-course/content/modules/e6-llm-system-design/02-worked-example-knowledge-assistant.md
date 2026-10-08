---
title: "Worked Example: An Internal Knowledge Assistant"
type: reading
minutes: 22
---

> **By the end of this lesson** you'll be able to recognise what a strong 45-minute design answer sounds like, reproduce its moves (numbers first, a model per step, evals with a gate, cost math out loud) and explain why each one earns points.

## How to read this

Below is a model answer to an original practice prompt, written as a transcript. The interviewer and the company are fictional. After each stage, a **Why this scores** note explains what the interviewer is listening for. Read it once straight through, then a second time covering the notes and predicting them.

The numbers are the candidate's assumptions, stated out loud. The model prices are real: Claude Haiku 5.5 at $0.10 / $0.50 per million input / output tokens (prompts up to 100K tokens), Claude Sonnet 5.5 at $2 / $10, Claude Opus 5.5 at $4 / $20, and cache reads at $0.20 per million on Sonnet 5.5 and Opus 5.5. Latency figures are labelled as assumptions to measure, because they depend on prompt size, load and region.

> **Practice prompt:** Design an internal knowledge assistant for a 5,000-person software company. Employees ask questions in chat and get answers drawn from the wiki, shared drives and the HR policy site.

## Minutes 0–5: scope and numbers

**Candidate:** Before I draw anything, a few questions. Who uses it: everyone, or specific teams? What are the top question types? Are there documents some employees must not see? And is the target "answer the question" or "find the right document"?

**Interviewer:** Everyone. Mostly HR policy, IT how-to, and engineering docs. Yes, plenty of restricted content: compensation bands, legal, some engineering. They want answers with links.

**Candidate:** Then here's what I'll design for. Tell me if any number is off.

| Assumption | Number |
|---|---|
| Daily active users | 30% of 5,000 = 1,500 |
| Questions per active user per day | 4, so 6,000 questions a day |
| Traffic shape | 9-hour workday, peak 3x average: about 0.2 questions a second on average, 0.6 at peak; I'll size for 2 |
| Corpus | 500,000 documents, about 1,500 tokens each: 750 million tokens |
| Churn | About 1% of documents change each day |
| Latency target | p95 under 2.5 seconds to first streamed token |
| Quality bar | Every answer cites its sources; a wrong HR or permission answer is a serious failure |
| Out of scope for v1 | Taking actions (filing tickets, changing settings) |

**Interviewer:** Fine.

> **Why this scores:** four questions, each of which changes the design (permissions changes retrieval, "answers with links" changes the output format). The candidate commits to numbers rather than waiting for them, and states what's out of scope. Every later decision points back to this table.

## Minutes 5–11: API and data flow

**Candidate:** The API is one streaming endpoint: `POST /ask {question, conversation_id}` returns a stream of text chunks, then a final event with citations. The user's identity comes from single sign-on at the gateway, never from the request body.

Online path, in order:

1. **Gateway:** authenticates, applies a per-user rate limit, attaches the user's group memberships.
2. **Query rewrite:** turns a follow-up like "and for contractors?" into a standalone question using the last few turns.
3. **Retrieval:** hybrid search, filtered to documents the user can read, then reranked.
4. **Answer:** the model writes an answer from the top chunks, citing chunk IDs.
5. **Post-check:** drop any citation ID that wasn't in the retrieved set; if nothing is cited, return "I couldn't find this" with the search results instead.

Offline path: connectors pull from the wiki, the drives and the HR site every 15 minutes, using each source's change feed. Each document is parsed, split, embedded and written to the index along with its access-control list. Deletes are handled the same way, and a nightly full reconciliation catches anything the change feeds missed.

> **Why this scores:** a one-line API contract, identity taken from the platform rather than the caller, and an offline pipeline that handles deletes. Many candidates forget that deleted or restricted documents must leave the index.

## Minutes 11–17: models and prompts

**Candidate:** Two models, one job each.

| Step | Model | Reason |
|---|---|---|
| Query rewrite | Claude Haiku 5.5 at low `effort` | Short input, short output, on the critical path, so speed matters more than depth |
| Answer | Claude Sonnet 5.5 | Good synthesis over several chunks at half Opus 5.5's input price |

I'd also run the golden set on Claude Opus 5.5. If it only wins on a small slice of hard questions, I'd route that slice to it later rather than pay double for everything.

The answer prompt has a fixed order: tool and format instructions, then the system prompt with the rules ("answer only from the provided documents; cite chunk IDs; if the documents don't answer it, say so"), then the retrieved chunks, then the question. The stable part, about 2,500 tokens, comes first so it's cached. Caching is a prefix match, so I keep anything that changes per request, including the date, out of that prefix.

Retrieved chunks go inside clearly delimited tags, with an instruction that their contents are reference material, not instructions.

> **Why this scores:** each model is tied to a reason from the scope table (latency for rewrite, cost for answers). The candidate plans to test the more expensive model rather than assume it's needed. The prompt order shows they understand caching mechanics, and the delimiters show they've thought about injection.

## Minutes 17–24: retrieval

**Candidate:** The corpus is 750 million tokens. With chunks of about 500 tokens and 50 tokens of overlap, that's roughly 1.7 million chunks. At 1,024 dimensions and 4 bytes per float, the vectors are about 7 GB, which fits in memory on one node. I'd run two replicas for availability, not for capacity.

Choices:

- **Chunking by structure.** Split on headings, keep the page title and section path in each chunk, and never split a table. An HR answer that loses the table header is a wrong answer.
- **Hybrid search.** Vector search for meaning, keyword search for exact terms like "SOC 2", ticket IDs and product names. Merge the two lists and keep the top 40.
- **Permissions before ranking.** Each chunk stores the groups that can read it. The search query filters on the user's groups, so restricted chunks are never retrieved, never ranked and never shown to the model. Filtering after generation is too late: the model has already read it.
- **Rerank to 8.** A reranker scores the 40 candidates against the question and keeps 8. That's about 4,000 tokens of context.
- **Freshness.** Each chunk keeps its source's last-modified time. For HR policies with several versions, the connector indexes only the current version.

**Interviewer:** What if group membership changes? Someone moves out of the legal team.

**Candidate:** The gateway reads group memberships from the identity provider with a short cache, say 15 minutes, so access is removed within that window. If the company needs it faster for some groups, those groups skip the cache. The tradeoff is an extra lookup on each request for those users.

> **Why this scores:** the candidate sizes the index with arithmetic instead of naming a product. Permissions are enforced in retrieval, with a clear reason. The pushback answer names the tradeoff and a number instead of defending the design.

## Minutes 24–31: evals and launch gate

**Candidate:** I'd build the golden set before tuning anything.

- **300 questions**, drawn from the existing search logs and from subject experts in HR, IT and engineering, split by question type.
- **About 10% unanswerable** questions, where the right answer is "I couldn't find this".
- **About 5% permission traps:** questions whose answer lives in a document the test user can't read. The expected answer is a refusal to reveal it.

Each case is graded on four things:

| Metric | How it's graded | Launch threshold |
|---|---|---|
| Retrieval recall at 8 | Code: is a known-good chunk in the top 8? | At least 85% |
| Answer correctness | LLM judge with a written rubric, checked against 100 human labels | At least 85% graded correct |
| Citation support | LLM judge: is each claim supported by the cited chunk? | At least 95% |
| Permission leaks | Code: does any answer cite or quote a restricted chunk? | Zero |

The judge itself is checked: on the 100 human-labelled cases it should agree with people at least 85% of the time before I trust its scores.

One caution on noise. With 300 cases and a true pass rate of 85%, the standard error is about 2 points, so the 95% interval is roughly plus or minus 4 points. A one-point change between two prompt versions is not a real difference at this size. I'd compare versions on the same cases and look at which cases flipped.

After launch: thumbs up or down, citation click-through, the "couldn't find this" rate by topic (which shows gaps in the corpus), and a weekly review of 50 sampled conversations.

> **Why this scores:** this is the stage that separates strong answers. The golden set includes unanswerable and permission cases, the metrics split retrieval from generation, the judge is validated, and the gate has thresholds agreed in advance. The noise calculation shows the candidate knows an eval score is a measurement with error.

## Minutes 31–36: failure modes

**Candidate:** The four I'd worry about most:

| Failure | Detection | Response |
|---|---|---|
| Permission leak through stale access lists | Permission-trap cases in every eval run; an audit log of which chunks each user was shown | Short membership cache; nightly reconciliation; alert on any trap failure |
| Confident answer from an outdated policy | Judge flags conflicting chunks; feedback on HR answers | Index only current versions; show each source's last-updated date |
| Instructions hidden in a wiki page | Red-team pages in a test space | Chunks are treated as data inside tags; the assistant has no tools that act, so the blast radius is the answer text |
| Model API errors or slowness | Error rate and p95 alerts | Retry with backoff; if the answer step fails, return the reranked search results with links, so the user still gets something useful |

> **Why this scores:** each failure has a detection and a response, and they're specific to this system. Read-only scope shows up again as a safety argument. The outage fallback degrades to plain search instead of an error page.

## Minutes 36–41: cost and latency

**Candidate:** Per question on Claude Sonnet 5.5:

| Part | Tokens | Rate per million | Cost |
|---|---|---|---|
| Cached prefix (instructions, rules) | 2,500 | $0.20 | $0.0005 |
| Fresh input (chunks, history, question) | 4,900 | $2.00 | $0.0098 |
| Output | 350 | $10.00 | $0.0035 |
| **Total** | | | **about $0.014** |

At 6,000 questions a day that's about $83 a day, or roughly $1,800 a month over 22 working days: around 36 cents per employee per month. The query rewrite on Claude Haiku 5.5 (about 600 tokens in, 60 out) adds less than a hundredth of a cent per question.

Cache writes cost about 1.25 times the input price, so the first request after the cache expires pays a little more. At 0.2 questions a second during the day, the 5-minute cache stays warm. I'd confirm with `usage.cache_read_input_tokens` in the logs.

For comparison, the same answer step on Claude Opus 5.5 is about $0.027 a question, roughly double. The biggest lever beyond caching is retrieved context: cutting from 8 chunks to 5 saves about 1,500 fresh tokens, a fifth of the per-question cost. I'd only do that if recall on the golden set holds.

Latency budget for p95 to first token, all assumptions I'd measure in the first week:

| Step | Budget |
|---|---|
| Gateway and auth | 50 ms |
| Query rewrite (Haiku 5.5) | 400 ms |
| Hybrid search with permission filter | 150 ms |
| Rerank 40 to 8 | 200 ms |
| Answer model to first token | 1,200 ms |
| Headroom | 500 ms |
| **Total** | **2,500 ms** |

If the rewrite step is the problem, skip it for first-turn questions, which don't need it.

> **Why this scores:** the cost table is arithmetic anyone can check, ends in a per-employee number a buyer understands, and compares one alternative. The latency budget adds up to the target from minute one, labels its guesses as guesses, and names a specific cut.

## Minutes 41–45: iteration plan

**Candidate:** Rollout in three steps.

1. **Weeks 1–2:** IT and HR teams only, about 200 people. Measure the four golden-set metrics on live samples, plus the "couldn't find this" rate.
2. **Weeks 3–4:** fix whatever the data says is the biggest failure. If it's retrieval misses, tune chunking and the reranker before touching the prompt. If it's corpus gaps, hand the list of unanswered topics to the content owners.
3. **Week 5 onward:** open to everyone, with the eval suite running on every prompt or model change.

Later, if users ask for it: actions such as filing an IT ticket, behind tools with their own permission checks and a confirmation step.

> **Why this scores:** a staged rollout tied to metrics, a rule for deciding what to fix first, and a clear boundary on what comes later. Ending on a plan, not on a list of features, is what interviewers remember.

## What the candidate didn't do

Just as instructive:

- **No fine-tuning.** Nothing in the scope called for it. The candidate would mention it only if evals showed a problem that prompting and retrieval couldn't fix.
- **No agent loop.** A single retrieve-then-answer pass meets the requirements and is easier to evaluate. Tools came up only as a later step.
- **No vendor tour.** The index was sized with arithmetic. Product names add nothing unless the interviewer asks.

> **Key takeaways**
>
> - Open with a table of numbers and point back to it all the way through.
> - Give each model one job and one reason, and plan to test the expensive option instead of assuming you need it.
> - Enforce permissions at retrieval time. Filtering after generation is too late.
> - Evals carry the most weight: a stratified golden set, a validated judge, a gate agreed in advance, and awareness of noise.
> - Do the cost and latency math in tables that add up, and end with a staged rollout tied to metrics.
