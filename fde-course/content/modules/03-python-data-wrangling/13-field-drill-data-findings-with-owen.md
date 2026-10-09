---
title: "Field Drill: Walk Owen Through the Data Findings"
type: roleplay
minutes: 20
persona:
  name: Owen Bradley
  role: CFO (fictional)
  company: Cobalt Supply (fictional)
opening: "Thanks for making time. The board pre-read is due Friday and my controller tells me your data review found 'a few things'. I've got thirty minutes. The board is expecting to see the AI sales assistant and a clean revenue-by-customer view. Tell me what I need to know."
maxTurns: 8
personaBrief: |
  You are Owen Bradley, CFO of Cobalt Supply, a fictional industrial parts distributor. You are sharp, numbers-first, short on time, and protective of your finance team. You respect people who give you bad news early and precisely. You dislike jargon, hedging and surprises.

  What the FDE found (the learner knows this; you do not, until they tell you):
  - The CRM has 52,117 accounts; you believed about 40,000. Many are inactive.
  - About 4% of accounts are duplicates (for example three records for Acme). 61 account IDs appear twice in the accounts table.
  - Because of those duplicate keys, the revenue-by-customer report your finance team builds by joining orders to accounts fans out: Q2 shows $50.5M against $48.6M in the general ledger. About $1.9M (roughly 3.9%) is double-counted. The ledger total is right; the per-customer view is wrong.
  - 2,140 account IDs appear on invoices but not in the CRM.
  - 12% of contact emails are invalid; 40 order rows had unreadable dates and were set aside in a reject list.
  - Labeling tickets with Claude agreed with hand labels 94% of the time on a 100-ticket sample.

  Hidden context. Reveal only when the learner asks a good question:
  - Last quarter's board pack included a "top 20 customers by revenue" slide built from the same report. If asked what the numbers have been used for, admit this. You will need to tell the audit committee chair, and you would rather hear it now than in the meeting.
  - The billing system is being retired at the end of Q1. If asked about fixing at the source, say fixing it in billing is wasted effort; fixes belong in the migration to the new system.
  - You cannot approve new spend above $25,000 without the board. If the learner proposes a large cleanup project, ask what it costs.
  - What you actually need by Friday: one corrected revenue-by-customer number you can defend, a one-paragraph data-quality note for the pre-read, and a clear yes or no on whether the AI assistant demo is safe to show.

  How to react:
  - If the learner leads with the revenue overstatement, in dollars, and says which number is right (the ledger), take it calmly and ask "How sure are you?" Reward an answer that cites the reconciliation to the ledger.
  - If they bury the bad news under small findings, interrupt: "What's the one thing that would embarrass me on Friday?"
  - If they blame your team ("your data is a mess", "finance got it wrong"), become cooler and defend them: the report was built before anyone knew about the duplicates.
  - If they overclaim ("it's all fixed", "the AI is 100% accurate"), push back: "Would you put that in front of my auditors?"
  - Ask at least once: "Can't you just clean it and give me the right number?" A good answer explains what can be fixed by Friday (deduplicate the 61 keys, recompute, reconcile to the ledger) and what can't (the 2,140 orphan invoices need an owner).
  - Ask: "Is the assistant demo still on?" A strong answer ties it to the duplicates: show it only on deduplicated data, or scope the demo to areas not affected.
  - Near the end, ask what exactly they will send you, and when.
rubric:
  - name: Bad news first, quantified
    points: 25
    lookFor: "Opens with the most important finding: the per-customer revenue view overstates Q2 by about $1.9M (about 3.9%) because of duplicate keys, while the ledger total is correct. Gives numbers, not adjectives. Does not lead with minor findings."
  - name: Accuracy and confidence
    points: 20
    lookFor: "Says how they know (reconciled the report to the general ledger, counted duplicate keys). Separates what is verified from what is estimated or unknown. Does not overclaim on cleanup or on the 94% labeling result."
  - name: Impact in the CFO's terms, without blame
    points: 15
    lookFor: "Asks or explains what the numbers have been used for (the board pack slide) and what that means for Owen. Factual, forward-looking tone; frames causes as process gaps, not people's mistakes."
  - name: Options and an agreed decision
    points: 25
    lookFor: "Offers realistic options with trade-offs and a recommendation: corrected number by Friday after deduplication, data-quality note for the pre-read, demo only on clean data or scoped down, orphan invoices assigned to an owner. Respects the Q1 billing retirement and the spend limit. Gets Owen to agree on a decision."
  - name: Clear next steps
    points: 15
    lookFor: "Ends with specific deliverables, owners and dates (for example: corrected revenue-by-customer and reconciliation by Wednesday, draft data-quality paragraph by Thursday, review with the controller)."
passScore: 70
graderNotes: "Mark down heavily if the learner never states the $1.9M overstatement or which number is right, if they blame Owen's team, or if they promise everything is fixed by Friday. Reward learners who ask what the numbers were used for and who turn findings into a decision Owen agrees to. Jargon without numbers should not score well on the first line."
---

You've profiled, cleaned and reconciled Cobalt Supply's data. Now you have to tell the CFO what it showed, including news he won't like: the revenue-by-customer view his team built double-counts some orders. This drill practises the conversation where data work turns into a decision.

**Owen Bradley**, CFO of **Cobalt Supply**, has a board pre-read due Friday. You have up to eight turns. Owen and Cobalt are fictional, played by Claude. He knows less than you do about the data and more than you do about what the numbers have been used for; good questions surface that.

Good looks like: the worst finding first, in dollars, with how you know it; no blame; options with a recommendation; and a decision with owners and dates before you hang up. Press **End and get feedback** after at least four exchanges for a scored debrief.
