---
title: Handling Objections Without Overclaiming
type: reading
minutes: 18
---

> **By the end of this lesson** you'll have a three-step method for executive objections (acknowledge, evidence, offer a test), worked answers for the six objections you'll hear most, and a clear line between a confident answer and an overclaim.

## Why objections are good news

An executive who objects is still engaged. Silence and "send me something" are worse. An objection tells you exactly which worry stands between you and a decision, so you can address it instead of guessing.

The trap is the urge to win the point. Under pressure, architects say things like "it doesn't hallucinate with our setup" or "the cost is fixed". Those sentences close the meeting and open a problem: the first time production contradicts them, you lose the account's trust, and often the account.

How it shows up in interviews: customer role-plays in architect loops are reported to include an interviewer pushing back as a skeptical executive (**Anecdotal**). Interviewers are usually listening for whether you hold your ground on facts while giving up ground you shouldn't hold. Lessons 04 to 06 let you practise exactly that.

## The method: acknowledge, evidence, offer a test

| Step | What you do | What it sounds like |
|---|---|---|
| **1. Acknowledge** | Restate the worry in their words and agree with whatever is true in it. Don't argue with the feeling. | "You're right that the model will sometimes get things wrong. That's the risk to design around." |
| **2. Evidence** | Give the specific number, document or design choice that addresses it, with its limits. | "On 400 of your own claims, 6% had an error. Every one of those was caught by the validation step or sent to a reviewer, except 3." |
| **3. Offer a test** | Propose a cheap, time-boxed way for them to see it for themselves, with a pass/fail criterion they help set. | "Let's pick 200 claims your team chooses, including the ugly ones, and agree now what error rate is acceptable." |

The third step is what turns a debate into a plan. You stop asking them to believe you and start asking them to judge a result.

Two rules hold across all of it:

- **Never claim more than your evidence shows.** If you measured 400 documents, say 400. If you haven't tested something, say so and offer to.
- **Ask a clarifying question when the objection is vague.** "When you say it's too expensive, compared to what?" Often the real objection is different from the first one.

## The six objections you'll hear most

### 1. "These models hallucinate."

- **Acknowledge.** True. Language models can produce confident, wrong answers. No honest vendor says otherwise.
- **Evidence.** What you've measured on their data, and the design controls: grounding answers in retrieved documents with citations, structured outputs validated against schemas and business rules, confidence-based routing to people, and an eval set that runs before every change.
- **Test.** An eval on their hardest cases, with an error budget agreed in advance.
- **Don't say:** "Our setup eliminates hallucinations." Say what rate you measured and how errors are caught.

### 2. "Our data can't leave our environment." (or "Is our data secure?")

