import math

# GOLDEN_SET, TRAFFIC_MIX and kestrel_router(text) are loaded for you.
# print(GOLDEN_SET[0]) or print(TRAFFIC_MIX) to look at them.


def wilson_interval(passes, n, z=1.96):
    """95% Wilson score interval for passes/n, as (low, high) rounded to 3 decimals."""
    # TODO
    pass


def cases_needed(margin, p=0.5, z=1.96):
    """Smallest n whose normal-approximation half-width z*sqrt(p(1-p)/n) is <= margin."""
    # TODO
    pass


def run_golden_set(cases, system):
    """Run system(text) on every case and grade it. One row per case, in order."""
    # TODO
    pass


def summarize(rows, min_n=5):
    """Overall and per-category pass rates with Wilson intervals. Errors are not scored."""
    # TODO
    pass


def traffic_report(summary, traffic_mix, min_n=5):
    """Traffic-weighted pass rate, coverage gaps and the share of traffic with no scored cases."""
    # TODO
    pass


# --- Try it out (not graded) ---
rows = run_golden_set(GOLDEN_SET, kestrel_router)
summary = summarize(rows) if rows else None
if summary:
    print(f"Overall: {summary['passes']}/{summary['n']} = {summary['pass_rate']}  95% CI {summary['ci']}  errors: {summary['errors']}")
    for cat, b in summary["by_category"].items():
        flag = "  (too few cases)" if b["low_n"] else ""
        print(f"  {cat:15} {b['passes']}/{b['n']}  rate={b['pass_rate']}  CI={b['ci']}{flag}")
    print("Traffic view:", traffic_report(summary, TRAFFIC_MIX))
print("Cases for a +/-5 point margin at p=0.5:", cases_needed(0.05))
