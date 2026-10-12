---
title: "Write It: A Field Report That Turns Workarounds into a Product Request"
type: written
minutes: 40
sections:
  - key: ask
    label: 1. The ask, in three sentences
    prompt: "What should the product team build, for whom, and what changes for the field if they do? A busy product lead should be able to stop reading here."
    words: [40, 120]
  - key: evidence
    label: 2. Evidence
    prompt: "The three workarounds as one problem: customers affected, engineer-days spent, incidents and risks, and the pipeline at stake. Show your arithmetic. Say which numbers are measured and which are estimates."
    words: [100, 260]
  - key: request
    label: 3. The request, scoped
    prompt: "The smallest version that removes the workarounds, what it deliberately leaves out, and how you'd know it worked."
    words: [100, 250]
  - key: cost_of_waiting
    label: 4. The cost of doing nothing
    prompt: "What happens over the next two quarters if this isn't built? Be concrete and don't exaggerate."
    words: [50, 160]
  - key: field_commitments
    label: 5. Open questions and what the field will do
    prompt: "What you don't know yet, and what you and the FDE team will contribute (code, test customers, reviews)."
    words: [50, 160]
rubric:
  - name: A clear, generalised ask
    points: 20
    lookFor: "Opens with one request that names the root cause shared by all three workarounds (the starter kit isn't deployable in locked-down networks) rather than three customer stories or a customer-specific feature. Says who benefits and what changes."
  - name: Quantified, honest evidence
    points: 25
    lookFor: "Uses the numbers from the brief correctly: 4 x 3 + 3 x 6 + 2 x 4 = 38 engineer-days so far; the verify=False fork and the skipped aud check as security incidents caused by forks; the $1.9M late-stage pipeline labelled as a sales estimate. Separates measured from estimated. Invents nothing."
  - name: Scoped, testable request
    points: 25
    lookFor: "Proposes a smallest valuable version: config-driven proxy and CA bundle with a startup self-check, OIDC validation with group-to-tool mapping via a maintained library, and an offline bundle with a hash-locked lock file and a documented intake process. Names what is out of scope (for example SAML, a custom mirror product, per-customer UI). Gives success measures such as engineer-days per regulated deployment, number of live forks, security findings."
  - name: Cost of waiting without hype
    points: 15
    lookFor: "Projects from the brief's own rates (for example the three late-stage prospects needing the same work, and forks multiplying the security exposure) and says plainly what is uncertain. No claims that deals will certainly be lost."
  - name: The field shares the work
    points: 15
    lookFor: "Offers concrete contributions: the field's existing code as a starting point, Quarrybank or Brightline as design partners (with their agreement), reviews of the design, and retiring the forks once it ships. Lists open questions such as which identity providers to support first."
passScore: 70
graderNotes: |
  This is an internal report from an FDE to their own company's product team about the company's own starter kit (a fictional internal product). Judge it as a product lead would.
  - Numbers not in the brief (new customers, extra revenue, invented incident counts) are fabrication: cap "Quantified, honest evidence" at 10/25.
  - Presenting the $1.9M pipeline as committed or certain revenue caps the same criterion at 15/25.
  - Wrong arithmetic on engineer-days (the correct total is 38) costs at least 5 points there.
  - Three separate feature requests with no shared root cause caps "A clear, generalised ask" at 10/20.
  - A request to build something specific to one customer (for example "add Quarrybank's proxy hostname as a default") is the consultant trap: cap "Scoped, testable request" at 10/25.
  - Don't reward length. A report that fits on one screen and could be pasted into a planning document is the goal.