- **Acknowledge.** Their obligations are real, and the security team should decide, not you.
- **Evidence.** Facts you can point to in a document: the data flow (what is sent, where it's stored, for how long), the access path (Claude is available through the Anthropic API and also through Amazon Bedrock, Google Vertex AI and Microsoft Foundry, so it can often be reached through a cloud account they already approved), and the contract. For example, Anthropic's [Commercial Terms](https://www.anthropic.com/legal/commercial-terms) state that Anthropic may not train models on customer content from its services.
- **Test.** A security review with their team using the provider's current documentation, before any real data is used.
- **Don't say:** "It's fully compliant" or name certifications from memory. Certifications, retention terms and regional options change. Point to the current trust and legal documents, and say "let's confirm that with the current documentation" when you aren't sure.

### 3. "What if costs run away?"

- **Acknowledge.** Usage-based pricing is harder to budget than a licence, and agent loops can multiply calls.
- **Evidence.** The unit cost from your measurements, the volume assumption, and the controls: per-request token limits, a cap on agent steps, prompt caching for shared prefixes, the Batch API (50% off) for work nobody is waiting on, smaller models for simple steps, and spend alerts and limits.
- **Test.** Run the pilot with a hard monthly budget and report actual cost per unit each week against the estimate.
- **Don't say:** "It'll never cost more than X." Say what you expect, the range, and what triggers an alert.

### 4. "We'll build it ourselves."

- **Acknowledge.** Often a reasonable option, especially if they have a strong platform team. Say so.
- **Evidence.** Compare on their criteria: time to first value, the people needed to run it (serving, scaling, upgrades, on-call), quality on their eval set, and total cost over two or three years. Module A3 has the full total-cost model.
- **Test.** A bake-off: both options on the same eval set, the same success criteria, the same deadline.
- **Don't say:** "You'll never match our quality." You don't know that. Let the eval decide. Sometimes the answer is a hybrid: they own the orchestration and data, and call a hosted model.

### 5. "Your competitor is cheaper."

- **Acknowledge.** It may be, per token.
- **Evidence.** Price per token isn't price per outcome. Compare cost per correct result: a cheaper model that needs more human review or more retries can cost more overall. Show the arithmetic.
- **Test.** Run both on the same eval set and compare cost per correctly handled case.
- **Don't say:** anything negative about the competitor you can't back with a measurement. Talk about results on their data.

### 6. "This will cost people their jobs." (often unspoken)

- **Acknowledge.** Take it seriously, and don't pretend roles won't change. The concern may come from the executive or from the team they lead.
- **Evidence.** Be specific about what the system does and doesn't do. In most deployments people review exceptions, handle the hard cases and own decisions. Point to what the team will spend its time on instead, using the business's own plans, not your promises.
- **Test.** Involve the people who do the work today in building the eval set and in reviewing the pilot. They know where it will fail.
- **Don't say:** "Nobody will lose their job" (not yours to promise) or "you'll cut headcount by 40%" (not yours to decide, and it turns the team against the project). Staffing decisions belong to the customer's leadership.

## Confident versus overclaiming

| Overclaim | Confident and honest |
|---|---|
| "It's 99% accurate." | "It was 97% field-accurate on 500 of your documents; handwritten ones were 79%, so those go to a person." |
| "There's no risk to your data." | "Here's exactly what data goes where, and here's the clause on training. Your security team should review it." |
| "It will pay for itself in three months." | "Payback rests on two numbers we should check together: how many documents still need a person, and your loaded cost per clerk hour. Here's the range for both." |
| "We can definitely hit that date." | "We can hit that date for the auto line. The full scope needs four more weeks, and here's why." |

A useful test before you say a sentence: **if this turned out to be wrong in six months, could I show them where I said it was uncertain?** If not, rewrite it.

## When you don't know

You will be asked something you can't answer. The strongest move is short and specific:

1. "I don't know that one for certain."
2. "Here's what I do know." (only if it's relevant)
3. "I'll confirm with [the right person or document] and send it to you by [day]."

Then do it. A follow-up that arrives when you said it would is one of the cheapest ways to earn trust.

## Practice prompts

Original prompts, in the style of a customer role-play. They aren't real interview questions. Answer each with acknowledge, evidence, test, in under 90 seconds.

1. "I read that these models make up legal citations. Why would I let one near our contracts?"
2. "Our cloud vendor's own model is half the price. Why are we even talking?"
3. "My platform team says they can build this in a quarter with open-source models."
4. "What stops an agent from running up a $50,000 bill over a weekend?"
5. "My claims team thinks this is a plan to replace them. What do I tell them?"

> **Key takeaways**
> - An objection names the worry blocking the decision. Treat it as information, not an attack.
> - Acknowledge what is true, give specific evidence with its limits, and offer a test with a pass/fail line agreed in advance.
> - Never claim more than you measured; point to current documents for security and compliance instead of reciting from memory.
> - Compare cost per correct outcome, not price per token, and let a bake-off settle build-vs-buy.
> - "I don't know, I'll confirm by Thursday" followed by doing it builds more trust than a confident guess.
