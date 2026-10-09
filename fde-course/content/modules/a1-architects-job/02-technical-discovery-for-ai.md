---
title: Technical Discovery for AI Projects
type: reading
minutes: 20
---

> **By the end of this lesson** you'll be able to run technical discovery for an enterprise AI project: map the stakeholders, capture the current workflow in numbers, build a data inventory, turn vague goals into metrics with baselines, surface the constraints that change the architecture, and spot the red flags that predict a stalled deal.

## Why architects run discovery differently

FDE module 02 (Customer Discovery) teaches discovery for the engineer who will build the thing. Read it if you haven't; this lesson assumes its basics (asks versus needs, "walk me through the last time", talking less than the customer). The architect's version differs in three ways:

1. **You're earlier.** Often there's no signed deal yet, the use case isn't fixed, and some people in the room haven't decided whether AI is a good idea at all.
2. **You're deciding fit, not just gathering requirements.** Part of discovery is qualification: is this worth a proof of concept, and is Claude the right tool for it?
3. **AI projects have their own failure points.** Data the model can't reach, a quality bar nobody has defined, and security or residency rules that rule out a deployment option. Each changes the architecture, so you find them before you draw a box.

Discovery has six outputs. If you leave without any of them, your next meeting is about that gap.

| Output | The question it answers |
|---|---|
| Stakeholder map | Who decides, who pays, who can block, who uses it? |
| Current-state workflow | What happens today, how often, how long, how wrong? |
| Data inventory | What data does the solution need, where is it, and can we reach it? |
| Success metrics with baselines | What number moves, from what, to what, measured how? |
| Constraints | What rules out options: security, residency, latency, budget, platform? |
| Decision process and timeline | What happens between "this looks good" and a signed contract, and when? |

## 1. The stakeholder map

Enterprise AI decisions involve more people than most engineers expect. Use this map in every account.

| Role | What they care about | Ask them |
|---|---|---|
| Economic buyer | Return on spend, risk to their reputation | "What would make this worth it to you in a year?" |
| Executive sponsor | A visible win, usually tied to a stated goal | "Which of your goals for this year does this support?" |
| Business owner | The workflow and its team; often your best source of numbers | "How do you measure this team today?" |
| Champion | Making the project happen; may or may not have authority | "Who else needs to say yes, and what will they ask?" |
| Technical owner | Integration effort, maintainability, their roadmap | "What's the system of record, and how do other tools connect to it?" |
| Data owner | Who may see which data, and under what agreement | "Who approves access to this data for a new processor?" |
| Security / CISO | Data handling, vendor risk, access control | "What does your review process for a new AI vendor look like, and how long does it take?" |
| Legal, privacy, procurement | Contract terms, data processing terms, purchasing path | "Do you have an existing agreement or cloud commitment we'd buy through?" |
| End users | Whether it saves them time or adds work | "Show me the last one you did." |

A common mistake is to spend every meeting with the champion. Champions are enthusiastic and often can't sign or approve anything. **Ask to meet the data owner and security early**; they are the two people most likely to stop an AI project late.

## 2. The current-state workflow, in numbers

Before you design anything, write down what happens today as a sequence of steps, each with a volume, a time and an error rate. Ask for the **last real example**, not the typical one, and ask for a sample of real items (say, 50) you can look at under whatever agreement is needed.

A good current-state summary reads like this:

> Claims intake: about 1,800 new claims a week arrive by web form, email and phone. Twelve handlers read each claim, classify it into one of 9 types, check the policy, and route it to an adjuster team. Median handling time is 22 minutes. About 1 in 7 claims is routed to the wrong team, which adds a median of 3 days. Time to first customer contact is a median of 4.5 business days against an internal target of 2.

Every number in that paragraph is a future baseline. Where judgment happens ("check the policy") is where a model might help; where a rule decides ("route by type") might not need a model at all.

## 3. The data inventory

