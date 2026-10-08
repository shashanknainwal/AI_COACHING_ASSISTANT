---
title: "Build, Buy or Partner"
type: reading
minutes: 16
---

> **By the end of this lesson** you'll be able to lay out the three ways an enterprise can put Claude to work (Claude's own apps, a build on the API, or a product from a software vendor), score them on five criteria, and recommend a mix instead of a single answer.

## How this comes up in interviews

An applied architect at a model provider is not paid to maximize API builds. The posting describes being a trusted technical advisor to the customer (Official, from Anthropic's Solutions Architect, Applied AI posting). Advisors sometimes say "you don't need to build this." In a case round, a strong answer usually splits the customer's wish list: some of it is a seat licence, some of it is a build, and some of it is already sold by a vendor. Expect follow-ups like "why not just buy?" whichever way you lean.

## The three paths

| Path | What the customer gets | Who builds and runs it |
|---|---|---|
| **Buy: Claude's apps** | Claude on web, desktop and mobile, Claude Code for developers, with team or enterprise administration | Anthropic. The customer configures and governs. |
| **Build: the API** | Claude inside their own product or workflow, through the Claude API or a cloud platform (Amazon Bedrock, Google Vertex AI, Microsoft Foundry) | The customer's engineers, often with help from the provider's applied AI team |
| **Partner: a software vendor** | A finished product for one job (claims intake, contract review, a support desk) built on a frontier model | The vendor. The customer integrates and configures. |

Module A2 covers the API-versus-cloud-platform choice in depth. Here, treat it as one "build" path.

## What "buy" includes today

The plan matrix changes, so check [claude.com/pricing](https://claude.com/pricing) before you quote anything. As of October 2026, that page lists:

- **Team plans** with Claude Code, SSO, central billing, admin controls for connectors, usage analytics, and no model training on the customer's content by default.
- **Enterprise plans** that add role-based access, SCIM, audit logs, the Compliance API, custom data retention controls, IP allowlisting and network-level access control, with a HIPAA-ready offering available.

For an architect, the point is this: a large share of "we want AI for our employees" requests (drafting, analysis, research, coding help, questions over shared documents) are met by seats plus connectors to the customer's existing tools. No one has to build or maintain anything. Don't design a custom internal chat app when the customer needs a seat licence and a rollout plan.

## When to build

Build on the API when at least one of these holds:

- **The AI is inside the customer's product.** Their customers, not their employees, use it.
- **The workflow is specific and repeated at volume.** Processing 40,000 claims a month is a pipeline, not a chat.
- **It must connect deeply to systems of record**, with custom permissions, validation and audit trails.
- **They need control** over the prompt, the model per task, latency, cost and evaluation.
- **It's a differentiator.** If how they do this is how they compete, owning it matters.

Building means owning evals, monitoring, prompt changes, model upgrades and on-call. Count those costs (lesson 3 does).

## When to partner

A vendor product fits when:

- **The job is common across companies** (contract review, support desk, meeting notes) and a mature product exists.
- **Time to value beats control.** A product can be live in weeks.
- **The customer lacks the engineering skills** or the appetite to run an AI system.

Questions to ask any vendor, in your own words:

1. Which model and provider do you use, and on which platform? Where is data processed and stored?
2. What do you retain, for how long, and is any of it used for training?
3. Show measured accuracy on *our* documents in a pilot, not a demo deck.
4. How do you evaluate quality, and how do you handle model upgrades?
5. What happens to our data and workflows if we leave?

## Five criteria

Score each path for the specific use case, not in general.

| Criterion | Buy (apps) | Build (API) | Partner (vendor) |
|---|---|---|---|
| **Time to value** | Days to weeks | Months | Weeks to months |
| **Control** (prompts, models, UX, evals) | Low to medium | Full | Low; depends on the vendor |
| **Data** (where it goes, retention, residency) | Governed by the provider's plan terms | The customer decides within the provider's options | Adds a third party to review |
| **Cost shape** | Per seat | Build cost, then usage and run costs | Licence, often per seat or per document |
| **Skills needed** | Change management and training | AI engineering, evals, operations | Integration and vendor management |

Two patterns hold most of the time:

- **Cost per unit falls with build, but fixed cost rises.** Buy is cheaper at low volume. Build wins at high volume over a long horizon, if the team can run it. The exercise in lesson 3 shows the horizon flipping the answer.
- **Data review effort grows with each party.** A vendor adds its own sub-processors and retention terms to the customer's security review. That's not a reason to reject vendors, but it takes time. Plan for it.

## Recommend a portfolio, not a winner

Most enterprises end up with all three. A typical shape:

- **Seats for knowledge workers** (Team or Enterprise), with connectors to email, documents and chat.
- **Claude Code for engineering teams.**
- **Two or three API builds** on the workflows that are high volume and specific to the business.
- **A vendor product** where a mature one exists for a commodity job.

In a customer meeting or case round, say it in this form: "For employee productivity, buy. For the claims pipeline, build. For contract review, run a pilot with a vendor against the same eval we'd use for a build. Here's how we'd decide."

## Practice (say it out loud)

Original prompts in the style of a solutions architect case round:

- "A 30,000-person hospital network wants 'AI for everyone.' What do you buy, what do you build, and in what order?"
- "The customer's CIO says building is always cheaper in the long run. Agree or disagree, with numbers you'd need."
- "A vendor claims 95% accuracy on invoice extraction. Design the two-week pilot that tests it."

> **Key takeaways**
>
> - Three paths: Claude's apps (buy), the API or a cloud platform (build), and vendor products (partner). Most enterprises need a mix.
> - Buy for general employee productivity. Build when the AI is in the product, the workflow is specific and high-volume, or control matters.
> - Partner when the job is common, a mature product exists, and time to value beats control.
> - Score options on time to value, control, data, cost shape and skills, for the specific use case.
> - Check plan features on the current pricing page before quoting them; they change.
