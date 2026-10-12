---
title: The Loop, Round by Round
type: reading
minutes: 22
---

> **By the end of this lesson** you'll be able to name every round in a frontier-lab interview loop, say what each one tests, and tell an official fact from a candidate rumour.

## Three kinds of claim

Interview processes change, and most of what's written about them comes from candidates, not companies. Throughout this course, every claim about hiring carries one of three labels:

- **Official:** the company says it, on its own site or in a posting.
- **Reported:** several independent candidate accounts agree.
- **Anecdotal:** one or two accounts. Useful colour, not a plan.

When you prepare, put your hours where the official and reported facts are. When a recruiter tells you something different, the recruiter wins.

The tables below were last checked on 2026-10-08, and Anthropic's [careers page](https://www.anthropic.com/careers) on 2026-10-10. Processes change, so confirm the details for your role with your recruiter.

## Anthropic

| Stage | What happens | Label |
|---|---|---|
| Application | A written answer to a question like "Why Anthropic?". Treat it as your first interview: specific beats impressive. | Reported |
| AI use | Write your own first drafts; Claude may help you refine them. No AI in take-homes or live interviews unless they tell you otherwise. Using Claude to prepare is encouraged. | **Official** |
| Recruiter screen | About 30 minutes on background, motivation, level and team fit. | Reported |
| Online assessment | One progressive Python problem on CodeSignal, about four levels, about 90 minutes. Practical code, not puzzles. Module C3 trains this. | Reported |
| Coding tools | Anthropic's careers page says technical interviews use live coding tools such as Colab and CodeSignal, that you can look things up, and that you should be comfortable enough with basic syntax and the standard library that they don't eat your time. All interviews run over Google Meet. | **Official** |
| Onsite, part 1 | Coding, system design (often LLM infrastructure) and a culture interview. Part 2 is cancelled if part 1 doesn't go well. | Reported |
| Onsite, part 2 | Your experience and goals, plus a deep dive into a project you built. | Reported |
| Culture / values | A culture interview sits in the first onsite loop. Module C5 trains this. | Reported |
| Who runs it, how hard it is | One newsletter says an employee nominated for the role runs it. Several career guides call it the round that fails the most candidates. Guides aren't candidate reports, and Anthropic publishes no pass rates. | Anecdotal |
| References and team match | Can add two to four weeks or more. | Reported |

