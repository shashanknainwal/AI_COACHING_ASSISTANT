# Capstone brief: Applied AI Engineer track

**Goal:** a RAG or agent service on the real API that you can defend line by line in a project deep dive, with evidence that it works and a gate that stops it getting worse.

**Time:** about 12 to 20 hours over one or two weekends. **Budget:** under $5.

## Build

1. A service that answers questions or completes tasks over a domain you chose. Either:
   - **RAG:** retrieval over at least 50 documents or chunks you did not write for the purpose, with citations back to the source; or
   - **Agent:** a tool loop with at least three tools, one of which writes and sits behind an approval step.
2. Start from `app/`. Replace the data and the tools. Keep the manual loop or move to the SDK tool runner, and say why in the decision record.
3. Structured outputs where code consumes the model's answer, `stop_reason` checked before parsing, explicit `effort`, usage logged per request.

## Evidence

| Deliverable | Bar |
|---|---|
| Golden set | 40+ cases labelled from sources before tuning; 10+ deliberate edge cases; a held-out slice |
| Eval runs | 3+ runs; pass rate as counts with Wilson intervals; flaky cases listed; errors and refusals separate |
| Calibrated judge | Your own labels on 20+ items; kappa per run and for the majority vote; one rubric change and its effect |
| CI gate | `evals/gate.py` in `.github/workflows/evals.yml`; a screenshot or log of it failing on a deliberate regression |
| Cost and latency table | Model, effort, mean input/output/thinking tokens, cost per request, p50/p95 latency, at two configs |
| Failure log | 10+ real failures grouped by type with counts, and what you changed for the top group |
| Decision record | 3 to 5 decisions, each with the alternative you rejected, the measurement, and the cost |
| One measured improvement | A change (retrieval, prompt, model routing, tool design) with before and after numbers and intervals |

## The deep-dive questions to be ready for

Original practice questions, in the style of a project deep dive: Why this model and effort? What does one request cost, including thinking? Which failure would hurt a user most, and how would you catch it in production? What would you change with ten times the traffic? Which of your numbers would you not trust, and why?
