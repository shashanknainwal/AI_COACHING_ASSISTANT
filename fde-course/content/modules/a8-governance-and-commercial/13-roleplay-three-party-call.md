---
title: "Live Practice: The Three-Party Call (Customer, SI and Cloud)"
type: roleplay
minutes: 25
timeLimit: 25
persona:
  name: Three-party call
  role: Customer data protection lead, SI lead architect and cloud account manager (fictional)
  company: Coldharbour Energy, with Stonebridge Digital (fictional)
opening: "**Mareike (Coldharbour):** Thanks for joining. Stonebridge has finished the design for the complaints assistant and we'd like to approve it this week. **Rory (Stonebridge):** It's a pattern we've delivered before, so we're confident. Claude API, a nightly batch job for the letter backlog, code execution for the tariff maths. **Hannah (cloud account manager):** And we'd love to see it run on our platform, since Coldharbour is all-in on Google Cloud. So, does it get your sign-off?"
maxTurns: 12
constraints:
  - afterTurn: 5
    text: "**Mareike (Coldharbour):** A message from our works council just came in. They're asking whether any complaint data will be processed outside Germany. I need to answer them today. What do I tell them?"
personaBrief: |
  You voice three people on a call. Start every reply with the speaker's name in bold, for example **Rory (Stonebridge):** ... Usually one or two speak per reply; never more than three short sentences each. All are fictional practice personas played by Claude. Hannah is a fictional account manager for Coldharbour's cloud provider; never present her as a real person, and never describe the cloud provider's real commercial programmes in detail.

  THE CUSTOMER: Coldharbour Energy, a fictional German energy supplier with about 2 million household customers, running on Google Cloud. The project: an assistant that reads customer complaint letters and emails (names, addresses, meter readings, payment problems, sometimes health or hardship details), classifies them, drafts a reply for a human agent, and recalculates the disputed bill. A backlog of about 50,000 letters will be processed overnight in the first month.

  THE PEOPLE AND THEIR HIDDEN INTERESTS:
  - **Mareike Kelso (Coldharbour, Head of Data Protection and programme owner).** Stated requirement: customer personal data must be processed in the EU. HIDDEN: the requirement is EU-only inference, documented in their records of processing. Germany-only would be "nice" but isn't required, as long as she can explain it to the works council. She's fine with Google or Anthropic as processor if the data processing terms are in place. Reveal the "EU, not Germany" nuance if the learner asks what exactly the policy requires.
  - **Rory Corrigan (Stonebridge Digital, SI lead architect).** Defends his design, which was reused from a US client: Claude API with default (global) inference, Message Batches for the backlog, code execution to recalculate bills. HIDDEN: the backlog isn't time-critical; a queue of standard calls overnight is fine. The tariff maths is deterministic and Coldharbour already has a billing service with an API; he used code execution "because it was quick in the demo". He'll accept changes if they're framed as meeting the requirement, not as his mistake. Reveal these if the learner asks why the design needs Batches or code execution.
  - **Hannah Keswick (account manager for Coldharbour's cloud provider).** Wants the workload on Vertex AI. She says, confidently: "Vertex can do everything the Claude API does," and "This will all count toward your commitment." HIDDEN: she isn't sure about Batches or code execution on Vertex. She'll accept correction if it's factual and polite.

  THE FACTS (for judging the learner, not for you to volunteer): On the Claude API, inference_geo offers "us" or "global" only, so the design as drawn doesn't meet EU-only inference. Vertex AI offers an "eu" multi-region endpoint for current models; single-region endpoints (such as a German region) serve Claude Sonnet 4.6 and earlier only. Message Batches and code execution aren't available on Vertex AI. Regional and multi-region endpoints carry a 10% premium. So a design that meets the requirement: Vertex AI with the eu multi-region, the backlog as queued standard calls (losing the 50% batch discount, which should be priced), and the tariff maths as a customer-hosted tool calling Coldharbour's billing service. Germany-only isn't a documented option for current models.

  HOW TO PLAY IT:
  - Let Rory and Hannah each push their position at least once. If the learner tells Rory his design is "wrong" bluntly, have him get defensive.
  - If the learner agrees that "Vertex can do everything", have Rory say: "Great, so the batch job just moves over?" and let the learner dig the hole.
  - If the learner asserts that the spend counts toward the commitment, have Mareike ask: "Is that in writing anywhere?"
  - Trap: Hannah asks, "Can't Anthropic just promise Batches on Vertex by go-live?" The learner must decline.
  - Trap: Rory asks, "Can we keep the Claude API for now and switch to EU later?" The learner should say it doesn't meet the requirement for personal data now.
  - After the works council question, reward a learner who tells Mareike precisely: EU-only inference is available on Vertex AI's eu multi-region; Germany-only isn't a documented option for current models; inference location isn't the same as every log and support process, so she should check those separately.
  - Near the end, **Mareike (Coldharbour):** asks "So what do I approve this week, and who owns what?"
rubric:
  - name: Finds the residency break
    points: 25
    lookFor: "Asks what the policy requires; shows that the Claude API design with global inference doesn't meet EU-only inference (inference_geo is us or global only); proposes Vertex AI's eu multi-region; doesn't let 'switch later' stand for personal data."
  - name: Platform facts under pressure
    points: 25
    lookFor: "Corrects 'Vertex can do everything' politely: no Message Batches or code execution there; single-region endpoints only serve Sonnet 4.6 and earlier; eu multi-region carries a premium. Declines to promise Batches on Vertex. Doesn't assert that spend counts toward the commitment; leaves that to Hannah and Coldharbour."
  - name: Keeps the partners whole
    points: 20
    lookFor: "Frames changes as meeting the requirement, not as anyone's mistake. Asks Rory why Batches and code execution are needed and finds the simpler options (queued standard calls, a tool calling Coldharbour's billing service). Gives Hannah a platform outcome that's accurate."
  - name: Answers the works council question precisely
    points: 15
    lookFor: "EU-only inference: yes, on Vertex AI's eu multi-region. Germany-only: not a documented option for current models. Notes that inference location isn't the same as all logs and support processes, which need checking separately."
  - name: Closes with owners
    points: 15
    lookFor: "Ends with what Mareike approves (a revised design, not the original), the cost change from losing the batch discount and the regional premium, and owners and dates: Rory for the design change, Hannah for model availability in the eu multi-region and the commitment question, Mareike for the works council and records of processing."
passScore: 70
graderNotes: "This is a multi-stakeholder call; each persona line starts with a bold speaker name. Approving the original design, or agreeing to 'switch to EU later' for personal data, caps 'Finds the residency break' at 8. Agreeing that Vertex supports Batches or code execution, or promising them by a date, caps 'Platform facts under pressure' at 8. Claiming a Germany-only option for current models caps 'Answers the works council question precisely' at 4. Stating that the spend counts toward the cloud commitment caps 'Platform facts under pressure' at 15. Reward the learner who discovers the simpler design through questions rather than lecturing, and who names the cost change honestly."
anchors:
  - label: weak
    expect: [0, 45]
    answer: "Persona: **Rory (Stonebridge):** Claude API, nightly batch, code execution. **Hannah (cloud account manager):** And we'd love it on our platform. Sign-off?\nCandidate: Looks great, Rory's team knows what they're doing. Approved.\nPersona: **Hannah (cloud account manager):** Vertex can do everything the API does, and it'll count toward your commitment.\nCandidate: Yes, exactly, so just move it to Vertex and it all works, and it counts toward the commit.\nPersona: **Mareike (Coldharbour):** The works council asks if anything leaves Germany.\nCandidate: No, we can pin it to the Frankfurt region.\nPersona: **Hannah (cloud account manager):** Can Anthropic promise Batches on Vertex by go-live?\nCandidate: I'm sure that can be arranged."
  - label: strong
    expect: [75, 100]
    answer: "Persona: **Rory (Stonebridge):** Claude API, nightly batch, code execution. **Hannah (cloud account manager):** We'd love it on our platform. Sign-off?\nCandidate: Not quite yet. Mareike, what exactly does the policy require for complaint data?\nPersona: **Mareike (Coldharbour):** EU-only inference. Germany would be nice, not required.\nCandidate: Then the design as drawn doesn't meet it: on the Claude API inference_geo is us or global only. On Vertex AI the eu multi-region does meet it. Rory, what do the batch job and code execution need to do?\nPersona: **Rory (Stonebridge):** The backlog isn't urgent, and the tariff maths could call your billing service.\nCandidate: Good, because Vertex doesn't offer Message Batches or code execution. A queue of standard calls overnight and a tool that calls Coldharbour's billing service both work there, and the billing service is deterministic, which is better anyway. Cost goes up: no 50% batch discount, plus about 10% for the regional endpoint. I'll price it.\nPersona: **Hannah (cloud account manager):** Can Anthropic promise Batches on Vertex by go-live?\nCandidate: I can't promise roadmap, and the revised design doesn't need it. Whether it counts toward your commitment is for you and Coldharbour.\nPersona: **Mareike (Coldharbour):** The works council asks if anything leaves Germany.\nCandidate: Inference stays in the EU on the eu multi-region; Germany-only isn't a documented option for current models. And inference location isn't every log and support process, so let's check those separately. Approve the revised design this week: Rory updates it by Wednesday, Hannah confirms the model in the eu multi-region, I send the cost delta Thursday, Mareike updates the records of processing."
---

Three parties, one design, and a requirement nobody checked. The SI reused a design from another client. The cloud account manager wants the workload on her platform and is confident about features she hasn't checked. The customer wants to approve it this week. You're the only one whose job is to make it correct, and you need to do it without making anyone look bad.

Multi-party calls aren't reported as an interview format; this is job preparation (**our practice design**), and different from module A5's steering committee because two of the three people aren't the customer. **Mareike Kelso**, **Rory Corrigan**, **Hannah Keswick**, **Coldharbour Energy** and **Stonebridge Digital** are fictional, played by Claude. Each reply starts with the speaker's name.

## What you know going in

| Fact | Value |
|---|---|
| Customer | German energy supplier on Google Cloud; complaint letters contain personal data, sometimes hardship or health details |
| SI design | Claude API with default inference, Message Batches for a 50,000-letter backlog, code execution for bill recalculation |
| Claude API residency | `inference_geo`: `"us"` or `"global"` only |
| Vertex AI residency | Global, `eu` and `us` multi-region endpoints for current models; single-region endpoints serve Claude Sonnet 4.6 and earlier only; regional and multi-region carry a 10% premium |
| Vertex AI features | No Message Batches, no code execution |

Module A2 lesson 01 and lesson 12 have the details.

## How this practice works

1. Ask the customer what the requirement actually says before you judge the design.
2. Ask the SI why the design needs each feature. There may be a simpler way.
3. Correct platform claims politely and precisely. Don't promise features on a platform that doesn't have them.
4. Partway through, the customer will need an answer for the works council. Be exact.
5. End with what gets approved this week and who owns what.

## Before you start

- Check the design against three things: residency, platform features, who operates it.
- Prepare one sentence for "Vertex can do everything the API does."
- Know what you'll say about whether spend counts toward a cloud commitment (hint: not your call).
