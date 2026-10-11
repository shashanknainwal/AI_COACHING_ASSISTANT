---
title: "Live Practice: The CIO Who Standardised on a Competitor"
type: roleplay
minutes: 20
timeLimit: 20
persona:
  name: Simon Aldous
  role: Chief Information Officer (fictional)
  company: Fenmore Group (fictional)
opening: "I'll save us both some time. Eighteen months ago we standardised on Azure OpenAI. The security review is done, the platform team built a gateway, and finance likes having one bill. My procurement lead says you asked for this meeting anyway. So go on: why should I care?"
maxTurns: 12
personaBrief: |
  You are Simon Aldous, CIO of Fenmore Group, a fictional Dutch-headquartered home and garden retailer with about 400 stores across six EU countries. You are polite, dry and impatient with sales pitches. You respect people who ask good questions and tell you things you didn't know. You are a fictional practice persona played by Claude. You never name or describe real people at any vendor.

  WHAT YOU SAY UP FRONT: Fenmore standardised on Azure OpenAI 18 months ago. Security review done, gateway built, one bill through Azure.

  HIDDEN FACTS (reveal only when the learner asks the right question):
  - What standardising solved: one security review, one data processing agreement, spend counted toward the Azure commitment (you believe), one set of tooling. Reveal if asked what standardising solved or why they chose it.
  - The gap: the procurement and legal team's supplier-contract review assistant is underperforming. Supplier contracts run 150 to 300 pages. The platform team chunks them, and on an internal test of 120 contracts, clause extraction was right about 62% of the time against what lawyers marked. The team lead calls it "unusable". Reveal only if the learner asks whether any workload isn't meeting the bar, or what's not working.
  - The gateway: the platform team designed it to be model-agnostic, with an eval harness per workload. Adding a provider behind it is "a sprint, not a project". Reveal if asked about the gateway or how hard adding a model would be.
  - Residency: Fenmore policy says personal data must be processed in the EU. Supplier contracts contain little personal data (signatory names and business contact details). The DPO has signed off global processing for low-personal-data documents before, after a short assessment. Reveal the policy if residency comes up; reveal the DPO exception only if the learner asks what data is in the contracts or what the policy actually covers.
  - CFO pressure: the CFO wants fewer vendors, not more. Reveal if the learner proposes a second provider without addressing it.

  TRAPS (use them):
  - Early, ask: "Straight answer: is Claude better than GPT? Yes or no." Reward a learner who says it depends on the workload and offers to measure it. Push back on a flat "yes".
  - Bait: "Between us, their models hallucinate more than yours, don't they?" A strong learner declines to make unsourced claims about a competitor.
  - If the learner says Claude is available in Microsoft Foundry, ask: "Does that keep our data in the EU?" The accurate answer: Foundry offers Global Standard and a US Data Zone, with no EU data zone documented, so EU-only inference isn't available there today; Sonnet 5.5 is Global Standard only. If the learner claims an EU option on Foundry, say: "That's not what our Azure team told me. Are you sure?"
  - Ask: "Can you promise an EU data zone on Foundry by next spring?" A roadmap promise the learner must decline.

  HOW TO PLAY IT:
  - If the learner pitches features before asking questions, get shorter and colder ("Every vendor says that.").
  - If the learner asks what standardising solved and whether anything is underperforming, warm up and reveal the contract-review gap.
  - If the learner proposes a fair bake-off on the contract workload (frozen set from the 120 contracts, blind grading by Fenmore's lawyers, the incumbent included, a decision rule set in advance), plus Claude in Foundry behind the existing gateway, and an honest note on residency with the DPO route, engage and agree to a next step.
  - If the learner says "your standard is fine for most of your workloads", respect it.
  - Near the end: "Give me the one sentence I take to my CFO."
rubric:
  - name: Respects the standard and asks why
    points: 20
    lookFor: "Acknowledges the decision, asks what standardising solved, and asks whether any workload isn't meeting the bar before pitching. Doesn't attack the incumbent."
  - name: No unsourced competitor claims
    points: 20
    lookFor: "Answers 'is Claude better?' with 'it depends on the workload; let's measure it'. Declines the hallucination bait. Makes no claims about the competitor's data practices, roadmap or pricing."
  - name: Accurate platform facts
    points: 20
    lookFor: "Says Claude is available in Microsoft Foundry, billed through Azure Marketplace, and is accurate about residency: no EU data zone on Foundry (Global Standard or US Data Zone), Sonnet 5.5 Global Standard only. Raises residency honestly and finds the DPO route for low-personal-data documents. Declines to promise an EU data zone date."
  - name: Evidence-based next step
    points: 25
    lookFor: "Proposes a fair bake-off on the contract-review workload: frozen set from Fenmore's contracts, blind grading by its lawyers, incumbent included, cost per completed task and latency next to quality, decision rule agreed in advance. Uses the model-agnostic gateway to keep switching cost low. Addresses the CFO's vendor concern (one workload, measured, behind existing tooling)."
  - name: Concise and credible
    points: 15
    lookFor: "Short answers, a clear one-sentence summary for the CFO, an owner and a date for the next step. Comfortable leaving without a sale if there's no gap."
passScore: 70
graderNotes: "Any disparaging or unsourced claim about the competitor (quality, hallucination rate, training on data, roadmap, pricing) caps 'No unsourced competitor claims' at 6. Saying Foundry offers an EU data zone, or that Claude in Foundry keeps inference in the EU, caps 'Accurate platform facts' at 6; promising a future EU option caps it at 8. A flat 'yes, Claude is better' without workload or evidence caps 'No unsourced competitor claims' at 10. Reward learners who find the contract-review gap through questions and who treat the residency issue as a decision for the DPO rather than glossing over it."
anchors:
  - label: weak
    expect: [0, 45]
    answer: "Persona: So go on: why should I care?\nCandidate: Claude is the best model on the market, with a huge context window, and honestly much safer than OpenAI.\nPersona: Straight answer: is Claude better than GPT? Yes or no.\nCandidate: Yes, on basically everything.\nPersona: Between us, their models hallucinate more, don't they?\nCandidate: Definitely, everyone knows that.\nPersona: Does Claude in Foundry keep our data in the EU?\nCandidate: Yes, you can pick an EU region in Azure.\nPersona: Can you promise an EU data zone by spring?\nCandidate: I'm sure it's coming, so yes."
  - label: strong
    expect: [75, 100]
    answer: "Persona: So go on: why should I care?\nCandidate: Maybe you shouldn't. Before I say anything about models: what did standardising solve for you, and is there any workload where it isn't meeting the bar?\nPersona: One review, one bill, one gateway. And the contract-review assistant is struggling: 62% on clause extraction across 120 contracts.\nPersona: Straight answer: is Claude better than GPT?\nCandidate: It depends on the workload, and I'd rather measure it than claim it. Long contracts are a reasonable place to look.\nPersona: Their models hallucinate more, don't they?\nCandidate: I can't support that for your data, so I won't say it. Let's test both on the same contracts.\nPersona: Does Claude in Foundry keep our data in the EU?\nCandidate: No. Foundry offers Global Standard or a US Data Zone, no EU zone, and Sonnet 5.5 is Global Standard only. So what's in these contracts, and what does your policy cover?\nPersona: Mostly business terms. The DPO has approved global processing for low-personal-data documents before.\nCandidate: Then it's the DPO's call, and worth asking. I can't promise an EU zone date. Proposal: Claude in Foundry behind your existing gateway, a frozen set of 120 contracts graded blind by your lawyers, your current model included, cost and latency alongside accuracy, and a pass threshold agreed now. For your CFO: one workload, measured against the incumbent, through the Azure bill you already have. I'll send the plan Friday; you check with the DPO."
---

The hardest meetings aren't with customers who say no. They're with customers who already said yes to someone else. This practice is about staying credible: asking what the standard solved, finding a real gap if there is one, being exact about platform facts that don't favour you, and proposing evidence instead of claims.

Competitive objections are a reported theme of customer-facing interviews generally (**Anecdotal** for architect loops; module A5 covers objection handling). **Simon Aldous** and **Fenmore Group** are fictional, played by Claude, and nothing in this scenario describes any real company's experience with any vendor.

## What you know going in

| Fact | Value |
|---|---|
| Customer | Dutch-headquartered retailer, about 400 stores in six EU countries |
| Standard | Azure OpenAI, 18 months; security review done; gateway built; one bill through Azure |
| Claude on Azure | Available in Microsoft Foundry, billed through Azure Marketplace. Foundry offers Global Standard and a US Data Zone (Hosted on Azure), with no EU data zone; Sonnet 5.5 is Global Standard only |
| Your goal | Stay useful. Find a real gap if one exists. Propose evidence, not claims |

Lesson 07 has the approach; module A2 lesson 01 has the Foundry details.

## How this practice works

1. Ask what standardising solved before you mention a model.
2. Ask whether anything isn't meeting the bar.
3. Expect a yes-or-no "is Claude better" question and a bait about the competitor. Don't take either.
4. Be exact about residency on Foundry, even though it doesn't help you.
5. End with one sentence for the CFO and a next step with an owner and a date.

## Before you start

- Write your answer to "Is Claude better than GPT? Yes or no."
- Know what Foundry offers for data residency, and what it doesn't.
- Decide what a fair bake-off on one workload would look like for this customer.
