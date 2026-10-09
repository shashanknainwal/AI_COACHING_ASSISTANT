---
title: "Write It: The 'Fine-Tune on Our Manuals' Memo"
type: written
minutes: 40
sections:
  - key: recommendation
    label: 1. Recommendation
    prompt: "The approach you recommend and why, in terms the CTO cares about. Put the answer in the first two sentences."
    words: [100, 250]
  - key: alternatives
    label: 2. Alternatives considered
    prompt: "At least three alternatives, including the fine-tuning the CTO asked for, and why each lost (or where it might still fit later)."
    words: [120, 300]
  - key: cost
    label: 3. Cost estimate
    prompt: "Monthly model cost from explicit token assumptions and the prices given, plus the other costs of ownership. Show the arithmetic."
    words: [100, 280]
  - key: risks
    label: 4. Risks and mitigations
    prompt: "The risks that could sink this, how you'd detect each, and what you'd do about it."
    words: [100, 280]
  - key: next_steps
    label: 5. Pilot plan and decision criteria
    prompt: "What the 8-week pilot does, what it measures, and the numbers that decide go or no-go."
    words: [80, 220]
rubric:
  - name: Recommendation fits the facts
    points: 25
    lookFor: "Leads with a clear recommendation (typically retrieval over the manuals with citations, prompting and structured answers, access filtering by region and contract) and ties it to the specific facts: monthly revisions, exact part numbers, restricted manuals, scanned PDFs, the 8-week window. Redirects the fine-tuning request to the CTO's actual goal without dismissing him."
  - name: Alternatives weighed honestly
    points: 20
    lookFor: "At least three alternatives, including fine-tuning, a long cached prompt or whole-manual context, an agent, a vendor product or improving search alone. Gives a concrete reason each loses here, and says what evidence would bring fine-tuning back (a measured style or format gap a prompted baseline can't close, and confirmed availability for the chosen model and platform)."
  - name: Cost estimate with visible arithmetic
    points: 20
    lookFor: "Derives monthly volume (about 528,000 questions) and a per-question token assumption, applies the given prices with caching on the stable prefix, reaches a plausible monthly model cost, and adds the non-API costs (engineering, document conversion, operations, evaluation). Compares against the support-desk cost or value of technician time. Arithmetic is shown and roughly right."
  - name: Risks and mitigations
    points: 20
    lookFor: "Names the real risks: wrong part numbers or torque values, unsafe procedure advice, stale answers after revisions, leaking restricted manuals across regions or contracts, poor extraction from scanned PDFs and diagrams, low adoption on poor connectivity. Each has a detection method and a mitigation (citations, refusal when retrieval is weak, verbatim quoting of safety steps, re-indexing on revision, access filters, a human escalation path)."
  - name: Pilot plan an executive can sign
    points: 15
    lookFor: "An 8-week plan with a scoped pilot group and product lines, a golden question set built with senior technicians, and numeric go/no-go thresholds (for example answer accuracy, citation correctness, zero critical safety errors on the test set, share of questions answered without a desk call). Plain language, no hype."
passScore: 70
graderNotes: "Mark down memos that simply agree to fine-tune, that dismiss the CTO's request without explaining the gap in his terms, or that never produce a number. A memo that claims a specific fine-tuning offering exists for a given Claude model or platform as fact, without saying it must be confirmed, should lose points under Alternatives. Cost estimates need not match a single answer: 528,000 questions a month on Sonnet 5.5 with a cached prefix lands between a few thousand and a few tens of thousands of dollars a month (for example 8,000 cached tokens, 4,000 retrieved tokens and 500 output tokens per question is about $0.0138 per question, about $7,300 a month; heavier assumptions can reach $15,000 to $25,000). Accept any well-reasoned estimate with shown arithmetic; penalize estimates off by 10x or more without explanation. Safety handling must be explicit: a memo that lets the model paraphrase lockout or pressure-release procedures without verification cannot score above 10 on Risks."
---

Grace Liu here. I need a recommendation memo by Friday. This is a realistic pre-sales situation: the customer has already chosen a technique, and your job is to recommend what will actually work and bring them along.

## The situation

**Kestrel Fluid Systems** (fictional) makes industrial pumps and valves. Their CTO, Martin Oyelaran (also fictional), opened our call with: "We want to fine-tune a model on our service manuals so our field technicians can just ask it anything."

What discovery found:

- **People.** 1,200 field technicians. Each asks about 20 questions per working day, 22 working days a month.
- **Today.** Technicians search a PDF portal or call a support desk of 18 staff. About 30% of questions end in a desk call averaging 12 minutes. Desk staff cost about $48 an hour fully loaded.
- **Content.** About 3,400 manuals, roughly 40,000 pages, across 60 product lines. About 5% of pages are revised every month. Older manuals are scanned PDFs with exploded-view diagrams. Part numbers and torque values must be exact.
- **Safety.** Manuals include lockout and pressure-release procedures. A wrong step can injure someone.
- **Access.** Some manuals are restricted by region or by customer contract. A technician in one region must not see another region's restricted documents.
- **Field conditions.** Technicians use tablets. Connectivity at some plant sites is poor.
- **Stack and team.** Kestrel runs mostly on Microsoft Azure. Their platform team has three engineers. Claude is available through the Anthropic API and on Microsoft Foundry, among other platforms (module A2 covers that choice).
- **Timeline.** The CTO wants a pilot in front of technicians in 8 weeks.

Prices to use (per million tokens): Claude Sonnet 5.5 $2 input, $10 output, $0.10 cache read; Claude Opus 5.5 $4 input, $20 output, $0.20 cache read; Claude Haiku 5.5 $0.10 input, $0.50 output for prompts up to 100K tokens. Cache writes are about 1.25x the input price.

## The task

Write the memo in the five sections on the right. The reader is the CTO. He's technical, busy, and attached to his idea. Write so he can forward it to his CEO.

## What good looks like

- **Answer first.** Your recommendation is in the first two sentences.
- **His goal, in his words.** He wants technicians to get correct answers fast. Show how your approach gets there better than fine-tuning, using his facts: monthly revisions, restricted manuals, exact part numbers.
- **Keep the door open.** Say what evidence would make fine-tuning worth testing later. Don't claim a specific fine-tuning offering exists for a model or platform unless you've confirmed it; write "to be confirmed with the vendor" instead.
- **Numbers.** Volume, tokens per question, monthly cost, and what it replaces. Show the arithmetic.
- **Safety is not a footnote.** Say exactly how the system handles procedures where a wrong answer can hurt someone.

Lesson 1 (the decision ladder), lesson 3 (cost of ownership) and lesson 4 (unit economics and sensitivity) give you everything you need.

Submit for review when you're done. You'll get a score per rubric line, the strongest part of your memo, and the one change to make first. Write the draft yourself; use Claude to critique it afterwards if you like.
