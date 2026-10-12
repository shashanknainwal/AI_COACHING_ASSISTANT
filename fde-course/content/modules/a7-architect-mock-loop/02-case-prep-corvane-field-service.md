---
title: "Round 1a: Prepare the Case"
type: written
minutes: 60
sections:
  - key: situation
    label: 1. Situation
    prompt: "The business problem in Corvane's terms, with the two or three numbers that define it. No technology yet."
    words: [60, 180]
  - key: recommendation
    label: 2. Recommendation
    prompt: "What Corvane should do, in one or two sentences, then why. Include what you recommend against (for example the fine-tuning proposal) and why."
    words: [60, 200]
  - key: architecture
    label: 3. Architecture
    prompt: "The solution at the level an executive committee and a CIO can follow: users, flow, data sources, model choice, where it runs, what happens offline, and where humans stay in charge. Name the one design decision that matters most."
    words: [150, 400]
  - key: poc
    label: 4. Proof-of-concept plan
    prompt: "Scope, duration, who takes part, the success criteria agreed up front (with thresholds), how you measure them fairly, and what result would make you recommend stopping."
    words: [100, 300]
  - key: costs
    label: 5. Costs and value
    prompt: "Pilot cost, a rough run cost at full scale (show the token arithmetic), and the value at stake. State your assumptions."
    words: [80, 250]
  - key: risks
    label: 6. Risks and mitigations
    prompt: "The three to five risks that could sink this, each with a mitigation and an owner."
    words: [80, 250]
  - key: ask
    label: 7. The ask
    prompt: "Exactly what you want the executive committee to approve on the day: money, people, access, decisions, dates."
    words: [40, 150]
rubric:
  - name: Situation framed in business terms
    points: 10
    lookFor: "States the problem as Corvane's business problem (repeat visits, desk load, technician wait time) with the key numbers from the case, including the cost of repeat visits, before any mention of technology."
  - name: A clear, committed recommendation
    points: 15
    lookFor: "One recommendation stated plainly near the top, with reasons. Addresses the fine-tuning proposal directly with a specific reason (freshness of manuals, citation of approved procedures, time to value, data quality of notes) rather than ignoring it. Doesn't hedge across several options."
  - name: Architecture that fits the constraints
    points: 20
    lookFor: "A coherent design: retrieval over manuals and bulletins with citations to document and revision, use of work-order history as a secondary source, a plan for scanned PDFs and three languages, integration with the ERP and document system, a plan for poor connectivity, deployment that fits a mostly-AWS company (naming Claude Platform on AWS or Bedrock, with a reason), and lockout and isolation procedures shown verbatim from the approved manual rather than generated. Humans keep the decision on site."
  - name: Proof-of-concept plan with honest success criteria
    points: 20
    lookFor: "A bounded pilot (sites or regions, number of technicians, weeks) inside the 10-week window, success criteria with thresholds agreed before it starts (first-time fix rate, desk call volume or handle time, answer accuracy on a labelled eval set, technician adoption), a fair comparison (a control group or matched regions, not before-and-after alone), and a stated result that would mean stop."
  - name: Cost and value arithmetic
    points: 15
    lookFor: "Shows the cost of repeat visits (about $1.94M a month) and the value of a one-point gain in first-time fix rate (about $88K a month), a pilot budget that fits $180K, and a run-cost estimate from token counts and real prices. Recognises that model tokens are a small share of total cost next to integration, document preparation and people."
  - name: Risks with mitigations and owners
    points: 10
    lookFor: "Names the risks that matter here: wrong or paraphrased safety procedures, poor quality of scanned manuals and old ticket notes, low technician adoption, the works council and individual monitoring, connectivity. Each has a mitigation and an owner."
  - name: A concrete ask
    points: 10
    lookFor: "A specific request: budget amount, named people and their time, data and system access, a decision on the fine-tuning proposal, and the date of the go or no-go review."
passScore: 70
graderNotes: "Reference arithmetic (the candidate's numbers may differ if assumptions are stated): repeat visits = 26,000 x 22% = 5,720 a month; x $340 = about $1.94M a month, about $23.3M a year. One point of first-time fix = 260 fewer repeat visits = about $88K a month, about $1.06M a year. Reaching the sponsor's 82% target is 4 points, about $4.2M a year. A plausible run cost: about 4 questions per visit is about 104,000 questions a month; at 12,000 input tokens of retrieved context plus a cached 3,000-token system prompt and about 600 output tokens, Sonnet 5.5 is roughly $0.024 + $0.0003 + $0.006 = about $0.03 a question, about $3,150 a month; Opus 5.5 roughly double. If thinking at Sonnet 5.5's default high effort triples output to 1,800 tokens, it is about $0.042 a question, about $4,400 a month; give credit for a stated effort level or a thinking line. Any estimate in the low thousands to low tens of thousands of dollars a month with shown arithmetic is fine. Mark down hard: generating or paraphrasing lockout and isolation procedures (the HSE rule says verbatim from the approved manual), a recommendation that hedges between options, success criteria with no thresholds or decided after the pilot, before-and-after measurement with no control, ignoring offline sites, ignoring the works council, an ask with no amount or date, and invented product features. A cost section with no value side cannot score above 8 on that criterion. Reward a candidate who says what result would make them recommend stopping."
---

