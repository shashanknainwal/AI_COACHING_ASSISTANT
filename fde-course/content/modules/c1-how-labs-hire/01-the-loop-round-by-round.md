---
title: The Loop, Round by Round
type: reading
minutes: 18
---

> **By the end of this lesson** you'll be able to name every round in a frontier-lab interview loop, say what each one tests, and tell an official fact from a candidate rumour.

## Three kinds of claim

Interview processes change, and most of what's written about them comes from candidates, not companies. Throughout this course, every claim about hiring carries one of three labels:

- **Official:** the company says it, on its own site or in a posting.
- **Reported:** several independent candidate accounts agree.
- **Anecdotal:** one or two accounts. Useful colour, not a plan.

When you prepare, put your hours where the official and reported facts are. When a recruiter tells you something different, the recruiter wins.

## Anthropic

| Stage | What happens | Label |
|---|---|---|
| Application | A written answer to a question like "Why Anthropic?". Treat it as your first interview: specific beats impressive. | Reported |
| AI use | Write your own first drafts; Claude may help you refine them. No AI in take-homes or live interviews unless they tell you otherwise. Using Claude to prepare is encouraged. | **Official** |
| Recruiter screen | About 30 minutes on background, motivation, level and team fit. | Reported |
| Online assessment | One progressive Python problem, about four levels, about 90 minutes. Practical code, not puzzles. Module C3 trains this. | Reported |
| Onsite, part 1 | Coding, system design (often LLM infrastructure) and a culture interview. Part 2 is cancelled if part 1 doesn't go well. | Reported |
| Onsite, part 2 | Your experience and goals, plus a deep dive into a project you built. | Reported |
| Culture / values | Run by an employee nominated for it. Several guides call it the round that fails the most candidates. Module C5 trains this. | Reported |
| References and team match | Can add two to four weeks or more. | Reported |

The official piece is worth reading in full: Anthropic publishes [guidance on using Claude during the hiring process](https://www.anthropic.com/candidate-ai-guidance). The short version: be yourself, write first drafts yourself, and assume assessments are AI-free unless told otherwise.

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

These come from Anthropic's postings (official, though wording changes as roles are reposted):

- **Applied AI Engineer:** a technical, customer-facing advisor from discovery through deployment. Builds eval frameworks, pairs with customer engineers, knows prompting, agents and retrieval.
- **Solutions Architect, Applied AI:** pre-sales architecture for large enterprises. Fits Claude into their stack, builds evals, designs architectures that scale.
- **Forward Deployed Engineer, Applied AI:** builds production applications on Claude inside customer systems (MCP servers, sub-agents, agent skills) and spends a real share of time at customer sites.

## A note on this course

This course isn't affiliated with any lab. Every practice question here is original, written in the style of what candidates publicly describe. Don't go looking for leaked questions: they're often wrong, they break the confidentiality candidates agree to, and interviewers can tell when an answer was memorised.

> **Key takeaways**
>
> - Label every hiring "fact" as official, reported or anecdotal, and prepare in that order.
> - Every loop tests four things: practical coding, LLM system design, a project deep dive, and motivation and values.
> - At Anthropic, the written application and the values round matter as much as the code.
