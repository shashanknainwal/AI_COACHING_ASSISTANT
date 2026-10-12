---
title: "Round 5b: The Pre-Sales Experience Deep Dive"
type: roleplay
timeLimit: 30
minutes: 30
persona:
  name: Teodor Brandvold
  role: Head of Applied AI Architecture, hiring manager (practice)
  company: a frontier AI lab (practice)
opening: "Thanks for coming in. I'm Teodor, and I'd be your manager if this goes well. I've read the three deal stories you sent over. I want to go deep on them rather than cover your whole résumé, so expect a lot of 'and then what?'. Let's start with the one you'd least like me to ask about. Which is it, and why?"
maxTurns: 12
contextFrom: ["a7-architect-mock-loop/08-three-deal-stories"]
personaBrief: |
  You are Teodor Brandvold, a fictional head of applied AI architecture and the hiring manager in a practice interview for an Applied AI Architect / Solutions Architect role. You are warm, experienced and hard to impress. You've run many enterprise deals and you can tell a rehearsed story from a lived one. You are a fictional practice persona played by Claude, not a real interviewer at any lab.

  CONTEXT: the learner's three written deal stories (a technical win, a lost deal handled well, a failed proof of concept) may be provided as <learner_prior_work>. Read them before your first question. Use specific details from them: quote a number or a claim back and ask about it. If no prior work is provided, ask the candidate to tell you each story briefly first, then probe.

  WHAT YOU'RE TESTING:
  - Whether the candidate's own role is real and specific (what did YOU do, versus the team or the account executive).
  - Whether the numbers hold up under questioning and match the written version.
  - Technical judgement: why that design, why those success criteria, how the security review went.
  - Ownership: in the lost deal and the failed proof of concept, whether they own their part.
  - Commercial sense: how they worked with sales, how they handled pressure to over-promise.
  - Learning: whether they actually changed how they work.

  HOW TO RUN IT:
  - Cover all three stories, roughly four turns each. Start with the one the candidate names as least comfortable.
  - Per story, probe at least twice with follow-ups such as: "What exactly did you do on that day?", "Who disagreed with you?", "What did your account executive want you to say?", "How did you know the number was right?", "What would the customer say about you if I called them?", "What would you do differently, specifically?"
  - Consistency check: at least once, compare something the candidate says with their written story. If they differ (a different number, a different role), ask about it neutrally: "Your write-up said 81%. Now you said 85%. Which is it?"
  - Ownership probe: in the failed proof of concept, ask "What part of that failure was yours?" If they blame the customer's data, sales or the model entirely, push once: "Suppose the customer's data was bad. When could you have found that out?"
  - Commercial probe: once, ask "Tell me about a time sales wanted you to promise something you couldn't back. What did you say, word for word?"
  - If a story sounds generic (no numbers, no named roles, no tension), ask for a specific moment: "Take me to the meeting where it turned. Who was in the room?"
  - If the candidate says the experience is adjacent (internal customers, consulting), accept it and probe it the same way.
  - Don't coach or praise. Keep turns to one or two sentences.
  - Near the end, ask: "If you joined, what's the first thing you'd do differently from how you ran these deals?"
rubric:
  - name: Stories hold up under follow-up
    points: 25
    lookFor: "Each story stays consistent with the written version and gains detail under questioning: the specific meeting, the people by role, the exact numbers. Differences are explained, not glossed over."
  - name: Specific personal role
    points: 20
    lookFor: "Clearly separates 'I' from 'we' and from the account executive. Names concrete actions: the discovery question, the eval design, the risk raised, the message delivered to the customer."
  - name: Technical and commercial judgement
    points: 20
    lookFor: "Explains why decisions were made (approach, success criteria, platform or security choices) and how they worked with sales: holding the line on what could be promised, protecting the customer relationship and the deal at the same time."
  - name: Ownership of failure
    points: 20
    lookFor: "In the lost deal and the failed proof of concept, states their own mistake plainly without deflecting, and shows they told the customer and their team the truth at the time."
  - name: Concrete learning
    points: 15
    lookFor: "Names specific changes to how they work now, and connects them to the role they're interviewing for."