The official piece is worth reading in full: Anthropic publishes [guidance on using Claude during the hiring process](https://www.anthropic.com/candidate-ai-guidance). The short version: be yourself, write first drafts yourself, and assume assessments are AI-free unless told otherwise. Lesson 3 of this module goes through it in detail.

## OpenAI (forward deployed engineering)

| Stage | What happens | Label |
|---|---|---|
| Recruiter screen | Background, motivation, your views on AI and customer-facing work. | Reported |
| Technical screen | Two 60-minute screens, or a take-home with a review call. | Reported |
| Virtual onsite | Four to six interviews: practical coding, LLM system design, and a project deep dive where you defend something you built. | Reported |
| Assessed on | Scoping ambiguous problems, building systems around models, proving they work with evals, and talking to non-technical stakeholders. | Reported |

One candidate describes a week-long take-home case study followed by a panel walking through it from several angles, and an AI-enabled coding screen. That's **anecdotal**: one account, one team.

## Perplexity

| Stage | What happens | Label |
|---|---|---|
| Screens | An HR screen, then a project-style online assessment (multi-part, predefined tests) or live coding. | Reported |
| Onsite | Four or five rounds: domain-flavoured coding (tokenisation, streaming), AI system design (RAG, latency, caching), and a hiring-manager deep dive. | Reported |
| Senior roles | A technical interview with a founder. | Reported |

## What every loop has in common

Strip away the company names and four rounds keep coming back:

1. **Practical coding.** Build and extend working code quickly. Not LeetCode trivia.
2. **System design for LLM products.** Requirements, architecture, evals, failure modes, cost.
3. **A deep dive on something you built.** You defend your own decisions under follow-up questions.
4. **Motivation and values.** Why this lab, why now, and how you behave when the right thing is expensive.

That's the backbone of this course. The shared core trains all four; your track adds the role-specific depth.

## The applied roles, from the job postings

Postings are **Official**: the company wrote them. But they're reposted often and the wording drifts, so treat the details below as a snapshot and read the live posting for the role you apply to.

Where to look: Anthropic's [open roles page](https://www.anthropic.com/jobs) groups these jobs under **Applied AI**. On 2026-10-10 it listed Applied AI Engineer, Applied AI Architect and Forward Deployed Engineer roles in several cities. Our research on 2026-10-08 read the postings through job-board mirrors: [Applied AI Engineer](https://jobs.accel.com/companies/anthropic/jobs/81748657-applied-ai-engineer), [Solutions Architect, Applied AI](https://jobs.accel.com/companies/anthropic/jobs/69412282-solutions-architect-applied-ai) and [Forward Deployed Engineer](https://jobs.generalcatalyst.com/companies/anthropic/jobs/89778489-forward-deployed-engineer). Mirrors can lag the company's own board.

| Role | What the posting describes | Hard requirements we saw | Label |
|---|---|---|---|
| **Applied AI Engineer** | A technical, customer-facing advisor from discovery through deployment. Builds eval frameworks, pairs with customer engineers, knows prompting, agents and retrieval. | 4+ years in a technical role. | Official (posting, read 2026-10-08) |
| **Solutions Architect, Applied AI** (titled Applied AI Architect on the live listing) | Pre-sales architecture for large enterprises. Fits Claude into their stack, builds evals, designs architectures that scale. | We didn't record a years figure. Read the live posting. | Official (posting, read 2026-10-08) |
| **Forward Deployed Engineer, Applied AI** | Builds production applications on Claude inside customer systems (MCP servers, sub-agents, agent skills), white-glove deployment. | 25–50% travel. Python plus at least one more programming language. | Official (posting, read 2026-10-08) |

Two cautions. A years figure is a guide, not a wall: postings describe the person they'd ideally hire. And titles move: the same job can be reposted under a new name, so search by team (Applied AI) as well as by title.

### Turn the posting into a gap list

Before you plan your prep (lesson 5), copy the live posting for your target role and do this in ten minutes:

1. **List every requirement** as one line: "builds eval frameworks", "Python plus one more language", "travel 25–50%".
2. **Write your evidence next to each one.** A project, a number, a customer. If you'd struggle to talk about it for two minutes, it isn't evidence yet.
3. **Mark each line** green (strong evidence), amber (some evidence) or red (none).
4. **Map the reds to modules.** Evals, agents and retrieval live in your track's modules. Customer work lives in the FDE and architect tracks. A missing second language is a red you can't fix in six weeks, so say so honestly if asked.
5. **Check the logistics lines too.** Travel share, location and office expectations decide whether you want the job at all. Ask the recruiter if anything is unclear.

The amber lines are where your prep hours pay off most.

> **From my loop**
>
> When I interviewed at Amazon, the round that surprised me was the bar raiser. I expected a spread of questions. Instead, the interviewer took one story and spent 40 minutes on it: what I personally decided, what the data said, what I'd do differently. Every "we" answer got redirected to "what did *you* do?"
>
> My advice: prepare 6 to 8 stories, and for each one know your own actions, one metric, and one thing you'd change. Practice with someone who interrupts you. Write "I" in your notes and cut every "we."

## A note on this course

This course isn't affiliated with any lab. Every practice question here is original, written in the style of what candidates publicly describe. Don't go looking for leaked questions: they're often wrong, they break the confidentiality candidates agree to, and interviewers can tell when an answer was memorised.

> **Key takeaways**
>
> - Label every hiring "fact" as official, reported or anecdotal, and prepare in that order.
> - Every loop tests four things: practical coding, LLM system design, a project deep dive, and motivation and values.
> - At Anthropic, the written application and the values round matter as much as the code.
