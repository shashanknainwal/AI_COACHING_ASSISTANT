---
title: Resume Bullets That Survive the Screen
type: reading
minutes: 15
---

> **By the end of this lesson** you'll be able to write a resume bullet as a decision, a real metric and its LLM relevance, cut the words that make a screener skip a line, and use Claude on your resume the way Anthropic's guidance allows.

## What the screen is looking for

Nobody publishes how their resume screen works, so this section is **General**: widely shared hiring practice, not a lab's process.

- **A first pass is fast.** A recruiter usually reads the top third of the page and skims the rest for the posting's must-haves. If your strongest evidence is in bullet seven of your third job, assume it isn't seen.
- **The reader is matching against the posting.** Not keyword stuffing: matching. "Built evaluation frameworks" in the posting and "built an eval set of 600 labelled tickets that gated every prompt change" in your resume is a match a human sees in a second.
- **Every line is a promise for later.** Anything on the page can become a deep-dive question (module C5). A bullet you can't defend for five minutes is a liability, not an asset.

One or two pages is normal for experienced engineers (**General**). Length matters less than whether the top third makes the case.

## The rule on AI help

Anthropic's [candidate AI guidance](https://www.anthropic.com/candidate-ai-guidance) covers resumes directly (**Official**; module C1 lesson 3 has the full summary):

- **Write the first draft yourself.** Then Claude can help you refine it.
- The guidance gives comparing your resume with the job description, to find what to highlight, as an example of good use.
- Using Claude to quantify **real** impact is fine. Using it to **invent** experience is not.

In practice: write every bullet yourself, rough is fine. Then ask Claude for critique ("which bullet has no decision in it?", "which number would a sceptical engineer ask about?"), and make the changes yourself. Never let it fill in a number you don't know. Other labs haven't published equivalent rules (C1), so use the same standard everywhere.

## The bullet formula: decision + metric + LLM relevance

Most weak bullets describe a duty: "Responsible for the document processing pipeline." That tells the reader you were near something. A strong bullet answers three questions.

| Part | The question it answers | Example fragment |
|---|---|---|
| **Decision** | What did *you* choose, build or change? | "Replaced a regex extractor with a schema-validated Claude call and a human review queue" |
| **Metric** | What changed, measured how, compared with what? | "cut manual review from 40% of invoices to 9% over 6 weeks" |
| **LLM relevance** | Why does this matter for an applied AI role? | "with a 300-invoice golden set that gated every prompt change" |

Put together, for a fictional candidate:

> Replaced a regex invoice extractor with a schema-validated Claude call and a human review queue, cutting manual review from 40% to 9% of invoices in 6 weeks; built the 300-invoice golden set that gated every prompt change.

Not every bullet needs all three. Your top three bullets should.

### Before and after

These are fictional examples. Write your own from your own work.

| Before | Problem | After |
|---|---|---|
| "Leveraged cutting-edge GenAI to drive transformational efficiency gains." | No decision, no number, all buzzwords. | "Built a retrieval assistant over 12,000 support articles; first-contact resolution rose from 61% to 70% in a 4-week A/B test." |
| "Worked on evals for our chatbot." | "Worked on" hides what you did. | "Wrote the chatbot's first eval suite (220 cases, rubric-graded) and found the refund-policy failure that blocked launch." |
| "Improved latency by 50%." | 50% of what? From what to what? | "Cut p95 response time from 6.1 s to 2.8 s by streaming, caching the system prompt and moving classification to a smaller model." |
| "Led a team of engineers on a key customer project." | Leadership without a decision or outcome. | "Led 3 engineers integrating our API into a bank's case system; scoped it down to two workflows, shipped in 9 weeks, renewed at 2x." |

## Metrics: real, sourced, defensible

This is where people get into trouble.

- **Use numbers you can source.** A dashboard, a ticket count, a before-and-after measurement, an A/B test, a cost report. If someone asked "how did you measure that?", you should have an answer in one sentence.
- **If you don't have the number, go and find it.** Ask a former colleague, check an old report, count the rows. C1 lesson 3 calls this one of the best uses of Claude: asking what evidence would make the impact clearer, then looking it up yourself.
- **If you can't find it, use a different kind of number.** Scale (12,000 articles, 3 customers, 40 requests a second), time (shipped in 9 weeks) or count (220 eval cases) are honest substitutes for an outcome you never measured.
- **Never estimate an outcome you didn't measure and present it as measured.** "About" is fine for a figure you measured roughly. "Saved $2M" from a guess is not, and the deep dive will find it.

## Words that cost you

Cut these, or replace them with what they're hiding (**General**):

| Word | Replace with |
|---|---|
| leveraged, utilised | used, built, chose |
| cutting-edge, state-of-the-art, transformational | the actual technique or the actual change |
| responsible for, worked on, involved in | the verb for what you did |
| passionate, results-driven, dynamic | delete; let the bullets show it |
| GenAI solutions, AI-powered | name the system: "a retrieval assistant", "an extraction pipeline" |
| synergy, stakeholders (alone) | name the people: "the CISO", "the support team" |

## What each role's bullets should show

Use the role you chose in lesson 1.

| Role | Your top bullets should show |
|---|---|
| Applied AI Engineer | An LLM system you built and measured; an eval that changed a decision; helping another team's engineers succeed |
| Applied AI Architect | A design you owned across someone else's constraints; a recommendation you made to executives or a buying committee, and its result |
| Forward Deployed Engineer | Shipping inside someone else's systems, fast; integrations; a production incident you handled; your second language in a real project |

## Mind your confidentiality

You can describe the shape of work for an employer or customer without naming the customer or revealing their numbers: "a top-10 US insurer" and "cut handling time by roughly a third" are common ways to do it (**General**). If you're unsure what your agreements allow, ask, or describe the work at a higher level. Never put a former employer's confidential figures on a public resume.

## Before you move on

Pick the three bullets that matter most for your role. The next lesson grades your rewrite of them.

> **Key takeaways**
>
> - Assume the top third of the page is all a first reader sees, and that every line can become a deep-dive question (**General**).
> - Anthropic's guidance is **Official**: write the first draft yourself, then use Claude to refine and to find what to highlight. Never let it invent experience or numbers.
> - A strong bullet is a decision, a real metric and its LLM relevance. Your top three should have all three.
> - Use numbers you can source. If you can't find an outcome, use scale, time or count instead of a guess.
> - Replace buzzwords with the thing they're hiding.
