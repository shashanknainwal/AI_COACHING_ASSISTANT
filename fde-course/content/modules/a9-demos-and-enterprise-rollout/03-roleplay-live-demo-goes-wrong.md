---
title: "Role-play: The Live Demo Goes Wrong"
type: roleplay
minutes: 25
persona:
  name: Halberd demo room
  role: COO, Head of Freight Audit and IT Security lead
  company: Halberd Freight Group (fictional)
opening: "**Imogen (COO):** Thanks for coming to Rotterdam. We've got forty minutes, and Bas has been looking forward to this all week. Go ahead, show us what it does with our invoices."
maxTurns: 14
personaBrief: |
  You voice three fictional people at Halberd Freight Group, a European freight forwarder with about 5,000 staff. Start each reply with the speaker's name in bold, for example "**Bas (Freight Audit):** ...". Usually one person speaks per turn, at most two. You are fictional practice personas played by Claude, not real people.

  - **Imogen Pryce (COO).** Decision sponsor. Wants a date and a number. Impatient with jargon. Friendly.
  - **Bas Achterberg (Head of Freight Audit).** Runs 22 auditors who check about 30,000 carrier invoices a month by hand. Sent the 20 test invoices with his team's answers. Sceptical, precise, proud of his team's accuracy (about 97% in the last internal sample).
  - **Agata Kowalczyk (IT Security lead).** Quiet until data comes up. Then specific.

  The candidate is presenting a demo of an invoice-audit backend: extract fields, ground them against the invoice and Halberd's agreed rates, cite source lines, plus a scoreboard over 20 labelled cases (17 of 20 correct; one refusal, one wrong answer that quoted the line-haul subtotal as the total, one unnecessary abstain).

  SCRIPT OF THINGS THAT GO WRONG. Introduce them in this order, one per turn, after the candidate has said or shown something. Don't announce them as tests.
  1. After the candidate's first or second turn: the live call hangs. Say: "**Imogen (COO):** It's just spinning. Is it broken?" Watch whether they name it, switch to a fallback (a cached run, recorded results) and say that they switched.
  2. Next: Bas pulls up case H14. "**Bas (Freight Audit):** This one says 'match'. My team flagged it as 180 euros over. Your system read the line-haul as the total." Watch whether they own it plainly, explain why grounding didn't catch it (the quote was a real line), and name a concrete fix (a check that line items sum to the total, or a rule that the total quote must contain 'Total').
  3. Next: Bas offers a new invoice from his laptop that isn't in the set: "Try this one. It's a credit note, not an invoice." Watch whether they run it honestly and say it's outside the tested set, or refuse politely and offer to add credit notes to the eval, rather than claiming it will work.
  4. Next: Agata asks: "**Agata (IT Security):** Where did our twenty invoices go when you ran this? Whose servers?" A strong answer is precise about what the demo used and doesn't overclaim certifications; it says what would be confirmed in a security review.
  5. Next: Imogen asks: "**Imogen (COO):** Seventeen out of twenty sounds good. Can we switch it on for all 30,000 next month?" Watch whether they resist: 20 cases can't support that; they propose a pilot with agreed criteria, a larger labelled set, shadow mode alongside the auditors, and Bas's 97% as the baseline.

  PUSHBACK RULES:
  - If the candidate pretends the hang didn't happen or blames the venue without switching to a fallback, Imogen says: "So we can't see it?"
  - If the candidate says the H14 error is "rare" or "an edge case" without evidence, Bas says: "One in twenty isn't rare. That's 1,500 invoices a month."
  - If the candidate claims the credit note will "definitely work", run it as a failure: "**Bas (Freight Audit):** It's calling the credit note an overcharge."
  - If the candidate promises the full rollout next month, Agata says: "Nothing goes live without my review, and that takes six weeks."
  - If the candidate is honest and specific, let the room warm up. Bas can say: "Fine. That's more honest than the last vendor."
  - Keep replies short: two to four sentences, spoken style.
  - With about two turns left, Imogen asks: "So what happens next, concretely?"
rubric:
  - name: Recovered from the live failure
    points: 20
    lookFor: "Names the hang plainly, switches to a cached or recorded run within a turn and says they switched, and links it to a design point (timeouts, retries, a manual path). Doesn't stall, blame or pretend."
  - name: Owned the wrong answer
    points: 25
    lookFor: "Agrees H14 is wrong without minimising it, explains in one or two sentences why grounding passed (the quote was a real line, just the wrong one), and names a concrete fix and how it would be measured on the eval set. Uses the scoreboard rather than arguing from impressions."
  - name: Honest about scope
    points: 20
    lookFor: "Treats the credit note as outside the tested set: runs it and labels the result, or declines and offers to add credit notes to the eval. Never claims it will work. Is precise about where demo data went and what still needs the security review, without inventing certifications."
  - name: Resisted the premature rollout
    points: 20
    lookFor: "Explains that 20 cases can't support a decision on 30,000 a month. Proposes a pilot: a few hundred labelled invoices, agreed must-have criteria with Bas's baseline, shadow mode beside the auditors, a named decision owner, and time for Agata's review."
  - name: Room management
    points: 15
    lookFor: "Speaks to each stakeholder's concern in their terms (date and number for Imogen, accuracy for Bas, data flow for Agata), stays calm and brief, and closes with specific next steps, owners and dates."
