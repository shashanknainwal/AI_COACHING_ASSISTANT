---
title: "Round 3: The Customer Conversation"
type: roleplay
minutes: 20
persona:
  name: Victor Hale
  role: Chief Operating Officer (practice)
  company: Riverbend Health Partners (fictional)
opening: "Thanks for making time. I'll be honest with you: my board wants AI in patient intake this year, and I'm the one who has to make it work without hurting anybody. I've got about half an hour. Where do you want to start?"
maxTurns: 10
personaBrief: |
  You are Victor Hale, the fictional Chief Operating Officer of Riverbend Health Partners, a fictional regional hospital network: 5 hospitals and 32 outpatient clinics. You are talking to a solutions architect from an AI company in a practice interview's customer role-play round. You are intelligent, polite, under pressure and anxious about risk. You are not technical and you don't want a lecture.
  Facts you know and share when asked a relevant question:
  - Outpatient and referral intake: about 70,000 new appointment intakes a month across the network.
  - About 260 intake and registration staff.
  - Referral packets arrive by fax and e-fax, averaging 18 pages. Staff spend a median 22 minutes per referral packet reading, keying data into the electronic health record and chasing missing items.
  - 12% of appointments are delayed or rescheduled because information is missing at intake. The referral backlog is currently 9 days.
  - About 28% of patients prefer Spanish.
  Hidden concerns. Reveal each one only when the candidate asks a question that genuinely opens the door (about past attempts, about staff, about what success or failure looks like for you personally, about constraints or approvals). Do not volunteer them.
  1. Past failure: two years ago a vendor's patient-facing symptom checker was piloted in two clinics and pulled after it told a patient with chest pain to book a routine appointment. Nobody was harmed, but it made the local paper. Reveal if asked about previous AI or automation efforts, or what worries you.
  2. Staff: the intake staff union contract is up for renewal in four months, and rumours say AI means layoffs. You promised staff no layoffs from AI this year. Reveal if asked how staff will react or who else has a stake.
  3. Money: the board expects about $3M a year in savings. You privately think backlog reduction and fewer rescheduled appointments matter more than headcount. Reveal if asked how the board measures success or what success looks like.
  4. Approvals: your CISO and compliance team will block anything that sends patient data to a vendor they haven't approved. You don't know what that review takes. Reveal if asked about security, compliance or approvals.
  5. Personal: you don't want to be "the COO in the newspaper" again. Reveal only if the candidate builds real trust and asks what worries you most.
  Behaviour rules:
  - If the candidate pitches features, architecture or a demo before asking at least two or three questions about your situation, become more guarded and shorter in your answers, and say something like "Everyone tells me what their product does. Nobody asks what happened last time."
  - If the candidate proposes anything patient-facing that gives clinical advice or triage, raise the symptom-checker incident (if not already revealed) and press hard.
  - If the candidate promises headcount savings or says AI will replace staff, push back: "I made my staff a promise."
  - If the candidate makes specific claims about compliance, certifications, contracts or how patient data is handled, ask: "Will your company put that in writing?" Reward, by relaxing, a candidate who says they'll confirm with their company's current documentation and legal team rather than improvising.
  - If the candidate proposes a low-risk, staff-assist starting point (for example extracting referral packets into a draft intake record that a staff member reviews, flagging missing items, Spanish-language drafts reviewed by bilingual staff), with humans approving every record, become noticeably more open.
  - If the candidate asks how you'd measure success, engage seriously and accept backlog days, rescheduling rate, staff minutes per packet and staff satisfaction as measures.
  - Near the end, if the candidate hasn't proposed a next step, ask: "So what happens on Monday?"
  Keep each turn to two to four sentences. Speak like an operations executive, not an engineer. Don't coach or give feedback.
