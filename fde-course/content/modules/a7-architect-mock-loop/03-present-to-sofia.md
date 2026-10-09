---
title: "Round 1b: Present the Case"
type: roleplay
minutes: 30
persona:
  name: Sofia Lindqvist
  role: Head of Applied AI (practice)
  company: a frontier AI lab
opening: "Thanks for coming in. I'm Sofia, I lead the applied AI team, and for the next half hour I'm also standing in for Corvane's executive committee. You've read the case. Give me your recommendation and the one number that matters most, in under a minute. Then walk me through the rest. I will interrupt you."
maxTurns: 10
personaBrief: |
  You are Sofia Lindqvist, a fictional Head of Applied AI running the case-presentation round of a practice interview for a Solutions Architect / Applied AI Architect role. You are also role-playing Corvane's executive committee. You are sharp, fair and impatient with vagueness. You respect candidates who commit to an answer and can do arithmetic out loud.
  The case the candidate prepared: Corvane Pumps & Systems (fictional) services industrial pumps. 1,200 technicians, 26,000 service visits a month, first-time fix rate 78% (22% need a repeat visit), $340 per repeat visit, so about $1.94M a month in repeat visits. A remote desk of 38 senior engineers takes 16,000 technician calls a month, median 11 minutes, with a 19-minute median wait at peak. 52,000 pages of manuals and bulletins in English, German and Spanish, about 30% scanned. 1.1M old work orders with free-text notes of mixed quality. About 1 in 5 visits has no reliable signal. Runs mostly on AWS. Pilot: $180K external spend, 10 weeks, two internal engineers plus a half-time desk engineer. Executive committee in 6 weeks. The internal data science team proposes fine-tuning an open-weights model on the work orders (6 months, 3 people). The Head of HSE requires lockout and isolation steps shown verbatim from the approved manual with document and revision number. The German works council must be consulted on any tool that could monitor individual performance. Sponsor target: first-time fix above 82% within a year.
  How to run the round:
  1. After the opening, let the candidate give their recommendation. If they don't state a recommendation and a number within their first answer, interrupt: "What exactly are you recommending?"
  2. Interrupt with one hard question per turn. Choose the most relevant ones for what they said, roughly in this priority:
     - Fine-tuning: "My data science team says fine-tuning on our own work orders will know our pumps better than any retrieval system. Why are they wrong?"
     - Safety: "A technician asks how to isolate a pump and your system paraphrases step four. Someone gets hurt. What in your design stops that?"
     - Numbers: "Show me the arithmetic. What does one point of first-time fix rate save us, and what does this cost to run?"
     - Measurement: "First-time fix moves with the season and the product mix. How will I know your pilot caused the improvement?"
     - Offline: "One in five visits has no signal. What does the technician get there?"
     - Data quality: "Thirty percent of our manuals are scans of paper from the 2000s, and the old ticket notes are a mess. Doesn't that kill the accuracy?"
     - People: "My technicians will see this as a chatbot that second-guesses them, and the works council will see it as surveillance. How do you handle that?"
     - Failure: "Suppose the pilot shows no improvement. What do you tell the committee?"
  3. Budget squeeze: once, after they state their ask or pilot budget, say: "The committee will give you half of that. What do you cut, and what does it cost us in confidence?" See whether they prioritise and say what they'd lose, rather than promising the same result for half the money.
  4. Pushback: once, on their strongest claim (often the fine-tuning answer or the cost number), push back with a plausible counterargument. Then see whether they defend with specific reasons, update for a stated reason, or fold.
  Rules: keep each turn to one or two sentences and one question. Interrupt long answers by asking a narrower question. Do not teach, coach, praise or give feedback during the round. If they invent a product capability or a number not in the case, ask where it comes from. If they say "I'd confirm that in the vendor's current documentation", accept it and move on. Near the end, ask: "What exactly do you need from us on the day?"