Data access is one of the most common reasons an AI proof of concept slips, and one of the cheapest to catch early. Build an inventory with one row per source the solution needs.

| Source | System of record | Format | Volume and freshness | Owner | Access path | Sensitivity | Can it go to an external processor? |
|---|---|---|---|---|---|---|---|
| Claim forms | Claims platform | Structured fields + free text | 1,800/week, real-time | Claims IT | REST API (read) | Personal data | Unknown: ask data owner |
| Adjuster notes | Claims platform | Free text | 6 years of history | Claims IT | Nightly export only | Personal and health data | Unknown |
| Policy wordings | Document store | PDF, 140 documents | Changes quarterly | Product team | File share | Internal | Yes |

The last three columns are the ones that bite. For each source, find out:

- **Access path.** Is there an API, an export, or only screen access? Who builds the connector?
- **Sensitivity.** Personal, health, payment or confidential business data? Each class tends to bring its own approvals.
- **Third-party restrictions.** Data hosted or administered by another company may be governed by that company's contract, which can forbid sending it to a new processor without an amendment. That can add months, and the business owner often doesn't know it exists. **Ask directly**: "Is any of this data hosted or managed by a third party? Does that contract say anything about sharing it?"

## 4. Success metrics with baselines

"Use AI to improve claims" is a wish. A success metric names the number, its current value, the target, and how it's measured. Work down from the business outcome to what an eval can test.

| Level | Example | Baseline | Target | Measured by |
|---|---|---|---|---|
| Business outcome | Time to first customer contact | 4.5 business days (median) | 2 days | Claims platform timestamps |
| Operational | Misrouted claims | 14% | Under 5% | Re-assignment events |
| Operational | Handler minutes per claim | 22 | 8 | Time-tracking sample |
| Model quality | Classification accuracy on a labelled set | Handlers: measure on the same set | At least the handlers' rate | Golden set of 400 past claims, labelled by two senior handlers |

Three rules:

1. **No baseline, no target.** If the customer doesn't know the current number, measuring it is the first task of the proof of concept. FDE module 02 has a lesson on measuring baselines.
2. **Compare the model with the humans on the same items.** A model at 92% sounds bad until you learn handlers agree with each other 89% of the time.
3. **Agree on the minimum acceptable result before the proof of concept.** Afterwards, everyone moves the goalposts in their own favour. Module A4 builds on this.

## 5. Constraints that change the architecture

Ask about each of these explicitly. Customers rarely volunteer them because they don't know which ones matter to an AI design.

| Constraint | What to ask | Why it changes the design |
|---|---|---|
| Security | "What data classifications are involved? What does your AI vendor review require?" | Decides what data can be sent at all, and whether you need redaction before the model call |
| Data residency | "Must data be processed in a particular country or region?" | Narrows deployment options and features |
| Retention | "What retention terms does your policy require from a processor?" | Can rule out specific models (below) |
| Platform and procurement | "Do you buy cloud services through an existing AWS, Google Cloud or Azure commitment?" | Often decides how the customer reaches Claude |
| Latency | "Is someone waiting on the answer? How long is acceptable at the 95th percentile?" | Interactive versus batch; model size; streaming |
| Volume | "How many items per day, and how spiky?" | Rate limits, cost, batching |
| Budget | "Is there a budget for this year? Who approves more?" | Model choice and scope |
| Human oversight | "Which decisions must a person make or approve?" | Where the workflow stops for review |

Some of these interact with Claude's deployment options in ways worth knowing before your first call. Claude is available through the Anthropic API, Claude Platform on AWS, Amazon Bedrock, Google Cloud Vertex AI and Microsoft Foundry, and **features differ by platform**. Two examples from Anthropic's platform documentation at the time of writing:

- **Message Batches** (asynchronous processing at 50% off, results within 24 hours) is available on the Anthropic API and Claude Platform on AWS, but not on Bedrock, Vertex AI or Foundry.
- The **`inference_geo`** request setting, which pins where inference runs, is available on the Anthropic API and Claude Platform on AWS, but not on Bedrock, Vertex AI or Foundry.

