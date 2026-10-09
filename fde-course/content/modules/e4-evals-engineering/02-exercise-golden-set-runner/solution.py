import math

# GOLDEN_SET, TRAFFIC_MIX and kestrel_router(text) are loaded for you.


def wilson_interval(passes, n, z=1.96):
    """95% Wilson score interval for passes/n, as (low, high) rounded to 3 decimals."""
    if n == 0:
        return (0.0, 1.0)
    p = passes / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (round(center - half, 3), round(center + half, 3))


def cases_needed(margin, p=0.5, z=1.96):
    """Smallest n whose normal-approximation half-width z*sqrt(p(1-p)/n) is <= margin."""
    return math.ceil(z * z * p * (1 - p) / (margin * margin))


def run_golden_set(cases, system):
    """Run system(text) on every case and grade it. One row per case, in order."""
    rows = []
    for case in cases:
        row = {"id": case["id"], "expected": case["expected"], "actual": None, "status": "error", "error": None}
        try:
            actual = system(case["text"])
        except Exception as e:
            row["error"] = f"{type(e).__name__}: {e}"
        else:
            row["actual"] = actual
            ok = isinstance(actual, str) and actual.strip().lower() == case["expected"]
            row["status"] = "pass" if ok else "fail"
        rows.append(row)
    return rows


def _rate_block(scored, passes):
    return {
        "n": scored,
        "passes": passes,
        "pass_rate": round(passes / scored, 3) if scored else None,
        "ci": wilson_interval(passes, scored),
    }


def summarize(rows, min_n=5):
    """Overall and per-category pass rates with Wilson intervals. Errors are not scored."""
    scored = [r for r in rows if r["status"] != "error"]
    passes = sum(r["status"] == "pass" for r in scored)
    out = _rate_block(len(scored), passes)
    out["errors"] = len(rows) - len(scored)
    by_category = {}
    for cat in sorted({r["expected"] for r in rows}):
        cat_scored = [r for r in scored if r["expected"] == cat]
        block = _rate_block(len(cat_scored), sum(r["status"] == "pass" for r in cat_scored))
        block["low_n"] = block["n"] < min_n
        by_category[cat] = block
    out["by_category"] = by_category
    return out


def traffic_report(summary, traffic_mix, min_n=5):
    """Traffic-weighted pass rate, coverage gaps and the share of traffic with no scored cases."""
    by_cat = summary["by_category"]

    def n_of(cat):
        return by_cat.get(cat, {}).get("n", 0)

    tested = [c for c in traffic_mix if n_of(c) > 0]
    weight = sum(traffic_mix[c] for c in tested)
    weighted = round(sum(traffic_mix[c] * by_cat[c]["pass_rate"] for c in tested) / weight, 3) if weight else None
    gaps = sorted((c for c in traffic_mix if n_of(c) < min_n), key=lambda c: (-traffic_mix[c], c))
    untested = round(sum(traffic_mix[c] for c in traffic_mix if n_of(c) == 0), 3)
    return {"weighted_pass_rate": weighted, "gaps": gaps, "untested_share": untested}


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
