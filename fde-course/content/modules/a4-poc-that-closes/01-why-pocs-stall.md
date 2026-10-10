---
title: "Why Proofs of Concept Stall, and the Plan That Prevents It"
type: reading
minutes: 18
---

> **By the end of this lesson** you'll be able to name the six usual reasons an AI proof of concept stalls, write a one-page POC plan that prevents them (success criteria with baselines, scope, timeline, data access, decision owner and exit rules), and answer the interview question "how would you run a POC for this customer?" with a concrete plan instead of a list of good intentions.

## The problem: pilot purgatory

A proof of concept (POC) is supposed to answer one question: **should this customer put this system into production?** Many never answer it. The demo goes well, people are impressed, the POC is extended "to look at a few more things", and three months later nobody can say whether it worked. People call this **pilot purgatory**.

You'll see survey numbers claiming that most AI pilots never reach production. The exact percentages vary a lot by survey and by what counts as "production", so don't quote one in an interview unless you've read the method. The pattern itself is not in dispute, and an architect is expected to prevent it.

Grace Liu, the Principal architect who coaches this track (a fictional character), puts it this way: *"A POC that ends without a decision has failed, even if the model was great. My job is to make the decision easy and on time."*

## Six ways a POC stalls

| Cause | What it looks like in week 6 | What prevents it |
|---|---|---|
| **No agreed definition of success** | "It looks promising." Each stakeholder has a different bar, and the bar moves after the results come in. | Written success criteria, signed before any work starts |
| **No baseline** | "92% accurate" with nothing to compare it to. Is the current process at 80% or 99%? | Measure today's process in weeks 1–2 |
| **Demo-driven evaluation** | An executive tries ten prompts in a meeting and forms an opinion. One bad answer sinks it, or one great one oversells it. | A frozen eval set from real data, graded the agreed way |
| **Data and access arrive late** | Week 4 and the team still has synthetic documents because the real ones need a security review. | Data access and the security review are week-0 tasks with named owners and dates |
| **No decision owner** | The champion loves it but can't sign. The person who can sign was never in the room. | One named decision owner, and a readout meeting booked on their calendar at kickoff |
| **No path to production** | It works, then someone asks about cost at full volume, the integration, the security review, or who runs it. | The plan includes a production sketch, a cost-at-scale estimate and the next phase's budget question |

Notice that only one of the six is about the model. Most stalls are **process failures**, which is why this job sits with the architect and not only with the engineers building the prototype.

## The POC plan: one page, signed

Write the plan before kickoff and get the decision owner to agree to it in writing. One page is enough. These are the sections:

### 1. The business outcome and the question

One or two sentences. *"Thornbury Mutual wants to cut claim-intake keying time. The POC answers: can automated extraction meet the accuracy bar on our real claims, at a cost and speed that make a production rollout worth funding?"* The question is what you'll answer at the readout. If you can't write it, you're not ready to start.

### 2. Scope: in and out

Name the documents, channels, languages, user groups and systems in scope, and **explicitly** list what's out. "Out of scope: handwritten forms, the Spanish-language portal, writing back to the claims system." Out-of-scope lists prevent the slow creep that turns a six-week POC into a six-month one.

### 3. Success criteria, with baselines

This is the core. Use a table. Each row has:

| Field | Why it matters |
|---|---|
| **Metric** and **how it's measured** | "Field accuracy" means nothing until you say: which fields, on which cases, graded by whom, against what labels |
| **Baseline** | Today's number for the same metric, measured the same way |
| **Target** and direction | "At least 95%" or "at most 20 seconds" |
| **Must-have or nice-to-have** | A missed must-have is a no-go. A missed nice-to-have is a note in the readout |
| **Owner** | The person on the customer side who accepts the number |

Good criteria share a few traits:

- **Few.** Three to six. Twelve criteria guarantee that something is always red and nothing is decisive.
- **Tied to the business outcome.** Accuracy matters because rework costs money. Say how.
- **Quality, operations and safety together.** At least one quality metric, latency and cost (operations), and any hard guardrail (for example "zero personal data written outside the claims system"). A system that's accurate but too slow or too expensive doesn't close.
- **Sized for the evidence.** A 95% target measured on 40 cases is a coin toss: the 95% interval on 38 out of 40 runs from about 83% to 99%. Agree the eval set's size along with the target. The E4 module (*Evals as Engineering*) covers the statistics; as an architect you need the rough sizes near a 95% target. The interval is lopsided there: 95 out of 100 gives a Wilson interval of about 89% to 98% (roughly 6 points down, 3 up), and 380 out of 400 gives about 92% to 97% (roughly 2 to 3 points either way). The familiar "±10 at 100 cases" holds only near a 50% pass rate.
- **A borderline rule.** Decide up front what happens when a result lands right at the line. "Within 2% of the target counts as borderline, and borderline must-haves mean a conditional go with a fix plan" is a sentence that saves a week of argument later. You'll build exactly this rule in the next exercise.

### Why baselines matter so much

Without a baseline, every result is ambiguous. With one, it's a comparison the customer already understands.

