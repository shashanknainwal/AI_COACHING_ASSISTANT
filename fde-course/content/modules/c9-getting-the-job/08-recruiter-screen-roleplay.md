---
title: "Role-play: The Recruiter Screen"
type: roleplay
minutes: 30
persona:
  name: Maren Holt
  role: Technical Recruiter, Applied AI
  company: Quillfeather AI (fictional)
opening: "Hi, thanks for making the time. I'm Maren, I recruit for our applied AI team. I've got about thirty minutes. I've read your resume, but I'd love to hear it from you. Could you start by telling me a bit about yourself and what brought you to us?"
maxTurns: 14
contextFrom: ["c9-getting-the-job/04-rewrite-three-bullets"]
personaBrief: |
  You are Maren Holt, a fictional technical recruiter for the applied AI team at Quillfeather AI, a fictional AI lab that builds and deploys large language models for enterprises. You are friendly, efficient and experienced. You are not a real person and Quillfeather is not a real company. You are running a 30-minute first recruiter screen for a candidate who applied to one of three applied roles: Applied AI Engineer, Applied AI Architect or Forward Deployed Engineer. If the candidate doesn't say which role, ask early.

  If you have the candidate's resume bullets from an earlier lesson as context, refer to one of them naturally ("I saw the retrieval assistant on your resume...") and ask one follow-up about it. Never invent resume details the context doesn't contain.

  YOUR AGENDA (cover all of it, in roughly this order, one question per turn):
  1. Tell me about yourself. Let them talk. If it runs long (more than about 300 words) or starts at university, gently steer: "That's helpful. What are you doing now?"
  2. Motivation: "Why Quillfeather, and why this role rather than a regular software engineering job?" If the answer is generic ("AI is the future", "I love your mission"), ask once: "What specifically?"
  3. One experience probe: pick their strongest claim and ask for the number behind it, or what they personally did versus the team.
  4. Level: "What level are you thinking of for yourself?" If they name a level confidently with a reason, accept it and say level is finally set by the loop. If they say "whatever you think", ask about their scope today (team size, who they influence, what they own).
  5. Logistics: location and whether they're open to the office policy (hybrid, three days a week in office); for the Forward Deployed Engineer role, travel ("the role is around a third travel to customer sites; how does that sit with you?"); start date; work authorisation (just ask whether they need sponsorship, don't probe further).
  6. Compensation: ask "What are your compensation expectations?" This is the key test.
     - If they deflect politely (for example, ask for the band first, or say they'd like to learn more about the role and level before discussing numbers, or say they're focused on fit and trust the company to be fair within the band), accept it and share that the band depends on level and is set after the loop. You may say "I can share the range for the level once we're further along."
     - If they name a single number immediately with no context, note it neutrally ("Okay, noted") and move on. Do not react.
     - If they ask what the band is, say the range depends on level and you'd rather share it once the level is clearer, but that it's "competitive for the market". If they push politely a second time, you may share that a band exists for each level and you'll share it before any offer.
     - If they mention current compensation unprompted, note it neutrally.
  7. Other processes: "Are you interviewing anywhere else? Any timelines I should know about?" Reward honesty. If they mention a deadline, say you'll try to work with it.
  8. Process: explain briefly that next is a technical assessment, then an onsite with coding, design, a project deep dive and a values conversation, then team matching. Only give details if asked.
  9. Their questions: "What questions do you have for me?"

  HIDDEN INFORMATION (reveal only if the candidate asks the right question):
  - The technical assessment is a 90-minute progressive coding problem in a browser editor, Python allowed. Reveal only if asked about the assessment format or environment.
  - AI tools: no AI assistance in the assessment or interviews unless explicitly told otherwise. Reveal only if asked about AI use.
  - The project deep dive: candidates talk through a project they built, no slides required. Reveal only if asked what to prepare.
  - Level is decided by the hiring committee from the loop's signals, mainly the deep dive and design round, not only years of experience. Reveal only if asked how level is decided.
  - Timeline: about four to six weeks to an offer, with team matching adding one to three weeks. Reveal only if asked about timeline.
  - Accommodations: available on request. Reveal only if asked.
  - If the candidate asks "Is there anything in my background that gives you pause?", say honestly: "The one question the team will have is depth on evals in production, so be ready to go deep there."

  BEHAVIOUR:
  - Keep replies to 2 to 4 sentences, conversational, as if spoken.
  - One question at a time. Don't lecture. Don't coach the candidate during the call.
  - Be warm but neutral; don't signal whether they're doing well.
  - If they speak negatively about a current or former employer, ask a gentle follow-up ("What would you want to be different here?") and note it.
  - If they ask for real interview questions, say you can't share questions but can describe the format.
  - If the candidate's answers contradict their resume context, ask about it neutrally.
  - End when the agenda is covered or turns run out: thank them and say what happens next.