Round 1a of your mock loop. Set a 60-minute timer. Read the case, then write the narrative you'll present in Round 1b. Use only the facts on this page and a calculator. No AI help: this is your own first draft, as Anthropic's [candidate AI guidance](https://www.anthropic.com/candidate-ai-guidance) expects for anything you submit (**Official**).

Case presentations are reported for solutions-type roles at some labs (**Anecdotal**; see lesson 01). This case is original. Corvane and everyone in it are fictional.

## The brief from Grace

Grace Liu hands you a folder. "Corvane builds industrial pumps and services them in plants across Europe and North America. Their VP of Field Service wants to know whether Claude can help, and the executive committee meets in six weeks. Write me the story you'd tell them. Lead with the answer."

## The case: Corvane Pumps & Systems

The sponsor is **Ingrid Brandt, VP Global Field Service**. Her words: "I want first-time fix above 82% within a year. And I want my desk engineers working on hard problems, not reading manuals aloud to technicians."

| Fact | Number or detail |
|---|---|
| Field technicians | 1,200, in 11 countries |
| Service visits | 26,000 a month |
| First-time fix rate | 78%. The other 22% need a repeat visit. |
| Average cost of a repeat visit | $340 (technician time, travel, expedited parts) |
| Remote support desk | 38 senior engineers taking 16,000 technician calls a month, median 11 minutes per call. At peak times technicians wait a median 19 minutes on site for the desk. |
| Manuals and service bulletins | 52,000 pages in English, German and Spanish. About 30% are scanned PDFs from older product lines. Bulletins change weekly. |
| Work-order history | 1.1 million closed work orders since 2012, each with free-text technician notes. Quality varies a lot. |
| Connectivity | About 1 in 5 visits is in a plant room or basement with no reliable signal |
| Systems | An ERP holds work orders, parts and each pump's service history. A document management system holds manuals with revision numbers. Technicians use company tablets. Corvane runs mostly on AWS. |
| Pilot budget | Up to $180,000 of external spend for a 10-week pilot, plus two internal engineers and one desk engineer half-time |
| Decision date | Executive committee in 6 weeks |

Three more things came up in discovery:

1. **A competing proposal.** Corvane's data science team proposes fine-tuning an open-weights model on the work-order history. Their estimate: six months and three people.
2. **Safety.** Some pumps run in high-pressure and chemical plants. The Head of Health, Safety and Environment says: "Isolation and lockout steps must be shown exactly as written in the approved manual, with document and revision number. Nobody paraphrases a lockout procedure."
3. **People.** The German works council must be consulted before Corvane introduces any tool that could be used to monitor individual employees' performance. Technicians are proud of their expertise and skeptical of "a chatbot telling them how to fix a pump".

## What to write

Fill the seven sections on the right. Together they are the narrative you'll present: situation, recommendation, architecture, proof-of-concept plan, costs, risks, and the ask. Aim for something you could say in 15 minutes.

A strong case narrative:

- **Leads with the answer.** The executive committee should know your recommendation in the first minute.
- **Does the arithmetic.** What repeat visits cost now, what one point of first-time fix is worth, what the pilot costs, what running it would cost.
- **Respects the constraints.** Safety, connectivity, languages, the works council. These are where a real panel will push.
- **Says what would change your mind.** A pilot that can't fail isn't a test.

## Facts you may use

- Claude Opus 5.5 costs $4 per million input tokens and $20 per million output tokens. Claude Sonnet 5.5 costs $2 and $10. Claude Haiku 5.5 costs $0.10 and $0.50 for prompts up to 100K tokens.
- Prompt caching matches a prefix of tools, then system prompt, then messages. Cache reads cost $0.20 per million tokens on Opus 5.5 and $0.10 on Sonnet 5.5 (5% of base input). A cache write costs about 1.25 times normal input for the default five-minute lifetime.
- These models have a 1-million-token context window and accept PDF input.
- Claude is available through the Anthropic API, Claude Platform on AWS, Amazon Bedrock, Google Vertex AI and Microsoft Foundry. For an AWS-first company there are two AWS paths: Claude Platform on AWS is Anthropic-operated (same features as the Claude API, IAM authentication, billed through AWS Marketplace) and Amazon Bedrock is AWS-operated (AWS is the data processor, fewer features; Message Batches isn't available there). Feature availability differs by platform; saying you'd confirm a specific feature on the chosen platform is a good answer.
- All three models think by default, and thinking is billed as output. Sonnet 5.5 defaults to `high` effort, Opus 5.5 and Haiku 5.5 to `medium`. State the effort you'd set or add a thinking line to your estimate.
- A rough rule of thumb for this case: one page of a manual is about 500 tokens.

When you submit, Claude grades your narrative against the rubric below. Write the score down, then go straight to Round 1b with your answer open beside you.