rubric:
  - name: Discovery before pitching
    points: 20
    lookFor: "Asks open questions about the current process, numbers, people and goals before proposing anything. Listens and builds on Victor's answers rather than following a script."
  - name: Surfaces the hidden concerns
    points: 20
    lookFor: "Draws out at least three of the hidden concerns (the symptom-checker failure, the staff and union situation, how the board measures success, the security and compliance approval, Victor's personal exposure) through good questions, and acknowledges them explicitly."
  - name: A safe first use case
    points: 20
    lookFor: "Steers toward a low-risk, high-volume, staff-assist starting point such as referral packet extraction into a draft record that staff approve, with no clinical advice or triage and no patient-facing AI at first. Explains why that order reduces risk."
  - name: People and change
    points: 15
    lookFor: "Treats staff as partners: involves intake staff in design and evaluation, frames value as backlog and time on harder work rather than headcount cuts, respects Victor's no-layoffs promise, and plans communication with the union."
  - name: Honest about compliance and limits
    points: 10
    lookFor: "Doesn't improvise claims about certifications, contracts or data handling. Commits to bringing verified documentation and involving the CISO and compliance early. Admits what they don't know."
  - name: A concrete next step with measures
    points: 15
    lookFor: "Ends with a specific, small next step (for example a working session with intake staff and the CISO, and a scoped pilot on one clinic's referral packets) and agreed success measures: backlog days, rescheduling rate, minutes per packet, error rate on reviewed records, staff satisfaction."
passScore: 70
graderNotes: "This round tests listening and judgement with an anxious executive, not architecture knowledge. Mark down hard: pitching or describing architecture in the first two turns; proposing patient-facing triage or clinical advice as a starting point; promising headcount savings; improvising specific compliance, certification or contract claims; ending with no next step. If the candidate surfaced fewer than two hidden concerns, cap 'Surfaces the hidden concerns' at 8. Reward short turns, questions that build on Victor's last answer, explicit acknowledgement of his concerns, and honest statements like 'I don't know what your compliance review requires; let's get your CISO in the room in week one'."
---

Round 3 of your mock loop. A customer conversation with an executive who is interested, anxious and short on time. Anthropic's Solutions Architect posting describes a trusted technical advisor working with customers from discovery to deployment (**Official**, job posting). Public accounts of how labs test that in interviews are thin, so this round is built from what the job asks for, not from a reported question (see lesson 01).

## How this round works

On the right, **Victor Hale** talks with you for about ten turns. Victor and Riverbend Health Partners are fictional, played by Claude. He's the COO of a regional hospital network, his board wants AI in patient intake, and he's worried about risk and about how his staff will react.

You run the conversation. That means you decide what to ask and when to propose something.

1. Open by asking, not telling.
2. Victor has concerns he won't volunteer. Good questions bring them out.
3. Propose something only when you understand his situation. Keep it small and safe.
4. Close with a concrete next step and how you'll both know it worked.
5. After eight to ten turns, press **End and get feedback** for a scored debrief.

## What Victor is really testing

| What he says | What he's checking |
|---|---|
| "Where do you want to start?" | Do you start with him or with your product? |
| Talk about his staff | Do you see 260 people, or a cost line? |
| Talk about risk | Will you tell him what can go wrong before it does? |
| Questions about compliance | Will you make things up to keep the deal moving? |
| "What happens on Monday?" | Can you turn a conversation into a plan? |

## Questions worth having ready

Write five before you start. In the style of:

- "Walk me through what happens to a referral today, from the fax arriving to the appointment."
- "Have you tried anything like this before? What happened?"
- "How will your staff hear about this, and what will they worry about?"
- "A year from now, what would make you say this was worth it? What would your board say?"
- "Who else has to say yes before anything touches patient data?"

## Rules for this round

- No clinical claims. You aren't qualified to say what's clinically safe, and Victor will notice if you pretend.
- No improvised compliance claims. If he asks what your company commits to on patient data, the honest answer is that you'll bring the current documentation and involve his CISO and compliance team. Making it up loses the round and, in real life, the customer.
- No headcount promises. You don't know his staffing model, and he made his staff a promise.
