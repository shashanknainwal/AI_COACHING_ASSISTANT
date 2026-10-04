---
title: What is a Forward Deployed Engineer?
type: reading
minutes: 12
---

A **Forward Deployed Engineer (FDE)** is a software engineer who works directly with a customer to make a product deliver real value in that customer's environment. They write production code, but the customer's problem decides what they build, not a product roadmap.

The word *forward* is borrowed from the military idea of a forward operating base: you are stationed close to where the action is, not back at headquarters. For an FDE, "the action" is the customer's data, systems, people, and deadlines.

> **One-sentence definition:** An FDE is an engineer who owns the outcome at a customer, and writes whatever code it takes to get there.

## Where the role came from

Palantir made the title well known. Its products (data integration and analytics platforms) were powerful but useless until someone connected them to a customer's messy, idiosyncratic data and workflows. Palantir sent engineers on-site to do exactly that, and learned two things:

1. **Deployments generate the best product insight.** Engineers who see the same integration pain at five customers know what the product should do next.
2. **Speed at the customer wins deals.** A working prototype on the customer's own data in week two beats a slide deck every time.

The model spread. Today you'll see FDE (or "forward deployed", "deployed engineer", "solutions engineer – implementation") roles at AI labs, AI-native startups, data platforms, and enterprise software companies. The surge in large language models made the role even more important. A general-purpose model like Claude can do an enormous range of tasks, but someone still has to find the *right* task at a customer, connect the model to the customer's data and tools, prove it works with evaluations, and ship it.

## What FDEs actually do all week

A realistic week for an FDE on an active engagement:

| Day | What happens |
|---|---|
| Monday | Call with the customer's ops lead to review last week's pilot metrics. Two edge cases are failing. |
| Tuesday | Write a Python script to pull 30 days of tickets from the customer's API, clean them, and add the failing cases to the eval set. |
| Wednesday | Change the prompt and the retrieval step. Eval accuracy goes from 81% to 90%. Ship to the pilot group. |
| Thursday | The customer's security team asks how data is handled. Write a one-page data-flow doc and walk them through it. |
| Friday | Write an internal note to your product team: "Three customers have now asked for X. Here's the workaround I built and why it should be a feature." |

Notice the mix: data work, integration code, LLM engineering, writing, and customer conversations. That mix *is* the job.

## The FDE skill stack

This course is built around six skill areas. You need all of them, but not all at expert level on day one.

1. **Customer discovery.** Find out what problem is actually worth solving, who cares, and how success will be measured.
2. **Data wrangling.** Customer data is always messier than promised. You'll profile, clean, and reconcile it quickly.
3. **Integration engineering.** APIs with rate limits, pagination, auth, and surprise schema changes.
4. **LLM application engineering.** Building with the Anthropic SDK: prompts, structured outputs, tool use, retrieval, agents, and evals.
5. **Production engineering.** Deploying into environments you don't control, observing them, and debugging under pressure.
6. **Communication.** Writing briefs, running demos, managing expectations, and feeding insights back to your product team.

## Traits of great FDEs

Technical skill gets you in the door. These traits make you great at it:

- **Bias to a working thing.** You'd rather show a rough prototype on real data on Thursday than a polished plan next month.
- **Ownership of the outcome, not the ticket.** "I closed my tasks" doesn't count. "The customer's ops team now handles 40% more tickets" does.
- **Comfort with ambiguity.** Requirements will be vague and change. You turn ambiguity into a written, agreed scope.
- **Low ego about the stack.** Sometimes the right answer is a SQL query and a cron job, not an agent.
- **Translator mindset.** You explain model limits to an executive and customer workflows to your own engineers.

## How this course works

Each lesson has two halves:

- **Left:** the explanation you're reading now.
- **Right:** a real Python environment running in your browser. On reading lessons it's a scratchpad. On exercises, your code is checked by automated tests when you press **Submit**.

When an exercise calls Claude, it uses a faithful offline simulator of the official `anthropic` Python SDK. The function names, parameters, response objects, and errors are the same as the real SDK, so everything you write here works against the real API once you run `pip install anthropic` and set your `ANTHROPIC_API_KEY`. The simulator returns scripted responses so grading is deterministic and you never need an API key to learn.

**Try it now:** press **Run** in the editor on the right.
