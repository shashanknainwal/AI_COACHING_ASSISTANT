---
title: "Write It: Should Lumenfold Fine-Tune for Headlines?"
type: written
minutes: 30
contextFrom: ["e10-inference-and-model-choices/03-design-an-inference-serving-tier"]
sections:
  - key: recommendation
    label: Recommendation
    prompt: "One paragraph for Noor: fine-tune or not (or not yet), and the one reason that decides it."
    words: [50, 130]
  - key: ladder
    label: What to try first, and what it would cost
    prompt: "The rungs below fine-tuning you would try first for this workload, in order, with what each could fix. Use the numbers in the brief."
    words: [100, 250]
  - key: data
    label: Data and rights
    prompt: "If a fine-tune were justified later: what training data you would need, how you would check the labels, and what must be confirmed about data rights."
    words: [70, 180]
  - key: eval
    label: The eval that decides
    prompt: "The test set, the baseline, the metrics and the threshold that would change your recommendation. Include cost and latency."
    words: [80, 200]
  - key: platform
    label: Platform and ownership
    prompt: "What you would confirm about fine-tuning options for Claude or open-weight models before promising anything, and who would own the model after launch."
    words: [50, 150]
rubric:
  - name: A clear, justified recommendation
    points: 20
    lookFor: "Gives a direct answer (most strong answers: not yet) tied to the deciding facts in the brief: the task is open-ended and the style guide changes quarterly, prompting hasn't been seriously tried (no examples, default effort), and labels disagree. Doesn't hedge into no answer."
  - name: The ladder, with numbers
    points: 25
    lookFor: "Proposes concrete cheaper steps in a sensible order: few-shot examples from the 2,000 approved headlines, the style guide in a cached system prefix, structured output for the five candidates, explicit effort (for example low on Sonnet 5.5 or Haiku 5.5) measured on the eval, a model comparison. Uses the brief's numbers (volume, latency, cost) to show what each step could save."
  - name: Data quality and rights
    points: 15
    lookFor: "Notices the 71% editor agreement caps achievable accuracy, proposes adjudicated labels or pairwise preferences, asks for production-like inputs and hard cases, and says publisher contracts must allow training use of their headlines."
  - name: An eval that can decide
    points: 25
    lookFor: "A frozen held-out set by publisher and section, the strongest cheap baseline, a metric that fits open-ended output (pairwise editor preference or a calibrated judge checked against editors), cost per accepted headline and p95 latency, and a stated threshold that would change the decision."
  - name: Honest about platforms and ownership
    points: 15
    lookFor: "Does not claim a Claude fine-tuning option exists on a given platform; says it would check current Anthropic and cloud docs. Names open-weight tuning as an alternative with its serving and licence costs. Names an owner and a retraining trigger (the quarterly style-guide change)."
passScore: 70
graderNotes: |
  The brief in the lesson body gives the facts. If the learner's answer to the serving design round (lesson 03) is available, reward consistency with it, but don't require it.
  Mark down: recommending a fine-tune without trying few-shot examples first; ignoring that the style guide changes quarterly; ignoring the 71% label agreement; an eval that uses exact-match on headlines; stating that a specific Claude fine-tuning product exists on a specific platform as fact (cap 'Honest about platforms and ownership' at 5); cost claims without the numbers in the brief; quoting a cost or latency for Sonnet 5.5 or Haiku 5.5 without saying which effort it assumes (deduct up to 4 from 'The ladder, with numbers'). Reward a clear "not yet, here's what would change my mind" over a vague "it depends".
anchors:
  - label: weak
    expect: [0, 45]
    answer: "Yes, Lumenfold should fine-tune Claude on their 2,000 headlines because fine-tuned models are always better at style. They can fine-tune Claude on Bedrock. The data is the headlines. We'll measure accuracy against the editors' headlines with exact match. The ML team will own it."
  - label: strong
    expect: [75, 100]
    answer: "Recommendation: not yet. The style guide changes every quarter and prompting hasn't really been tried: the current prompt has no examples and runs at Sonnet 5.5's default effort (high). A fine-tune would freeze this quarter's style into weights and need retraining four times a year. Ladder: (1) put the style guide and 30 approved headlines from the same section in a cached system prefix (about 6,000 tokens, read at $0.10 per million on Sonnet 5.5 instead of $2); (2) return the five candidates with structured outputs; (3) sweep effort low/medium/high on Sonnet 5.5 and try Haiku 5.5 at medium; at 400,000 requests a month, Haiku 5.5 at about 7,000 input and 600 output tokens (thinking included) is roughly $0.001 a request against roughly $0.02 on Sonnet 5.5 uncached, so the eval decides whether the quality holds. Data: editors agree only 71% of the time, so any label set needs adjudication or pairwise preferences; publisher contracts must allow training use. Eval: 300 held-out articles across publishers and sections, frozen; pairwise editor preference against the current headline, plus a judge calibrated against editors on 100 pairs; cost per accepted headline and p95 under 3 seconds. I'd revisit fine-tuning only if the best prompted setup is still below 60% editor preference after two style-guide cycles. Platform: I'd check current Anthropic and cloud docs for any Claude fine-tuning option before mentioning it; an open-weight model with LoRA is possible but adds serving and licence work. Owner: Noor's team, retraining on each style-guide change."
---

Noor has a new question. Lumenfold's headline suggester gives editors five headline candidates for each article. It runs on Sonnet 5.5. An executive read that fine-tuned models write "more on-brand" and wants to fine-tune. Write Noor a one-page recommendation. Noor and Lumenfold are fictional.

## The brief

- **Volume:** about 400,000 requests a month across 300 publishers. Peak 20 per second.
- **Prompt:** a 300-word instruction, the article (about 6,000 tokens on average), and no examples. Output: five headlines, about 120 visible tokens. Effort isn't set, so Sonnet 5.5 runs at its default, `high`, and thinks before answering. Thinking averages about 500 tokens per request.
- **Quality today:** editors pick one of the five candidates 48% of the time.
- **Data available:** 2,000 headlines editors wrote or approved last quarter, from 40 publishers. When two editors rated the same 200 candidates, they agreed 71% of the time.
- **The style guide** changes every quarter.
- **Latency:** editors want the five candidates within 3 seconds at p95. Today p95 is 4.1 seconds.
- **Prices (per million tokens):** Sonnet 5.5 $2 input, $10 output, $0.10 cache reads. Haiku 5.5 $0.10 input, $0.50 output (prompts up to 100K tokens). Thinking tokens are billed as output.

Your answer to the serving design round is available to the grader as context, if you did it.

## What to cover

Work through the five sections. Use the numbers. Be direct: Noor wants a recommendation, not a survey. Where a fact depends on a platform feature, say you'd confirm it in the current docs.
