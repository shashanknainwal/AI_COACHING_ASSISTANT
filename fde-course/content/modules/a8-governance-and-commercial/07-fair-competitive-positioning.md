---
title: "Fair Competitive Positioning: When the CIO Already Chose Someone Else"
type: reading
minutes: 16
---

> **By the end of this lesson** you'll be able to respond to a CIO who has standardised on another provider (for example Azure OpenAI or Google's Gemini) without disparaging it, propose an evidence-based way to compare, argue for a multi-model strategy where it genuinely helps the customer, and recognise the sentences that should never leave your mouth.

## How this comes up

Many enterprises you meet will already have a standard. A CIO signed an enterprise agreement, the security review is done, the platform team built a gateway, and "we're an Azure OpenAI shop" or "we've standardised on Gemini" is the first thing they say. Interviewers for customer-facing roles use this kind of objection too: it tests judgement, honesty and composure more than product knowledge (**Anecdotal** for architect loops specifically; module A5 covers objection handling in general).

Your goal in that meeting is not to win the argument. It's to stay useful and credible, so that when a workload comes along where Claude is the better fit, you're the person they call.

## What you're actually up against

A standard is rarely a judgement about model quality. Usually it's about:

- **Procurement:** a signed agreement and spend that counts toward a cloud commitment.
- **Security:** a completed review, an approved data processor, approved regions.
- **Engineering:** a gateway, SDKs, logging and evaluation tooling already built.
- **Risk:** one vendor to manage instead of several.

Each of those is reasonable. Find out which ones matter before you say anything about models. "What did standardising solve for you?" is a better first question than any claim.

## Facts that change the conversation

Several "competitor standards" are also places where Claude runs. From Anthropic's platform documentation (module A2 lesson 01 has the details; re-check before quoting):

- **Microsoft Foundry** offers Claude, billed through Azure Marketplace, with Microsoft Entra ID authentication available. In the "Hosted on Azure" option, Anthropic's docs say prompts and completions stay within Azure. Know the limits too: no EU data zone, Sonnet 5.5 only as Global Standard, and some models and features only on "Hosted on Anthropic" deployments.
- **Google Cloud (Vertex AI)** offers Claude, billed by Google Cloud, with Google as the data processor, and with global, `eu` and `us` multi-region endpoints for current models.
- **Amazon Bedrock** and **Claude Platform on AWS** cover AWS customers.

So "we've standardised on Azure" or "we're a Google Cloud shop" often doesn't exclude Claude at all. It changes which platform you'd propose, and which features are available (Batches, code execution and others vary by platform). Lead with that, accurately, including the gaps.

## Evidence-based differentiation

Claims don't move a CIO who has heard every vendor say they're the best. Evidence on their own data does.

1. **Pick one workload** where the difference would matter: long documents, complex tool use, coding, a hard extraction task. Let the customer choose it if possible.
2. **Run a fair bake-off** (module A4 lesson 03): the same frozen eval set from their data, the same system boundary, blind grading, cost per completed task and latency next to quality, and a decision rule written before anyone sees results. Include their incumbent model.
3. **Report it honestly**, including where the incumbent wins. A result the customer can trust is worth more than a win they suspect.
4. **Price the switching cost**, not just the per-token cost. Re-running their security review, new SDK integration, new monitoring. If the gain doesn't cover it, say so.

What you can say about Claude in general is what Anthropic publishes: model capabilities, context window, pricing, platform availability. Public benchmark numbers belong in the conversation only with a source and a caveat that benchmarks aren't their workload.

## The multi-model strategy

Many large enterprises end up with more than one model provider, because different tasks suit different models and because a second provider is a resilience and negotiation lever. You can propose it honestly when:

- **The workloads differ.** A high-volume classification task and a complex agentic coding task don't need the same model.
- **The gateway can route.** If the platform team built a model gateway, adding a second provider behind it is an engineering task, not a re-platforming. Ask whether their gateway is model-agnostic.
- **Resilience matters.** A second provider for critical workloads reduces dependence on one vendor's capacity and roadmap.
- **The eval suite is shared.** One eval set per workload, run against any model, makes the choice a measurement instead of a debate.

Don't propose it when the customer is small, the workloads are similar, and a second vendor would double the governance burden for little gain. Saying "your standard is fine for this workload" builds more trust than any pitch.

## What never to say

| Never say | Why | Say instead |
|---|---|---|
| "Their model hallucinates more." | An unsourced claim about a competitor. You can't support it for their workload. | "Let's measure both on your cases." |
| "They train on your data." | A claim about another vendor's data practices you can't verify, and often wrong for enterprise agreements | "Your security team will have checked that in their review. Here's what Anthropic's terms say for ours." |
| "Their roadmap is behind." | You don't know their roadmap, and you can't promise yours either | Talk about what's documented today |
| "Everyone is moving off them." | An unverifiable market claim | Talk about this customer's workload |
| "Claude is better at everything." | Not true of any model, and the CIO knows it | "Here's where we'd expect a difference, and how we'd check." |
| Anything about a competitor's pricing you haven't seen in writing | Pricing changes, and enterprise prices are confidential | "Compare total cost per completed task on the bake-off." |

Also never share or ask for a competitor's confidential terms, benchmark results the customer received under NDA, or anything from a previous employer. If a customer offers it, decline.

## A shape for the conversation

1. **Acknowledge the decision.** "That makes sense. What did standardising solve for you?"
2. **Find the gap, if there is one.** "Is there a workload where the current setup isn't meeting the bar?" If not, you're done for today. Leave a useful note and go.
3. **Lower the switching cost.** Claude in their cloud, behind their gateway, under their existing security review where possible. Be accurate about feature gaps.
4. **Offer evidence, not claims.** A bake-off on one workload, with the incumbent included and the decision rule agreed in advance.
5. **Agree a next step with an owner and a date**, or agree there isn't one.

## Practice prompts (original, in the style of a customer role-play)

1. "We signed a three-year enterprise agreement with Azure OpenAI last quarter. Why are you here?"
2. "Our Gemini rollout is going fine. Convince me there's a reason to look at anything else."
3. "Is your model better than theirs? Yes or no."

> **Key takeaways**
> - A standard usually solves procurement, security, engineering and risk problems. Ask what it solved before you say anything about models.
> - Claude runs in Microsoft Foundry and on Google Cloud as well as on AWS and the Claude API, so a cloud standard often changes the platform, not the answer. Be accurate about each platform's gaps.
> - Differentiate with a fair bake-off on the customer's data, incumbent included, with the switching cost priced in.
> - Propose multi-model only when workloads differ, a gateway can route, and the customer gains resilience or fit.
> - Never make unsourced claims about a competitor's quality, data practices, roadmap or pricing. "Let's measure it" beats every adjective.
