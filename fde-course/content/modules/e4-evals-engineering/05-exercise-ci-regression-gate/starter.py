import math

# BASELINE_RUN and CANDIDATE_RUN are loaded for you: [{"id", "category", "status"}, ...]

GATE_CONFIG = {
    "category_floors": {"billing": 0.85, "cancel": 1.0, "sim_swap_fraud": 0.9},  # hard minimums
    "max_category_drop": 0.10,   # largest allowed drop in any category's pass rate
    "min_category_n": 5,         # below this many scored cases, a drop needs review, not a block
    "max_error_rate": 0.05,      # more errors than this means the run itself is suspect
    "alpha": 0.05,               # significance level for the paired sign test
}


def pass_rates(rows):
    """Overall and per-category pass rates. Errors are counted, not scored."""
    # TODO
    pass


def paired_flips(baseline, candidate):
    """Case-by-case changes between two runs, in baseline order."""
    # TODO
    pass


def sign_test_p(regressions, fixes):
    """One-sided exact sign test: P(at least this many regressions | no real change)."""
    # TODO
    pass


def gate(baseline, candidate, config):
    """Decide ship / review / block for a candidate run. Returns {"decision", "reasons", "p_value"}."""
    # TODO
    pass


# --- Try it out (not graded) ---
base, cand = pass_rates(BASELINE_RUN), pass_rates(CANDIDATE_RUN)
if base and cand:
    print(f"Headline: baseline {base['overall']['rate']}  ->  candidate {cand['overall']['rate']}")
print("Flips:", paired_flips(BASELINE_RUN, CANDIDATE_RUN))
result = gate(BASELINE_RUN, CANDIDATE_RUN, GATE_CONFIG)
if result:
    print("Decision:", result["decision"].upper(), f"(sign test p={result['p_value']})")
    for reason in result["reasons"]:
        print(f"  [{reason['severity']}] {reason['code']}: {reason['detail']}")
