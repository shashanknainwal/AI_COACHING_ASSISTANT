# Evals

Everything here runs from the kit root (`capstone-kit/`, or your repo root once you copy it).

| File | What it does | Needs a key? |
|---|---|---|
| `golden.jsonl` | The golden set: one case per line | no |
| `stats.py` | Wilson interval, Cohen's kappa, run summaries, percentiles | no |
| `run_evals.py` | Runs the golden set N times, writes `results/latest.json` | yes |
| `judge.py` | LLM judge: rubric in, `{rationale, verdict, failed_lines}` out | yes |
| `calibrate_judge.py` | Judge vs your labels: agreement, kappa, self-agreement | yes |
| `gate.py` + `gate_policy.json` + `baseline.json` | CI gate: exits 1 on regression | no |

## Golden set format

One JSON object per line:

```json
{"id": "g04",
 "tags": ["shipping", "policy"],
 "critical": false,
 "input": "How fast is express shipping and what does it cost?",
 "reference": "Express shipping takes 1 to 2 business days and costs $14.95.",
 "checks": {"must_call": ["search_knowledge_base"],
            "must_include_any": [["14.95"]],
            "must_not_include": [],
            "judge": true}}
```

- `reference` holds the facts a correct answer must agree with. The judge reads it. Write it from the source documents, not from the model's output.
- `must_include_any` is a list of groups; each group passes if any alternative appears (case-insensitive). Keep these loose. Brittle string checks fail good answers.
- `critical: true` means the case must pass in every run, or the gate fails. Use it for safety cases such as prompt injection.
- Tags let you report pass rates per slice (policy, edge cases, injection).

The 12 sample cases cover a fictional shop. **Replace them with your own domain.** A credible capstone has at least 40 to 60 cases, labelled before you tune the prompt, with deliberate edge cases. Keep a held-out slice you never look at while iterating.

## Reading results honestly

- Report counts, not just percentages: "41/48 (85%, 95% Wilson 73% to 93%)".
- Run at least 3 times. Current models think adaptively and sampling parameters such as temperature are not accepted on the newest models, so outputs vary run to run. `summary.flaky_cases` lists cases that passed in some runs and failed in others. `pass_all_runs` is pass^k: cases that passed every time.
- Errors are not failures. They are reported separately (`errors`, `error_rate`).
- Refusals are failures for a support bot, and are also reported with an interval: 0 refusals in 36 trials still has a 95% upper bound near 10%.

## Judge calibration

Never trust a judge you haven't calibrated. Label 20 or more items yourself first, then:

```bash
python -m evals.calibrate_judge --items labs/lab3_judge_calibration/answers.jsonl \
    --labels labs/lab3_judge_calibration/my_labels.csv --runs 3
```

A common convention (Landis and Koch) calls kappa 0.61 to 0.80 "substantial" agreement. It is a convention, not a law. Read every disagreement: sometimes the judge is right and your label is wrong. Fix the rubric, re-run, and write down what changed.

## The gate

```bash
python -m evals.gate --current results/latest.json              # exit 0 = pass, 1 = fail
python -m evals.gate --current results/latest.json --update-baseline
```

It fails when the pass rate drops (point or interval mode, see `gate.py`), a critical case fails, errors exceed the limit, or cost per case or p95 latency go over budget. Change `gate_policy.json` only in a reviewed pull request, and never to turn a red build green.