| Metric | Without a baseline | With a baseline |
|---|---|---|
| Field accuracy 94.8% | "Is that good?" | "Your double-keying process measures 93.0%. We're 1.8 points better and 0.2 below the target we agreed." |
| Cost per claim $0.11 | "Cheap, I guess?" | "Manual keying costs $4.80 a claim in loaded labour." |
| p95 latency 14 s | "Fine?" | "Claims wait about 4 hours for keying today." |

Two warnings. First, **measure the baseline the same way you'll measure the system**: same cases, same graders, same definition. A baseline from a vendor's slide or a three-year-old audit isn't comparable. Second, many customers **don't know** their baseline. Measuring it is often the most valuable thing the POC produces, so budget a week for it.

### 4. Eval set and grading

Where the cases come from (real, recent, representative, including the hard ones), how many, who labels them, how disagreements are settled, and when the set is **frozen**. Freeze the test set before anyone tunes a prompt against it. Keep a separate development set for iteration.

### 5. Data access and security

What data, from which system, approved by whom, by what date. Start the security review in week 0, in parallel. Data access is the most common reason a POC slips, and it's almost never the model team's fault. It still lands on your timeline. (Module A2 covers the security review itself.)

### 6. Timeline with checkpoints

A typical shape for a time-boxed POC. The length is a negotiation; what matters is that it's fixed and has checkpoints.

| Week | Milestone | Checkpoint question |
|---|---|---|
| 0 | Plan signed, data request and security review started, readout booked | Do we have a decision owner and a date? |
| 1–2 | Real data in place, baseline measured, eval set labelled and frozen | Is the baseline what everyone assumed? |
| 3–4 | Build and iterate on the development set | Are we trending toward the targets? If clearly not, stop early |
| 5 | Final run on the frozen test set, cost and latency measured | Results are what they are |
| 6 | Readout and decision | Go, conditional go, or no-go |

### 7. Decision owner and exit criteria

Name **one** person who makes the call, and write the decision rules down now:

- **Go:** every must-have met. The next phase starts on the agreed date with the agreed budget.
- **Conditional go:** must-haves met or borderline, with a written fix plan and a date to re-measure.
- **No-go:** any must-have clearly missed. You say so, and you say what it would take to change the answer.
- **Incomplete:** a must-have couldn't be measured. Agree in advance whether that means an extension (with a new date) or a stop.

Writing the no-go rule down feels like inviting failure. It's the opposite. It tells the customer you'll be honest with them, and it gives your champion something to point to when someone asks "how will we know if this is a waste of money?"

### 8. What happens after "go"

One paragraph: the next phase (often a limited production pilot with real users), its rough cost, who funds it and when that budget decision gets made. A POC that succeeds into a budget cycle that closed last month still stalls.

## Scoping the POC: prove the risky part

A POC is cheap compared with production, so don't spend it on things that are already known to work. Ask: **what is the riskiest assumption in this deployment?** Then design the POC to test it.

| If the riskiest assumption is... | ...the POC should focus on |
|---|---|
| The model can do the task on their messy documents | Accuracy on a real, frozen eval set |
| The workflow will actually change (people will use it) | A shadow run or a small user pilot, measuring adoption and time saved |
| It integrates with a legacy system | A thin end-to-end slice through the real integration, not a polished UI |
| It's affordable at their volume | Measured tokens per task and a cost-at-scale model |
| Security will approve it | The security review, run in parallel from day one |

A common mistake is to prove the model works (the part most likely to succeed) and leave integration and adoption (the parts most likely to fail) for "phase 2".

## How this shows up in interviews

Solutions architect and applied architect loops are thinly documented in public. Candidate accounts suggest a case discussion and a presentation are common (**Anecdotal**), and a POC plan is a natural thing to be asked for in either. Anthropic's architect postings describe working with customers from discovery through deployment and building evals (**Official**, from the job postings). Ask your recruiter what the case round looks like.

What strong answers do: they start with the decision the POC must support, write criteria with baselines and a must-have split, size the eval set, name a decision owner, and say what happens on a no-go. Weak answers describe the prototype in detail and never say how anyone will decide.

### Practice prompts (original, in the style of a case round)

- "A regional bank wants a six-week POC of an assistant that drafts responses to card disputes. Walk me through your POC plan. What are your success criteria?"
- "The customer's CIO says 'just show us something impressive in two weeks and we'll take it from there.' How do you respond?"
- "Halfway through your POC, the customer's data team says real documents won't be available for another month. What do you do?"
- "Your POC hit three of four must-haves. The fourth missed by one point. What do you recommend?"

Answer one out loud in under four minutes. Then check: did you name a baseline, a decision owner and an exit rule?

> **Key takeaways**
>
> - A POC exists to support a decision. One that ends without a decision has failed, however good the model was.
> - Most stalls are process failures: no agreed success, no baseline, demo-driven judging, late data, no decision owner, no path to production.
> - Write a one-page plan before kickoff: the question, scope in and out, 3–6 success criteria with baselines and a must-have split, the eval set, data access, a timeline with checkpoints, one decision owner, and written go / conditional / no-go / incomplete rules.
> - Measure the baseline the same way you'll measure the system. Often the baseline is the most useful thing the POC produces.
> - Size the eval set with the target, and agree a borderline rule up front.
> - Spend the POC on the riskiest assumption, which is often integration or adoption, not the model.
