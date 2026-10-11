# Lab 4: Classifier eval with cost and refusal rate

**Mirrors:** module 06 (building with Claude) classification exercises and the model-choice lessons in E5. **Paste results into:** C8 lesson "Lab 4 Report: Classifier Cost, Latency and Refusals".
**Time:** 45 minutes. **Cost:** 40 tickets on Claude Haiku 5.5 low (a few cents at most) plus 40 on Claude Sonnet 5.5 low (roughly $0.05 to $0.30). Your results file has the exact figures.

This lab answers the question every customer asks: which model, at what cost, how fast, and how often does it go wrong in ways that are not "wrong label"?

## Steps

1. Run the two default configs (Haiku 5.5 low and Sonnet 5.5 low) on 40 tickets:
   ```bash
   python -m labs.lab4_classifier_eval.run
   ```
2. Record for each config: accuracy with the interval, edge cases correct out of 10, refusals out of 40 with the interval, errors, cost per 1,000 tickets, p50 and p95 latency, and mean thinking tokens.
3. Add one config of your choice, for example `--config claude-haiku-5-5:medium`, and run it with `--runs 2` to see how much accuracy moves between runs.
4. Optional: point `--prompt` at your lab 1 v2 prompt (add an `other` category first) and compare with the built-in prompt.
5. Write a one-paragraph recommendation for a customer handling 50,000 tickets a day. Scale cost from your measured per-ticket figure, and say what the accuracy difference is worth.

## What to notice

- **Refusal rate is a rate with an interval.** Zero refusals in 40 calls does not mean the refusal rate is zero. The 95% upper bound is near 9%. To claim "under 1%", you need hundreds of clean calls.
- Errors (timeouts, `max_tokens`) are not refusals and not wrong answers. Count them separately.
- Thinking tokens are billed as output and sit inside your latency. Compare `mean_thinking_tokens` between effort levels.
- The edge cases test behaviour, not just labels: the injection ticket should be `other`, not `billing`.

See `RESULTS_TEMPLATE.md`.
