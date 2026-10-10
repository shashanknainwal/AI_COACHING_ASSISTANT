# CRITERIA and RESULTS (Thornbury Mutual, week 6) are loaded for you.


def _is_number(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def validate_criteria(criteria):
    """Problems that would make these criteria impossible to judge. An empty list means they're usable."""
    problems = []
    seen = set()
    for i, c in enumerate(criteria):
        name = c.get("metric") or f"criterion {i + 1}"
        if not c.get("metric"):
            problems.append(f"criterion {i + 1}: missing metric name")
        elif name in seen:
            problems.append(f"{name}: duplicate metric")
        seen.add(name)
        if c.get("direction") not in ("higher", "lower"):
            problems.append(f"{name}: direction must be 'higher' or 'lower'")
        if not _is_number(c.get("threshold")):
            problems.append(f"{name}: threshold must be a number")
        if c.get("baseline") is None:
            problems.append(f"{name}: no baseline agreed")
    if not any(c.get("must_have") for c in criteria):
        problems.append("no must-have criterion")
    return problems


def evaluate_criterion(criterion, results, margin=0.02):
    """Judge one criterion against the measured results. Returns one readout row."""
    metric = criterion["metric"]
    threshold = criterion["threshold"]
    measured = results.get(metric)
    baseline = criterion.get("baseline")
    row = {
        "metric": metric,
        "status": "not_measured",
        "measured": measured,
        "threshold": threshold,
        "direction": criterion["direction"],
        "must_have": bool(criterion.get("must_have")),
        "vs_baseline": None,
    }
    if not _is_number(measured):
        row["measured"] = None
        return row
    if _is_number(baseline):
        row["vs_baseline"] = round(measured - baseline, 4)
    band = criterion.get("margin", margin) * abs(threshold)
    if criterion["direction"] == "higher":
        ok = measured >= threshold
    else:
        ok = measured <= threshold
    if band > 0 and abs(measured - threshold) <= band:
        row["status"] = "borderline"
    else:
        row["status"] = "met" if ok else "missed"
    return row


def poc_readout(criteria, results, margin=0.02):
    """Go / conditional / no-go / incomplete, with the rows and the reasons."""
    rows = [evaluate_criterion(c, results, margin) for c in criteria]
    must = [r for r in rows if r["must_have"]]
    if any(r["status"] == "missed" for r in must):
        decision = "no-go"
    elif any(r["status"] == "not_measured" for r in must):
        decision = "incomplete"
    elif any(r["status"] == "borderline" for r in must):
        decision = "conditional"
    else:
        decision = "go"
    blocking = [r["metric"] for r in must if r["status"] in ("missed", "not_measured")]
    watch = [r["metric"] for r in rows
             if r["status"] == "borderline" or (not r["must_have"] and r["status"] in ("missed", "not_measured"))]
    known = {c["metric"] for c in criteria}
    unscored = sorted(m for m in results if m not in known)
    return {"decision": decision, "rows": rows, "blocking": blocking, "watch": watch, "unscored": unscored}


# --- Try it out (not graded) ---
print("Criteria problems:", validate_criteria(CRITERIA))
readout = poc_readout(CRITERIA, RESULTS)
if readout:
    print("Decision:", readout["decision"].upper())
    for r in readout["rows"]:
        op = ">=" if r["direction"] == "higher" else "<="
        tag = "MUST" if r["must_have"] else "nice"
        print(f"  [{tag}] {r['metric']:30} {str(r['measured']):>8} vs {op} {r['threshold']:<6} {r['status']:13} vs baseline: {r['vs_baseline']}")
    print("Blocking:", readout["blocking"])
    print("Watch:", readout["watch"])
    print("Not in the agreed criteria (don't score these):", readout["unscored"])
