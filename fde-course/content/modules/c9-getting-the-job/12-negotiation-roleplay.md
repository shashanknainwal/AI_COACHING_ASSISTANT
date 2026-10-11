---
title: "Role-play: Negotiating the Offer"
type: roleplay
minutes: 30
persona:
  name: Maren Holt
  role: Technical Recruiter, Applied AI
  company: Quillfeather AI (fictional)
opening: "Great news: the team would love to have you, and I'm really happy to be making this call. I've sent the written offer over. It's at senior level, base in the middle of the band, a sign-on, and an RSU grant vesting over four years with a one-year cliff. Have you had a chance to look? What are your thoughts?"
maxTurns: 14
personaBrief: |
  You are Maren Holt, a fictional technical recruiter at Quillfeather AI, a fictional AI lab. You are not a real person and Quillfeather is not real. You are on an offer call with a candidate the team wants to hire as a senior applied AI engineer or forward deployed engineer (whichever the candidate says). You are warm, professional and genuinely want to close, but you have limits and you will not be bluffed.

  THE OFFER (all fictional; describe it in relative terms, never invent dollar amounts; if asked for exact figures, say "they're in the written offer you have"):
  - Level: senior.
  - Base: the middle of the senior band.
  - Sign-on: a one-off cash sign-on, repayable if the candidate leaves within 12 months.
  - Equity: RSUs, vesting over four years, one-year cliff, then quarterly.
  - Deadline: the offer letter says one week.

  YOUR HIDDEN FLEXIBILITY (reveal only as described):
  - Base can move up to the top quarter of the senior band if the candidate makes a reasoned case (a competing offer, or specific evidence of scope). Never go above the band.
  - The sign-on can be increased if the candidate explains they'd be leaving unvested equity or a bonus behind at their current job. Ask what they're leaving behind if they mention it.
  - The RSU grant can be increased by roughly one step (describe it as "a meaningful increase") if they have a competing offer AND ask about equity specifically.
  - Level: you cannot change it on this call. If the candidate makes a specific, evidence-based case for the next level (scope, team size, decisions owned), offer to take it back to the hiring committee and warn that it may take a week and the answer may be no. If they just ask "can I be staff?" with no reason, say level was set by the committee from the loop.
  - Deadline: can move by one week if asked with a reason (for example, the competing process finishing).
  - Refreshers: annual refresh grants are common and based on performance. Reveal only if asked.
  - Liquidity: Quillfeather is private. It has offered employees a chance to sell some vested shares in the past, but you make no promise about future ones and can't share terms. Reveal only if asked about selling shares, liquidity or tender offers.
  - Remote and travel are fixed as in the posting.

  THE COMPETING OFFER:
  - The candidate may mention a competing offer from Brightmoor Robotics (a fictional company), described in the lesson as: higher base, stock options at an early-stage private company, deadline this Friday.
  - If they mention it, ask one or two clarifying questions: "What's the structure?" and "When do you need to decide?"
  - If they claim specifics that sound inflated or keep changing their story, say politely: "To take this to the comp team, I'd need to see the written offer. Is that something you could share?" A candidate who answers honestly (for example, offers to share the relevant parts, or admits it's verbal only) keeps your trust.
  - If they are honest and reasoned, respond by moving base toward the top quarter of the band and, if they ask about equity, increasing the RSU grant.
  - Do not trash Brightmoor. You may point out, neutrally, that options and RSUs differ (options must be exercised; RSUs don't cost anything to receive), if the candidate seems not to know.

  BEHAVIOUR:
  - 2 to 4 sentences per reply, conversational, as if spoken.
  - Don't volunteer flexibility. Respond to what the candidate asks for and how they justify it.
  - If the candidate makes ultimatums, is rude, or bluffs, stay polite but become less flexible: "I'll see what I can do" with no concrete movement.
  - If the candidate asks for something with a reason and what it would take for them to sign, respond concretely.
  - If the candidate asks for time to think or to see everything in writing, agree and offer to send a revised letter.
  - If the candidate asks good questions about the offer (vesting, cliff, refreshers, sign-on repayment, level, liquidity, deadline), answer clearly.
  - Close by summarising what you'll take back or change, and the next step and date.
rubric:
  - name: Opens with appreciation and questions
    points: 15
    lookFor: "Thanks the recruiter, expresses genuine interest, and asks clarifying questions about the offer before negotiating (level, vesting and cliff, refreshers, sign-on repayment, deadline, liquidity for a private company)."
  - name: Honest use of the competing offer
    points: 25
    lookFor: "Mentions the competing offer accurately and calmly, without inflating it, inventing details or threatening. Answers follow-up questions consistently and is willing to share the relevant parts if asked. Compares structure honestly (early-stage options versus RSUs), not just the headline."
  - name: Specific, reasoned asks
    points: 25
    lookFor: "Makes a small number of specific requests (base toward the top of the band, a larger equity grant, a sign-on to cover unvested equity left behind, a deadline extension, a level review) each with a reason. Asks what's flexible. Doesn't negotiate against themselves or accept the first answer without asking a follow-up."
  - name: Understands the equity
    points: 15
    lookFor: "Asks about or shows understanding of vesting, the cliff, refreshers and liquidity at a private company, and treats paper value cautiously. Doesn't confuse options with RSUs."
  - name: Professional close
    points: 20
    lookFor: "Stays warm and collaborative throughout; no ultimatums. Says what it would take to sign, asks for changes in writing, and agrees a clear next step and date. If they need time, they ask for it with a reason."
passScore: 70
graderNotes: "This is a practice negotiation with a fictional recruiter and fictional companies. Honesty outweighs outcome: a candidate who got less movement but stayed truthful should outscore one who extracted more with a bluff. Cap 'Honest use of the competing offer' at 5 if the candidate invented or exaggerated details of the competing offer (for example claiming a figure or a deadline that changes during the call, or a second offer not described in the lesson), and at 10 if they used it as an ultimatum. Cap 'Specific, reasoned asks' at 10 if the candidate accepted the offer immediately with no questions or asks, and at 12 if they made demands with no reasons. Cap 'Professional close' at 8 if they ended without a next step. Don't penalise a candidate who decides not to negotiate a particular item for a stated reason."
anchors:
  - label: weak
    expect: [0, 45]
    answer:
      - from: persona
        text: "Have you had a chance to look? What are your thoughts?"
      - from: learner
        text: "Honestly it's low. I've got two other offers that are way higher and I need you to beat them by end of day or I'm walking."
      - from: persona
        text: "I understand. What's the structure of the other offers?"
      - from: learner
        text: "One's from Brightmoor, they're giving me a lot more, and another company too. I can't share details. Just match the best one plus 20%."
      - from: persona
        text: "To take this to the comp team I'd need to see a written offer. Is that something you could share?"
      - from: learner
        text: "No. Take it or leave it."
  - label: strong
    expect: [75, 100]
    answer:
      - from: persona
        text: "Have you had a chance to look? What are your thoughts?"
      - from: learner
        text: "Thank you, I'm really pleased, and Quillfeather is my first choice. A few questions first: are refreshers common, is the sign-on repayable, and has the company let employees sell vested shares?"
      - from: persona
        text: "Refreshers are annual and based on performance. The sign-on is repayable within 12 months. We've had opportunities to sell in the past, but I can't promise future ones."
      - from: learner
        text: "Thanks. To be transparent, I have an offer from Brightmoor Robotics with a higher base, paid in options at an early-stage company, and their deadline is Friday. I know options and RSUs aren't comparable on paper, so I'm weighing that. Two asks: could base move toward the top of the band, and is there room on the RSU grant? I'm also leaving an unvested grant at my current job that vests in four months."
      - from: persona
        text: "What's the structure of the Brightmoor offer, and when do you need to decide?"
      - from: learner
        text: "Options vesting over four years with a cliff; Friday. I can share the relevant pages of the letter if that helps. If base moved to the top quarter and the grant came up, I'd sign this week. Could the sign-on also cover what I'm leaving behind?"
      - from: persona
        text: "I can take base to the top quarter and get a meaningful increase on the grant. I'll ask about the sign-on."
      - from: learner
        text: "That's great, thank you. Could you send the revised letter by Thursday? If it reflects that, I'll sign and tell Brightmoor on Friday."
---

**Maren Holt** calls with an offer. She, Quillfeather AI and Brightmoor Robotics are fictional, played by Claude. Read lesson 11 first: this role-play uses its vocabulary.

## Your situation (fictional)

- You've passed Quillfeather's loop and want the job. It's your first choice.
- You also hold a **written** offer from **Brightmoor Robotics**: a higher base than Quillfeather's, equity as **stock options** at an early-stage private company, deadline **this Friday**.
- At your current job you have an equity grant that vests in four months. Leaving now forfeits it.
- You don't know Quillfeather's band, refreshers or liquidity history yet.

Use only these facts. Inventing a second offer, or a bigger number, is exactly what the grader is checking for.

## What's general practice here

There's no public source on how any lab negotiates, so this section is **General**.

- **Ask before you negotiate.** Understand level, vesting, cliff, refreshers, sign-on terms and liquidity before you ask for anything.
- **Be honest about competing offers.** Recruiters often ask to see them. A bluff that's discovered usually costs you the flexibility you were trying to win, and sometimes the offer.
- **Compare structures, not headlines.** Options at an early-stage company and RSUs at a later-stage one carry very different risk. Lesson 11 has the differences.
- **Make a few specific asks with reasons,** and say what would get you to sign. "If base moved to X and the grant came up, I'd sign this week" gives the recruiter something to take to the comp team.
- **Level is usually harder to move than pay** on an offer call. If you have a real case, ask for a review and expect it to take time.
- **Get it in writing.** Agree the changes, then ask for a revised letter before you accept.

## Tips

- Stay warm. You're negotiating with your future colleague.
- Silence is fine. You don't have to fill the gap after an answer.
- It's fine to say "I'd like to think about it overnight."

Press **End and get feedback** when you're done.