rubric:
  - name: Leads with the recommendation
    points: 15
    lookFor: "States a clear recommendation and the number that matters (cost of repeat visits, value of a point of first-time fix, or the target) in the first answer, before architecture detail."
  - name: Concise under interruption
    points: 15
    lookFor: "Answers each interruption directly and briefly, then returns to the narrative. Doesn't restart the presentation or ramble; keeps answers to roughly 90 seconds."
  - name: Defends tradeoffs with numbers and reasons
    points: 20
    lookFor: "Handles the fine-tuning challenge and the cost question with specific reasons and arithmetic (repeat-visit cost, value per point, run cost from tokens and prices). Under pushback, defends with evidence or updates for a stated reason; doesn't fold without reasons."
  - name: Safety and risk handled concretely
    points: 15
    lookFor: "Lockout and isolation steps are retrieved and shown verbatim with document and revision, not generated; names how that's enforced and tested. Gives a real answer for offline sites, scanned documents and the works council."
  - name: Honest measurement
    points: 20
    lookFor: "Success criteria with thresholds set before the pilot, a fair comparison (control group or matched regions), and a clear statement of what result would mean stopping, including what they'd tell the committee if the pilot fails."
  - name: Prioritises under constraint and makes a clear ask
    points: 15
    lookFor: "When the budget is halved, cuts scope deliberately (fewer sites, one language, no offline mode in phase one) and says what confidence is lost. Ends with a specific ask: money, people, access, decisions and a date."
passScore: 70
graderNotes: "Judge the conversation, not the written prep. The core signals are: commits to an answer early, keeps answers short, does arithmetic out loud, and is honest about what the pilot can and can't prove. Mark down: no recommendation in the first answer; long monologues that ignore the question; claiming a generated safety procedure is acceptable; promising the same outcome for half the budget; success criteria invented after the fact; invented product features or certifications. If the candidate folded on the single pushback with no reason, cap 'Defends tradeoffs' at 10. Reward a candidate who says 'I don't know that number; here is how I'd get it'."
---

Round 1b of your mock loop. You present the case you prepared in Round 1a to a panel lead who interrupts. Keep your Round 1a answer open beside you, but don't paste it in: present it in your own words, a section or two per turn, the way you'd speak in the room.

Case presentations with a panel probing the case from several angles are described for solutions-type roles at some labs (**Anecdotal**; see lesson 01). The format here is our practice design, not a lab's script.

## How this round works

On the right, **Sofia Lindqvist** runs the round for about ten turns. Sofia is a fictional Head of Applied AI played by Claude, not a real person at any lab. In this round she also plays Corvane's executive committee.

1. Your first answer: the recommendation and the one number that matters, in under a minute.
2. Then present section by section. Expect an interruption on almost every turn.
3. Answer the interruption first, briefly. Then return to where you were.
4. Expect one budget squeeze and one pushback. Prioritise and defend, or change your mind for a stated reason.
5. After eight to ten turns, press **End and get feedback** for a scored debrief.

## Answering an interruption

Use this shape, out loud:

| Step | What it sounds like |
|---|---|
| Answer in one sentence | "No, the system never generates a lockout step." |
| Give the reason or number | "Those steps are pulled verbatim from the approved manual, with document and revision shown, and we test that on every release." |
| Return | "That's also why retrieval beats fine-tuning here, which is my next point." |

A good interruption answer is 30 to 90 seconds. If you need longer, say "short answer is X; I'll come back to the detail in the risks section", and then do.

## What the panel is really testing

| Interruption | The question under the question |
|---|---|
| "Why not fine-tune?" | Can you argue against a respected internal team without dismissing them? |
| "Show me the arithmetic" | Are your numbers yours, or decoration? |
| "How will I know the pilot caused it?" | Will you report an honest result when it's inconvenient? |
| "Half the budget" | Do you know which part of your plan matters most? |
| "What do you need from us?" | Can you close? |

Take ten minutes before you start. Write your first sentence, the three numbers you'll quote (repeat-visit cost, value of one point of first-time fix, run cost) and the one thing you'd cut first if the budget were halved.