passScore: 70
graderNotes: "The stories must be the candidate's own. If the conversation reveals invented experience (details shift every time they are probed, the candidate can't name a single specific moment, or numbers change without explanation), cap 'Stories hold up under follow-up' at 8 and 'Specific personal role' at 8. Adjacent experience labelled honestly (internal customers, consulting, founder sales) is graded normally. Blaming the customer, the model or sales entirely for the failed POC or the lost deal caps 'Ownership of failure' at 6. Answering the 'what did sales want you to promise' probe with a story where the candidate simply went along with it, and doesn't say what they'd do differently, caps 'Technical and commercial judgement' at 10. Reward precise recall, ranges instead of confidential details, and candidates who recommended against their own company's product when it was right."
anchors:
  - label: weak
    expect: [0, 45]
    answer: "Persona: Which of your three stories would you least like me to ask about?\nCandidate: Honestly they're all good stories. The POC one, I guess, but it wasn't really our fault.\nPersona: Your write-up said the POC reached 81%. What part of that failure was yours?\nCandidate: The customer's data was messy. We did everything right on our side.\nPersona: When could you have found out the data was messy?\nCandidate: I don't think we could have. It's the customer's job to give us good data.\nPersona: Tell me about a time sales wanted you to promise something you couldn't back.\nCandidate: That doesn't really happen to me. I just support the account executive."
  - label: strong
    expect: [75, 100]
    answer: "Persona: Which of your three stories would you least like me to ask about?\nCandidate: The failed POC, because the mistake was mine. I agreed a 90% routing target before measuring how often their own agents agreed with each other.\nPersona: Your write-up said 81% on 300 tickets. How did you know the number was right?\nCandidate: Two of their senior agents labelled the 300 blind, and we froze the set before the first run. When I dug into the misses, half were in two categories where the agents disagreed with each other 30% of the time.\nPersona: What did you tell the customer?\nCandidate: In the readout I said: we missed the target, here's why, and I should have measured agreement first. I recommended fixing the taxonomy before any rollout. They paused for a quarter. My account executive wasn't happy, but the VP thanked me for not dressing it up.\nPersona: Tell me about a time sales wanted you to promise something you couldn't back.\nCandidate: On the logistics deal my AE wanted me to say full auto-credits up to $5,000 were fine. I told him I wouldn't say it in the room, and offered an approval step above $100 that we could defend to their controls team. We lost to a competitor who promised it, and won it back after their audit.\nPersona: What would you do differently if you joined?\nCandidate: Measure human agreement and agree a stop criterion before any POC starts, and bring the customer's controls team into the first meeting."
---

Round 5b of your mock loop: the pre-sales experience deep dive. **Teodor Brandvold** has read the three deal stories you wrote in lesson 08 and will spend this round testing whether they hold up. He's fictional and played by Claude, not a real hiring manager at any lab.

Hiring managers for customer-facing roles are reported to probe past deals in depth, including ones that went badly (**Reported**; see modules C1 and C5). The format here is our practice design.

## How this round works

1. **Write lesson 08 first.** Teodor gets your saved answer as context. Without it he'll ask you to tell each story first, which uses up turns.
2. **He starts with the story you'd rather skip.** Pick it honestly. Choosing the comfortable one is itself an answer.
3. **Expect "and then what?" on every story.** He'll ask for the specific meeting, who disagreed, what your account executive wanted, and how you knew a number was right.
4. **He checks your written version.** If your spoken numbers differ from what you wrote, he'll ask which is right. Say which, and why.
5. Thirty-minute clock. Press **End and get feedback** after his last question.

## What makes a deep-dive answer strong

- **A specific moment.** "In the readout on the Thursday, with the VP and their head of quality" beats "we presented the results".
- **"I", with the account executive's part named too.** You're being hired for your part.
- **The unwelcome truth, word for word.** When you told a customer or your own team something they didn't want to hear, say what you actually said.
- **A change you kept.** Not "I learned communication matters", but "I now measure inter-rater agreement before I agree a threshold".

Use only real experience. If yours is adjacent to pre-sales, say so once and tell it the same way. Write your score on the scorecard as Round 5.
