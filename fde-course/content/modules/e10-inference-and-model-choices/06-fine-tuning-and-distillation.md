---
title: "Fine-Tuning and Distillation: When, With What Data, and How You'd Know"
type: reading
minutes: 15
---

> **By the end of this lesson** you'll be able to place fine-tuning and distillation on the ladder of options after prompting and retrieval, say what data each one needs, design the eval that decides, and talk honestly about which options exist for Claude and for open-weight models.

## "When would you fine-tune, then?"

The course has told you "don't fine-tune first" (E6). That's the right default, but it's not an answer when an interviewer asks "so when would you?" A strong answer names the conditions, the data, the eval and the operating cost, and doesn't promise a platform feature you haven't checked.

## The ladder

Climb one rung at a time. Move up only when the eval says the rung below can't reach the target.

| Rung | Changes | Fixes | Doesn't fix |
|---|---|---|---|
| 1. Prompting | Instructions, examples, output format | Most task-definition problems | Missing knowledge |
| 2. Structured outputs, tools | Schema, tool definitions | Format errors, actions | Judgment |
| 3. Retrieval (RAG) | What the model sees per request | Missing or changing knowledge, citations | Style, latency, cost per call |
| 4. Model and effort choice | Which model, how much thinking | Cost and latency within quality | A task the model can't learn from the prompt |
| 5. Fine-tuning | The model's weights | Consistent narrow behaviour, format or style at scale; shorter prompts | Knowledge that changes weekly; anything you can't evaluate |
| 6. Distillation | A smaller model trained on a bigger model's outputs | Cost and latency for one narrow, high-volume task | Breadth; tasks that drift |

Fine-tuning teaches **behaviour**: a format, a label set, a tone, a narrow skill. It's a poor way to teach **facts**. Facts change, a fine-tuned model can't cite where a fact came from, and you'd have to retrain to update it. Use retrieval for facts.

## When fine-tuning is worth it

Look for most of these together:

1. **A narrow, stable task.** For example: tag articles against a fixed 400-label taxonomy, or extract 30 fields from one form type.
2. **High volume**, so a smaller tuned model saves real money, or a **hard latency target** that a bigger model can't meet.
3. **Prompting has plateaued** on a trustworthy eval, and you've tried few-shot examples, structured outputs and a stronger model.
4. **You have the data**, or can get it: hundreds to thousands of high-quality labelled examples for classification or extraction, more for open-ended generation.
5. **Someone will own it.** Retraining when the taxonomy changes, re-evaluating, serving, monitoring and on-call.

If the first or last is missing, stop. A moving task or an unowned model turns a one-off win into permanent debt.

## The data a fine-tune needs

- **Inputs that look like production.** Same length, same messiness, same distribution of edge cases. A model tuned on clean examples fails on real ones.
- **Labels you trust.** Check agreement between labellers on a sample. If two experts agree only 80% of the time, the model can't reliably beat 80%.
- **Coverage of the hard cases**, deliberately oversampled, plus examples of "none of these" or "I can't tell".
- **A held-out test set frozen before training**, never seen by the training run or by anyone tuning hyperparameters. This is the same discipline as E8's frozen test set.
- **Data rights.** Confirm the customer may use the data for training, and where it may be processed.

## Distillation

Distillation trains a small "student" model to imitate a larger "teacher" on one task. In practice: run the teacher over a large set of real inputs, keep the outputs that pass your checks, and fine-tune the student on those.

What to watch:

- **The student inherits the teacher's mistakes.** Filter teacher outputs with validators or graders, and spot-check by hand.
- **Coverage.** The student only learns the inputs you showed it. Out-of-distribution inputs need a fallback route to the big model.
- **Terms of use.** Read the provider's terms before training a model on another model's outputs. Model providers' terms commonly restrict using outputs to build competing models. On the Claude side, the safety classifiers on some models (Claude Haiku 5.5, for example) include a `frontier_llm` refusal category for requests that could assist the development of competing AI models. Check Anthropic's current terms for the exact rules, and get the customer's legal team to confirm.

## The eval decides

Design it before you train:

| Measure | Why |
|---|---|
| Task accuracy on the frozen test set, with a confidence interval | The headline number, compared with the prompted baseline on the same set |
| Accuracy on hard-case and out-of-distribution slices | Fine-tunes often win on average and lose on the tail |
| Cost per correct answer and p95 latency | The reason you tuned in the first place |
| Regression checks on behaviour you didn't train for | Safety, refusals, formatting outside the task |
| Drift over time | A tuned model goes stale when inputs or labels change |

Then compare against the strongest cheap baseline, not the weakest. For example: Haiku 5.5 at `effort: "low"` with 20 good few-shot examples and structured outputs, with prompt caching on the static prefix. A fine-tune that beats a lazy prompt hasn't proved anything.

## What exists for Claude, and for open-weight models

**Claude.** The Claude API skill reference we use for this course documents no fine-tuning option for current Claude models on any platform. Availability has changed over time and differs by cloud platform. Before you mention fine-tuning Claude to a customer, check Anthropic's current docs and the docs for their cloud platform. Until you've checked, say "I'd confirm whether that's offered for the model and platform you're on." On the Claude side, the levers you can count on are prompting, retrieval, structured outputs, tools, model choice and effort.

**Open-weight models.** These are published models you can download and run, in sizes from about 1B to hundreds of billions of parameters. You can fully fine-tune them, or use parameter-efficient methods such as LoRA, which trains small adapter matrices and leaves the base weights frozen. Then you serve them yourself or through a hosting provider. The tradeoffs:

- **For:** full control, data stays where you put it, low cost per token at high volume, and you can tune for one narrow task.
- **Against:** you own serving, scaling, security patches and evals (lesson 03 showed what serving takes). A small model is usually weaker on anything outside its task. Each model has its own licence terms, so read them.

A common hybrid is a tuned small open-weight model for one high-volume narrow task, with a Claude model as the fallback and for everything else. That's Lumenfold's setup in lesson 03.

> **Key takeaways**
> - Fine-tuning teaches behaviour, not facts. Use retrieval for facts.
> - Fine-tune only for a narrow, stable, high-volume task, after prompting has plateaued on a trustworthy eval, with trusted data and an owner.
> - Freeze the test set before training, and compare against the strongest cheap baseline.
> - Distillation copies a teacher's mistakes and is bound by the teacher's terms of use. Filter its outputs and read the terms.
> - Don't promise fine-tuning for Claude on a given platform without checking current docs. Open-weight models can be tuned, but you own everything after that.
