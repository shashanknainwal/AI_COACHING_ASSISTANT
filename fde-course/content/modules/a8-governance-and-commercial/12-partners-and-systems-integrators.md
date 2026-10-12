---
title: "Partners and Systems Integrators: Co-Sell, Three-Party Deals and Hand-Overs"
type: reading
minutes: 16
---

> **By the end of this lesson** you'll be able to explain who does what when a deal involves a cloud provider and a systems integrator (SI) as well as the customer, keep a three-party design honest when the partners' incentives pull against the customer's requirements, and hand a project over to a partner without losing the quality bar.

## Why this matters

Large enterprises rarely buy and build with one vendor. A typical deal has the customer, the model vendor, the cloud provider whose marketplace or service carries the bill, and an SI or consultancy that does most of the build. Each has its own goals. The architect is often the only person in the room whose job is to make the design correct rather than to win a share of the work.

Anthropic's architect postings mention working with partners alongside customers (**Official**, job postings; check the current wording). How partner programmes and co-sell arrangements work inside any vendor isn't public in detail, so this lesson describes **general practice** across the industry, plus the platform facts from module A2 that change who can do what.

## The parties and what they want

| Party | Typical goal | Where it can pull against the customer |
|---|---|---|
| **Customer** | A working system that meets its requirements, at a predictable cost | Sometimes states positions instead of requirements (module A5) |
| **Model vendor (you)** | A successful deployment that grows | Pressure to oversell features or timelines |
| **Cloud provider** | Workloads and spend on its platform; spend that counts toward the customer's commitment | May push its own platform or service even when a feature the design needs isn't available there |
| **Systems integrator** | A delivered project, a good reference, follow-on work | May reuse a design from another client that doesn't fit this customer's constraints; may prefer a bigger build |

None of these goals is wrong. Problems start when one party's incentive quietly overrides a customer requirement, such as residency or a feature the design depends on.

## Co-sell and marketplace deals

**General practice:** cloud providers run co-sell programmes in which their account teams work with a software vendor's account team on a shared customer, often when the vendor's product is bought through the cloud's marketplace. For the customer, a marketplace purchase can simplify procurement (one bill, an existing vendor relationship).

What's documented for Claude (module A2 lesson 01 and lesson 05):

- **Claude Platform on AWS** is bought through AWS Marketplace; **Claude in Microsoft Foundry** through Azure Marketplace. Both bill in Claude Consumption Units. Private offers on AWS are accepted in the AWS Console.
- **Amazon Bedrock** and **Google Cloud** are billed by the cloud provider as their own services, and the cloud provider is the data processor there.
- Features differ by platform. Batches, code execution, Agent Skills and the Files API, among others, aren't available everywhere.

So "let's put it through the marketplace" or "let's run it on our platform" is never only a commercial decision. It changes the data processor, the features and sometimes the residency options. Your job is to make that visible before anyone signs.

Whether marketplace spend counts toward a customer's cloud commitment is between the customer and the cloud provider. The cloud account manager can speak to their own programme; you shouldn't speak for them.

## Three-party design reviews

When an SI brings a design, review it like any other, with three extra checks:

1. **Does it meet this customer's stated requirements?** Residency, processor, retention, identity. A design reused from another client often carries that client's assumptions, for example global inference where this customer needs EU-only.
2. **Does every feature it uses exist on the chosen platform?** A design built against the Claude API that moves to Bedrock or Vertex AI may lose Batches, code execution or server-side tools.
3. **Who operates what after go-live?** Monitoring, evals, model upgrades and incident response need a named owner at the customer or the SI, with a contract that says so.

When you find a problem, raise it as a requirement mismatch, not a criticism: "The customer's requirement is EU-only inference. On the Claude API, `inference_geo` offers `us` or `global`, so this design doesn't meet it as drawn. Here are two ways that would." Give the SI a way to fix it that keeps their credibility with the customer.

## Handing over to a partner

Many deployments end with the vendor's architect stepping back and the SI or the customer's own team running the system. A good hand-over leaves behind:

- **The design doc**, current, with the decisions and the rejected options.
- **The eval suite**: the frozen set, the graders, the thresholds, and how to run it. This is what protects quality after you leave.
- **The capacity plan** (lesson 06), with the real limits and the date they were checked.
- **The change-control process** for model upgrades and prompt changes (lesson 01), including who decides.
- **Open items** with owners and dates, and a named contact at the vendor for escalation.
- **A joint session** where the partner runs the eval suite and a model-upgrade rehearsal while you watch, not the other way round.

## What to say, and what not to

| Say | Don't say |
|---|---|
| "The customer's requirement is X; this design does Y. Here are two options." | "Your design is wrong." |
| "That feature isn't available on that platform today; here's what changes." | "It'll be there by launch." |
| "Whether this counts toward your commitment is a question for your cloud account team." | "Yes, it all burns down your commit." |
| "Who owns the eval suite after go-live?" | "The partner will handle quality." |

> **Key takeaways**
> - Enterprise deals often involve the customer, the model vendor, a cloud provider and an SI, each with legitimate but different goals. The architect's job is a correct design.
> - Marketplace and platform choices change the processor, the features and the residency options, not just the bill. Make that visible before anyone signs.
> - Review partner designs against this customer's requirements and the chosen platform's features; raise gaps as requirement mismatches with options.
> - Hand over with the design doc, eval suite, capacity plan, change control, open items and a rehearsal the partner runs.
> - Don't speak for the cloud provider's commercial programmes, and don't promise features on a platform that doesn't have them.
