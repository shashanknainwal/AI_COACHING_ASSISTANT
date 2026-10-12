---
title: "Hill-Climbing Without Overfitting"
type: reading
minutes: 16
---

> **By the end of this lesson** you'll be able to run a prompt-improvement loop that produces a number you can defend: split cases into dev, validation and a frozen test set, keep the test set honest, spot an overfit change, decide when a suite is saturated, and answer "did you tune on your test set?" in a deep dive.

## The trap

You have 60 golden cases. You read the failures, change the prompt, rerun, read the new failures, change the prompt again. After ten rounds you're at 95%. Every one of those rounds looked at the same 60 cases, so the prompt has partly learned *those cases*. On new traffic it may be no better than where you started, or worse.

This is overfitting, the same idea as in machine learning, with you as the optimizer. The fastest route to it is pasting failing examples, or their specific nouns, straight into the prompt. "We tuned on the golden set" is a classic deep-dive follow-up for that reason. The practice prompts below are original, in the style of those rounds.

## Three splits, three jobs

| Split | Share (typical) | Who looks at it | Job |
|---|---|---|---|
| **Dev** | ~60% | You, every round: read transcripts, find failures | Generating ideas for changes |
| **Validation** | ~20% | Scores only, every round. No reading of transcripts. | Deciding whether a change generalizes |
| **Test** | ~20% | Nobody, until the end. One run. | The number you report |

Rules that keep the split honest:

- **Split by hash of a stable case ID**, not by shuffling. A hash split is reproducible, and adding cases never moves old ones between splits.
- **Split by group when cases are related.** Five messages from the same customer or seeds of the same synthetic family (lesson 08) go in the same split, or the test set leaks.
- **Freeze the test set with a fingerprint** (a hash of its IDs) and check it before the final run. If it changed, the result is about a different test set.
- **Read the test set once.** Every extra look leaks a little of it into your choices. If you must iterate after the test run, the old test set becomes validation, and you need a new one.

## The loop

1. Read dev failures. Write down the **behaviour** that went wrong ("quotes a price before confirming the tariff"), not the content ("customer GN-204117 asked about Fixed 24").
2. Make one change that addresses the behaviour generally.
3. Score the change on dev and validation against its parent. Use paired comparisons on the same cases, as in E4.
4. **Accept** if dev improves by a meaningful margin and validation doesn't drop. **Flag as overfit** if dev improves and validation drops. Otherwise **reject**.
5. Repeat. At the end, run the best variant on the test set once and report that number, with its interval.

With small suites the validation number is noisy. A one-case drop on 15 validation cases isn't proof of overfitting. Repeat runs to separate a real drop from noise (lesson 11), and never let validation alone carry the decision on a tiny set.

## Signs you're overfitting

- **Dev climbs, validation is flat or falls.** This is the classic signature, and the drill in the next lesson makes you detect it.
- **The prompt contains case-specific nouns:** account numbers, product names that appear in one case, near-copies of failing inputs as few-shot examples.
- **Big gains from tiny changes** on a small dev set.
- **The generalization gap grows:** dev minus test, measured at the end. Some gap is normal. A large one means the dev number was flattering.
- **Fixes that need exceptions:** "if the customer mentions X, do Y" for one X.

## When the suite is saturated

If the best variant passes 95% or more of dev and validation, more climbing measures noise: the remaining failures are a handful of cases, often label errors or genuinely ambiguous inputs. Signs and responses:

| Sign | Response |
|---|---|
| Dev and validation both ≥ ~95% | Stop climbing this suite |
| The remaining failures are label disputes | Fix the labels through adjudication (E4), not the prompt |
| Production still has failures the suite doesn't | Add those cases, from error analysis (lesson 05), as a new version |
| Every candidate ties | The suite can't discriminate. Add harder cases or pairwise judging (E4). |

Freeze a new version (`golden-v4`) when you add cases, and re-baseline every variant on it. Don't compare a v3 score with a v4 score.

## What to say in a deep dive

"We split 300 cases by hashed case ID: 180 dev, 60 validation, 60 test, with each customer's messages kept together. I read dev failures only. Each change was scored against its parent on dev and validation, and two changes that won on dev and lost on validation were reverted, including one that pasted failing examples into the prompt. The test set was fingerprinted and run once at the end: 88%, Wilson interval 78% to 94%, against 91% on dev. That gap is within noise at 60 cases. After that run, the test set became validation and we drew a new one from October traffic."

Each sentence answers a follow-up before it's asked.

## Practice (say it out loud)

These are original prompts, in the style of project deep dives.

- "You improved the prompt from 74% to 93% in a week. How do I know you didn't overfit?"
- "Your test set has 40 cases, and you've looked at it five times. What's your test set now?"
- "Every variant you try scores between 96% and 97%. What do you do next?"

> **Key takeaways**
>
> - Iterating on the same cases overfits the prompt to them. Pasting failing examples into the prompt is the fastest way to do it.
> - Use dev for reading failures, validation for accepting changes (scores only) and a frozen test set for one final, reported run.
> - Split by hash of a stable ID, keep related cases together, fingerprint the test set and look at it once.
> - A dev gain with a validation loss is overfitting. Revert it and describe behaviours, not case content.
> - At ~95% on dev and validation the suite is saturated. Add harder real cases as a new version instead of climbing further.
