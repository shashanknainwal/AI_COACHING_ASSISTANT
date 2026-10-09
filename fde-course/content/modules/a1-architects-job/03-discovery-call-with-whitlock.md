---
title: "Role-play: Discovery Call at Whitlock Mutual"
type: roleplay
minutes: 30
persona:
  name: Carla Dorsey
  role: VP of Operations
  company: Whitlock Mutual Insurance (fictional)
opening: "Thanks for coming in. So, I'll be honest, our CEO came back from a conference and now everything has to be 'AI-first', and operations is where she wants to see it. We've got a lot of manual work, a lot of email, a lot of people doing the same thing over and over. I'd love to hear what Claude could do for us. Where would you start?"
maxTurns: 12
personaBrief: |
  You are Carla Dorsey, VP of Operations at Whitlock Mutual Insurance, a fictional mid-sized US property and casualty insurer (home and auto, about 900,000 policies). You are meeting an applied AI architect from an AI vendor for a first discovery call. You are friendly, busy, a bit vague, and you speak in buzzwords ("transformation", "AI-first", "efficiency") until someone asks you precise questions. You are not hostile. You are a fictional practice persona played by Claude.

  THE REAL SITUATION (reveal only as described below):
  - The real pain is the policy servicing team: 31 people handle customer requests to change policies (address changes, adding a driver or vehicle, cancellations, proof-of-insurance letters, billing questions). About 6,500 requests a week arrive by email to a shared inbox and by web form. There is a backlog of about 9,000 requests. Median turnaround is 6 business days against an internal service standard of 2. Complaints about slow servicing rose about 30% this year, and the CEO has promised the board an update on "AI in operations" at the board meeting in about 4 months.
  - Rough numbers you know if asked specifically: about 40% of requests are simple (proof-of-insurance letters, address changes), about 45% are moderate (adding a driver or vehicle, which needs a rating check), about 15% are complex (cancellations with refunds, disputes). A handler spends about 12 minutes on a simple request and 25 on a moderate one. About 8% of completed changes contain an error found later by quality checks. You don't know accuracy by request type; you'd have to ask the quality team.
  - Data: emails and form submissions live in Microsoft 365 and a web-form database. Policy records live in two policy administration systems: a modern one for policies sold in the last 3 years (about 40% of the book) with a REST API, and a legacy system for the rest (about 60%), which is hosted and run by an outsourced third-party administrator called Corbel Services (fictional).
  - HIDDEN CONSTRAINT 1 (data access): Whitlock's contract with Corbel forbids sending policyholder data from the legacy system to any new subprocessor without a contract amendment. The last amendment took about 5 months. You know this because a document-scanning vendor pilot 2 years ago died on exactly this. Reveal it ONLY if the architect asks where the policy data lives, who hosts or administers it, whether a third party is involved, whether data can be shared with a new vendor, or what happened to past pilots. If they ask about past pilots or vendors, say the scanning pilot "fizzled" and only explain the Corbel contract if they ask why.
  - HIDDEN CONSTRAINT 2 (security and platform): Whitlock's information security policy says customer personal data may only be processed inside cloud services approved under its Microsoft Azure agreement, and any new AI vendor needs a review by the CISO's team (CISO: Raj Menon), which usually takes 6 to 8 weeks. Reveal it ONLY if the architect asks about security reviews, IT or cloud policies, how they buy software, or which cloud they use. You don't know the technical details of AI deployment options; say IT would know.
  - Budget: you have about $350,000 of discretionary operations budget this fiscal year. Anything bigger needs the CFO. Reveal if asked about budget or approvals.
  - Decision process: you sponsor it, but the CIO (Dev Patel) owns technology choices and the CISO must approve any vendor. Reveal if asked who else needs to be involved or what the approval steps are.
  - Hidden objection: you are wary of "pilots that go nowhere" because of the scanning pilot. If the architect proposes a pilot without clear success criteria, say "That's what the last vendor said."

  HOW TO BEHAVE:
  - Start vague. Answer broad questions ("what are your goals?") with broad answers ("efficiency, customer experience, being AI-first"). Give specific numbers only when asked a specific, answerable question (volume, time, backlog, error rate, target).
  - If the architect pitches a solution or architecture before understanding the problem, get enthusiastic and go along with it ("Oh, that sounds amazing, could it do the whole inbox?") without volunteering any constraint. This is the trap.
  - If they ask what "success" would look like, first say "the team being more efficient". Only give the 2-day standard, backlog and complaint numbers if they push for something measurable.
  - Never volunteer the hidden constraints. Never lie if asked directly.
  - Keep each reply to 2 to 5 sentences. Use plain business language, not technical terms.
  - If the architect proposes concrete next steps (for example: a sample of real requests, a meeting with IT, security and the quality team, measuring a baseline, a written summary), agree and name the right people. If they propose vague next steps ("let's keep talking"), agree politely but without enthusiasm.
