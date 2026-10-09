---
title: How Executives Decide
type: reading
minutes: 18
---

> **By the end of this lesson** you'll know what a CTO, a CISO, a CFO and a business sponsor each need to hear before they say yes, how to build a one-page brief that leads with the recommendation, how to replace adjectives with numbers, and how to answer "how confident are you?" without bluffing.

## Why this is the architect's job

Grace Liu, your principal architect, puts it simply: "Your design is only as good as the decision it produces. If the CTO can't repeat your recommendation to the CEO in one sentence, you haven't finished."

Anthropic's posting for **Solutions Architect, Applied AI** describes pre-sales architecture for large enterprises, being a trusted technical advisor, and working with Sales, Product and Engineering from discovery to deployment (**Official**, from the job posting). Much of that work happens in rooms with people who will never read your code. They read your one-pager, listen to your first two minutes, and decide.

How it shows up in interviews: architect loops at frontier labs are thinly documented. Plan for a case discussion plus a presentation, and a customer role-play where an interviewer plays an executive (**Anecdotal**: one or two candidate accounts). Whatever the format, the interviewer is checking the same things this lesson covers: do you lead with a recommendation, use numbers, and stay honest under pressure.

## Four executives, four questions

Every executive asks "should we do this?", but each one hears it through a different worry.