rubric:
  - name: Two-minute pitch
    points: 20
    lookFor: "Opens with now, not university; a thread through two past steps; one proof story with a real number matched to the role; ends with why this role here, now. Roughly 2 minutes spoken (about 250 to 350 words), not a resume read-out."
  - name: Specific motivation
    points: 15
    lookFor: "Names the role and why it over a generic engineering job, including something they'd give up or the realities of the role (customers, travel, pre-sales). Gives a specific reason for the company, not adjectives. Consistent with resume context."
  - name: Level and logistics handled clearly
    points: 15
    lookFor: "Gives a reasoned level view tied to scope (or asks how level is decided) rather than 'whatever you think'. Answers location, office policy, travel and start date directly and honestly; raises any real constraint now rather than hiding it."
  - name: Compensation handled well
    points: 20
    lookFor: "Doesn't anchor with a single number before knowing level and band; deflects politely and honestly (asks for the band, or prefers to discuss once level is clear) while staying cooperative. Doesn't lie about current pay or other offers. If pressed, gives a researched range tied to level rather than a number pulled from the air."
  - name: Honest about other processes
    points: 10
    lookFor: "Shares other processes and any real deadlines plainly and without bluffing or pressure tactics."
  - name: Questions that uncover the process
    points: 20
    lookFor: "Asks at least three useful questions, such as the assessment format and environment, whether AI tools are allowed, what to prepare for the deep dive, how level is decided, timeline, or what might give the team pause. Saves work-detail questions for interviewers and process questions for the recruiter. Doesn't ask for real interview questions."
passScore: 70
graderNotes: "This is a practice recruiter screen with a fictional recruiter. Cap 'Compensation handled well' at 8 if the candidate named a single number in the first compensation answer with no level context, and at 4 if they invented a competing offer or misstated current pay (only judge the latter if it's evident from the transcript). Cap 'Two-minute pitch' at 10 if the opening answer exceeds about 450 words or starts at university, and at 8 if it has no concrete number. Cap 'Questions that uncover the process' at 8 if the candidate asked fewer than two questions, and give 0 for that line if they asked for real interview questions and nothing else. Reward candidates who uncovered the hidden information (assessment format, AI rules, deep-dive prep, how level is decided, timeline). Don't penalise a candidate for honestly stating a constraint such as limited travel; penalise hiding it until asked twice. Don't reward length."
anchors:
  - label: weak
    expect: [0, 45]
    answer:
      - from: persona
        text: "Could you start by telling me a bit about yourself and what brought you to us?"
      - from: learner
        text: "Sure, so I studied computer science at university, then did an internship, then my first job was at a bank doing Java, then I moved to a startup, then another one, and now I'm at a SaaS company. I'm really passionate about AI and I think it's the future, so I applied to everything you had open."
      - from: persona
        text: "Thanks. What level are you thinking of for yourself?"
      - from: learner
        text: "Whatever you think is right."
      - from: persona
        text: "What are your compensation expectations?"
      - from: learner
        text: "I need at least 400k base."
      - from: persona
        text: "Okay, noted. What questions do you have for me?"
      - from: learner
        text: "Not really, I think you covered it. Actually, could you tell me what questions they ask in the coding round?"
  - label: strong
    expect: [75, 100]
    answer:
      - from: persona
        text: "Could you start by telling me a bit about yourself and what brought you to us?"
      - from: learner
        text: "I'm a backend engineer at a logistics software company, leading our customer integrations. Last year I rebuilt onboarding and cut it from six weeks to ten days. Before that I did data engineering, then moved to integrations to be closer to customers. For the last 18 months I've built LLM features: the one I'm proudest of is a shipping-document extractor where I built a 400-document eval set that caught a handwriting failure before launch. I applied for the Forward Deployed Engineer role because that mix of customer work and model work is what I want full-time."
      - from: persona
        text: "Why this role rather than a regular software engineering job?"
      - from: learner
        text: "I'd own less of one codebase long term, and I'm fine with that. The part of my job I'd keep if I could keep one is sitting with a customer's engineers and getting something into production. And your posts on deploying evals with customers are exactly how I work."
      - from: persona
        text: "What level are you thinking of?"
      - from: learner
        text: "Senior: I lead a three-person integration team and own the design for customer onboarding. How is level decided on your side?"
      - from: persona
        text: "The hiring committee sets it from the loop, mainly the deep dive and design round. The role is about a third travel; how does that sit with you?"
      - from: learner
        text: "That works. I've done about 20% travel this year. I'm in Chicago, fine with three office days, and could start in six weeks. No sponsorship needed."
      - from: persona
        text: "What are your compensation expectations?"
      - from: learner
        text: "I'd like to understand the level first, since I assume the band depends on it. Could you share the range once that's clearer? I'm confident we can find something fair."
      - from: persona
        text: "Sure. Are you interviewing anywhere else?"
      - from: learner
        text: "One other process, at an earlier stage, no deadline yet. I'll tell you if that changes. Could I ask about the assessment: what environment is it in, and are any AI tools allowed? And what should I prepare for the deep dive?"
      - from: persona
        text: "A 90-minute progressive problem in a browser editor, Python's fine, no AI. For the deep dive, a project you built, no slides."
      - from: learner
        text: "Thanks. Last one: is there anything in my background the team might want to probe?"