anchors:
  - label: weak
    expect: [0, 45]
    answer:
      ask: "Quarrybank really needs proxy support, SSO and offline installs. Please add these as soon as possible because they are very important."
      evidence: "Lots of customers have asked for this. It has taken a huge amount of time and we will probably lose millions in deals if we don't fix it."
      request: "Add proxy support, add SSO with SAML and OIDC for all identity providers, build an internal package mirror, and add a Quarrybank configuration preset."
      cost_of_waiting: "We will lose every regulated customer."
      field_commitments: "None, this is a product problem."
  - label: strong
    expect: [75, 100]
    answer:
      ask: "Make the agent starter kit deployable in locked-down enterprise networks: proxy and CA configuration, OIDC sign-in with tool permissions, and an offline install bundle. Every regulated deployment so far has forked the kit to add these, and two forks shipped security defects. If the kit did this out of the box, a regulated deployment would stop starting with a week of plumbing."
      evidence: "Measured, from our time tracking: proxy/CA patches at 4 customers x 3 days = 12; OIDC bolt-ons at 3 customers x 6 days = 18; hand-built wheelhouses at 2 customers x 4 days = 8. Total 38 engineer-days, all on the same root cause. Incidents: one fork shipped verify=False for two weeks before review caught it; another skipped the aud check and a customer pen test found it. Estimate, from sales: three late-stage regulated prospects ($1.9M combined annual contract value, not committed) list all three in their security requirements."
      request: "Smallest version: (1) proxy URL and CA bundle from config, with a startup self-check that refuses to run on bad settings and never offers verify=False; (2) OIDC token validation through a maintained library, with groups mapped to the tools the agent is offered; (3) a release artifact that includes a hash-locked lock file and wheels for our supported base image, plus intake documentation. Out of scope: SAML, running our own package mirror, per-customer presets. Success: engineer-days of plumbing per regulated deployment from about 9 to under 2, zero live forks of these modules, no repeat findings."
      cost_of_waiting: "If the three prospects close at our current rates we spend roughly the same 9 days of plumbing each, about 27 more days, and create three more forks to patch. Each fork is a place a security fix can be missed. We don't know whether any deal depends on this alone, and I wouldn't claim that."
      field_commitments: "Open: which identity providers to test first (our customers use two), and whether the offline bundle should cover more than one base image. The field will contribute the Quarrybank versions of the self-check and validator as a starting point, ask Quarrybank and Brightline to act as design partners, review the design, and retire our forks within a month of release."
---

Module 1 warned you about the consultant trap: solving the same problem by hand at every customer and never making it reusable. Here's the remedy: a written field report that turns repeated workarounds into a product request your own company's product team can prioritize.

## What a good field report does

- **Leads with the ask.** Product leads read dozens of these. The first three sentences decide whether they read the rest.
- **Finds the root cause.** Three workarounds that look different often have one cause. A request that names the cause gets built. Three customer anecdotes go into a backlog and stay there.
- **Brings evidence and labels it.** Customers affected, engineer-days, incidents, pipeline. Say which numbers you measured and which came from someone's estimate.
- **Scopes the smallest valuable version.** Say what's out. A request with no edges reads as "build everything".
- **Shares the work.** The field already has code, design-partner customers and opinions. Offer them.

## The situation

Your team deploys an internal **agent starter kit** (your company's reusable template: the agent loop, tools, an admin page, and a container image) at every customer. It assumes open internet, API keys and `pip install` at container start. In regulated accounts, FDEs have patched it by hand, which is what you practised in exercises 03 to 05. Your engagement lead asks you to write it up for the product team's planning cycle.

Everything here is fictional, including the starter kit.

| Workaround | Customers | Engineer-days per customer (time tracking) | What went wrong |
|---|---|---|---|
| Patched the kit's HTTP client for a proxy and corporate CA | Quarrybank, Harbor Bank, Brightline Health, Lumen Insurance (4) | 3 | One fork shipped with `verify=False` for two weeks before code review caught it |
| Bolted OIDC validation and group-to-tool mapping onto the admin page and agent | Quarrybank, Brightline Health, Lumen Insurance (3) | 6 | Two forks use different JWT libraries; one skipped the `aud` check, found by a customer pen test |
| Hand-built wheelhouses because the image installs packages at start | Quarrybank, Brightline Health (2) | 4 | Quarrybank's first attempt took four intake rounds |

**From sales (an estimate, not committed revenue):** three late-stage prospects in banking, insurance and healthcare, $1.9M combined annual contract value, list proxy support, SSO and offline installation in their security requirements.

## Your task

Write the report in the five sections. Use only the numbers above, show your arithmetic, and label estimates. Aim for something that fits on one screen.
