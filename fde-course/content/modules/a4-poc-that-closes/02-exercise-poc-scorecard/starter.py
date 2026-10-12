# CRITERIA and RESULTS (Thornbury Mutual, week 6) are loaded for you.
# print(CRITERIA[0]) or print(RESULTS) to look at them.


def validate_criteria(criteria):
    """Problems that would make these criteria impossible to judge. An empty list means they're usable."""
    # TODO
    pass


def evaluate_criterion(criterion, results, margin=0.02):
    """Judge one criterion against the measured results. Returns one readout row."""
    # TODO
    pass


def poc_readout(criteria, results, margin=0.02):
    """Go / conditional / no-go / incomplete, with the rows and the reasons."""
    # TODO
    pass


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
