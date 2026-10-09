# Ellery Bank (fictional): card-dispute triage bake-off.
# 40 real (anonymized) dispute messages, frozen before any candidate was tuned. Each candidate
# had to return a reason code and a one-paragraph case summary. Two dispute analysts graded every
# output blind (candidate names hidden, order shuffled) and adjudicated disagreements, so `correct`
# is already decided. The numbers are invented for this exercise: they say nothing about how any
# real model or vendor performs on real tasks.
EVAL_CASE_IDS = [f"D-{i:02d}" for i in range(1, 41)]

CONSTRAINTS = {
    "min_accuracy": 0.85,        # must-have agreed with Ellery's dispute operations lead
    "max_cost_per_task": 0.01,   # USD, from the business case
    "max_p95_ms": 3000,          # the analyst screen waits on this call
    "max_error_rate": 0.05,      # errors and missing cases, as a share of the 40 cases
}

# Per-million-token list prices. quillon-v4 is the incumbent vendor's (fictional) quote.
PRICING = {
    "opus-rubric":    {"model": "claude-opus-5-5",   "input_per_mtok": 4.00, "output_per_mtok": 20.00},
    "sonnet-rubric":  {"model": "claude-sonnet-5-5", "input_per_mtok": 2.00, "output_per_mtok": 10.00},
    "haiku-fewshot":  {"model": "claude-haiku-5-5",  "input_per_mtok": 0.10, "output_per_mtok": 0.50},
    "haiku-zeroshot": {"model": "claude-haiku-5-5",  "input_per_mtok": 0.10, "output_per_mtok": 0.50},
    "quillon-v4":     {"model": "Quillon Triage v4", "input_per_mtok": 3.00, "output_per_mtok": 15.00},
}

_PLAN = {
    #                 prompt extra, out base, out spread, lat base, lat step, lat spread, failed cases, errored, missing
    "opus-rubric":    (400, 340, 90, 2400, 263, 2400, {12, 27, 35}, set(), set()),
    "sonnet-rubric":  (400, 260, 80, 1300, 197, 1500, {8, 12, 22, 27, 35}, {31}, set()),
    "haiku-fewshot":  (1500, 220, 70, 600, 89, 700, {4, 12, 17, 27, 35, 39}, set(), set()),
    "haiku-zeroshot": (200, 220, 70, 500, 71, 600, {4, 9, 12, 14, 17, 25, 27, 35, 39}, set(), set()),
    "quillon-v4":     (300, 250, 60, 1100, 151, 1700, {12, 27}, set(), {7, 19, 28, 33}),
}


def _build():
    results = {}
    for name, (extra, ob, os_, lb, ls, lsp, failed, errored, missing) in _PLAN.items():
        rows = []
        for i in range(1, 41):
            if i in missing:
                continue
            if i in errored:
                rows.append({"id": f"D-{i:02d}", "correct": False, "input_tokens": 0, "output_tokens": 0,
                             "latency_ms": 30000, "error": "TimeoutError: no response after 30s"})
                continue
            rows.append({
                "id": f"D-{i:02d}",
                "correct": i not in failed,
                "input_tokens": 1700 + (i * 137) % 600 + extra,
                "output_tokens": ob + (i * 53) % os_,
                "latency_ms": lb + (i * ls) % lsp,
                "error": None,
            })
        results[name] = rows
    return results


# RESULTS[name] is a list of records, one per case the candidate returned:
# {"id": "D-01", "correct": True, "input_tokens": 2237, "output_tokens": 393, "latency_ms": 2663, "error": None}
RESULTS = _build()
