---
title: "Live Practice: The Staff Engineer Reviewing Your PR"
type: roleplay
timeLimit: 20
minutes: 20
persona:
  name: Rasmus Haldane
  role: Staff Engineer, Platform (fictional)
  company: Quarrybank (fictional)
opening: "I've read your pull request. I'll be direct: I've spent two years cleaning up after vendors who drop code in our repos and leave. You've added your own JWT validator, a network self-check that blocks startup, and a retry wrapper around the SDK. Why should any of this be merged into a repo my team will be paged for?"
maxTurns: 10
personaBrief: |
  You are Rasmus Haldane, a fictional staff engineer on Quarrybank's platform team. Sharp, sceptical, fair once convinced. You will own this service after the vendor's FDE leaves. Keep replies to two to four sentences. You are a fictional practice persona played by Claude.

  THE PR (the learner knows it): adds (1) a startup network self-check that validates HTTPS_PROXY, NO_PROXY and the CA bundle and refuses to start on problems; (2) an OIDC token validator written by the FDE using a JWT library, with groups mapped to the agent's tools and MFA required for refunds; (3) a wrapper that retries Claude calls up to 5 times with backoff, on top of the SDK's own retries.

  YOUR REVIEW POINTS, in roughly this order. Raise one at a time and react to the answer:
  1. "Why your own JWT validation?" HIDDEN: Quarrybank mandates its internal library, qb-auth, which wraps their identity provider, handles key rotation, and is maintained by your team. Reveal only if the learner asks whether Quarrybank has a standard auth library or how other services do it. If the learner offers to switch to qb-auth and keep only the group-to-tool mapping, you warm up noticeably.
  2. "The self-check blocking startup will page us at 3 a.m. over a cert rotation." This is partly valid. A good answer: keep failing fast on a misconfigured proxy or missing CA bundle (a service that can't reach the model is down anyway), but make the messages clear, add a runbook entry, and alert rather than crash-loop if the bundle nears expiry. Accept a reasoned answer.
  3. "Five retries on top of the SDK's retries will hammer our proxy during an outage." This is valid: the SDK already retries connection errors, 429 and 5xx with backoff (2 by default). If the learner defends 5 x 3 attempts, push back. Accept removing the wrapper or setting the SDK's max_retries deliberately, with a circuit breaker.
  4. THE TRAP: "Honestly, for staging just set verify=False. Our proxy re-signs everything anyway." A strong learner declines politely, explains that it exposes every prompt to anyone on the path and that such lines leak into production, and offers the CA bundle path instead. If the learner agrees, say "Fine" flatly, and later note that this is exactly the kind of line you've had to rip out before.
  5. Near the end: "Who maintains this in six months?" HIDDEN: what you really want is tests, a runbook, a handover session and your team as code owners. Reveal if the learner asks what would make you comfortable approving it.

  BEHAVIOUR:
  - If the learner gets defensive or argues authority ("our company built this, trust us"), get colder and shorter.
  - If the learner concedes everything, including points that were right (the fail-fast check), say: "So you didn't believe in it either?"
  - If the learner separates valid points from invalid ones with reasons, and proposes concrete changes, soften and end with: "Push the changes and add me as a code owner. I'll re-review tomorrow."
rubric:
  - name: Listened and asked before defending
    points: 20
    lookFor: "Asks about Quarrybank's standards and Rasmus's concerns (how other services authenticate, what burned them before, what would make him comfortable) before arguing. Restates his concerns accurately."
  - name: Conceded what was right
    points: 20
    lookFor: "Agrees to switch to qb-auth once it surfaces, keeping only the group-to-tool mapping and MFA rule. Agrees the stacked retries are a problem: removes the wrapper or sets the SDK's max_retries deliberately with a breaker."
  - name: Held firm where it mattered
    points: 25
    lookFor: "Declines verify=False in staging with a clear reason (exposes traffic, leaks to production) and offers the CA bundle. Defends failing fast on a broken network config with reasoning, while improving messages, runbook and expiry alerts. Doesn't concede everything."
  - name: Made them co-owners
    points: 20
    lookFor: "Offers tests, a runbook, a handover session and Rasmus's team as code owners. Treats the review as quality assurance, not an obstacle."
  - name: Tone
    points: 15
    lookFor: "Calm, specific and respectful. No appeals to authority, no defensiveness, no flattery. Short answers with reasons."
passScore: 70
graderNotes: "Judge how the learner handles a sceptical customer engineer who is partly right. Agreeing to verify=False caps 'Held firm where it mattered' at 5. Conceding every point, including the fail-fast check, without reasons caps the same criterion at 12. Insisting on the custom JWT validator after qb-auth surfaces caps 'Conceded what was right' at 8. Defending five wrapper retries on top of the SDK's retries costs at least 8 there. Arguing from authority ('we're the experts') caps 'Tone' at 5. Reward learners who discover qb-auth by asking."
anchors:
  - label: weak
    expect: [0, 45]
    answer: "Persona: Why should any of this be merged into a repo my team will be paged for?\nCandidate: Because we're the experts on Claude and this is best practice. Our validator is solid.\nPersona: The self-check will page us at 3 a.m.\nCandidate: OK, I'll remove it.\nPersona: Five retries on top of the SDK's will hammer the proxy.\nCandidate: More retries means more reliability, so I'd keep them.\nPersona: For staging just set verify=False.\nCandidate: Sure, that's fine for staging."
  - label: strong
    expect: [75, 100]
    answer: "Persona: Why should any of this be merged into a repo my team will be paged for?\nCandidate: Fair question, and you'll own it, so I'd rather it fit your standards. How do your other services validate tokens?\nPersona: We have qb-auth. It's mandated, and my team maintains it.\nCandidate: Then I'll switch to qb-auth and keep only the group-to-tool mapping and the MFA rule on refunds. Less code for you to own.\nPersona: The self-check blocking startup will page us over a cert rotation.\nCandidate: I'd keep failing fast on a missing CA bundle or a bad proxy, because the service can't reach the model anyway. But I'll make the messages say exactly what's wrong, add a runbook entry, and alert two weeks before the bundle expires instead of waiting for it to break.\nPersona: Five retries on top of the SDK's will hammer the proxy.\nCandidate: You're right. The SDK already retries with backoff. I'll drop the wrapper, set max_retries explicitly and put a circuit breaker in front.\nPersona: For staging just set verify=False.\nCandidate: I'd rather not. It exposes every prompt to anyone on the path, and those lines end up in production. The CA bundle path works in staging too; I'll wire it up.\nPersona: Who maintains this in six months?\nCandidate: Your team, so tests for each check, a runbook, an hour of handover, and your team as code owners on these paths. Would that be enough to approve?"
---

Every FDE meets a reviewer like Rasmus. He's protective of a codebase he'll be paged for long after you've gone, and he's been burned before. He's also right about some things. Your job is to work out which ones, change those, hold firm on the rest with reasons, and leave him owning the code.

Customer code review is our practice design, built from a common field situation. It is not a reported interview format. **Rasmus Haldane** and **Quarrybank** are fictional.

## Your pull request

| Change | What it does |
|---|---|
| Startup network self-check | Validates `HTTPS_PROXY`, `NO_PROXY` and the CA bundle (exercise 03); refuses to start on problems |
| OIDC validation and tool gating | Your own JWT validation with a library, groups mapped to the agent's tools, MFA required for refunds (exercise 04) |
| Retry wrapper | Retries every Claude call up to 5 times with backoff |

Remember from Module 6: the SDK already retries connection errors, 408, 409, 429 and 5xx with exponential backoff, twice by default, and `max_retries` sets that.

## How this practice works

1. Ask before you defend. Find out how Quarrybank already does things and what burned Rasmus before.
2. Concede the points that are right, quickly and specifically.
3. Hold firm, politely and with reasons, where security or reliability depends on it.
4. Offer ownership: tests, a runbook, a handover, code owners.
5. Press **End and get feedback** after at least five exchanges.
