import math

MAX_FALSE_REFUSAL = 0.02   # agreed with Quarrybank: at most 2% of should-answer cases declined
MIN_CASES = 30


def wilson(k, n, z=1.96):
    """95% Wilson score interval for k successes out of n (given)."""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def slice_stats(records, by="slice"):
    """Refusal counts and rates per value of the `by` field."""
    # TODO
    pass


def flag(stats, max_false_refusal=MAX_FALSE_REFUSAL, min_cases=MIN_CASES):
    """List of (key, reason) for slices that need attention, sorted by key."""
    # TODO
    pass


def escalation_packet(records, slice_name):
    """Evidence for the account team: counts, categories and request IDs. No ticket text."""
    # TODO
    pass


# --- Try it out (not graded) ---
stats = slice_stats(EVAL_RESULTS)
if stats:
    for name, s in sorted(stats.items()):
        lo, hi = wilson(s["false_refusals"], s["should_answer"]) if s["should_answer"] else (0, 0)
        print(f"{name:<14} n={s['n']:<3} false refusals {s['false_refusals']:>2} ({s['false_refusal_rate']:.1%}, CI {lo:.1%}-{hi:.1%})  missed declines {s['missed_declines']}")
    print("Flags:", flag(stats))
packet = escalation_packet(EVAL_RESULTS, "sensitive")
if packet:
    print("Packet:", {k: v for k, v in packet.items() if k != "request_ids"}, f"+ {len(packet['request_ids'])} request IDs")