And one retention example: **Claude Fable 5.1 requires 30-day data retention** and isn't available to organisations on zero data retention unless Anthropic has expressly authorised it. A customer whose policy demands zero retention can't simply pick that model.

These details change; confirm them against current documentation for every deal. The point for discovery is that **"which cloud do you buy through?" and "what retention do you require?" are architecture questions**, not procurement trivia. Module A2 covers deployment options and security reviews in depth.

## 6. Decision process and timeline

Ask: "Suppose the proof of concept hits every target. What happens next, step by step, until people are using it?" Then write down every approval, its owner and how long it usually takes. Ask what happened the last time they bought software like this, and whether any earlier AI pilot was stopped and why. A failed earlier pilot is useful: it tells you which objection you'll hear.

## A question bank

Use these as a checklist, not a script.

**Goals:** What prompted this now? What happens if you do nothing for a year? Which goal for this year does this support?
**Workflow:** Walk me through the last one. How many a week? How long does each take? How often is it wrong, and how do you find out?
**Data:** Where does each input live? Who owns it? Is any of it hosted by a third party? Can we see 50 real examples?
**Quality:** Who decides what "correct" looks like? Do your experts agree with each other? What mistake would be unacceptable?
**Constraints:** What would security ask first? Any residency or retention requirements? Which cloud do you buy through? How fast must it be?
**Decision:** Who else needs to say yes? What's the budget path? When do you need to show results, and to whom?

## Red flags

| You hear | What it usually means | What to do |
|---|---|---|
| "Let's just see what AI can do." | No problem owner, no metric | Ask which number they'd report to their boss; don't start a proof of concept without one |
| "We'll get you the data later." | Access isn't approved, maybe not approvable | Make data access the first milestone, with a named owner and date |
| "Security doesn't need to be involved yet." | They will be, at the worst time | Ask to brief security now, with a one-page data-flow diagram |
| "It needs to be 100% accurate." | No baseline, no tolerance for error defined | Measure human accuracy; design human review for the high-risk cases |
| "The board wants an AI story by next quarter." | Deadline driven by optics | Scope a small, measurable win; say what isn't realistic |
| The use case changes every meeting | No executive alignment | Ask the sponsor to pick one, in writing |
| Only the champion ever attends | Single-threaded deal | Ask for the data owner, security and a real user by name |

## After the call

Send a short summary within a day: what you heard (in their numbers), the proposed success metrics, the constraints, open questions with an owner and a date each, and the next step. If you got something wrong, they'll correct it now rather than in the proof of concept.

## How this shows up in interviews

- Reports of applied architect loops mention a **customer scenario**, sometimes as a role-play where an interviewer plays the customer (**Anecdotal**). This is discovery under observation: the interviewer is checking whether you ask before you design, and whether you find what they've hidden.
- In LLM system design rounds at every lab this course covers, candidates are expected to **scope before designing** (**Reported**; see module E6). Discovery questions are how you spend the first five minutes.

**Practice prompt** (original): "I'm the COO of a hospital network. We want to use AI to reduce nurse paperwork. You have ten minutes. Go." Write down the six questions you'd ask first and which of the six discovery outputs each one feeds. Then try it live in the next lesson.

> **Key takeaways**
>
> - Leave discovery with six outputs: stakeholders, workflow numbers, data inventory, metrics with baselines, constraints, and the decision process.
> - Meet the data owner and security early; data access and security reviews are common reasons AI projects stall, and both are cheap to start early.
> - Every metric needs a baseline, a target and a measurement method, agreed before the proof of concept.
> - Platform, residency and retention questions are architecture questions: they can rule out deployment options, features and even models.
> - Watch for red flags such as no metric, data "later", and a single-threaded champion, and act on them immediately.
