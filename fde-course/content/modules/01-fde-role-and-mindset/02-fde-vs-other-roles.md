---
title: FDE vs. SWE, Solutions Engineer, and Consultant
type: reading
minutes: 10
---

Hiring managers, recruiters, and even FDEs themselves often blur these roles together. Knowing the differences helps you explain your value, pick the right job, and avoid doing the wrong job well.

## The comparison

| | Product SWE | Solutions / Sales Engineer | Consultant | **Forward Deployed Engineer** |
|---|---|---|---|---|
| **Primary goal** | Build the product for *all* customers | Win the deal | Deliver a statement of work | Make *this* customer successful, and make the product better |
| **Who sets the work** | Product roadmap | Sales cycle | Contract | Customer outcome + company strategy |
| **Writes production code?** | Yes | Mostly demos and proofs of concept | Sometimes | **Yes**, deployed in the customer's environment |
| **Time horizon** | Quarters | Weeks (pre-sale) | Fixed project | Months, through and after go-live |
| **Success metric** | Features shipped, reliability | Revenue closed | Project delivered on time | Customer's business metric moved, expansion, product insight |
| **Typical artifacts** | PRs, design docs | Demos, RFP answers | Decks, reports | Integrations, pipelines, LLM apps, eval sets, briefs |

## The key differences, explained

### FDE vs. product software engineer

A product SWE builds *generalized* software. They ask: "What should the product do for everyone?" An FDE builds *specific* solutions first and generalizes later. They ask: "What does this customer need working by Friday?"

The two roles need each other. FDEs find patterns ("five customers have built the same CSV importer") and product engineers turn the pattern into a feature. A healthy FDE organization has a formal channel for this feedback, which you'll practice in this course.

### FDE vs. solutions engineer

Solutions (or sales) engineers work **before** the contract is signed. Their job is to prove the product *can* solve the problem. FDEs usually work **after** the contract, proving it *does* solve the problem in production. In smaller companies one person often does both. That's fine, but know which hat you're wearing: a demo can cut corners that a production deployment cannot.

### FDE vs. consultant

Consultants deliver what a contract specifies, and the engagement ends. FDEs represent a product company. Their deeper goal is to make the *product* successful at the customer so the customer renews and expands, and to bring lessons back so the next deployment is faster. An FDE who builds a beautiful bespoke system that only they understand has failed, even if the customer is happy today.

> **Watch out for the "consultant trap":** if every deployment needs custom code that never makes it back into the product, your company becomes a services business with software margins in name only. Great FDEs constantly ask, "How do I make this the last time anyone has to build this by hand?"

## Where FDEs sit in a company

FDEs usually report into one of three places, and it shapes the job:

- **Engineering.** Strong technical bar, close to the product team, risk of drifting from customer needs.
- **Customer success / delivery.** Close to the customer and revenue, risk of becoming a ticket queue.
- **A dedicated "Deployment" org.** Often the healthiest: its own leadership, explicit goals for both customer outcomes and product feedback.

When you interview for an FDE role, ask: *"How does feedback from deployments reach the product roadmap? Give me a recent example."* The answer tells you a lot about whether the role is real engineering or disguised support.

## The LLM-era FDE

With general-purpose models like Claude, a lot of the product's value is created at deployment time: choosing the use case, writing the system prompt, connecting tools and data, building evals, and tuning cost and latency. In many AI companies the FDE is effectively the person who turns a model into a product for a specific customer. Modules 6 to 8 of this course focus on exactly that work.
