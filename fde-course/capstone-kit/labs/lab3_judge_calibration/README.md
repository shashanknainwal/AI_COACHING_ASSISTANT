# Lab 3: Judge calibration

**Mirrors:** the judge and eval exercises in E4 (evals engineering) and module 08. **Paste results into:** C8 lesson "Lab 3 Report: Calibrating an LLM Judge".
**Time:** 60 minutes, half of it labelling. **Cost:** 20 items x 3 runs = 60 judge calls on Claude Sonnet 5.5 at effort low. Expect roughly $0.15 to $0.50; your results file has the exact figure. Use `--model claude-haiku-5-5` to compare a cheaper judge.

An LLM judge is a measuring instrument. Before you report "the judge says 85% pass", you need to know how often the judge agrees with a careful human. That number is Cohen's kappa.

## Steps

1. **Label first, alone.** Open `answers.jsonl`. For each of the 20 items, decide pass or fail using the rubric in `evals/judge.py` (`DEFAULT_RUBRIC`). Write your verdict in `my_labels.csv` (`id,verdict,note`). Do not look at `author_labels.jsonl` yet. Note any item you found hard.
2. Compare with the author's labels (free, no API calls):
   ```bash
   python -m labs.lab3_judge_calibration.compare_labels
   ```
   Four items are marked `borderline` in the author's file. Did you disagree on those?
3. Run the judge three times against your labels:
   ```bash
   python -m evals.calibrate_judge --runs 3
   ```
   Record agreement and kappa per run and for the majority vote, the judge's self-agreement across runs, and the disagreements.
4. Read the judge's rationale for every disagreement in `results/judge_calibration.json`. For each: was the judge wrong, was your label wrong, or is the rubric unclear?
5. Improve the rubric. Copy `DEFAULT_RUBRIC` into a file (for example `labs/lab3_judge_calibration/rubric_v2.txt`), fix the unclear line, and re-run with `--rubric labs/lab3_judge_calibration/rubric_v2.txt`. Fixing your own label after you see the judge is allowed only if you write down that you did it and why.

## What to notice

- With 20 items, one disagreement moves agreement by 5 points and kappa by more. Say so.
- Kappa corrects for chance. A judge that says "pass" to everything gets 55% agreement here (11 of 20 author labels are pass) and a kappa of 0.
- Self-agreement below 100% means the judge itself is noisy on some items: those are usually the borderline ones, and usually a rubric problem.

See `RESULTS_TEMPLATE.md`.
