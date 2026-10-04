---
title: "Stakeholder Mapping: Power, Interest, and Politics"
type: reading
minutes: 15
---

> **By the end of this lesson you will be able to:**
> - Place every stakeholder on a power/interest grid and pick the right engagement for each
> - Test whether your "sponsor" and "champion" really are one
> - Spot the stakeholder risks that quietly kill engagements, and act on them early

## Software is adopted by people, not companies

You can build exactly the right thing and still fail because the wrong person was surprised by it. A stakeholder map is a simple written picture of **who matters, how much, and what they need from you**. It takes 20 minutes to draft and saves weeks of politics.

## The power/interest grid

Rate each stakeholder on two 1-5 scales:

- **Influence (power):** how much can they help or hurt the engagement? Budget authority, veto power, and control of data all count.
- **Interest:** how much does the outcome affect them day to day?

Then place them in four quadrants:

```
                 INTEREST →
              low (1-2)          high (3-5)
         ┌──────────────────┬──────────────────┐
 high    │  KEEP SATISFIED  │  MANAGE CLOSELY  │
 (3-5)   │  e.g. CISO, CFO  │  e.g. sponsor,   │
INFLUENCE│                  │  champion        │
   ↑     ├──────────────────┼──────────────────┤
 low     │     MONITOR      │  KEEP INFORMED   │
 (1-2)   │  e.g. adjacent   │  e.g. end users, │
         │  teams           │  team leads      │
         └──────────────────┴──────────────────┘
```

| Quadrant | Strategy | Typical cadence |
|---|---|---|
| **Manage closely** | Involve in decisions, no surprises ever | Weekly 1:1 or working session |
| **Keep satisfied** | Short, crisp updates; consult before anything that touches their area | Every two weeks |
| **Keep informed** | Show progress, gather feedback, make them feel heard | Weekly email or demo |
| **Monitor** | Light touch; watch for changes in interest | Monthly note |

People move between quadrants. A security lead with low interest becomes very interested the day you request production data access. Revisit the map every couple of weeks.

## The roles, and how to test them

In Module 1 you met the four roles. Here's how to check you've identified them correctly.

### Executive sponsor

Owns the budget and the business outcome.

**The test:** *Can this person say yes to more budget or more scope without asking someone else?* If not, they're not the sponsor; find out who they'd ask.

**What they need:** evidence the investment is working, in their numbers, in under two minutes of reading.

### Champion

Your day-to-day advocate inside the customer.

**The test:** *Will they spend political capital for this?* A real champion introduces you to people, pushes for data access, and defends the project in meetings you're not in. Someone who is merely friendly and responsive is a **contact**, not a champion.

**What they need:** quick wins they can show, responsiveness, and credit for the success.

### Users

The people whose daily work changes.

**What they need:** to be asked about their workflow early, to see their feedback reflected, and a tool that saves them time in week one, not month six.

### Gatekeepers

Security, IT, legal, procurement, data owners. They can't make the project succeed, but they can stop it.

**What they need:** early involvement, clear documentation (data flows, access needs, retention), and respect for their process and timelines.

## Stance: supporter, neutral, or skeptic

Add a third dimension: how does each person feel about the project right now?

- **Supporters** want it to work. Use them, and don't take them for granted.
- **Neutrals** haven't decided. Most users start here. Win them with early value.
- **Skeptics** have doubts. A skeptic with high influence is the most important person on your map.

Skeptics usually have a reason: a past failed project, fear for their team's jobs, worries about data security, or simply being left out of the decision. **Meet skeptics early and one-on-one.** Ask what would need to be true for them to be comfortable. You'll often learn about a real risk you'd otherwise discover in production. Occasionally a skeptic becomes your strongest champion, because you were the first person who listened.

## Example: Lumen Insurance

Here's a map from the claims-processing engagement you saw in the last exercise.

| Name | Title | Influence | Interest | Stance | Role | Quadrant |
|---|---|---|---|---|---|---|
| Joan Pierce | VP Claims | 5 | 4 | Supporter | Sponsor | Manage closely |
| Marcus Lee | Claims Ops Lead | 3 | 5 | Supporter | Champion | Manage closely |
| Ravi Shah | CISO | 5 | 2 | Skeptic | Gatekeeper | Keep satisfied |
| Adjuster team (12) | Claims Adjusters | 2 | 5 | Neutral | Users | Keep informed |
| Dee Ortiz | Finance BP | 2 | 2 | Neutral | — | Monitor |

What jumps out?

- **Ravi (CISO) is a high-influence skeptic.** He's the biggest risk on the map. Action: book a meeting this week, bring a data-flow diagram, and ask what he needs to approve.
- **The adjusters are neutral users.** Action: sit with two adjusters for an hour each to watch them work, and make them co-designers of the review screen.
- **The sponsor and champion are both supporters.** Good, but there's only one champion. Action: multi-thread (see below).

## Multi-threading: never depend on one person

If all your relationships run through one champion and they go on leave, change jobs, or get reorganized, the engagement stalls overnight. This happens constantly.

**Aim for at least two strong relationships at each level:** two people on the working team, and a relationship with the sponsor that doesn't depend on the champion relaying messages.

## Politics without being political

You'll encounter competing priorities, turf, and people with agendas. A few principles keep you effective and trusted:

- **Be the honest broker.** Share the same facts with everyone. People notice when your story changes depending on who's listening.
- **Never surprise a high-influence stakeholder** in a group setting. Preview bad news one-on-one first.
- **Give credit generously,** especially to your champion and to users who gave feedback.
- **Write things down.** Decisions recorded in a short email are hard to relitigate.

## Putting it into practice

A stakeholder map is a list of people with a few attributes, and the strategy follows mechanically from those attributes. That makes it a perfect thing to encode. In the next exercise you'll write the code that turns a list of stakeholders into a prioritized engagement plan and a list of risks to act on.

> **Key takeaways**
> - Rate stakeholders on influence and interest; the quadrant determines the engagement strategy and cadence.
> - Test your sponsor ("can they say yes to budget?") and champion ("will they spend political capital?").
> - A high-influence skeptic is your biggest risk. Meet them early and one-on-one.
> - Multi-thread: build at least two strong relationships at each level.