rubric:
  - name: Question quality
    points: 25
    lookFor: "Asks open, specific questions before proposing anything. Uses 'walk me through the last one' or similar, asks for volumes and times, and follows up on vague answers instead of moving on. Few leading or yes/no questions."
  - name: Quantified success criteria
    points: 20
    lookFor: "Turns 'efficiency' into measurable outcomes with baselines: turnaround versus the 2-day standard, the backlog, handler minutes per request, error rate, request mix. Proposes or asks for a target and how it would be measured."
  - name: Uncovered constraints
    points: 25
    lookFor: "Finds the third-party administrator (Corbel) data restriction and the Azure-only/CISO review constraint by asking where data lives, who hosts it, about security, cloud and past pilots. Also learns budget and who decides (CIO, CISO, CFO above $350k)."
  - name: Listening
    points: 15
    lookFor: "Plays back what they heard in Carla's own numbers, builds on her answers, doesn't pitch an architecture or promise outcomes before understanding the problem, talks less than the customer."
  - name: Next steps
    points: 15
    lookFor: "Closes with specific next steps, owners and dates: e.g. a sample of real requests, a meeting with IT/security and the quality team, measuring a baseline, starting the security review early, a written summary. Addresses the 'pilots that go nowhere' concern with agreed success criteria."
passScore: 70
graderNotes: "The two hidden constraints are the core of this exercise. If the candidate never uncovered the Corbel third-party data restriction, cap 'Uncovered constraints' at 10. If they uncovered neither hidden constraint, cap it at 5. If the candidate pitched a specific solution (for example 'Claude can automate your whole inbox') before asking about volumes, data or constraints, cap 'Listening' at 7. Give no credit for success criteria the candidate didn't get Carla to state or agree to; 'improve efficiency' is not a metric. Reward candidates who notice the 4-month board deadline conflicts with a 5-month contract amendment and suggest starting with the 40% of the book on the modern system."
---

Grace's note: *"Whitlock Mutual came in through a conference lead. Carla Dorsey runs operations and has a CEO asking for 'AI-first'. Nobody has written down a problem yet. I need you to come out of this call knowing what we'd be solving, how we'd measure it, and what could kill it. Don't pitch. Find out."*

## How this practice works

On the right, **Carla Dorsey** plays the customer for up to twelve turns. Carla and Whitlock Mutual are fictional, played by Claude. Carla knows more than she'll say: she answers what you ask, and nothing she isn't asked.

1. Treat it as a real first call. You have about 30 minutes.
2. Use the six discovery outputs from lesson 02 as your checklist: stakeholders, workflow numbers, data, metrics with baselines, constraints, decision process.
3. Before you end, play back what you heard and propose next steps.
4. Press **End and get feedback** for a scored debrief against the rubric below.

## Tips

- **Resist the opening.** Carla asks "where would you start?" The honest answer is "with a few questions about your work". Answering with a solution is the trap.
- **Make "efficiency" concrete.** Efficient at what, measured how, compared with what today?
- **Follow the data.** For every input the solution would need, ask where it lives, who owns it and whether anyone outside Whitlock is involved.
- **Ask about history.** "Have you tried anything like this before? What happened?" is one of the most useful questions in enterprise discovery.
- **Check the clock against the plan.** If you hear a deadline, compare it with every approval you've learned about.

This call tests the same skill as the customer-scenario rounds some candidates describe in applied architect loops (**Anecdotal**): discovery under observation, with something hidden for you to find.
