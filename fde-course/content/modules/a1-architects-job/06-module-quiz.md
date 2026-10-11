---
title: "Module A1 Quiz"
type: quiz
minutes: 10
questions:
  - q: "Which description best matches Anthropic's posting for its applied architect role (Solutions Architect, Applied AI)?"
    options:
      - "A post-sales support engineer who resolves escalated customer tickets and maintains the integration runbooks"
      - "A research engineer who trains and fine-tunes a custom model for each large enterprise customer"
      - "A pre-sales architect and trusted advisor who fits Claude into large enterprises' stacks"
      - "An account executive who owns the enterprise relationship, the commercial deal and the revenue forecast"
    answer: 2
    explain: "The posting describes pre-sales architecture for large enterprises, working with Sales, Product and Engineering from discovery to deployment. The account executive owns the deal; the architect owns the technical win."
  - q: "How much reliable public information is there about the applied architect interview loop?"
    options:
      - "Very little beyond the official AI-use rules; confirm it with your recruiter"
      - "A lot: each round and its scoring rubric are published on the careers page"
      - "Enough to be sure it's identical to the Applied AI Engineer loop in every round"
      - "None at all, so there's nothing useful you can do to prepare for it"
    answer: 0
    explain: "Reports of a technical design screen and a customer scenario exist but are sparse and anecdotal. Prepare for them, label them honestly, and ask your recruiter."
  - q: "A customer asks whether Claude can fully automate their claims payouts. What does the trusted-advisor answer sound like?"
    options:
      - "'Yes, Claude can handle that end to end, and we've seen customers remove manual review entirely.'"
      - "'Let's start a pilot on live claims next week and see what accuracy we get once it's running.'"
      - "'I'd rather not commit to anything about automation until the contract and pricing are signed.'"
      - "'Triage and drafting, yes; payouts stay with a person. First, today's error rate.'"
    answer: 3
    explain: "Advisors make specific, honest claims, recommend human control where the risk calls for it, and anchor the conversation in a baseline."
  - q: "Which pair of stakeholders does the lesson say to meet early because they most often stop AI projects late?"
    options:
      - "The project champion and the end users who will work with the tool every day"
      - "The data owner and security"
      - "The economic buyer and the procurement team that negotiates the final contract"
      - "The executive sponsor and the board members who approve the annual budget"
    answer: 1
    explain: "Data access approvals and security reviews are common late blockers. Meeting those owners during discovery turns surprises into scheduled work."
  - q: "Which is a usable success metric for a proof of concept?"
    options:
      - "Improve the efficiency and morale of the servicing team across all regions this year"
      - "Achieve 100% accuracy on every request type before anything goes to production"
      - "Median acknowledgement from 3.5 to 2 days, from CRM timestamps, over 6 weeks"
      - "Make customers noticeably happier with the service by using modern AI throughout"
    answer: 2
    explain: "A metric names the number, its baseline, the target and how it's measured. The others are wishes, and '100% accuracy' has no baseline or tolerance."
  - q: "Your model gets 90% of classifications right on a golden set. Why also measure the human handlers on the same items?"
    options:
      - "To show the customer's leadership which of their staff are underperforming on the task"
      - "Without a comparison 90% means little; if experts agree 88% of the time, it's great"
      - "Because evaluation standards require at least two independent human graders on every item"
      - "So that the human labels can replace the LLM judge entirely once the pilot begins"
    answer: 1
    explain: "Human agreement on the same items is the realistic ceiling and the fair comparison. Without it, any accuracy number is hard to interpret."
  - q: "You learn the customer's policy requires zero data retention from processors. Why is that an architecture question?"
    options:
      - "It isn't; legal handles retention terms after the proof of concept has succeeded"
      - "Because retention terms only change the price per token, not which options exist"
      - "Because retention only matters for batch jobs, so it decides whether to batch"
      - "It can rule out options: Claude Fable 5.1 requires 30-day retention, for example"
    answer: 3
    explain: "Retention, residency and the cloud the customer buys through can rule out models, platforms or features. Fable 5.1 isn't available under zero data retention unless Anthropic expressly authorises it. Find these before you design, and confirm against current documentation."
  - q: "In a solution design doc, what is the main job of the non-goals section?"
    options:
      - "To stop silent scope growth by naming what a stakeholder might assume is included"
      - "To list the features planned for phase 2 so the roadmap looks complete to readers"
      - "To show the customer which capabilities competing vendors can't offer them today"
      - "To add length so the document looks thorough enough for an executive review"
    answer: 0
    explain: "Good non-goals are things someone could reasonably expect. Writing them down prevents arguments later."
  - q: "A reviewer asks why you didn't put all 38,000 pages of manuals into the context window. Which answer reflects the worked example?"
    options:
      - "Long context never works reliably for documents, so retrieval is the only real option here"
      - "About 19M tokens won't fit 1M; one 400K-token manual set would, at nearly twice retrieval's cost"
      - "Sending manuals in the prompt is against the model's terms of use for enterprise customers"
      - "Retrieval is always more accurate than long context, whatever the size of the corpus"
    answer: 1
    explain: "The design rejects the alternative with numbers: even read from cache on Sonnet 5.5, one model's manual set costs about $0.04 a question in input, nearly twice the whole retrieval design. It stays a fallback if retrieval misses its target."
  - q: "What should the security section of a design doc say about a cloud platform's data retention terms you haven't checked yet?"
    options:
      - "Assume they match the customer's policy, since the major platforms have similar terms"
      - "Leave the topic out of the document so the CISO doesn't ask about it in the review"
      - "Quote the terms you remember from a previous deal on the same cloud platform"
      - "To be confirmed against current docs, listed as an open question with owner and date"
    answer: 3
    explain: "Unverified claims in the security section can cost you the CISO's trust. Separate known facts from items to confirm."
---

Ten questions on the architect's role, technical discovery and solution design docs. You need 8 correct to pass.
