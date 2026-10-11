import math

# BASELINE_RUN, CANDIDATE_RUN, RERUNS, CONFIG, paired_flips() and t95() are loaded for you.


def rerun_policy(flips, k, max_calls):
    """Regressions first, then fixes; each rerun costs 2 * k calls (both versions)."""
    rerun, skipped, calls = [], [], 0
    for cid in flips["regressions"] + flips["fixes"]:
        if calls + 2 * k <= max_calls:
            rerun.append(cid)
            calls += 2 * k
        else:
            skipped.append(cid)
    return {"rerun": rerun, "calls": calls, "skipped": skipped}


def case_rate(statuses):
    """(passes, n) with errors left out."""
    scored = [s for s in statuses if s != "error"]
    return sum(s == "pass" for s in scored), len(scored)


def classify(base_statuses, cand_statuses):
    bp, bn = case_rate(base_statuses)
    cp, cn = case_rate(cand_statuses)
    if bn == 0 or cn == 0:
        return "unknown"
    b, c = bp / bn, cp / cn
    if b >= 0.8 and c <= 0.4:
        return "regression"
    if b <= 0.4 and c >= 0.8:
        return "fix"
    if 0 < b < 1 or 0 < c < 1:
        return "flaky"
    return "stable"


def observations(first_run, reruns, version):
    """{case_id: [0/1, ...]} from the first run plus any reruns, errors left out."""
    out = {}
    for row in first_run:
        statuses = [row["status"]] + reruns.get(row["id"], {}).get(version, [])
        out[row["id"]] = [1 if s == "pass" else 0 for s in statuses if s != "error"]
    return out


def clustered_rate(obs):
    groups = [v for v in obs.values() if v]
    n = sum(len(g) for g in groups)
    G = len(groups)
    p = sum(sum(g) for g in groups) / n
    se_naive = math.sqrt(p * (1 - p) / n)
    se_cl = math.sqrt(G / (G - 1) * sum(sum(y - p for y in g) ** 2 for g in groups)) / n
    return {"rate": round(p, 3), "n_obs": n, "n_cases": G, "se_naive": round(se_naive, 4),
            "se_clustered": round(se_cl, 4), "design_effect": round((se_cl / se_naive) ** 2, 2)}


def paired_difference(base_obs, cand_obs):
    d = [sum(cand_obs[c]) / len(cand_obs[c]) - sum(base_obs[c]) / len(base_obs[c])
         for c in base_obs if base_obs[c] and cand_obs.get(c)]
    n = len(d)
    mean = sum(d) / n
    sd = math.sqrt(sum((x - mean) ** 2 for x in d) / (n - 1))
    se = sd / math.sqrt(n)
    half = t95(n - 1) * se
    return {"n": n, "diff": round(mean, 3), "se": round(se, 4), "low": round(mean - half, 3), "high": round(mean + half, 3)}


def verdict(baseline, candidate, reruns, config):
    flips = paired_flips(baseline, candidate)
    plan = rerun_policy(flips, config["k"], config["max_calls"])
    category = {r["id"]: r["category"] for r in baseline}
    classes = {cid: classify(reruns[cid]["baseline"], reruns[cid]["candidate"]) for cid in plan["rerun"]}
    regressions = [c for c in plan["rerun"] if classes[c] == "regression"]
    diff = paired_difference(observations(baseline, reruns, "baseline"), observations(candidate, reruns, "candidate"))

    reasons = []
    for cid in regressions:
        bp, bn = case_rate(reruns[cid]["baseline"])
        cp, cn = case_rate(reruns[cid]["candidate"])
        critical = category[cid] in config["critical_categories"]
        reasons.append({"code": "critical_regression" if critical else "regression",
                        "severity": "block" if critical else "review",
                        "detail": f"{cid} ({category[cid]}): baseline {bp}/{bn}, candidate {cp}/{cn} on rerun"})
    if diff["high"] < 0:
        reasons.append({"code": "worse_overall", "severity": "block",
                        "detail": f"mean per-case change {diff['diff']:.3f} (95% CI {diff['low']:.3f} to {diff['high']:.3f})"})
    skipped_reg = [c for c in plan["skipped"] if c in flips["regressions"]]
    if skipped_reg:
        reasons.append({"code": "not_rerun", "severity": "review",
                        "detail": f"regressions not rerun within budget: {', '.join(skipped_reg)}"})
    sev = {r["severity"] for r in reasons}
    return {"decision": "block" if "block" in sev else "review" if "review" in sev else "ship",
            "reasons": reasons,
            "confirmed_regressions": regressions,
            "confirmed_fixes": [c for c in plan["rerun"] if classes[c] == "fix"],
            "flaky": [c for c in plan["rerun"] if classes[c] == "flaky"],
            "calls": plan["calls"], "difference": diff}


# --- Try it out (not graded) ---
flips = paired_flips(BASELINE_RUN, CANDIDATE_RUN)
print("first-run flips:", flips)
plan = rerun_policy(flips, CONFIG["k"], CONFIG["max_calls"])
print("rerun plan:", plan)
for cid in (plan or {}).get("rerun", []):
    print(f"  {cid}: {classify(RERUNS[cid]['baseline'], RERUNS[cid]['candidate'])}")
cand_obs = observations(CANDIDATE_RUN, RERUNS, "candidate")
if cand_obs:
    print("candidate pass rate:", clustered_rate(cand_obs))
v = verdict(BASELINE_RUN, CANDIDATE_RUN, RERUNS, CONFIG)
if v:
    print("decision:", v["decision"])
    for r in v["reasons"]:
        print("  ", r)
    print("  flaky:", v["flaky"], " difference:", v["difference"])
