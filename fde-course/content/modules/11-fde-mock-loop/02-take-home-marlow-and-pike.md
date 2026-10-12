---
title: "Round 1: The Take-Home Customer Case"
type: written
minutes: 120
sections:
  - key: framing
    label: 1. Problem framing and discovery questions
    prompt: "Restate the problem in Marlow & Pike's business terms with the numbers that matter. Say what is ambiguous or untrustworthy in the ask and the data. List the five to eight discovery questions you'd ask first, and who you'd ask."
    words: [150, 400]
  - key: approach
    label: 2. Proposed approach and two-week scope
    prompt: "What you would build first and why that use case beats the others. What is in scope for the first two weeks and what is explicitly out. Where Claude fits, where plain code fits, and where a person stays in charge."
    words: [150, 400]
  - key: data
    label: 3. Data plan
    prompt: "Which data you need, how you'd get it, what you'd check in the first day, and how you'd handle the known problems (customer part numbers, units of measure, attachments, unreliable labels)."
    words: [100, 300]
  - key: evals
    label: 4. Eval plan
    prompt: "How you'd know it works before anyone relies on it: the test set and where it comes from, what 'correct' means, the metrics and the thresholds you'd agree with the customer, and how you'd grade."
    words: [100, 300]
  - key: risks
    label: 5. Risks
    prompt: "The three to five risks most likely to sink this engagement, each with a mitigation."
    words: [80, 250]
  - key: demo
    label: 6. The first demo
    prompt: "What you would show Ines at the end of week two, on what data, and the one number you'd want her to remember."
    words: [60, 200]
rubric:
  - name: Problem framing and discovery questions
    points: 20
    lookFor: "Frames the problem in business terms (response times, rep hours on order keying and status lookups, cost of entry errors) with numbers derived from the case. Calls out that 'use AI to fix the inbox' is not a requirement yet and that the category mix and error rate rest on weak evidence. Asks specific discovery questions of named people (Ines, reps, IT, the CEO), including what success means to the CEO and how errors are really counted."
  - name: Approach and a realistic two-week scope
    points: 20
    lookFor: "Picks one first use case and defends the choice with volume, value and risk (for example email orders into draft orders that a rep confirms, or drafted status replies from read-only ERP data). States what is out of scope (pricing and quotes, sending email without review, writing to the ERP directly). Uses plain code where it's enough (rules, lookups, the cross-reference table) and Claude where language or messy documents need it. A person approves before anything reaches the ERP or a customer."
  - name: Data plan
    points: 15
    lookFor: "Names the data and access needed (a sample of the email archive with attachments, ERP read API, SKU master, cross-reference table, return records). Plans a first-day profile. Handles customer part numbers via the cross-reference table first and model-assisted matching with confidence second, normalises units of measure, treats phone photos and spreadsheets separately from PDFs, and doesn't trust existing inbox labels as ground truth."
  - name: Eval plan
    points: 20
    lookFor: "A labelled test set from historical emails matched to the orders actually keyed in the ERP (a natural ground truth), stratified by attachment type, with a held-out portion. Line-level metrics (correct SKU and quantity and unit), an 'abstain and flag' rate, and a business threshold agreed with Ines before results are seen. Grading mostly by code against ERP records; human review of a sample; an LLM judge only with a check against humans. Compares against today's error rate fairly."
  - name: Risks and mitigations
    points: 10
    lookFor: "Covers the risks that matter here: wrong items shipped from a confident wrong match, low rep trust or adoption, data access delays from a small IT team, weak baselines making success impossible to prove, scope creep into quotes and pricing, customer data handling. Each has a concrete mitigation."
  - name: The first demo
    points: 15
    lookFor: "A demo on Marlow & Pike's own historical emails (not a toy example), showing the rep's review flow and the eval numbers, including where it fails. Ends with one memorable number tied to her goals (for example minutes saved per order on the test set, or line accuracy versus today) and a clear decision or next step for her."
passScore: 70
graderNotes: "Reference arithmetic (the candidate's numbers may differ if the assumptions are stated): order emails are about 11,200 x 38% = about 4,260 a month; at 9 minutes each that is about 640 rep hours a month. Status emails are about 11,200 x 27% = about 3,020 a month; at 4 minutes about 200 hours. Entry-error returns cost about 1,270 x $96 = about $122,000 a year, about $10,000 a month. 28 reps work roughly 4,500 hours a month, so order keying is about 14% of team time. Model cost is small: an order email at about 3,000 input and 500 output tokens on Sonnet 5.5 is about $0.006 + $0.005 = about $0.011, about $50 a month for every order email; any estimate in tens to low hundreds of dollars a month with shown arithmetic is fine. The ambiguity the case plants: the category mix comes from 400 emails labelled by one rep and never checked; the 3.1% error rate counts only returns coded as entry errors, so it misses errors caught before shipping and returns coded otherwise; inbox labels cover about 30% of emails and are inconsistent; the CEO's 'cut costs' and the team's 'faster responses' are different goals. Mark down hard: building before asking; a two-week scope that tries to cover every email type; anything that sends email to customers or writes orders to the ERP without a person approving; pricing or quotes in the first two weeks (contract pricing for 1,900 accounts); an eval plan with no ground truth source or no thresholds agreed in advance; promising headcount cuts; invented product features or made-up claims about data handling. Reward a candidate who uses historical emails paired with keyed ERP orders as ground truth, who plans for 'not sure, send to a rep' as a first-class outcome, and who says what result would make them recommend stopping or changing course."
---

