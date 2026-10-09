import math

# BASELINE_RUN and CANDIDATE_RUN are loaded for you: [{"id", "category", "status"}, ...]

GATE_CONFIG = {
    "category_floors": {"billing": 0.85, "cancel": 1.0, "sim_swap_fraud": 0.9},  # hard minimums
    "max_category_drop": 0.10,   # largest allowed drop in any category's pass rate
    "min_category_n": 5,         # below this many scored cases, a drop needs review, not a block
    "max_error_rate": 0.05,      # more errors than this means the run itself is suspect
    "alpha": 0.05,               # significance level for the paired sign test
}


def _rate(n, passes):
    return {"n": n, "passes": passes, "rate": round(passes / n, 3) if n else None}


def pass_rates(rows):
    """Overall and per-category pass rates. Errors are counted, not scored."""
    scored = [r for r in rows if r["status"] != "error"]
    by_category = {}
    for cat in sorted({r["category"] for r in rows}):
        cat_rows = [r for r in scored if r["category"] == cat]
        by_category[cat] = _rate(len(cat_rows), sum(r["status"] == "pass" for r in cat_rows))
    return {
        "total": len(rows),
        "errors": len(rows) - len(scored),
        "overall": _rate(len(scored), sum(r["status"] == "pass" for r in scored)),
        "by_category": by_category,
    }


def paired_flips(baseline, candidate):
    """Case-by-case changes between two runs, in baseline order."""
    cand = {r["id"]: r["status"] for r in candidate}
    out = {"regressions": [], "fixes": [], "missing": []}
    for row in baseline:
        if row["id"] not in cand:
            out["missing"].append(row["id"])
            continue
        before, after = row["status"], cand[row["id"]]
        if before == "pass" and after == "fail":
            out["regressions"].append(row["id"])
        elif before == "fail" and after == "pass":
            out["fixes"].append(row["id"])
    return out


def sign_test_p(regressions, fixes):
    """One-sided exact sign test: P(at least this many regressions | no real change)."""
    n = regressions + fixes
    if n == 0:
        return 1.0
    return round(sum(math.comb(n, k) for k in range(regressions, n + 1)) / 2 ** n, 4)


def _reason(code, severity, detail):
    return {"code": code, "severity": severity, "detail": detail}


def gate(baseline, candidate, config):
    """Decide ship / review / block for a candidate run. Returns {"decision", "reasons", "p_value"}."""
    reasons = []
    base, cand = pass_rates(baseline), pass_rates(candidate)
    flips = paired_flips(baseline, candidate)

    if flips["missing"]:
        reasons.append(_reason("incomplete_run", "block",
                               f"{len(flips['missing'])} baseline cases missing from candidate: {', '.join(flips['missing'])}"))

    error_rate = cand["errors"] / cand["total"] if cand["total"] else 0.0
    if error_rate > config["max_error_rate"]:
        reasons.append(_reason("error_rate", "block",
                               f"candidate error rate {error_rate:.3f} above {config['max_error_rate']:.3f}"))

    for cat, floor in sorted(config["category_floors"].items()):
        rate = cand["by_category"].get(cat, {}).get("rate")
        if rate is None:
            reasons.append(_reason("no_data", "block", f"{cat} has no scored cases in the candidate run"))
        elif rate < floor:
            reasons.append(_reason("below_floor", "block", f"{cat} pass rate {rate:.3f} below floor {floor:.3f}"))

    for cat, b in base["by_category"].items():
        c = cand["by_category"].get(cat)
        if not c or b["rate"] is None or c["rate"] is None:
            continue
        if round(b["rate"] - c["rate"], 3) > config["max_category_drop"]:
            severity = "block" if c["n"] >= config["min_category_n"] else "review"
            reasons.append(_reason("category_drop", severity,
                                   f"{cat} dropped {b['rate']:.3f} -> {c['rate']:.3f} (n={c['n']})"))

    r, f = len(flips["regressions"]), len(flips["fixes"])
    p = sign_test_p(r, f)
    if r > f:
        detail = f"{r} regressions vs {f} fixes (sign test p={p:.4f})"
        if p < config["alpha"]:
            reasons.append(_reason("significant_regression", "block", detail))
        else:
            reasons.append(_reason("net_regression", "review", detail))

    severities = {x["severity"] for x in reasons}
    decision = "block" if "block" in severities else "review" if "review" in severities else "ship"
    return {"decision": decision, "reasons": reasons, "p_value": p}


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
