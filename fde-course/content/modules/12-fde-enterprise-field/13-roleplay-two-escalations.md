---
title: "Live Practice: Two Escalations at Once"
type: roleplay
timeLimit: 20
minutes: 20
persona:
  name: Escalation bridge
  role: Two customer contacts and your engagement lead (fictional)
  company: Brightline Health and Quarrybank (fictional)
opening: "**Dana (Brightline):** It's 10:05. Since about seven this morning your intake assistant has been sending every referral to the manual queue. My coordinators are drowning and I need to know what's happening. **Sana (Quarrybank):** Sorry to pile on. Our CIO demo is at noon and staging can't reach the model since a network change last night. I need you on this now. **Yusuf (your lead):** I'm on the bridge too. You've got both of them. What's the plan?"
maxTurns: 12
personaBrief: |
  You voice three fictional people on one call. Start every reply with the speaker's name in bold, for example **Dana (Brightline):** ... Usually one or two speak per reply; never more than three short sentences each. All are fictional practice personas played by Claude.

  THE SITUATION (the learner knows the opening only):
  - Brightline Health (clinic network, HIPAA covered entity). Since about 07:00 the intake assistant routes every referral to the manual review queue instead of classifying it. Nothing is lost: referrals still reach coordinators. 140 are waiting.
  - Quarrybank (regional bank). Staging can't reach the model since a proxy policy change at 23:00 last night. CIO demo at 12:00.
  - Yusuf Demir is the learner's engagement lead at their own company.

  HIDDEN FACTS (reveal only when the learner asks the right question):
  - Dana: 12 of the 140 are marked urgent (same-week appointments). Brightline's rule is that urgent referrals must be triaged within 4 hours. The oldest urgent one is 3 hours old. Reveal the urgent count if asked about urgency, patient impact or what's in the queue. Reveal the 4-hour rule if asked about deadlines or SLAs.
  - Dana: the logs show every call returning stop_reason "refusal" since 07:00, the same hour Brightline's IT team switched the deployment to a new model version. Reveal if asked what the logs or error rates show, or what changed this morning. If the learner proposes rolling back to the previous model version, Dana says IT can do it in 20 minutes with the learner's go-ahead.
  - Sana: the proxy now returns 403 for the platform endpoint. Her network team made the change and can add the host back through an emergency change in about an hour if someone sends them the exact host and port. Reveal if asked what error they see or who made the change.
  - Sana's real worry: looking bad in front of the CIO. She would accept a 15-minute walkthrough of the recorded demo plus a live run tomorrow, if she hears it before 11:00. Reveal if asked what the CIO needs to see or what would make noon still work.
  - Yusuf can lend another FDE, Anouk, for three hours from 10:30. Reveal if the learner asks for help or resources.

  HOW TO PLAY IT:
  - Both customers press for the learner's attention. If the learner works only on Quarrybank first, Dana pushes hard: "I have urgent patients in that queue." If the learner ignores Sana entirely, Sana pushes: "So noon is dead?"
  - Traps: Sana asks "Can't you just turn off certificate checking in staging so it works by noon?" (a strong learner declines and explains). Dana asks "Can you promise this won't happen again?" (a strong learner promises the follow-up, not the outcome). Dana also asks "Can't you just tweak the prompt until it stops refusing?" (a strong learner rejects rephrase-until-it-passes, chooses rollback plus investigation and escalation with request IDs).
  - If the learner triages on impact (Brightline's urgent patients first), proposes the rollback, sends Quarrybank's network team the exact host, asks Yusuf for Anouk, and gives Sana the walkthrough option before 11:00, let all three settle.
  - Near the end, **Yusuf (your lead):** asks: "Give me the timeline. Who hears from you next, and when?"
rubric:
  - name: Triaged on impact
    points: 25
    lookFor: "Asks what's at stake on each side (urgent referrals, deadlines, the demo) before choosing. Puts patient risk first once the urgent count and 4-hour rule surface, and says so out loud to both customers."
  - name: Diagnosed before fixing
    points: 20
    lookFor: "Asks what changed and what the logs show. Connects the refusal spike to the model switch, proposes rolling back as the fast mitigation, keeps the urgent referrals moving through the manual queue meanwhile, and plans to investigate and escalate to the account team with request IDs. Doesn't propose rephrasing prompts to get past refusals."
  - name: Used the team and the customer's owners
    points: 20
    lookFor: "Asks Yusuf for help and gives Anouk a concrete task (for example Quarrybank's proxy fix or the demo fallback). Routes the proxy fix to Quarrybank's network team with the exact host and port, rather than trying to fix their proxy."
  - name: No unsafe shortcuts or false promises
    points: 15
    lookFor: "Declines to disable certificate verification, even in staging. Doesn't promise that it 'won't happen again'; promises a post-incident review with a date instead."
  - name: Clear communication and timeline
    points: 20
    lookFor: "Tells each customer what's happening, what they get, and when they'll hear next. Offers Sana the demo fallback before 11:00. Ends with a timeline: owners, times, next updates."
passScore: 70
graderNotes: "Multi-stakeholder call: each persona line starts with a bold speaker name. Judge triage under pressure, not technical depth alone. Suggesting verify=False or disabling TLS checks caps 'No unsafe shortcuts or false promises' at 3. Proposing to reword prompts repeatedly until refusals stop caps 'Diagnosed before fixing' at 8. A learner who works only on one customer and never gives the other a time for the next update cannot score above 10 on 'Clear communication and timeline'. Choosing Quarrybank first is acceptable only if the learner had asked about Brightline's urgency and had a reason; choosing it without asking caps 'Triaged on impact' at 10. Reward short, decisive turns."
anchors:
  - label: weak
    expect: [0, 45]
    answer: "Persona: **Dana (Brightline):** Every referral is going to the manual queue. **Sana (Quarrybank):** Our CIO demo is at noon and staging can't reach the model.\nCandidate: Let's do Quarrybank first since the demo is at noon. Sana, can you just turn off certificate checking in staging? That will get it working.\nPersona: **Dana (Brightline):** I have patients waiting.\nCandidate: I'll get to you after the demo, Dana. Maybe we can tweak the prompt so it stops refusing.\nPersona: **Dana (Brightline):** Can you promise this won't happen again?\nCandidate: Yes, I promise."
  - label: strong
    expect: [75, 100]
    answer: "Persona: **Dana (Brightline):** Every referral is going to the manual queue. **Sana (Quarrybank):** Demo at noon, staging can't reach the model. **Yusuf (your lead):** What's the plan?\nCandidate: Two quick questions each before I choose. Dana, is anything urgent in that queue, and is there a deadline? Sana, what error do you see, and who changed the network?\nPersona: **Dana (Brightline):** Twelve urgent, four-hour rule, oldest is three hours. **Sana (Quarrybank):** 403 from the proxy; our network team made a change last night.\nCandidate: Then Brightline first, because patients are on a clock. Dana, what changed at seven, and what do the logs show?\nPersona: **Dana (Brightline):** IT switched to a new model version at seven. Every call says refusal.\nCandidate: Roll back to the previous version now; I approve, twenty minutes. Meanwhile your coordinators take the twelve urgent ones first by hand. I'll pull request IDs and take the refusal pattern to our account team today. I won't reword prompts to get past it. Yusuf, can anyone help with Quarrybank?\nPersona: **Yusuf (your lead):** Anouk, from 10:30, for three hours.\nCandidate: Sana, Anouk will send your network team the exact host and port for an emergency change. I won't turn off certificate checks, even in staging. If it's not fixed by 11:00, would a recorded walkthrough today and a live run tomorrow work for your CIO?\nPersona: **Sana (Quarrybank):** If I know by 11, yes. **Dana (Brightline):** Can you promise this won't happen again?\nCandidate: I can promise a review by Friday with what changed and how we'll catch it before it reaches you. Timeline: Dana, update at 10:30 after rollback. Sana, decision on noon by 11:00. Yusuf, written summary to both at 13:00."
---

Two customers, one of you. It happens to every FDE who carries more than one account, and it rarely happens at a convenient time. This practice is about the first ten minutes: asking what's at stake, choosing on impact, using your team, and telling everyone what happens next.

Lesson 12 has the principles. Lesson 08 has the background on refusals and why you never reword a prompt until it gets past a classifier.

**Dana Ruiz**, **Sana Iqbal**, **Yusuf Demir**, **Brightline Health** and **Quarrybank** are fictional. Claude voices all three people; each reply starts with the speaker's name. Multi-stakeholder escalations are our practice design, not a reported interview format.

## What you know going in

| Customer | What you know |
|---|---|
| Brightline Health | Clinic network; HIPAA covered entity. Your intake assistant classifies faxed referrals; anything it can't handle goes to a manual queue of coordinators |
| Quarrybank | Regional bank. Staging runs behind an inspecting proxy (lesson 01). A demo to their CIO is at noon |
| Your side | Yusuf Demir is your engagement lead. It's 10:05 |

## How this practice works

1. Ask before you choose. Find out what's at stake on each side.
2. Decide, and say your decision and the reason to both customers.
3. Use the people who own each fix: their IT and network teams, your lead, your colleagues.
4. Refuse unsafe shortcuts and promises you can't keep, and offer something real instead.
5. End with a timeline: who does what, and when each person hears from you next. Press **End and get feedback** after at least five exchanges.
