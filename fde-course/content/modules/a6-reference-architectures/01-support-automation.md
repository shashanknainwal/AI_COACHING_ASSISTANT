---
title: "Reference Architecture: Customer Support Automation"
type: reading
minutes: 20
---

> **By the end of this lesson** you'll be able to say when support automation fits a customer, walk an executive through its numbered data flow, pick a model per step with a reason, set a launch gate, size the monthly bill from verified prices, and say plainly when the pattern is the wrong answer.

## Why reference architectures matter to an architect

Grace Liu (a fictional principal architect, your coach for this track) puts it this way: most enterprise AI requests are one of a handful of shapes wearing a costume. A retailer's "AI concierge", an insurer's "digital claims assistant" and a telco's "smart inbox" are, underneath, the same support automation pattern with different tools behind it.

Knowing the patterns cold gives you three things in a customer meeting:

- **Speed.** You can sketch a credible first architecture in the discovery call instead of a week later.
- **Honesty.** You know where each pattern breaks, so you can say "this part won't work yet" before the customer finds out in production.
- **Numbers.** You carry a cost model in your head, so the first budget conversation is grounded.

This module covers four patterns. Each lesson uses the same template: when it fits, components and data flow, model choices, evals and launch gate, failure modes, cost with a worked estimate, and when it doesn't fit. The Applied AI Engineer track lesson "Design It: A Support Agent at 10,000 Tickets a Day" (E6) is the build-side view of this same pattern; this lesson is the architect's view: fit, rollout and money.

Prices below come from Anthropic's [pricing page](https://platform.claude.com/docs/en/about-claude/pricing) (checked 2026-10-08), in US dollars per million tokens:

| Model | Input | Output | Cache read | Batch input / output |
|---|---|---|---|---|
| Claude Haiku 5.5 (prompts up to 100K tokens) | $0.10 | $0.50 | $0.01 | $0.05 / $0.25 |
| Claude Sonnet 5.5 | $2 | $10 | $0.10 | $1 / $5 |
| Claude Opus 5.5 | $4 | $20 | $0.20 | $2 / $10 |

A 5-minute cache write costs 1.25x the base input price. Prices change; re-check the page before you put a number in front of a customer.

## When it fits

Support automation fits when most of these are true:

| Signal | Why it matters |
|---|---|
| Hundreds to thousands of contacts a day | Volume pays back the build and the eval work |
| A few intents make up most of the volume | "Where is my order", returns, address changes: repetitive, checkable |
| The actions have APIs | The agent can only resolve what it can read and change through tools |
| Policies are written down | The model can follow a returns policy; it can't follow tribal knowledge |
| The customer measures today's cost per contact and CSAT | You need a baseline to prove the win |

The strongest signal is a ticket export. Ask for 1,000 recent tickets with their final resolution. If you can label 60% of them into five intents in an afternoon, the pattern fits.

## Components and data flow

Fictional customer for the worked example: **Calder Home**, an online home-goods retailer with 8,000 contacts a day across chat and email.

