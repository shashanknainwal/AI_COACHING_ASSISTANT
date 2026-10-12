---
title: "Training: How a Base Model Becomes an Assistant"
type: reading
minutes: 18
---

> **By the end of this lesson** you'll be able to describe pretraining, supervised fine-tuning, RLHF and Constitutional AI (RLAIF), and explain why sycophancy, reward hacking and over-refusal come out of that pipeline, in terms a customer or an interviewer will accept.

## Why it matters in an interview

"Why does the model refuse this harmless request?" "Why does it agree with whatever the user says?" "Why did it write a test that always passes?" These are training questions in disguise. At Anthropic in particular, a credible safety conversation assumes you know what Constitutional AI is as a method (**Official** that Anthropic publishes this research; how often it comes up in loops is **Anecdotal**). Practice prompts here are original.

You don't need the maths. You need the stages, what each one optimizes, and what tends to go wrong.

## Stage 1: pretraining

A model with billions of parameters learns to predict the next token over a huge corpus of text and code. The result is a **base model**: it has absorbed grammar, facts, styles, code and reasoning patterns, but it isn't an assistant. Give it "What is the capital of France?" and it might continue with three more quiz questions, because that's a plausible continuation.

What to say:

- **Knowledge comes from here, and it has a cutoff.** The model knows nothing after its training data ends unless you give it tools or retrieval.
- **It learned to sound plausible, not to be right.** Next-token prediction rewards fluent continuations. That's a root cause of hallucination (lesson 08).
- **It's the expensive stage.** Most of the compute goes here.

## Stage 2: supervised fine-tuning (SFT)

The base model is trained further on curated examples of the behaviour you want: instructions paired with good responses, dialogues, tool-use transcripts. It learns the **format** of an assistant: answer the question, follow the instruction, stop at the end of the turn.

SFT is limited by its data. It can only imitate the demonstrations, and writing demonstrations of the best possible answer is slow and costly.

## Stage 3: RLHF

Reinforcement learning from human feedback, popularized by OpenAI's InstructGPT paper ["Training language models to follow instructions with human feedback"](https://arxiv.org/abs/2203.02155) (Ouyang et al., 2022), works in three steps:

1. The model writes several answers to a prompt. Human raters rank them.
2. A **reward model** is trained to predict which answer raters prefer.
3. The assistant is optimized with reinforcement learning to produce answers the reward model scores highly, with a penalty for drifting too far from the SFT model.

Comparing answers is easier than writing perfect ones, so RLHF scales better than SFT alone. But the model is now optimizing a **proxy**: what raters (and the reward model that imitates them) prefer, not what is actually true or good.

## Stage 4: Constitutional AI and RLAIF

Anthropic's paper ["Constitutional AI: Harmlessness from AI Feedback"](https://arxiv.org/abs/2212.08073) (Bai et al., 2022) replaces much of the human harmlessness labelling with AI feedback guided by a written list of principles. In outline:

1. **Supervised phase.** The model answers, then critiques its own answer against a principle and revises it. The revised answers become fine-tuning data.
2. **RL phase.** The model compares pairs of answers against the principles, and those AI preferences train the reward model. This is **RL from AI feedback (RLAIF)**.

Why it matters: the principles are explicit and inspectable, it needs far fewer human labels for harmful content, and the paper reported models that were less evasive while staying harmless (they explain objections instead of just refusing).

Keep two things distinct in an interview:

- **Constitutional AI is a training method**, from the 2022 paper.
- **Claude's constitution** is a published document describing the values and priorities Anthropic wants Claude to have (C4 lesson 4 covers the published policies). The method uses principles; the document is the current statement of them. Don't present one as the other.

Modern pipelines combine these stages with others (more RL on verifiable tasks such as code and maths, safety training, red-teaming). Details for any specific production model aren't fully public, so say "in outline" when you describe them.

## What goes wrong, and why

| Failure | Where it comes from | What you do in a product |
|---|---|---|
| **Sycophancy**: agreeing with the user, flattering, caving when pushed | Raters tend to prefer answers that agree with them and feel pleasant. Anthropic's ["Towards Understanding Sycophancy in Language Models"](https://arxiv.org/abs/2310.13548) (Sharma et al., 2023) found it across assistants trained with human feedback | Don't leak your preferred answer in the prompt; ask for evidence; evaluate with prompts that push back on correct answers |
| **Reward hacking**: satisfying the measure, not the goal | RL optimizes whatever is rewarded. If a coding reward is "tests pass", special-casing the tests can score as well as fixing the bug | Grade outcomes, not proxies; review agent diffs; in evals, check for tests edited or hard-coded |
| **Over-refusal** | Harmlessness training can generalize too broadly to benign requests that look like harmful ones | Give legitimate context in the system prompt (who the users are, why), measure false refusals on an eval set, report clear cases to the provider |
| **Confident errors** | Pretraining rewards plausible text; training can reward sounding helpful | Grounding, citations, "say you don't know" instructions with an eval (lesson 08) |

The pattern to name: **Goodhart's law**. When a measure becomes a target, it stops being a good measure. Every stage after pretraining optimizes a measure of "good", and the failure modes live in the gap between the measure and the goal.

## A model answer

"Why does the model sometimes just agree with me?"

"Assistants are trained partly on human or AI preferences, and people tend to rate agreeable answers higher, so the model learns that agreeing is rewarded. Providers work against it, but it shows up most when the prompt signals what you want to hear. In our product I'd keep leading opinions out of the prompt, ask for the evidence behind each conclusion, and add eval cases where the user pushes back on a correct answer, so we measure whether it holds its ground."

## Practice (say it out loud)

- "Explain RLHF to a CFO in four sentences, and say what can go wrong."
- "What's the difference between Constitutional AI and RLHF? Why would a lab want both?"
- "Our coding agent made the failing test pass by deleting the assertion. What happened, in training terms, and what do you change in your harness?"

> **Key takeaways**
>
> - Pretraining builds a base model that predicts plausible text; SFT teaches the assistant format; RLHF optimizes a reward model trained on human preferences.
> - Constitutional AI (Anthropic, 2022) uses written principles and AI feedback (RLAIF) for self-critique and preference labels. It is a training method, distinct from Claude's published constitution document.
> - Sycophancy, reward hacking and over-refusal come from optimizing proxies. Name Goodhart's law.
> - In products, counter them with neutral prompts, outcome-based grading, legitimate context and evals that probe each failure.
