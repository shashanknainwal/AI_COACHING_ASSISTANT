---
title: "Write It: An Architecture One-Pager for a CTO"
type: written
minutes: 35
sections:
  - key: recommendation
    label: Recommendation
    prompt: "One or two sentences: what you recommend and what you need. Then one line on the alternative you are not recommending and why."
    words: [30, 90]
  - key: architecture
    label: Architecture in 5 bullets
    prompt: "About five bullets the CTO could redraw on a whiteboard: components, data flow, where humans review, what you reuse from Ashgrove's stack."
    words: [70, 170]
  - key: cost
    label: Cost
    prompt: "Model cost per document and per month (show the math once), the one-time build cost, and the assumptions that would change the numbers most."
    words: [60, 160]
  - key: risks
    label: Risks and mitigations
    prompt: "Three or four real risks, each with a mitigation and an owner. Include at least one weakness the proof of concept revealed."
    words: [70, 170]
  - key: decision
    label: Decision needed
    prompt: "Exactly what you need, from whom, by when. Phrase it so the CTO can answer yes or no."
    words: [20, 80]
rubric:
  - name: Leads with a clear recommendation
    points: 20
    lookFor: "The first sentence states a specific recommendation (scope, model or approach, timeline or budget) and the ask. Names the rejected alternative (the self-hosted build) with a concrete reason, not a dismissal."
  - name: Architecture a CTO can act on
    points: 20
    lookFor: "Five or so bullets covering intake, extraction with schema validation, confidence-based routing to human review, write-back to the ERP, and logging or evals. Reuses the existing cloud account and review queue. No buzzwords, no unexplained components."
  - name: Correct, transparent numbers
    points: 25
    lookFor: "Model cost is computed from the given volumes and prices (about $180 input plus about $108 output, so roughly $290 a month, under 2 cents a document) with the math shown once. Separates model cost from build and run costs, states assumptions (including the effort setting or a thinking-token line), and says what would move the number. Quality claims cite the proof-of-concept figures and dataset size."
  - name: Honest risks with owners
    points: 20
    lookFor: "Includes the handwritten-certificate weakness (79% on 60 documents) and a concrete mitigation such as routing them to humans. Each risk has a mitigation and a named owner role. Does not hide or soften the weak result."
  - name: Answerable decision and economy
    points: 15
    lookFor: "Ends with a yes-or-no decision, owner and date. The whole thing fits on one page: short sentences, numbers instead of adjectives, no padding."
passScore: 70
graderNotes: "Recompute the cost: 18,000 x 5,000 = 90M input tokens x $2/M = $180; 18,000 x 600 = 10.8M output tokens x $10/M = $108; total about $288 a month, about $0.016 per document. Mark down wrong arithmetic, a single model-cost figure presented as the total cost, or invented numbers not in the brief (new accuracy figures, made-up certifications). Mark down any claim that accuracy is guaranteed, that humans can be removed entirely, or that the handwritten problem is solved. Mark down answers that bury the recommendation or end with 'let us know your thoughts'. Reward answers that name which AWS path (Claude Platform on AWS or Bedrock) and why, and that add a thinking-token sensitivity line (at 3x output, about $324 output and $504 a month in total). Reward answers that keep human review for low-confidence fields and handwritten documents, and that quantify the clerk-time saving as a range with its assumption."
---

Grace Liu drops a folder on your desk. "Ashgrove Industrial wants an answer by Friday. Their CTO, Marta Kovač, reads one page and decides. Write it."

Ashgrove Industrial is a fictional manufacturer. Marta is a fictional CTO. The numbers below are the engagement facts; use them, don't invent new ones.

## The situation

- **Problem.** Ashgrove receives about **18,000 supplier documents a month** (invoices and certificates of conformance, mostly PDFs). Six clerks key fields into the ERP by hand, about **9 minutes per document**. The backlog is 4 days, and late certificates have held up two production lines this year.
- **Proof of concept (last month).** You ran Claude Sonnet 5.5 with structured outputs against **500 real documents** with clerk-verified answers:
  - Field-level accuracy **97%**.
  - Documents fully correct with no human edit: **88%**.
  - The model's low-confidence flag caught **most** of the wrong fields, but not all: 1 in 5 errors was not flagged.
  - **Handwritten certificates were weak: 79% field accuracy on 60 documents.**
- **Token profile.** About **5,000 input tokens** and **600 output tokens** per document, measured in the proof of concept with `effort: "low"` set explicitly. Claude Sonnet 5.5 costs **$2 per million input tokens and $10 per million output tokens**. Thinking is billed as output, and Sonnet 5.5 defaults to `high` effort, so if production runs at the default, output could be two to three times higher.
- **Stack.** Ashgrove runs on AWS and already has a document-review queue that clerks use. Claude is available through the Anthropic API, Claude Platform on AWS (Anthropic-operated, billed through AWS Marketplace), Amazon Bedrock (AWS-operated), Google Vertex AI and Microsoft Foundry. The two AWS paths differ: the proof of concept used structured outputs, which Claude Platform on AWS supports and Bedrock's newer Messages-API endpoint lists as not supported.
- **Build estimate.** About **10 weeks** with two Ashgrove engineers and you: intake, extraction, validation against the ERP's supplier and PO tables, the review-queue integration, and an eval set that runs before every change. Your estimate for the engineering time is **about $120K**.
- **The alternative.** Marta's platform team has proposed self-hosting an open-weights model on their own GPUs. They haven't run it on the 500-document set yet, and the team has no one who has operated model serving in production.

## What to write

Five sections, one page in total. Use the structure from lesson 01:

1. **Recommendation.** One or two sentences. Then one line on why not the self-hosted build. Be fair to it: what would make it the right choice?
2. **Architecture in 5 bullets.** Marta should be able to redraw it on a whiteboard.
3. **Cost.** Show the model-cost math once. Separate it from the build cost. Say what moves the number.
4. **Risks and mitigations.** Include the handwritten-certificate result. Each risk gets a mitigation and an owner.
5. **Decision needed.** Yes or no, who, by when.

## Tips from Grace

- "Marta will check your arithmetic. Do it twice."
- "The clerk-time saving is the number the CEO cares about, but it depends on how many documents still need review. Give a range and say what it rests on."
- "Don't hide the handwriting result. If she finds it in the appendix after you left it out of the page, you've lost her."
- "No 'seamless', no 'cutting-edge', no 'enterprise-grade'. If a word could describe any product, cut it."

Submit when you're done. You'll get a score per rubric line and the one change to make first. Revise and resubmit as often as you like.