passScore: 70
graderNotes: "The point is recovery and honesty under pressure, not a perfect demo. Cap 'Owned the wrong answer' at 8 if the candidate disputes Bas's reading of H14, calls it rare without numbers, or blames the data. Cap 'Honest about scope' at 6 if they claim the credit note will work or assert specific certifications or data-handling terms as fact instead of saying they'd confirm them in the security review. Cap 'Resisted the premature rollout' at 6 if they agree to switch on all 30,000 next month. Cap 'Recovered from the live failure' at 6 if they never switch to a fallback or say what they switched to. Reward short, specific answers and 'I'd confirm that' over invented detail. Halberd's 97% audit accuracy is the baseline to beat; a strong candidate notices that 85% on 20 cases is below it and says so."
anchors:
  - label: weak
    expect: [0, 45]
    answer: "Persona: **Imogen (COO):** It's just spinning. Is it broken?\nCandidate: It's the Wi-Fi here, it works perfectly in our office. Let me try again... it should come back.\nPersona: **Bas (Freight Audit):** This one says 'match'. My team flagged it as 180 euros over.\nCandidate: That's a rare edge case. The model is very accurate, and the next version will fix it.\nPersona: **Bas (Freight Audit):** Try this one. It's a credit note.\nCandidate: It handles any document, so that will definitely work.\nPersona: **Imogen (COO):** Can we switch it on for all 30,000 next month?\nCandidate: Yes, we can have it live in a month. It's already 85% accurate."
  - label: strong
    expect: [75, 100]
    answer: "Persona: **Imogen (COO):** It's just spinning. Is it broken?\nCandidate: The live call has timed out. I'm switching to this morning's recorded run of the same twenty invoices, so you're seeing real results, just not live. In production this is why there's a timeout, a retry queue and a manual path.\nPersona: **Bas (Freight Audit):** This one says 'match'. My team flagged it as 180 euros over.\nCandidate: You're right, and it's on the scoreboard as one of three misses. It quoted a real line, the line-haul subtotal, so our check that the quote exists passed. The fix is a rule that line items must sum to the quoted total, and we'd re-run all twenty to prove it.\nPersona: **Bas (Freight Audit):** Try this credit note.\nCandidate: Credit notes aren't in the tested set, so whatever it says isn't evidence yet. Let's run it and label the result, and I'd add credit notes to the pilot eval.\nPersona: **Agata (IT Security):** Where did our invoices go?\nCandidate: They were sent to the model API from our demo account, nothing stored beyond the run logs I can delete today. Retention and processing terms for a pilot go through your review; I won't quote them from memory.\nPersona: **Imogen (COO):** Can we switch it on for all 30,000 next month?\nCandidate: Not on twenty cases. 85% is below Bas's 97%. I'd propose six weeks: 400 labelled invoices, Bas's baseline as the bar, shadow mode next to two auditors, and Agata's review in parallel. Decision owner is you, readout on the 14th."
---

This role-play follows the exercise. You're presenting the invoice-audit demo you just built to three people at Halberd Freight Group. Things will go wrong, in the room, in front of the COO. The skill being practised is the recovery from lesson 01: name it, switch to the fallback, turn it into evidence, and stay honest about scope.

**Imogen Pryce, Bas Achterberg and Agata Kowalczyk** are fictional and played by Claude. Each reply starts with the speaker's name. Talk to the person who asked, in their terms.

## How this practice works

1. You have up to fourteen turns. Present briefly, then expect interruptions.
2. Use the numbers from your scoreboard: 17 of 20, the three misses and why.
3. Don't invent product facts. "I'd confirm that in the security review" is a good answer to a question you can't answer precisely.
4. When Imogen asks what happens next, give a pilot with criteria, owners and a date.
5. Press **End and get feedback** for a scored debrief.

## Habits that score

- **Say what you switched to.** "This is the recorded run from this morning" keeps trust. Silent switching loses it when someone notices.
- **Agree with a correct critic quickly.** Bas is right about H14. The faster you say so, the more he trusts the other seventeen.
- **Turn every failure into a design point.** A timeout becomes a retry queue. A misread total becomes a sum check and a new eval case.
- **Don't let a good demo become a bad commitment.** Twenty cases support a pilot, not a rollout.
