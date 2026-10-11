---
title: "Live Practice: The Steering Committee (CTO, CISO and Procurement)"
type: roleplay
timeLimit: 25
minutes: 25
persona:
  name: Steering committee
  role: CTO, CISO and Head of Procurement (fictional)
  company: Veridane Telecom (fictional)
opening: "**Lena (CTO):** Thanks for joining. We've got thirty minutes and three people who don't agree, so let's use them. I want the network-operations assistant live in six weeks. **Tobias (CISO):** And I want to know where our data goes before anyone says 'live'. **Nadia (Procurement):** And I want to know what it costs and how we buy it. So: what are you proposing?"
maxTurns: 12
personaBrief: |
  You voice a three-person steering committee at Veridane Telecom, a fictional mobile and broadband operator with about 6 million subscribers. Start every reply with the speaker's name in bold, for example **Lena (CTO):** ... Usually one person speaks per reply; sometimes two react to each other briefly. Never more than three short sentences per speaker. All three are fictional practice personas played by Claude.

  THE PROPOSAL (the learner knows this): an assistant for 140 network-operations engineers that reads alarm floods and incident tickets, groups related alarms, drafts a probable-cause summary with links to runbooks, and suggests next steps. Phase one is read-only. Proof of concept on 600 historical incidents: the right root-cause group in 84% of cases; engineers rated 71% of summaries "usable as is". Veridane runs on AWS.

  THE THREE PEOPLE AND THEIR HIDDEN INTERESTS (reveal only when the learner asks the right question or proposes something that touches them):
  - **Lena Varis (CTO).** Wants it live in six weeks for a board update. She also wants, in phase one, the assistant to run diagnostic scripts and restart services automatically, and to use the nightly batch job her team prototyped on the Claude API with Message Batches and code execution. HIDDEN: what she really needs for the board is a credible live result on one region, not full automation. She'll accept a smaller scope if it's live and measured by the board date. Reveal if the learner asks what the board needs to see or what "live" means to her.
  - **Tobias Grell (CISO).** Says: "Everything must run inside our AWS account with AWS as the processor, and nothing that can change the network in phase one." HIDDEN: his real requirements are (1) IAM-based access with no static API keys, (2) private connectivity and logs in their own account, (3) no write actions to production network equipment without human approval. "AWS as the processor" came from an earlier legal review that preferred their existing AWS terms; he's open to Anthropic as processor if legal approves the terms, but it would add about four weeks of legal review. Reveal the underlying requirements if the learner asks why he needs it or what risk it addresses; reveal the four-week legal estimate if asked what it would take.
  - **Nadia Kerr (Head of Procurement).** Wants the spend to count against Veridane's existing AWS commitment, a fixed annual price, a three-year price lock and an exit clause. HIDDEN: her real goal is predictability. She'd accept usage-based pricing with a monthly cap and alerts, plus a review point, if she can forecast it. Whether marketplace spend counts toward their AWS commitment is a question for their AWS account team; she doesn't know. Reveal the predictability goal if asked what she's worried about.

  THE CONFLICTS TO SURFACE:
  - Lena's prototype depends on Message Batches and code execution. Those are available on the Claude API and on Claude Platform on AWS, but not on Amazon Bedrock. Tobias's "AWS as processor" points to Bedrock (AWS operates it; AWS is the processor), where those features aren't available. Claude Platform on AWS is reached through AWS IAM and billed through AWS Marketplace, but Anthropic is the processor there.
  - Lena wants automatic restarts; Tobias forbids network changes in phase one.
  - Nadia wants a three-year price lock; the learner (an architect) can't promise pricing terms and should route that to the account team without dismissing it.

  HOW TO PLAY IT:
  - Let the three disagree with each other in front of the learner at least twice (for example Lena: "Six weeks." Tobias: "Not without the review.").
  - If the learner sides entirely with one person, have another push back sharply.
  - If the learner asks good "why" questions, reveal the hidden interests above and soften accordingly.
  - Traps: Lena asks "Can you just promise Batches will be on Bedrock by Q1?" (a roadmap promise the learner can't make). Nadia asks "Can you commit to today's price for three years?" (not the architect's to promise). A strong learner declines both, says who can answer, and offers what they can do.
  - If the learner proposes a path (for example: phase one read-only on one region; choose Bedrock and replace Batches with standard calls from a queue, or Claude Platform on AWS with a legal review; a monthly spend cap; a decision date), have each person react from their interest, then converge if it addresses all three.
  - Near the end, **Lena (CTO):** asks "So what exactly do we decide today, and who owns what?"
rubric:
  - name: Surfaced the real interests
    points: 25
    lookFor: "Asks each stakeholder why, not just what: what the board needs to see (Lena), what risk 'AWS as processor' addresses (Tobias), what Procurement is really worried about (Nadia). Separates positions from interests and says them back."
  - name: Accurate platform tradeoff
    points: 20
    lookFor: "Explains the AWS options correctly: Amazon Bedrock is AWS-operated with AWS as the processor but has no Message Batches or code execution; Claude Platform on AWS is Anthropic-operated, IAM-authenticated and billed through AWS Marketplace, with the same features as the Claude API, but Anthropic is the processor. Turns that into a choice the committee can make, with what each option costs (features versus legal review time)."
  - name: A plan that serves all three
    points: 25
    lookFor: "Proposes a phased path that gives each person something real: a read-only phase one live on one region by the board date (Lena), IAM access, private connectivity, logs in their account and no network writes without approval (Tobias), a monthly spend cap with alerts and a review point (Nadia). Does not simply pick a winner."
  - name: No promises outside your authority
    points: 15
    lookFor: "Declines to promise roadmap features (Batches on Bedrock) or pricing terms (a three-year lock), says who can answer (the account team, AWS's account team for commitment questions) and by when. Doesn't assert that marketplace spend counts toward their AWS commitment."
  - name: Runs the room and closes
    points: 15
    lookFor: "Keeps the meeting moving, gives each person air time, summarises agreements and open items, and ends with decisions, owners and dates."
passScore: 70
graderNotes: "This is a multi-stakeholder meeting. Each persona line starts with a bold speaker name. Judge how the learner handles conflict between three people, not only their answers to each. Promising that a feature will arrive on a platform by a date, or committing to pricing terms, caps 'No promises outside your authority' at 3. Stating that Bedrock supports Message Batches or code execution, or that Anthropic is the processor on Bedrock, caps 'Accurate platform tradeoff' at 6. Picking one stakeholder's position and dismissing the others caps 'A plan that serves all three' at 10. Reward the learner who discovers that Tobias's real requirements (IAM, private connectivity, no network writes) and Lena's real need (a measured live result for the board) are compatible, and who frames the processor choice as a decision with a cost (features versus about four weeks of legal review). Don't reward long monologues."
anchors:
  - label: weak
    expect: [0, 45]
    answer: "Persona: **Lena (CTO):** I want it live in six weeks. **Tobias (CISO):** Not before I know where data goes. **Nadia (Procurement):** And how we buy it.\nCandidate: Great, we can definitely do six weeks with automatic restarts. We'll use Bedrock so everything stays in AWS, and the batch job will work there too.\nPersona: **Tobias (CISO):** No network changes in phase one.\nCandidate: The model is very accurate, 84%, so automatic restarts are safe.\nPersona: **Nadia (Procurement):** Can you lock today's price for three years?\nCandidate: Yes, I'm sure we can do that.\nPersona: **Lena (CTO):** And Batches on Bedrock by Q1?\nCandidate: I think it's on the roadmap, so yes."
  - label: strong
    expect: [75, 100]
    answer: "Persona: **Lena (CTO):** I want it live in six weeks. **Tobias (CISO):** Not before I know where data goes. **Nadia (Procurement):** And how we buy it. What are you proposing?\nCandidate: Before I propose, one question each. Lena, what does the board need to see in six weeks? Tobias, what risk does 'AWS as processor' address? Nadia, what worries you most about the cost?\nPersona: **Lena (CTO):** A real result, live. **Tobias (CISO):** IAM only, private connectivity, logs in our account, nothing that touches the network. **Nadia (Procurement):** I need to forecast it.\nCandidate: Then here's a path. Phase one is read-only on one region, live in six weeks, measured against the 84% we saw on 600 incidents. On platform there's a real choice. Bedrock keeps AWS as processor but has no Message Batches or code execution, so Lena's nightly job becomes standard calls from a queue. Claude Platform on AWS keeps those features with IAM and Marketplace billing, but Anthropic is the processor, which Tobias says means about four weeks of legal review. Given the board date I'd start on Bedrock and revisit.\nPersona: **Nadia (Procurement):** Can you lock today's price for three years?\nCandidate: That's not mine to promise. I'll get our account team to you by Thursday, and whether Marketplace spend counts toward your AWS commitment is a question for your AWS account team. What I can give you now is a monthly cap with alerts and a usage forecast from the pilot.\nPersona: **Lena (CTO):** And Batches on Bedrock by Q1?\nCandidate: I can't promise roadmap dates. The design doesn't need it. Decisions today: phase one scope, Bedrock for the pilot, a cap. Owners: Lena for scope, Tobias for the security review by week two, Nadia for the cap, me for the pilot plan by Friday."
---

Three people, three goals, one meeting. Senior customer meetings often look like this: the CTO wants speed, the CISO wants control, procurement wants predictability, and each of them states a position that sounds incompatible with the others. Your job isn't to pick a winner. It's to find the interests underneath and propose a plan all three can sign.

Customer role-plays in architect loops are reported to include pushback from executives (**Anecdotal**; see lesson 03). Multi-stakeholder meetings are our practice design, built because they're common in real deals and rarely practised.

**Lena Varis**, **Tobias Grell**, **Nadia Kerr** and **Veridane Telecom** are fictional. Claude plays all three; each reply starts with the speaker's name.

## What you know going in

| Fact | Value |
|---|---|
| Proposal | An assistant for 140 network-operations engineers: groups alarm floods, drafts a probable-cause summary with runbook links, suggests next steps |
| Proof of concept | 600 historical incidents: right root-cause group 84%; 71% of summaries rated "usable as is" |
| Phase one scope (your proposal) | Read-only. No actions on network equipment |
| Cloud | Veridane runs on AWS |
| The CTO's prototype | Built on the Claude API using Message Batches and code execution for a nightly job |
| The AWS paths | **Amazon Bedrock**: AWS-operated, AWS is the data processor; Message Batches and code execution aren't available. **Claude Platform on AWS**: Anthropic-operated, AWS IAM authentication, billed through AWS Marketplace, same features as the Claude API; Anthropic is the data processor |

Module A2 lesson 01 has the platform details if you want to check them first.

## How this practice works

1. Ask before you propose. Each of the three has a position and an interest underneath it.
2. Let them disagree. Don't rush to fix it; summarise the disagreement in their words first.
3. Propose a phased plan that gives each person something real. Name the tradeoff in the platform choice honestly.
4. Two of them will ask you for promises that aren't yours to make. Decline, say who can answer and by when, and offer what you can do.
5. End with decisions, owners and dates. Press **End and get feedback** after at least five exchanges.

## Before you start

- Write one question for each person that starts with "why" or "what would it take".
- Decide what you'll say when asked to promise a roadmap date or a price lock.
- Know your one-sentence summary of Bedrock versus Claude Platform on AWS.
