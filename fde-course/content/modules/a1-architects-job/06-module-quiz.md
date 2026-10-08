---
title: "Module A1 Quiz"
type: quiz
minutes: 10
questions:
  - q: "Which description best matches Anthropic's posting for its applied architect role (Solutions Architect, Applied AI)?"
    options:
      - "A post-sales support engineer who resolves customer tickets"
      - "A research engineer who trains custom models for each enterprise customer"
      - "A pre-sales architect and trusted technical advisor for large enterprises who fits Claude into their stack, builds evals and designs scalable architectures"
      - "An account executive who owns the deal and the revenue forecast"
    answer: 2
    explain: "The posting describes pre-sales architecture for large enterprises, working with Sales, Product and Engineering from discovery to deployment. The account executive owns the deal; the architect owns the technical win."
  - q: "How much reliable public information is there about the applied architect interview loop?"
    options:
      - "Very little: the formats beyond the official AI-use rules are anecdotal, so you confirm with your recruiter"
      - "A lot: the rounds are published on the careers page"
      - "Enough to be sure it's identical to the Applied AI Engineer loop"
      - "None at all, so there's nothing to prepare"
    answer: 0
    explain: "Reports of a technical design screen and a customer scenario exist but are sparse and anecdotal. Prepare for them, label them honestly, and ask your recruiter."
  - q: "A customer asks whether Claude can fully automate their claims payouts. What does the trusted-advisor answer sound like?"
    options:
      - "\"Yes, Claude can handle that end to end.\""
      - "\"Let's start a pilot and see.\""
      - "\"I'd rather not commit to anything until the contract is signed.\""
      - "\"Claude can do the triage and drafting well; I'd keep the payout decision with a person. Let's measure today's error rate first so we can compare.\""
    answer: 3
    explain: "Advisors make specific, honest claims, recommend human control where the risk calls for it, and anchor the conversation in a baseline."
  - q: "Which pair of stakeholders does the lesson say to meet early because they most often stop AI projects late?"
    options:
      - "The champion and the end users"
      - "The data owner and security"
      - "The economic buyer and procurement"
      - "The executive sponsor and the board"
    answer: 1
    explain: "Data access approvals and security reviews are common late blockers. Meeting those owners during discovery turns surprises into scheduled work."
  - q: "Which is a usable success metric for a proof of concept?"
    options:
      - "Improve the efficiency of the servicing team"
      - "Achieve 100% accuracy"
      - "Cut median acknowledgement time from 3.5 to 2 business days, measured from CRM timestamps, over a 6-week pilot"
      - "Make customers happier with AI"
    answer: 2
    explain: "A metric names the number, its baseline, the target and how it's measured. The others are wishes, and '100% accuracy' has no baseline or tolerance."
  - q: "Your model gets 90% of classifications right on a golden set. Why does the lesson say to also measure the human handlers on the same items?"
    options:
      - "To show the customer their staff are underperforming"
      - "Because 90% means nothing without a comparison: if experts agree with each other only 88% of the time, 90% may be excellent"
      - "Because evals require at least two graders by law"
      - "To replace the LLM judge"
    answer: 1
    explain: "Human agreement on the same items is the realistic ceiling and the fair comparison. Without it, any accuracy number is hard to interpret."
  - q: "During discovery you learn the customer's policy requires zero data retention from processors. Why is that an architecture question rather than a contract detail?"
    options:
      - "It isn't; legal handles it after the proof of concept"
      - "Because it only affects pricing"
      - "Because retention only matters for batch jobs"
      - "Because it can rule out options: for example, Claude Fable 5.1 requires 30-day retention and isn't available under zero data retention unless Anthropic expressly authorises it"
    answer: 3
    explain: "Retention, residency and the cloud the customer buys through can rule out models, platforms or features. Find them before you design, and confirm against current documentation."
  - q: "In a solution design doc, what is the main job of the non-goals section?"
    options:
      - "To stop scope from growing silently by stating what a reasonable stakeholder might otherwise assume is included"
      - "To list features that will come in phase 2"
      - "To show the customer what competitors can't do"
      - "To fill space so the doc looks thorough"
    answer: 0
    explain: "Good non-goals are things someone could reasonably expect. Writing them down prevents arguments later."
  - q: "A reviewer asks why you didn't put all 38,000 pages of manuals into the context window. Which answer reflects the worked example?"
    options:
      - "Long context never works for documents"
      - "It's against the model's terms of use"
      - "At roughly 19 million tokens the corpus doesn't fit a 1M-token context; one product's 400,000-token manual set would fit, but it costs several times more per question than retrieval, so it stays a fallback"
      - "Retrieval is always more accurate than long context"
    answer: 2
    explain: "The design rejects the alternative with numbers, not slogans, and keeps it as a fallback if retrieval misses its target."
  - q: "What should the security section of a design doc say about a cloud platform's data retention terms you haven't checked yet?"
    options:
      - "Assume they match the customer's policy"
      - "Leave the topic out so the CISO doesn't ask"
      - "Quote what you remember from a previous deal"
      - "State that they're to be confirmed against current documentation, and list it as an open question with an owner and a date"
    answer: 3
    explain: "Unverified claims in the security section can cost you the CISO's trust. Separate known facts from items to confirm."
---

Ten questions on the architect's role, technical discovery and solution design docs. You need 8 correct to pass.