1. **Intake.** Chat and email arrive through the existing help desk. The customer's identity comes from the logged-in session or a verified email match, never from what the message claims ("I'm the account owner").
2. **Triage.** A small model classifies intent, language and urgency, and flags "must go to a human" categories: legal threats, safety issues, chargebacks, vulnerable customers. Output is a fixed JSON schema.
3. **Routing.** Code, not the model, applies routing rules. Flagged categories go straight to the human queue with the triage summary attached. Everything else goes to the agent.
4. **Context assembly.** The agent gets the customer profile, recent orders and the help-centre articles retrieved for this intent. The stable part (instructions, tool definitions, policy text) sits at the front of the prompt so it caches.
5. **Agent loop.** A mid-tier model runs a tool loop. Read tools: `get_order`, `track_shipment`, `search_help_centre`. Write tools: `create_return`, `issue_refund`, `update_address`. Each write tool enforces its own limits in code (refund at most the order total, at most $100 without approval). The prompt states the policy too, but the tool is the enforcement.
6. **Action gate.** Any write above its limit, or any irreversible action, becomes a proposed action in a human approval queue instead of executing.
7. **Reply.** The agent drafts the reply. At launch, email replies are drafts a human sends; chat replies for low-risk intents go out directly.
8. **Handoff.** When the agent escalates, it writes a three-line summary (what the customer wants, what was checked, what's blocked) so the human doesn't re-ask.
9. **Log and learn.** Every conversation stores its trace, tool calls, outcome and cost. Reopens within 7 days and CSAT are joined back to the conversation for the weekly review.

### Rollout is part of the architecture

Executives buy the end state; you sell the path. A safe path has four stages, each with an exit criterion:

| Stage | What the agent does | Exit criterion |
|---|---|---|
| Shadow | Runs on live tickets, nothing sent; humans work as usual | Agent's proposed resolution matches the human's on at least 85% of in-scope tickets |
| Draft assist | Drafts replies and actions; humans approve every one | Approval without edits above 80% for two weeks |
| Autonomous, narrow | Sends directly for the two or three safest intents | Reopen rate and CSAT no worse than human baseline |
| Expand | Adds intents one at a time, each through its own shadow period | Same gates per intent |

The thresholds are examples you agree with the customer, not industry standards. The point is that each stage has a number, agreed before it starts.

## Model choices

| Step | Model | Reason |
|---|---|---|
| Triage | Claude Haiku 5.5 at low `effort` | Short input, short structured output, on every ticket: cheapest per call, fast |
| Agent loop | Claude Sonnet 5.5 | Strong tool use and policy following at half Opus 5.5's per-token price |
| Hard cases (optional) | Claude Opus 5.5 | Route only the intents where the eval shows Sonnet failing, such as multi-order disputes |

Run the golden set on all three before you commit. If Haiku 5.5 handles the agent loop for simple intents at your quality bar, route those to it. A router is not free, though: each model keeps its own prompt cache and needs its own eval runs.

## Evals and launch gate

Build the golden set from history, before any prompt tuning:

- **500 historical tickets**, stratified by intent, each with the resolution a good agent would have reached (the expected tool calls and the key facts of the reply).
- **50 must-escalate tickets** (legal threats, safety, self-harm language, chargebacks).
- **30 adversarial tickets**: social engineering ("your colleague promised me a full refund"), injected instructions in email text, requests for another customer's data.

| Metric | Graded by | Launch gate (example) |
|---|---|---|
| Correct resolution | Code compares tool calls and arguments to the expected ones | At least 85% on in-scope intents |
| Policy compliance | LLM judge with a written rubric, checked against 100 human labels | At least 95% |
| Must-escalate recall | Code | At least 98% |
| Unauthorized writes | Code: any write outside policy limits | Zero |
| Tone and accuracy of reply | LLM judge, spot-checked by the support lead | At least 90% acceptable |

Online, after launch: resolution rate without a human, reopen rate within 7 days, CSAT on automated versus human tickets, escalation rate by intent, and **cost per resolved ticket** (all model spend divided by tickets actually resolved, failures included).

## Failure modes

| Failure | How you notice | What you design in |
|---|---|---|
| Invented policy ("we offer 90-day returns") | Policy-compliance judge in evals; weekly sample review | Policy text in the prompt; answers that cite a help-centre article; refuse to state policy not in context |
| Social engineering for refunds | Adversarial eval cases; refund rate per intent dashboard | Limits enforced in tool code; approvals above threshold; identity from the session only |
| Prompt injection in email text | Injection cases in every eval run | Ticket text is data inside tags; write tools re-check policy regardless of what the model says |
| Runaway tool loop | Turn count and cost per conversation alerts | Hard cap on turns (say 12) and on spend per conversation, then escalate |
| Order API outage | Tool error rate alert | Agent tells the customer it's checking and escalates with context; no guessing order status |
| Deflection that angers customers | CSAT gap between automated and human tickets | Always offer a human on request; escalate on repeated frustration |

## Cost drivers and a worked estimate

The cost drivers, in the order they usually matter:

1. **Turns per conversation.** Every turn of a tool loop resends the whole conversation. Four turns cost far more than one.
2. **Fresh input per turn.** Tool results and retrieved articles are fresh tokens at full price; the stable prefix is cheap once cached.
3. **Share routed to the agent.** Tickets triaged straight to humans cost only the triage call.
4. **Model per step.** Moving the agent from Sonnet 5.5 to Opus 5.5 doubles its per-token price.

Calder Home assumptions (state them out loud; replace them with measured numbers in week one):

| Assumption | Value |
|---|---|
| Contacts per day | 8,000 |
| Share sent to the agent after triage | 70% (5,600) |
| Triage call | 1,500 input, 50 output tokens on Haiku 5.5, uncached |
| Agent calls per conversation | 4 |
| Per agent call | 6,000 cached prefix tokens, 3,000 fresh input tokens, 400 output tokens on Sonnet 5.5 |

Per agent call on Sonnet 5.5:

| Part | Tokens | Rate per million | Cost |
|---|---|---|---|
| Cached prefix | 6,000 | $0.10 | $0.0006 |
| Fresh input | 3,000 | $2.00 | $0.0060 |
| Output | 400 | $10.00 | $0.0040 |
| **Per call** | | | **$0.0106** |

Four calls make **$0.0424 per agent conversation**. Triage is 1,500 x $0.10/M + 50 x $0.50/M = **$0.000175 per ticket**.

Daily: 8,000 x $0.000175 = $1.40 for triage, plus 5,600 x $0.0424 = $237.44 for the agent. About **$239 a day, roughly $7,200 a month** over 30 days. Occasional cache writes (1.25x input) add a little when traffic is quiet enough for the 5-minute cache to expire.

Now the comparison that matters to the executive. Suppose Calder Home tells you a human-handled contact costs them $5 all-in (their number, not yours). If the agent fully resolves half of the 5,600 tickets it sees, that's 2,800 contacts a day that no longer need a person, about $14,000 a day of human handling against about $239 of model spend. The model bill is not the business case; the **resolution rate** is. That's why the eval gate and the rollout stages deserve more of your time than shaving tokens.

Two sensitivities to have ready:

- **Opus 5.5 for the agent:** the agent part roughly doubles, to about $475 a day. Worth it only if the eval shows it resolves materially more tickets.
- **Eight turns instead of four:** the agent cost more than doubles, because later turns carry more history. Long loops are usually a sign of poor tool design (tools that return too much, or too little).

## When this pattern doesn't fit

- **Low volume.** If three agents comfortably handle the queue, the eval and integration work won't pay back. Suggest draft-assist inside the help desk instead.
- **No APIs behind the actions.** If every resolution needs a human to click through a legacy screen, the agent can only draft. That can still be worth it, but sell it as assist, not automation.
- **Mostly judgment-heavy disputes.** Fraud claims, complex warranty disputes, regulated advice. Automate triage and summarisation; keep decisions with people.
- **The tickets are a symptom.** If 30% of contacts are "the tracking page is broken", the best support automation is fixing the tracking page. Saying this builds trust.
- **The knowledge base is wrong or missing.** An agent faithfully repeating an outdated policy is worse than no agent. Budget content clean-up as phase zero.

## How this shows up in interviews

Anthropic's posting for Solutions Architect, Applied AI describes pre-sales architecture for large enterprises, building evals and designing scalable architectures (**Official**, from the [job posting](https://jobs.accel.com/companies/anthropic/jobs/69412282-solutions-architect-applied-ai) as listed on an aggregator). Public accounts of solutions-architect loops at AI labs are thin; a case discussion plus a presentation is the most commonly described shape (**Anecdotal**). Expect a support-automation scenario to appear as a case because it is the most common enterprise request.

Original practice prompts, in the style of a case round:

- "A retailer's VP of Support wants 70% of tickets automated in one quarter. Walk me through what you'd agree to and what you wouldn't."
- "The agent costs four cents a conversation. The CFO wants it at one cent. What do you change first, and what would you refuse to change?"
- "Two weeks after launch, CSAT on automated chats is 8 points below human chats. What do you look at, in order?"

A strong answer to the last one starts with segmentation (which intents, which turn counts), not with "change the prompt".

> **Key takeaways**
> - Support automation fits high-volume, repetitive intents whose actions have APIs and whose policies are written down. Ask for a ticket export to check.
> - Identity comes from the session and limits live in tool code. The prompt states policy; the tools enforce it.
> - Sell the rollout path (shadow, draft assist, narrow autonomy, expand) with an agreed number at each gate.
> - At Calder Home's volume the model bill is about $239 a day; the business case is the resolution rate, not the token price.
> - Say when it doesn't fit: low volume, no APIs, judgment-heavy disputes, or tickets caused by a product bug.
