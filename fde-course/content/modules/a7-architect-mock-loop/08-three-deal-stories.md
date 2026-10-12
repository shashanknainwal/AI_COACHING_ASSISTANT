---
title: "Round 5a: Write Your Three Deal Stories"
type: written
minutes: 45
sections:
  - key: technical_win
    label: 1. A technical win
    prompt: "A deal or project where your technical work changed the customer's decision. The situation with its numbers, what you specifically did (discovery, design, proof of concept, eval, security review), what the customer decided, and what you'd do the same way again."
    words: [150, 350]
  - key: lost_deal
    label: 2. A lost deal you handled well
    prompt: "A deal you lost, or advised the customer not to pursue. Why it was lost, the moment you saw it coming, what you did about it, how you left the relationship, and what you changed afterwards."
    words: [150, 350]
  - key: failed_poc
    label: 3. A proof of concept that failed
    prompt: "A proof of concept or pilot that missed its success criteria. What the criteria were and who agreed them, what the results showed, what you told the customer and your own team, and what you'd design differently."
    words: [150, 350]
rubric:
  - name: Specific and quantified
    points: 25
    lookFor: "Each story has real numbers: deal or contract size range, volumes, baseline and result, timeline, the eval set size, cost. Names the stakeholders by role (CISO, account executive, VP of operations). No generic 'we delivered value'."
  - name: Clear personal role
    points: 20
    lookFor: "Separates what the candidate did from what the team or account executive did, using 'I' for their own actions. The technical contribution is concrete: the question they asked, the design choice, the eval they built, the risk they raised."
  - name: Technical substance
    points: 20
    lookFor: "Shows architect-level judgement in each story: why an approach was chosen or rejected, how success criteria were set up front, how security or data constraints were handled, what the numbers meant. A technical interviewer could ask three follow-ups from each story."
  - name: Ownership and honesty
    points: 20
    lookFor: "The lost deal and the failed proof of concept own the candidate's part of what went wrong without blaming the customer, sales or the model. Shows telling a customer or their own team an unwelcome truth. No story where everything was someone else's fault."
  - name: Learning and reflection
    points: 15
    lookFor: "Each story ends with a specific change in behaviour or method (for example 'I now agree a stop criterion before any POC starts') rather than a platitude."
passScore: 70
graderNotes: "These must be the candidate's own experiences. Anthropic's candidate AI guidance draws the line at invented experience, and the course does too. If a candidate has no pre-sales history, adjacent experience is acceptable and should be graded normally when it is labelled as such: an internal platform team 'selling' to internal customers, consulting, a startup founder selling to enterprises, a support engineer escalation that turned into a renewal. Mark down stories that read as invented or generic (no numbers, no named roles, no tension). Mark down a 'failed POC' story that is really a success story with a minor hiccup, and a 'lost deal' story that blames the customer or sales entirely; cap 'Ownership and honesty' at 8 in either case. Mark down confidential details that a real candidate shouldn't share (named customers under NDA, exact contract values): reward ranges and anonymised descriptions instead. Reward stories that show the candidate recommending against their own company's product when it was right."
anchors:
  - label: weak
    expect: [0, 45]
    answer:
      technical_win: "I helped close a big deal with a bank by showing them a great demo. They loved it and signed. It was a team effort and everyone did a great job."
      lost_deal: "We lost a deal because the customer chose a cheaper competitor. Sales didn't push hard enough on price. Nothing we could do."
      failed_poc: "Our POC failed because the customer's data was bad. We told them to clean their data and come back."
  - label: strong
    expect: [75, 100]
    answer:
      technical_win: "A regional insurer (contract in the low six figures a year) wanted to automate claim intake. In discovery I asked how they measured keying errors today; nobody knew. I proposed a two-week baseline on 400 claims before any build, which showed 6% field errors at 9 minutes a claim. Our POC hit 97% field accuracy on a frozen 400-claim set with low-confidence fields routed to people, at 2 cents a claim in model cost. The CFO approved because the comparison was against their own measured baseline, not our demo. I'd do the baseline-first step again."
      lost_deal: "A logistics company wanted an agent to auto-issue carrier credits up to $5,000. My account executive wanted to say yes. I told the VP that without an approval step and an audit trail their finance controls team would block it in month two, and proposed approval above $100. A competitor promised full automation and won. I sent the VP a short note with the controls checklist, and we stayed in touch. Nine months later they asked us back after an audit finding. I learned to bring the controls team into the first meeting instead of the third."
      failed_poc: "A manufacturer's POC on maintenance-ticket routing missed its agreed 90% routing accuracy: we reached 81% on 300 tickets. Error analysis showed half the misses came from two categories that their own agents disagreed on 30% of the time. I presented it as a miss, not a near-win, and recommended fixing the taxonomy before any rollout. They paused. My mistake: I'd agreed the target without measuring human agreement first. Now I measure inter-rater agreement before setting a threshold."
---

Round 5 of the architect loop is a pre-sales experience deep dive: a hiring manager asks about deals you've actually worked on, and keeps asking until the story either holds or falls apart. This lesson is the preparation. Lesson 09 is the interview, and the hiring manager will have read what you write here.

Questions about past customer work, including deals that went wrong, are reported for solutions and customer-facing roles across the labs this course covers (**Reported**; see modules C1 and C5). The three-story structure below is our practice design, not a lab's script.

## Why these three stories

A pre-sales hiring manager wants evidence of three things, and each story tests one:

| Story | What it shows |
|---|---|
| **A technical win** | Your technical work changed a decision. You can explain the mechanism, not just the outcome. |
| **A lost deal handled well** | You can lose without burning the relationship, and you can tell a customer, or your own account executive, an unwelcome truth. |
| **A failed proof of concept** | You set honest success criteria, reported a miss as a miss, and changed your method afterwards. |

Most candidates prepare the first and avoid the other two. The second and third are where trust is built, because they're hard to fake.

## Rules for the stories

- **They must be real.** Anthropic's [candidate AI guidance](https://www.anthropic.com/candidate-ai-guidance) says first drafts should be your own and draws the line at invented experience (**Official**). Write these yourself. You can ask Claude to critique a draft afterwards.
- **No pre-sales title? Use adjacent experience and say so.** An internal platform team winning adoption from other teams, a consulting engagement, a founder selling to enterprises, an escalation that saved a renewal. Label it plainly: "This was an internal customer, but the dynamics were the same."
- **Protect confidential details.** Use ranges ("low six figures") and descriptions ("a regional insurer") instead of names and exact contract values. Interviewers respect that.
- **Numbers in every story.** Volume, baseline, result, timeline, eval size, cost. If you don't remember exactly, say "about".
- **Say "I" for what you did.** "We" hides your contribution. The account executive's work is theirs; say so.

## A structure that holds up under follow-ups

For each story: **situation** (with two numbers), **the moment** (the decision point or the risk you spotted), **what you did** (specific actions), **result** (with a number), **what changed** (in how you work now). Aim for two minutes spoken. The written version can be a little longer, because the hiring manager will use it to pick follow-ups.

If you built a story bank in C5 ("Building Your Story Bank"), start from it. These are the customer-facing versions.

When you submit, Claude grades your stories against the rubric below. Then go to lesson 09, where Teodor will ask about them.