Round 1 of your mock loop. Set a two-hour timer. Read the case, then write your take-home answer in the six sections on the right. Use only the facts on this page and a calculator. No AI help: this is your own first draft, as Anthropic's [candidate AI guidance](https://www.anthropic.com/candidate-ai-guidance) expects for take-homes unless you're told otherwise (**Official**).

Take-homes with a review call are reported in OpenAI's FDE process, and one candidate describes a week-long case study followed by a panel walkthrough (**Reported** and **Anecdotal**; see lesson 01). This case is original. Marlow & Pike Distribution and everyone in it are fictional. You'll meet Ines again in Round 3, and she will have read what you write here.

## The brief from Theo

Theo Brandt sends you a forwarded email and a data sheet. "This is the kind of thing an FDE gets on day one. A customer with a vague ask and data nobody has looked at closely. Tell me what you'd do in the first two weeks, and what you'd show them at the end of it. I care more about your judgement than your architecture diagram."

The forwarded email is from Marlow & Pike's CEO to **Ines Carvalho, Director of Operations**: "Our customer service team is drowning in email. Let's use Claude to fix it. I want to see something real by the end of the quarter, and I want our service costs down." Ines added one line: "Can you help us figure out what 'fix it' should mean?"

## The company

Marlow & Pike Distribution sells electrical, plumbing and HVAC parts to trade contractors from 14 branches. About 620 employees and 4,800 active trade accounts.

| Fact | Number or detail |
|---|---|
| Inbound customer email | About 11,200 a month to two shared inboxes (orders@ and help@), average of the last three months |
| Email mix | From 400 emails one rep labelled last month: order requests 38%, order status questions 27%, quote and pricing requests 15%, returns and credits 8%, other 12%. Nobody checked the labels. |
| Customer service team | 28 reps at two sites |
| Handling time | Median 9 minutes to key an email order into the ERP. Median 4 minutes to answer a status question (look up the ERP, then the carrier's site). |
| Response time | Median first response 5.5 business hours. 22% of emails wait more than one business day. |
| Order-entry errors | Ines's team estimates 3.1% of email orders contain a wrong item or quantity. Source: last year's returns coded "entry error": 1,270 returns, average cost $96 each (freight, restocking, re-picking). |
| Pricing | 1,900 accounts have contract price lists. Quotes over $5,000 need a manager's approval. |

## The data

| Source | What it looks like |
|---|---|
| Email archive | 26 months, about 280,000 emails with attachments, in Microsoft 365. Inbox labels exist on about 30% of emails and are applied inconsistently. |
| Order attachments | Of order emails: 52% have a PDF purchase order, 21% a spreadsheet, 9% a phone photo of a handwritten list, 18% put the order in the email body. |
| ERP | On-premises, 15 years old. 58,000 active SKUs. Short descriptions are abbreviated (`CU PIPE L 1/2X10`) and 14% have no long description. The same item may be sold by the each, by a box of 25, or by the foot. |
| Customer part numbers | Customers often write their own part numbers or a manufacturer's number. A cross-reference table maps 61% of the distinct customer part numbers seen last year. |
| Order status | The ERP holds order and shipment status. A carrier tracking number is recorded for about 80% of shipments. |
| Integration | A three-person IT team. The ERP has a read-only REST API for orders, inventory and shipments. New orders get in by manual keying or a nightly CSV import. |

## What a strong answer does

- **Questions the ask before answering it.** "Fix the inbox" and "cut service costs" are not the same goal, and the numbers you were given have weak spots.
- **Picks one thing for two weeks.** Five email types, one engagement, ten working days.
- **Plans how to prove it.** The archive and the ERP together hold a lot of ground truth if you think about it.
- **Keeps a person in charge** of anything that reaches a customer or the ERP.
- **Ends with a demo Ines could show her CEO.**

## Facts you may use

- Claude Opus 5.5 costs $4 per million input tokens and $20 per million output tokens. Claude Sonnet 5.5 costs $2 and $10. Claude Haiku 5.5 costs $0.10 and $0.50 for prompts up to 100K tokens. Prices from Anthropic's [pricing page](https://platform.claude.com/docs/en/about-claude/pricing), checked 2026-10-08.
- These models accept images and PDFs as input, and structured outputs can constrain a reply to a JSON schema.
- Claude is available through the Anthropic API, Claude Platform on AWS (operated by Anthropic, with AWS IAM and AWS Marketplace billing), Amazon Bedrock, Google Vertex AI and Microsoft Foundry. Features differ: for example, Message Batches is not on Bedrock, Vertex or Foundry, and the MCP connector and Agent Skills are not on Bedrock or Vertex. If the customer's data rules point to one platform, saying you'd confirm the features you need on it is a good answer.
- A rough rule of thumb for this case: an order email with its attachment is about 3,000 input tokens, and an extracted order is about 500 output tokens.

When you submit, Claude grades your answer against the rubric below. Write the score down, keep your answer open, and move on to Round 2.
