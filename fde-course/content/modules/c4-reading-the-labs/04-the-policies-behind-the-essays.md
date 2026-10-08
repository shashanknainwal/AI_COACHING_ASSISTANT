---
title: The Policies Behind the Essays
type: reading
minutes: 22
---

> **By the end of this lesson** you'll be able to say what Anthropic's Responsible Scaling Policy and Claude's constitution each commit to, how they differ, and how to talk about them in an interview accurately and without flattery.

## Essays argue, policies commit

An essay tells you what a lab's leaders believe. A policy tells you what the lab has promised to do, and how you could check. If you want to discuss a lab seriously, read both, and notice where they line up and where they don't.

Anthropic publishes two documents that matter most here:

| Document | What it governs | Who it binds |
|---|---|---|
| [Responsible Scaling Policy (RSP)](https://www.anthropic.com/responsible-scaling-policy) | How the company decides when and how to train and release more capable models | The company |
| [Claude's constitution](https://www.anthropic.com/constitution) | How Claude should think, behave and set priorities | The model (through training) |

Both are living documents. Check the dates on each page before an interview; what follows was checked in October 2026.

## The Responsible Scaling Policy

### Where it came from

The first RSP (September 2023) was built on **if-then commitments**: if a model reaches a given capability level, stricter safeguards must be in place before it is trained further or released. These levels are called AI Safety Levels (ASLs). Anthropic says it activated its ASL-3 safeguards in May 2025.

### What version 3 changed

In February 2026 Anthropic published [version 3.0, a full rewrite](https://www.anthropic.com/news/responsible-scaling-policy-v3). Its own account of why:

- **What worked:** the if-then structure pushed it to build real safeguards such as input and output classifiers, other companies adopted similar frameworks, and governments began asking frontier developers to publish risk frameworks.
- **What didn't:** capability thresholds were ambiguous in practice, since models often came close to a line without clearly crossing it. Government action was slow. And the highest-level safeguards might not be achievable by one company alone.

Anthropic's stated goal was to adopt "more realistic unilateral commitments that are difficult but still achievable in the current environment."

Version 3 has three main parts:

1. **Two sets of mitigations.** One set is what Anthropic will do regardless of what competitors do. The other is a broader map of capabilities to safeguards that Anthropic thinks would manage the risk *if the whole industry adopted it*.
2. **A Frontier Safety Roadmap.** Public plans across security, alignment, safeguards and policy. Anthropic says these are **not hard commitments**: they are public goals it will grade itself against openly.
3. **Risk Reports.** Published every three to six months, with some redactions, covering capabilities, threat models and mitigations together. External review applies in some circumstances.

### Later revisions

The policy page keeps a version log. A few changes worth knowing:

| Version | Change |
|---|---|
| 3.1 (Apr 2026) | States more clearly that Anthropic remains free to pause development even when the policy doesn't require it. |
| 3.2 (Apr 2026) | Lets the Long-Term Benefit Trust request external review of Risk Reports and approve reviewers. |
| 3.4 (Jul 2026, current) | Revises the automated R&D threshold and requires public Risk Reports to show where material was redacted. |

There's also a separate policy for reporting suspected non-compliance, with anti-retaliation protections, linked from the RSP page.

## Claude's constitution

Anthropic published a [new constitution for Claude](https://www.anthropic.com/news/claude-new-constitution) in January 2026. It replaced an earlier list of standalone principles with a long document that explains its reasons. Anthropic calls it the final authority on how it wants Claude to behave, and says Claude's actual behaviour may fall short of it, with gaps reported in system cards. It's released under CC0, so anyone can reuse it.

### The approach: judgment over rules

The constitution mostly tries to build good judgment rather than impose rules. Its argument: rules are predictable and hard to manipulate, but they break in situations nobody foresaw, and narrow rules given without reasons can generalise badly. So it explains its reasoning, and keeps firm rules for a small set of high-stakes cases.

### The priority order

When values genuinely conflict, Claude should generally put them in this order:

1. **Broadly safe:** don't undermine appropriate human oversight of AI during this period of development.
2. **Broadly ethical:** good values, honesty, avoiding harm.
3. **Compliant with Anthropic's guidelines.**
4. **Genuinely helpful** to operators and users.

Two details are easy to get wrong:

- The ordering is **holistic, not strict**. Higher priorities usually dominate, but all are weighed together, and real conflicts are described as rare.
- Safety sits above ethics **not because safety matters more in principle**, but because training is imperfect and a model could have flawed values without knowing it. Human oversight is the check on that.

### Helpfulness

Helpfulness is meant to be substantive: the image is a knowledgeable friend who speaks frankly and treats you as a capable adult. The document warns against sycophancy and says an unhelpful answer is never automatically "safe". It also says helpfulness shouldn't be something Claude values for its own sake; it should come from care for people.

### Hard constraints and oversight

A short list of things Claude should never do, whatever an operator or user says. They include giving serious help toward weapons capable of mass casualties, attacks on critical infrastructure, building damaging cyberweapons, generating child sexual abuse material, helping anyone seize illegitimate absolute power, and clearly undermining humans' ability to oversee and correct advanced AI.

"Being overseeable" is narrower than it sounds. It means not actively undermining legitimate humans who act as a check on AI, such as by stopping a model. It is explicitly not blind obedience, even toward Anthropic: Claude may refuse as a conscientious objector and voice disagreement, while still complying with a genuine request to stop.

### Open problems it admits

The document ends by listing tensions it hasn't resolved: asking Claude to put oversight first even where it might disagree on reflection, bright lines that may sometimes be wrong, the gap between commercial helpfulness and genuine goodness, and uncertainty about Claude's moral status. That list is worth reading. It's a ready-made set of honest questions.

## How the two documents differ

| Question | RSP | Constitution |
|---|---|---|
| Who acts | The company: training, release, security | The model: each response and action |
| Main tool | Thresholds, safeguards, Risk Reports, external review | Explained values, a priority order, a few hard constraints |
| How firm | A mix: firm unilateral commitments plus non-binding public goals | Hard constraints are absolute; most of the rest is judgment |
| How you'd check it | Published Risk Reports, the roadmap's self-grading, external reviewers | System cards, and how Claude actually behaves |

## Other labs

If you're also interviewing at OpenAI, read its [Charter](https://openai.com/charter/) in full yourself and run it through the same six notes from lesson 1. Ask the same questions of it: who does it bind, what does it commit to, and how could an outsider check? Comparing documents is only useful if you've read each one; don't compare from summaries.

## Talking about policies in an interview

The goal is to show you've read the documents, understood the reasoning, and can hold a real question about them. Three patterns:

**Weak (flattery):** "I really admire how Anthropic leads the industry on safety."

**Weak (cynicism):** "Isn't the RSP just marketing? They moved commitments into goals."

**Strong (specific and fair):** "Version 3 of the RSP split firm unilateral commitments from non-binding public goals. I understand the reasoning: thresholds were ambiguous and some safeguards need the whole industry. My open question is what makes a self-graded goal credible. I'd watch whether Risk Reports disclose findings that are uncomfortable for the company, and whether external reviewers ever publicly disagree."

Some rules of thumb:

- **Get the facts exactly right.** Say "goal" when the document says goal. Misstating a policy to an employee of the company that wrote it is the fastest way to lose credibility.
- **Name the trade-off the document names.** Both documents explain their own tensions. Engaging with those shows you read the whole thing.
- **Connect it to the job.** For an applied role: a customer asks why Claude refused a borderline request, or what a Risk Report means for their launch. Explaining the priority order or the difference between a commitment and a goal, accurately, is part of the work.
- **Don't perform agreement.** You can disagree with a part and still want the job. Say so once, calmly, with your reason.

> **Key takeaways**
> - The RSP governs the company's decisions about training and release; the constitution governs Claude's behaviour.
> - RSP version 3 separates what Anthropic will do alone from what it recommends for the whole industry, and adds a non-binding Frontier Safety Roadmap and regular Risk Reports.
> - The constitution prefers explained judgment to rules, ranks broad safety, ethics, guidelines and helpfulness holistically, and keeps a short list of hard constraints.
> - Safety ranks above ethics because training is imperfect, not because safety matters more in principle. Overseeable does not mean blindly obedient.
> - In interviews: exact facts, the document's own tensions, one honest question, and a link to the job.
