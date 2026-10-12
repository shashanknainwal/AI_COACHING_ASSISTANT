---
title: "Real-Model Labs: How to Run Them on Your Key"
type: reading
minutes: 12
---

> **By the end of this lesson you will be able to:**
> - Set up the capstone kit and run a lab safely on your own API key
> - Read a lab's output: counts, intervals, run-to-run spread, cost and latency
> - Report results honestly in the four lab-report lessons that follow

## Why these labs exist

The exercises in this course run against a simulated `anthropic` package in your browser. It returns scripted responses, which makes grading reliable, but it never calls a real model. So prompt quality never changes a grade, and you never see variance, refusals, latency or cost.

The four labs fix that. Each one repeats an in-course exercise against the real model, on your machine. You then paste your numbers into the matching written lesson in this module, where a rubric grades the honesty and reasoning of your report, not how high your numbers are.

| Lab | Mirrors | Question | Report lesson |
|---|---|---|---|
| 1. Prompt iteration | E1 prompt exercises | Did my prompt change help, or is it noise? | 04 |
| 2. Retrieval eval | E3 and module 07 retrieval | Does the right document reach the model? | 05 |
| 3. Judge calibration | E4 and module 08 judges | Can I trust my LLM judge? | 06 |
| 4. Classifier eval | Module 06 classification, E5 model choice | Which model, what cost, how often does it refuse? | 07 |

## Setup

```bash
cp -r capstone-kit ~/my-capstone && cd ~/my-capstone
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q                  # no key needed; or python -m unittest discover -s tests -t .
export ANTHROPIC_API_KEY=sk-ant-...  # never commit it
```

Then set a spend limit in the Claude Console. Every kit script also stops itself at `CAPSTONE_BUDGET_USD` (default $1.00 per run). All four labs together should cost well under $2 on the defaults. Each lab's README lists its rough cost; your results file records the exact figure.

## Reading the output

Every lab prints the same kinds of numbers. Here's how to read them.

**Counts and intervals.** "27/30 = 90.0% (95% Wilson 74.4% to 96.5%)". With 30 items, one item is 3.3 points, and the interval is wide. Report the count and the interval, not just the percentage. The Wilson interval is used because it behaves well for small samples and for rates near 0% or 100%.

**Run-to-run spread.** Current models think adaptively, and the newest models reject sampling parameters such as `temperature`, so you can't force identical outputs. Lab 1 runs each prompt three times. If run 1 says 26/30 and run 3 says 28/30, a 2-ticket "improvement" from one prompt change proves nothing.

**Flips.** Items that got different answers across runs. They usually cluster on ambiguous items. That's a labelling or prompt-clarity problem, and it's a great deep-dive story.

**Errors versus wrong answers versus refusals.** A timeout is not a wrong label, and neither is a refusal. The kit counts them separately. Zero refusals in 40 calls is not a 0% refusal rate: the 95% upper bound is about 9%.

**Cost and latency.** Cost comes from each response's `usage` block and the price table in `app/config.py`. Output tokens include thinking tokens, which is why effort changes cost. Latency is measured per call; report p50 and p95.

## Rules for honest reports

1. **Paste what you got.** Low numbers with a clear explanation score better than high numbers with no evidence.
2. **Never tune on your test items.** Don't paste the 30 lab tickets into your prompt.
3. **Say what changed between runs** (prompt, model, effort, chunk size), one change at a time.
4. **If you couldn't run a lab, say so** and describe what you would expect and why. The rubric caps that answer, but it doesn't fail you for honesty.
5. **Record the model, effort and date** for every number. Prices and models change.

> **Key takeaways**
> - The browser simulator never calls a real model; the labs are where variance, refusals, latency and cost become real.
> - Run from the kit root on your own key, with a Console spend limit and the kit's per-script budget.
> - Report counts with Wilson intervals, the spread across runs, and errors and refusals separately.
> - The report lessons grade honesty and reasoning, not high scores.
