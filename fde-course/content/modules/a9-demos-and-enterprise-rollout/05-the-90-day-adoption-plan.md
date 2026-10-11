---
title: "The 90-Day Adoption Plan and Change Management"
type: reading
minutes: 16
---

> **By the end of this lesson you will be able to:**
> - Structure a 90-day rollout in three phases with exit criteria.
> - Recruit and use champions, design role-based training and set guardrails.
> - Pick adoption metrics that lead to outcomes, not vanity numbers.
> - Plan the conversation with works councils and unions before launch, not after.

Licences don't change how people work. Most seat rollouts stall the same way: a launch email, a spike of curiosity, a slide in month two showing 30% weekly use, and nobody can say what changed. The architect's job is to make the rollout a programme with owners, phases and measures. This lesson gives you the shape; lesson 06 has you write one.

## The three phases

| Days | Phase | Goal | Exit criteria |
|---|---|---|---|
| 0 to 30 | **Foundations and pilot** | Identity, connectors and policy in place; 2 or 3 pilot teams using it on real work | SSO and SCIM live; connector policy signed; pilot teams' baseline measured; no open security findings |
| 31 to 60 | **Expand with champions** | Department waves, each with trained champions and use cases | Each wave reaches its active-use target; first outcome measures from pilots |
| 61 to 90 | **Scale and embed** | Remaining staff; use cases written into team processes | Outcome numbers in front of the sponsor; decision on next 90 days |

Pick pilot teams with a measurable, repeated task and a manager who wants it: finance close, customer-service replies, tender responses. Not the team with the loudest sceptic, and not IT alone.

## Champions

Champions are the multiplier. A useful ratio is about one per 50 to 100 staff, drawn from the business, not IT. Give them:

- early access and a short advanced session;
- a channel to share prompts, Skills and failures;
- an hour a week of recognised time, agreed with their manager;
- a direct line to the programme team for questions they can't answer.

Their job is to show colleagues one real task done better, in that team's own work. That beats any all-hands demo.

## Training: by role, short, on real work

- **Everyone (45 minutes):** what it's good and bad at, what data may go in, how to check an answer, where to get help.
- **By role (60 to 90 minutes):** three use cases for that function, with their own documents and connectors.
- **Builders (half a day):** Skills, Projects, and for engineers, Claude Code with the org's managed settings.
- **Managers (30 minutes):** how to set expectations, what "good use" looks like, and what not to measure individuals on.

Record it, but don't make the recording the training. People learn by doing their own task with someone beside them.

## Guardrails

Guardrails are what let a cautious organisation say yes. Write them on one page:

- **Data classes:** what may go in (internal documents), what needs a connector instead of copy and paste, what never goes in (for example, special-category personal data without an approved use case).
- **Connectors:** the approved list from lesson 04, read-only first.
- **Human checking:** anything sent to a customer, regulator or court is reviewed by a person.
- **Disclosure:** when staff must say a draft used AI.
- **Escalation:** how to report a bad output or a data mistake, with no blame for reporting.

Enforce the technical ones in configuration (connectors, managed settings, retention), and the rest through training and managers.

## Measuring adoption honestly

| Layer | Examples | Use it for |
|---|---|---|
| Activity | Weekly active users, sessions, seats assigned versus used | Spotting stalled teams early |
| Depth | Use of connectors, Skills, Projects; repeat use per person | Telling curiosity from habit |
| Outcome | Hours saved on a measured task, cycle time, quality checks, satisfaction | The case for the next 90 days |

Measure outcomes on a few named tasks with a baseline taken before launch, the same way you would for a pilot (module A4). Don't report "hours saved" from a survey alone. And don't use activity data to rank or discipline individuals; say so in writing. It kills trust, and in many countries it triggers employee-representation rules.

## Works councils and unions

In much of Europe, and in many unionised workplaces elsewhere, introducing a tool that could be used to monitor staff, or that changes how work is done, needs consultation before launch. In Germany and the Netherlands, works councils have co-determination or consent rights over systems capable of monitoring employees. The exact rules vary by country and agreement. Your role isn't to give legal advice; it's to make sure the customer's HR and employment counsel are in the plan from day one.

What good looks like:

- **Early.** Brief the works council or union in the first two weeks, before the pilot, not the week of launch.
- **Concrete.** Show what is logged, who can see it, how long it's kept, and what it will not be used for (individual performance ranking).
- **Written.** An agreement or a written commitment on monitoring, data use and training.
- **Two-way.** A representative in the steering group, and a channel for concerns during the rollout.
- **Honest about jobs.** If the business case is "hours saved", say what the hours go to. Silence here is where resistance comes from.

Budget the time: a works-council agreement can take weeks. Put it on the critical path, not in a footnote.

## Common failure modes

- Launching to everyone on day one with no use cases.
- Champions chosen by IT, with no time allowed.
- Measuring only logins, then being unable to defend the renewal.
- Connectors switched on broadly with shared credentials.
- Discovering the works council in week eight.

> **Key takeaways**
> - Three phases with exit criteria: foundations and pilot, expand with champions, scale and embed.
> - Champions from the business, with time and a channel, are the multiplier.
> - Train by role on the person's own work; write guardrails on one page and enforce what you can in configuration.
> - Report activity, depth and outcome; outcomes need a baseline taken before launch.
> - Bring works councils and unions in early, in writing, and never use activity data to rank individuals.
