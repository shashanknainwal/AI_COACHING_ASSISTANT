---
title: "Written: A 90-Day Adoption Plan for 5,000 Staff"
type: written
minutes: 50
sections:
  - key: summary
    label: 1. The plan on one page
    prompt: "The recommendation for Imogen Pryce: phases, dates, who goes first and why, and the three numbers you'll report at day 90."
    words: [120, 300]
  - key: setup
    label: 2. Foundations and guardrails
    prompt: "Identity, connectors, Claude Code policy, data guardrails and what you'd confirm with the account team. Name an owner for each."
    words: [150, 400]
  - key: people
    label: 3. Champions, training and communication
    prompt: "Champion network, training by role, and the works-council and union plan for the Netherlands, Germany and the UK."
    words: [150, 400]
  - key: metrics
    label: 4. Measures and decision points
    prompt: "Activity, depth and outcome measures, the baselines you'll take before launch, and the go/hold criteria at day 30 and day 60."
    words: [100, 300]
  - key: risks
    label: 5. Risks and what you'd push back on
    prompt: "The biggest risks, and anything in the brief you'd refuse or change."
    words: [80, 250]
rubric:
  - name: Phasing with exit criteria
    points: 20
    lookFor: "Three phases across 90 days, with pilot teams chosen for measurable repeated tasks (for example freight audit, customer service replies, tender responses), department waves after that, and explicit exit criteria between phases. Does not launch to all 5,000 on day one."
  - name: Foundations and connector governance
    points: 20
    lookFor: "SSO and SCIM tied to the HR system, roles, one connector policy covering both the Claude apps and Claude Code (read-only first, per-user OAuth, named owners, no broad shared credentials), org-provisioned Skills for early use cases, and a correct plan for the 180 engineers: Bedrock with pinned models and endpoint-managed settings through MDM, because server-managed settings are skipped for third-party providers. Says what to confirm with the account team."
  - name: Champions, training and representation
    points: 20
    lookFor: "A champion network from the business with a ratio, time allowance and channel; role-based training on real work; manager briefing. Works councils in the Netherlands and Germany and the UK union are consulted before the pilot, with a written position on logging, visibility, retention and no individual ranking, and a representative in the steering group. HR and employment counsel are owners; the plan doesn't give legal advice."
  - name: Honest measurement
    points: 20
    lookFor: "Activity, depth and outcome measures; outcome measures on named tasks with baselines taken before launch; go/hold criteria at day 30 and 60. Notes that Claude Code usage on Bedrock won't appear in the claude.ai dashboard and plans OpenTelemetry or cloud billing instead. No invented productivity numbers."
  - name: Pushback and risk
    points: 10
    lookFor: "Pushes back on the CEO's '80% weekly active users by day 30' target and on using usage data in performance reviews; names realistic risks (shadow connectors, data-class mistakes, works-council delay, champion burnout) with mitigations."
  - name: Executive clarity
    points: 10
    lookFor: "Leads with the recommendation, uses dates, owners and numbers, short sections, and plain language a COO can act on."
passScore: 70
graderNotes: "Mark down: launching to all 5,000 on day one; agreeing to use activity data in performance reviews; no works-council or union step, or one that comes after launch; claiming server-managed settings will govern Bedrock users (the Claude Code docs say they're skipped for third-party providers); inventing plan features or certifications instead of saying they'd be confirmed; productivity numbers stated as fact without a baseline. Don't require exact setting names. Reward answers that keep the pilot small and measurable and that treat the 80% target as an activity number to replace with outcome measures. Legal advice presented as certain (for example 'German law requires X days') should lose points on representation; the right move is to involve employment counsel."
anchors:
  - label: weak
    expect: [0, 45]
    answer: "Summary: We will roll out Claude to all 5,000 staff in week one with a launch webinar, so everyone can benefit immediately. Target 80% weekly active users by day 30, as the CEO asked.\nFoundations: Turn on SSO. Enable all connectors so people get maximum value. Engineers can use Claude Code through Bedrock and we'll manage their settings from the admin console.\nPeople: IT will run a webinar and publish a prompt library. We'll tell the works council once it's live.\nMetrics: Weekly active users and number of prompts per person; we'll share a leaderboard and include usage in performance reviews to drive adoption.\nRisks: Low risk because Claude is secure."
  - label: strong
    expect: [75, 100]
    answer: "Summary: Three phases. Days 0-30: foundations plus three pilots (freight audit, NL customer service, UK tender team), about 150 people. Days 31-60: four department waves with champions. Days 61-90: remaining staff. At day 90 I report hours saved on three measured tasks against pre-launch baselines, active use by department, and open risks.\nFoundations: SSO and SCIM from the HR system (owner: identity team); connector policy, read-only and per-user OAuth for SharePoint and the ticketing system, each with a named owner, no shared credentials; three org Skills (customer letters, tender template, audit note). The 180 engineers use Claude Code on Bedrock in Halberd's AWS: models pinned, settings through MDM, because server-managed settings are skipped for third-party providers. I'd confirm SCIM provider support and Compliance API scope with the account team.\nPeople: 60 champions (about 1 per 80 staff), two hours a week agreed with managers. Role-based training on real documents. Works councils in NL and DE and the UK union briefed in week one, before pilots, with a written note on what is logged, who sees it, retention, and a commitment not to rank individuals; HR and employment counsel own the agreement; a representative joins the steering group.\nMetrics: Baselines in weeks 1-2 on three tasks. Day 30 go if pilots hit 60% weekly use and no data incidents; day 60 go if first outcome deltas hold. Bedrock usage measured through OpenTelemetry and the AWS bill, since the claude.ai dashboard won't see it.\nPushback: 80% WAU by day 30 measures logins, not value; I'd replace it with outcome measures. Usage data stays out of performance reviews."
---

Grace's note: *"Halberd liked the demo enough to buy seats first. Imogen Pryce wants a 90-day plan for the whole company before the contract starts. She'll forward it to the CEO and the works councils, so write it for them."*

## The brief

> **Halberd Freight Group** (fictional) is a freight forwarder with **5,000 staff**: 2,100 in the Netherlands (head office in Rotterdam), 1,400 in Germany, 900 in the UK and 600 in Poland. About **180 are software engineers**. Halberd has bought Claude Enterprise seats for everyone.
>
> - Identity: Microsoft Entra ID. HR system feeds joiners and leavers. Devices are managed with an MDM tool.
> - Systems: SharePoint for documents, a ticketing system for customer service, an in-house transport-management system (TMS) and a finance ERP.
> - Engineering: the CTO wants Claude Code to run through **Amazon Bedrock** in Halberd's own AWS account, so model traffic and spend sit there.
> - People: works councils in the Netherlands and Germany; a recognised union for UK warehouse and office staff. The Dutch works council has already asked "what will be logged about us?"
> - The CEO's ask: **"80% weekly active users by day 30, and I want to see who isn't using it."**
> - Imogen Pryce, COO (fictional), is the sponsor. She wants dates, owners and three numbers she can report at day 90.

## What to write

Five sections, on the right. Write it as the plan you'd actually send: dates, owners, numbers, and plain pushback where the brief asks for the wrong thing. Use lessons 04 and 05. Where a product detail isn't in those lessons, write "to confirm with the account team" instead of guessing.

Things to think about:

1. Which three pilot teams have a repeated, measurable task you can baseline in two weeks?
2. What does the connector policy say on day one, and who owns each connector?
3. How do policy and measurement reach engineers who run Claude Code on Bedrock?
4. What will you tell the Dutch works council about logging, before anyone starts?
5. What do you replace "80% weekly active users" with, and how do you say no to "who isn't using it"?