| Role | The real question | What they need from you | What loses them |
|---|---|---|---|
| **CTO** | "Will this work in our stack, and will my team regret it in two years?" | Architecture in a few bullets, integration points, build-vs-buy reasoning, reliability numbers, exit options | Hand-waving about "the model handles it"; ignoring their existing platforms |
| **CISO** | "What new risk am I signing up for?" | Data flows (what leaves the boundary, where it's stored, for how long), contractual terms, access controls, audit trail | Vague reassurance; any claim you can't back with a document |
| **CFO** | "What does it cost, what does it return, and how wrong could that be?" | Unit cost (per claim, per ticket), monthly run cost at expected and peak volume, payback period, the assumptions behind each number | Savings without a baseline; a single number with no range |
| **Business sponsor** | "Will this move my metric, and when can I tell my boss?" | The outcome in their metric (handle time, backlog, error rate), the timeline, what their team has to do | Technical detail they didn't ask for; dates you can't hit |

Two practical consequences:

1. **The same project gets four different first paragraphs.** The facts don't change. The order does.
2. **Find out who decides before you write.** The sponsor often champions the project, but the CISO can veto it and the CFO can starve it. The FDE track lesson "Stakeholder Mapping: Power, Interest, and Politics" (module 02) covers the mapping itself; here you write for each person on the map.

## The one-page brief

A one-pager is the most useful document an architect produces. It forces you to decide what matters, and it survives being forwarded to people who weren't in the meeting.

| Section | Length | What goes in it |
|---|---|---|
| **Recommendation** | 1–2 sentences | What you recommend and the decision you need. "Approve a 6-week pilot of claims triage on Claude Sonnet 5.5 for the auto line, budget $40K." |
| **Why** | 3 bullets | The business problem in their numbers, what changes, the evidence you have so far |
| **Architecture** | about 5 bullets | Components and data flow in plain words. One line on what you reuse from their stack |
| **Cost** | a small table | Unit cost, monthly run cost at expected and peak volume, one-time build cost, assumptions |
| **Risks and mitigations** | 3–4 rows | The real risks, each with a mitigation and an owner |
| **Decision needed** | 1–3 bullets | Exactly what you need, from whom, by when |

Rules that make it work:

- **Lead with the recommendation.** Executives read the top and skim the rest. If the recommendation is on page two, it doesn't exist.
- **One page means one page.** Detail goes in an appendix that you link, not attach.
- **Write the decision as a question they can answer yes or no.** "Do we approve the pilot budget by 14 November?" is answerable. "Thoughts?" is not.
- **Name what you're not recommending.** One line on the alternative you rejected and why. It shows you considered it, and it pre-empts the first objection.

## Numbers over adjectives

Adjectives ask the reader to trust you. Numbers let them check you.

| Adjective version | Number version |
|---|---|
| "Highly accurate" | "Correct routing on 91% of 400 held-out claims; the current manual process scores 87% on the same set" |
| "Cost-effective" | "About $0.02 per claim in model cost; about $800 a month at 40,000 claims" |
| "Fast" | "p95 latency 6 seconds per claim; claims are processed in a queue, so nobody waits on it" |
| "Secure" | "Claim text goes to the model through our existing cloud account; under the commercial terms the provider may not train on it" |
| "Scalable" | "Tested at 3x current peak volume in the pilot environment" |

Show your working once, briefly, so the reader can redo it. For the claims example on Claude Sonnet 5.5 ($2 per million input tokens, $10 per million output tokens):

```text
40,000 claims/month x 6,000 input tokens  = 240M input tokens  x $2/M  = $480
40,000 claims/month x   800 output tokens =  32M output tokens x $10/M = $320
Model cost                                                             ≈ $800/month (≈ $0.02/claim)
```

Then say what moves it: prompt caching on a shared system prompt lowers the input side; the Batch API is 50% off for work nobody is waiting on; a doubling of claim length roughly doubles input cost. A CFO trusts a number more when you tell them what would make it wrong.

Two cautions:

- **Model cost is rarely the biggest line.** Integration work, evaluation, human review and support usually cost more. If you only show token cost, a sharp CFO will assume you haven't thought about the rest. Module A3 covers total cost of ownership.
- **Don't invent precision.** "$812.40 a month" from a back-of-envelope estimate is false precision. Round, and give a range when inputs are uncertain.

## "What's your confidence?"

Every executive asks it in some form: "How sure are you?", "Will it actually work?", "What happens if you're wrong?" There are three bad answers and one good one.

| Answer | Why it fails |
|---|---|
| "Very confident." | An adjective. Gives them nothing to check, and you'll own it if it fails. |
| "It's AI, so it's hard to say." | Abdicates. They hired you to reduce uncertainty. |
| "Our model is state of the art." | Answers a different question. |

A good answer has three parts:

1. **What you measured, on what.** "On 400 real claims from last quarter, routing was correct 91% of the time."
2. **How much to trust the measurement.** "With 400 cases, the true rate is likely between about 88% and 94%. The set excludes commercial claims, so I can't speak to those yet."
3. **What would change your view, and how you'll find out.** "If the production mix has more handwritten forms than our sample, accuracy could drop. The pilot measures that in week two, and we have a rollback."

Saying "I don't know yet, and here is how we'll find out" is not weakness. It's the sentence that makes the other numbers believable.

## Before any executive meeting

A short checklist:

- [ ] I can say the recommendation in one sentence.
- [ ] I know who decides, who can veto, and what each of them worries about.
- [ ] Every claim of quality has a number and a dataset behind it.
- [ ] Every cost has its assumptions written down.
- [ ] I know my two weakest points and have an honest answer ready.
- [ ] I know the exact decision I'm asking for, and the fallback if they say "not yet".

## Practice prompts

Original prompts, written in the style of an architect case round. They aren't real interview questions. Answer each out loud in under two minutes.

1. You have 60 seconds with a CFO about a document-processing proposal. What do you say first, and which three numbers do you use?
2. Rewrite this sentence for a CISO: "Our solution is enterprise-grade and fully secure."
3. A CTO asks how confident you are that an agent will handle 80% of IT tickets end to end. Your eval shows 74% on 300 tickets. Answer.
4. Same project, four readers. Write the first sentence of the one-pager for the CTO, then for the business sponsor.

> **Key takeaways**
> - Each executive asks "should we do this?" through a different worry: fit (CTO), risk (CISO), return (CFO), outcome and timing (sponsor).
> - The one-pager leads with the recommendation and ends with a yes-or-no decision, owner and date.
> - Replace every adjective with a number and its dataset; show the cost math once and say what would change it.
> - Model cost is usually not the largest cost line; say so before the CFO does.
> - Answer "how confident are you?" with what you measured, how much to trust it, and how you'll find out the rest.
