---
title: "Field Realities: Travel, Access and Juggling Customers"
type: reading
minutes: 12
---

> **By the end of this lesson you will be able to:**
> - Read the travel line in a posting and ask the right follow-up questions
> - Plan the first two weeks around access lead times instead of code
> - Work productively on a customer's machine without admin rights
> - Run two or three customers at once without dropping one
> - Behave like the vendor's face in the room, including when you disagree

Most of this course is about engineering. This lesson is about the parts of the job that decide whether the engineering gets a chance: being on site, getting access, and keeping several customers happy at once. It's short because the advice is simple. Following it under pressure is the hard part.

## Travel: read each posting

The Anthropic Forward Deployed Engineer posting we read in October 2026 said 25 to 50 percent customer travel (**Official**, from the job posting; see Module C1 lesson 01). Treat that as a fact about one posting, not about the role everywhere. Travel shares differ by company, team, region and seniority, and they change. Read the line in each posting you apply to, and ask the recruiter:

- Is that an average across the year, or bursts around launches?
- Is it mostly one long-running customer, or many short visits?
- Who books and pays, and what's the policy on weekends?
- Is there a home office, and how often are you expected in it?

If 50 percent travel would break your life, that's a reason to ask early, not a weakness to hide.

## Access takes longer than code

Lesson 01's six walls each have a lead time. In practice, your first two weeks look like this:

| Day | What you're really doing |
|---|---|
| 1 | Kickoff. Get the names of the people who own network, identity, security review, change management and data access. File every access ticket the same day |
| 2–5 | Work in your own sandbox on synthetic or de-identified data. Write the environment doc. Chase tickets daily, politely, with the business reason attached |
| 6–10 | Access arrives in pieces. Test the riskiest wall first (usually the proxy or the private network path) with a real request, not a slide |

Two habits keep this from eating your timeline:

- **Make the waiting visible.** Put every access ticket on the same status page as the engineering work, with an owner at the customer and a date. When the go-live slips because the firewall change took three weeks, nobody should be surprised.
- **Never route around access.** No personal laptops on their network, no copying data to your machine "just for today", no shared credentials. One shortcut can end the engagement and your company's relationship with the customer.

## Working on their machine

Many regulated customers give you a virtual desktop or a locked laptop. Expect no admin rights, no Docker, a fixed Python version, blocked package installs and sometimes no copy and paste.

- **Ask for the tools by name and version in week one**, through their software request process. Include the business reason.
- **Keep your code runnable without admin rights:** user-level installs, pure-Python dependencies where possible, no assumption of Docker on the desktop.
- **Agree how code moves** between your repository and theirs. A pull request into their Git server is normal. A USB stick is not.
- **Keep notes outside their systems only if their policy allows it.** Customer data, credentials and screenshots of their systems never leave.

## Juggling two or three customers

FDEs commonly carry more than one account. The failure mode is predictable: the loudest customer gets all your time and the quiet one churns.

- **One page per customer:** status, next milestone, open asks, who's waiting on whom. Update it on a fixed day each week.
- **Protect blocks of time.** Deep work for customer A on Tuesday and Thursday mornings, for example, with a stated response time for everything else.
- **When two escalations land at once, triage on impact, not volume.** Who is harmed, how badly, and how soon? Then tell both customers what you're doing and when they'll hear from you next. A clear "I'm on Brightline's outage first; you'll have my answer on your question by 3 p.m." is better than half-attention for both.
- **Use your own team.** Your manager, the account team and other FDEs exist for exactly this. Asking for help with a clear ask is part of the job.

Lesson 13 is a role-play of exactly this situation.

## You're the vendor's face

On site, you represent your company in every hallway conversation. Three rules:

- **Don't promise what isn't yours to promise.** Roadmap dates, pricing and contract terms belong to other people. Say who can answer and by when.
- **Disagree in private, align in public.** If the customer's staff engineer thinks your design is wrong, have that argument in a review, with evidence. In front of their VP, present one plan.
- **Respect their engineers.** They'll run the system after you leave. A territorial reviewer is often someone who has been burned by a vendor before. Treat their review as free quality assurance, and make them a co-owner. Lesson 14 practises this.

> **Key takeaways**
> - Read the travel line in each posting and ask what it really means. One posting's 25 to 50 percent isn't a rule for every role.
> - File every access ticket on day one, track them where everyone can see, and never route around access.
> - On locked machines, ask for named tools early and keep your code runnable without admin rights.
> - With several customers, keep one page each, protect time, and triage escalations on impact, then tell everyone what happens next.
> - You're the vendor's face: no promises outside your authority, disagree in private, treat their engineers as future owners.
