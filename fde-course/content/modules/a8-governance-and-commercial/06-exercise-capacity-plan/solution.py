# EXAMPLE_LIMITS, PRIORITY_RATES and BRACKENRIDGE_WORKLOAD are already defined
# for you (see the lesson). The limits are made-up placeholders: never
# hard-code them. Your functions receive everything as arguments.
import math

METRICS = ("rpm", "itpm", "otpm")


def _validate(workload, peak_factor):
    if peak_factor < 1:
        raise ValueError(f"peak_factor must be at least 1, got {peak_factor}")
    cached = workload.get("cache_read_tokens", 0) + workload.get("cache_write_tokens", 0)
    if cached > workload["input_tokens"]:
        raise ValueError("cache reads plus cache writes can't exceed total input tokens")


def _peak_rpm(workload, peak_factor):
    return math.ceil(workload["calls_per_minute"] * peak_factor)


def capacity_plan(workload, peak_factor, limits, headroom=0.8):
    """Return one row per platform (sorted by name) with peak needs, utilization and flags."""
    _validate(workload, peak_factor)
    rpm = _peak_rpm(workload, peak_factor)
    rows = []
    for name in sorted(limits):
        lim = limits[name]
        counted_in = workload["input_tokens"]
        if not lim.get("cache_reads_count", False):
            counted_in -= workload.get("cache_read_tokens", 0)
        need = {"rpm": rpm, "itpm": rpm * counted_in, "otpm": rpm * workload["output_tokens"]}
        util = {m: round(need[m] / lim[m], 3) for m in METRICS}
        breaches = [m for m in METRICS if need[m] > lim[m]]
        tight = [m for m in METRICS if m not in breaches and need[m] > headroom * lim[m]]
        binding = max(METRICS, key=lambda m: (need[m] / lim[m], -METRICS.index(m)))
        rows.append({
            "platform": name,
            "peak_rpm": need["rpm"],
            "peak_itpm": need["itpm"],
            "peak_otpm": need["otpm"],
            "utilization": util,
            "breaches": breaches,
            "tight": tight,
            "status": "breach" if breaches else ("tight" if tight else "ok"),
            "binding": binding,
        })
    return rows


def priority_burndown(workload, peak_factor, commitment, rates):
    """Return how a peak minute burns a commitment measured in ITPM/OTPM."""
    _validate(workload, peak_factor)
    rpm = _peak_rpm(workload, peak_factor)
    read = workload.get("cache_read_tokens", 0)
    write = workload.get("cache_write_tokens", 0)
    uncached = workload["input_tokens"] - read - write
    ttl = workload.get("cache_ttl", "5m")
    geo = rates["us_only"] if workload.get("inference_geo") == "us" else 1.0
    in_burn = (read * rates["cache_read"] + write * rates["cache_write_" + ttl] + uncached) * geo
    out_burn = workload["output_tokens"] * geo
    fits = []
    if in_burn > 0:
        fits.append(commitment["itpm"] / in_burn)
    if out_burn > 0:
        fits.append(commitment["otpm"] / out_burn)
    covered = min(rpm, math.floor(min(fits) + 1e-9)) if fits else rpm
    return {
        "input_burn_per_call": round(in_burn, 2),
        "output_burn_per_call": round(out_burn, 2),
        "peak_input_burn": round(rpm * in_burn),
        "peak_output_burn": round(rpm * out_burn),
        "covered_rpm": covered,
        "overflow_rpm": rpm - covered,
        "covered_share": round(covered / rpm, 3) if rpm else 1.0,
    }


# --- Try it out (this part isn't graded) ---
for row in capacity_plan(BRACKENRIDGE_WORKLOAD, 3.0, EXAMPLE_LIMITS) or []:
    print(row["platform"], row["status"], row["utilization"], row["breaches"])

print(priority_burndown(BRACKENRIDGE_WORKLOAD, 3.0, {"itpm": 3_000_000, "otpm": 500_000}, PRIORITY_RATES))
