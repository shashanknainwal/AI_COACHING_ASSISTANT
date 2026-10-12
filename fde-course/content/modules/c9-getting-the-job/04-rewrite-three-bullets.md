---
title: "Write It: Rewrite Three Resume Bullets"
type: written
minutes: 30
sections:
  - key: target
    label: 1. Target role and what it asks for
    prompt: "Name the role you chose in lesson 1 and paste or paraphrase the two or three must-haves from the posting that your bullets should answer."
    words: [20, 120]
  - key: bullet1
    label: 2. Bullet one
    prompt: "Paste the original bullet. Then your rewrite (one or two lines). Then one line starting 'Source:' saying where the number comes from."
    words: [30, 150]
  - key: bullet2
    label: 3. Bullet two
    prompt: "Same format: original, rewrite, 'Source:' line."
    words: [30, 150]
  - key: bullet3
    label: 4. Bullet three
    prompt: "Same format: original, rewrite, 'Source:' line."
    words: [30, 150]
rubric:
  - name: A decision you made
    points: 25
    lookFor: "Each rewrite starts with a specific action the candidate personally took (built, replaced, chose, scoped, led), naming the system or change. No 'worked on', 'responsible for', 'helped with' or team-only 'we' with no personal role."
  - name: Real, sourced metrics
    points: 25
    lookFor: "Each rewrite has a number with a baseline or a scale (from X to Y, N cases, N customers, N weeks), and the Source line makes it believable (a dashboard, an A/B test, a report, a count). Where no outcome was measured, the candidate uses an honest scale, time or count figure instead of an estimated outcome."
  - name: Relevant to the target role
    points: 20
    lookFor: "The three bullets together answer the must-haves named in section 1, and at least two show LLM-relevant work (evals, prompting, retrieval, agents, integrating a model into a system) or, for an architect, design across a customer's constraints. Matches the posting's language naturally, without keyword stuffing."
  - name: Plain and concise
    points: 15
    lookFor: "Each rewrite fits in about two lines. No buzzwords (leveraged, cutting-edge, transformational, synergy, passionate, GenAI solutions). Concrete nouns and verbs."
  - name: Honest and defensible
    points: 15
    lookFor: "Nothing looks invented or inflated. Claims match the Source line. The candidate could plausibly defend each bullet for five minutes in a deep dive. Confidential details are generalised rather than exposed."
passScore: 70
graderNotes: "This is a resume exercise under Anthropic's 'first draft yourself' rule; grade the content, not polish. Watch for invented metrics: if a rewrite reports a precise outcome (for example '37% cost reduction', '$2.4M saved') and its Source line is missing, vague ('estimated', 'I think', 'roughly what it felt like') or doesn't support the number, treat that metric as unsourced. If two or more bullets have unsourced outcome metrics, cap 'Real, sourced metrics' at 8 and 'Honest and defensible' at 5, and say why in the feedback. A bullet with no number at all scores no more than 3 of the metric points for that bullet. Mark buzzword-heavy rewrites down hard under 'Plain and concise': three or more buzzwords across the bullets caps it at 5. If the rewrites are identical to the originals or only reworded, cap 'A decision you made' at 8. Do not reward length. If the Source line names a confidential customer and their figures, deduct 3 from 'Honest and defensible' and suggest generalising."
anchors:
  - label: weak
    expect: [0, 45]
    answer:
      target: "Applied AI Engineer. They want AI experience and Python."
      bullet1: "Original: Worked on chatbot. Rewrite: Leveraged cutting-edge GenAI to drive a 45% improvement in customer satisfaction across the business. Source: estimated."
      bullet2: "Original: Responsible for data pipelines. Rewrite: Spearheaded transformational, AI-powered data synergies that saved $3M. Source: my guess based on team size."
      bullet3: "Original: Helped with evals. Rewrite: We built a world-class evaluation framework. Source: n/a"
  - label: strong
    expect: [75, 100]
    answer:
      target: "Applied AI Engineer. Must-haves I'm answering: builds eval frameworks for LLM systems; pairs with customer engineers; prompting, agents and retrieval."
      bullet1: "Original: Worked on the support chatbot. Rewrite: Built a retrieval assistant over 12,000 help-centre articles with hybrid search and a reranker; first-contact resolution rose from 61% to 70% in a 4-week A/B test. Source: the A/B test readout our analytics team published internally."
      bullet2: "Original: Helped with evals. Rewrite: Wrote the assistant's first eval suite (220 rubric-graded cases from real tickets) and wired it into CI; it caught a refund-policy regression that would have shipped. Source: case count from the repo; the regression is in our incident log."
      bullet3: "Original: Supported partner integrations. Rewrite: Paired with engineers at 3 partner companies to integrate our extraction API, writing the reference implementation they copied; median integration time fell from 5 weeks to 2. Source: integration start and go-live dates in our CRM, which I pulled for a quarterly review."
---

Hana's note: *"Send me three bullets, before and after, and tell me where every number comes from. If a number has no source, I'll assume a recruiter will ask and you won't have an answer."*

Hana Ostrowski and Ossian Careers are fictional. The grading is done by Claude against the rubric below.

## The task

Choose the three bullets that matter most for the role you picked in lesson 1. For each one, paste the original, write the rewrite, and add a **Source:** line.

A rewrite should usually be:

1. **A decision you made:** the verb and the system.
2. **A metric:** a before-and-after, or an honest scale, time or count.
3. **Its relevance:** why it matters for this role, ideally LLM work.

## The rules

- **Your own first draft.** Anthropic's [candidate AI guidance](https://www.anthropic.com/candidate-ai-guidance) asks you to write the first draft of your application yourself, and lets Claude help refine it afterwards (**Official**). This exercise follows the same rule. After you're graded, you can ask Claude for critique on your next draft.
- **No invented numbers.** If you don't know a figure, the Source line should say what kind of number you used instead ("count of eval cases in the repo"). An unsourced outcome metric is marked down hard. That's deliberate: in a real loop, the deep dive is where it gets found.
- **Generalise confidential details.** "A top-10 US insurer" is fine. Their internal figures aren't.

## What gets marked down

- Duties instead of decisions ("responsible for", "worked on").
- Buzzwords in place of the actual technique.
- Precise outcomes with no source, or a source that doesn't support them.
- Bullets that don't connect to the must-haves you listed.

Submit when you're ready. You'll get a score per rubric line and the one change to make first. Revise and resubmit as often as you like.
