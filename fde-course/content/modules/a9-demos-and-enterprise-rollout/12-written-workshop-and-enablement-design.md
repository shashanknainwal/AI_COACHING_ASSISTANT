---
title: "Written: Design a Workshop That Ends in a Build"
type: written
minutes: 40
sections:
  - key: outcomes
    label: 1. Outcomes and audience
    prompt: "Who attends, what they can do at the end that they can't now, and how you'll know."
    words: [80, 220]
  - key: agenda
    label: 2. The agenda
    prompt: "A timed agenda for the day: blocks, minutes, who leads, and what each group produces. Include a live whiteboarding block."
    words: [180, 450]
  - key: prep
    label: 3. Preparation and materials
    prompt: "What you need from the customer beforehand (data, access, people), what you prepare, and the fallback if access fails on the day."
    words: [80, 250]
  - key: after
    label: 4. After the workshop
    prompt: "Follow-up within a week, how the work continues without you, and the one measure you'll report back."
    words: [60, 200]
rubric:
  - name: Outcomes tied to the customer's work
    points: 20
    lookFor: "Outcomes are concrete abilities on Halberd's own tasks (for example each team leaves with a working Skill or prompt over its own documents and a 10-case check), with a way to verify them. Audience is chosen deliberately (champions plus one engineer per team, not 200 people)."
  - name: Hands-on agenda with timing
    points: 25
    lookFor: "A realistic timed day where most time is building, not slides: short framing, a demo on the customer's data with its eval, team build blocks on real use cases, a live whiteboarding block where teams sketch their agent or workflow and get challenged on data, approvals and failure handling, then show-and-tell with honest results. Breaks included. Each block has a named output."
  - name: Preparation and fallback
    points: 20
    lookFor: "Use cases, sample documents and expected answers collected in advance; accounts, connectors and Skills provisioned and tested the day before; data rules agreed (what may be used); a fallback (pre-loaded files, recorded run) if access or the network fails."
  - name: Guardrails and honesty
    points: 15
    lookFor: "States the data guardrails for the day, shows at least one failure and how to check outputs, and avoids promising results the workshop can't show. Doesn't invent product features."
  - name: Continuation and measure
    points: 20
    lookFor: "A written follow-up within a week; each team's artefact has an owner and a next step; champions carry it forward; one outcome measure with a baseline is reported back at a set date."
passScore: 70
graderNotes: "Mark down agendas that are mostly presentations, have no timings, or have no customer data. Cap 'Hands-on agenda with timing' at 10 if there's no build time or no whiteboarding block. Cap 'Preparation and fallback' at 8 if there's no plan for access failing. Reward specific, small outcomes over grand ones. Don't require particular product names; reward 'confirm with the account team' where a product capability is uncertain."
anchors:
  - label: weak
    expect: [0, 45]
    answer: "Outcomes: Everyone will understand AI and be inspired to use Claude.\nAgenda: 9:00 Welcome. 9:30 History of AI. 10:30 Claude capabilities overview. 12:00 Lunch. 13:00 Use case brainstorming. 15:00 Q&A. 16:00 Close.\nPrep: Send a calendar invite to all staff.\nAfter: Share the slides."
  - label: strong
    expect: [75, 100]
    answer: "Outcomes: 24 people, 8 teams (2 champions plus 1 engineer each). Each team leaves with a working Skill or prompt over its own documents and a 10-case check showing how often it's right. Verified at the 15:30 show-and-tell.\nAgenda: 09:00-09:20 framing and guardrails. 09:20-09:50 demo on Halberd invoices with its scoreboard and one failure. 09:50-10:00 break. 10:00-12:00 build block 1: teams pick their use case from the pre-agreed list, write 10 expected answers, build a first version. 12:00-12:45 lunch. 12:45-13:45 live whiteboarding: each team sketches the workflow on a board; I challenge data access, approvals and what happens when it's wrong. 13:45-15:15 build block 2: fix the top failure, package as a Skill. 15:15-15:30 break. 15:30-16:30 show-and-tell with honest scores. 16:30-16:45 next steps per team.\nPrep: use cases and 10 sample documents per team two weeks ahead; seats, connectors and Skills tested the day before; data rules agreed with IT security; offline copies of documents and a recorded demo in case access fails.\nAfter: written summary in 3 days; each artefact has an owner; champions run a 30-minute follow-up in week 2; we report hours saved on two tasks against a baseline at day 30."
---

Grace's note: *"Imogen asked for 'an AI workshop' for the first champion cohort. Every vendor runs the same day: three hours of slides and a brainstorm. Ours ends with something built on Halberd's own work. Design it."*

## The brief

> **Halberd Freight Group** (fictional) is starting the champion phase of its 90-day plan (lesson 06). Imogen Pryce wants a one-day, in-person workshop in Rotterdam for the first cohort: about **16 champions** from customer service, freight audit, finance and tendering, plus **8 engineers**. Everyone has Claude Enterprise seats; read-only connectors to SharePoint and the ticketing system are live. The engineers have Claude Code.
>
> Imogen's request: "I want them to leave able to do something, not just excited."

## What to write

Four sections, on the right. A good workshop agenda reads like a build plan: every block has an output. Include a **live whiteboarding block**: teams sketch their workflow or agent on a board and you challenge it the way Ruairi did in lesson 09 (data, approvals, failure handling, how they'll know it works). It's practice for them, and live-whiteboarding practice for you.

Things to think about:

1. What can a team build and check in four hours on its own documents?
2. What do you need from Halberd two weeks before, and what do you test the day before?
3. Where does the day show a failure on purpose?
4. What happens on day two, when you've gone home?