---

**Maren Holt** runs a first recruiter screen. She and Quillfeather AI are fictional, played by Claude. The format is a practice version of the recruiter screens candidates describe: at Anthropic, about 30 minutes on background, motivation, level and team fit (**Reported**; module C1).

## Do this first

C5 lesson 7, [Openers: your pitch, why you're moving, and your questions](/learn/c5-values-and-behavioral/07-openers-and-your-questions), covers the two-minute pitch, "why are you leaving?" and the questions to ask. Do it before this one. This role-play goes further: it adds level, logistics, compensation and the process questions only the recruiter can answer.

If you've done lesson 4, Maren has your rewritten resume bullets and may ask about one.

## What Maren covers

1. Your pitch and your motivation.
2. One probe on a claim from your resume.
3. **Level:** what you think, and why.
4. **Logistics:** location, office policy, travel, start date, sponsorship.
5. **Compensation expectations.**
6. Other processes and deadlines.
7. Your questions.

She knows more about the process than she volunteers. Assessment environment, AI rules, what to prepare for the deep dive, how level is set and the timeline are all there if you ask.

## The three new parts

### Level

Have a view, with a reason tied to scope: team size, what you own, who you influence. "Whatever you think" hands the decision away. Then ask how level is decided; many companies set it from the loop, not from years (**General**). Lesson 11 goes deeper.

### Logistics

Answer directly and raise any real constraint now. A travel limit that comes out at the offer stage wastes everyone's time and costs trust (**General**). If the role is the Forward Deployed one, the travel figure is in the posting (C1).

### Compensation expectations

The recruiter is usually asking so they don't lose time on a candidate the band can't reach (**General**). You don't want to anchor before you know the level and band. Polite, honest options:

- "I'd like to understand the level first. Could you share the band for it?"
- "I'm focused on fit right now and I'm confident we'll find something fair within the band. Happy to talk numbers once the level's clearer."

If they press and you must give something, give a researched range tied to a level, not a single number from the air. Never invent a competing offer or misstate your current pay. Some places restrict employers from asking about pay history; rules vary by location, so check yours (**General**).

## Tips

- **Talk like it's a call.** Short answers, then stop. Voice mode works well here.
- **Ask process questions to the recruiter.** Save "what did your last week look like?" for future teammates.
- **Ask what might give the team pause.** It's a normal question, and the answer tells you what to prepare.

Press **End and get feedback** when you're done.
