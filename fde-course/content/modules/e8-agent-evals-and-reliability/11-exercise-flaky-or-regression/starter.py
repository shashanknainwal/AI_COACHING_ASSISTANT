import math

# BASELINE_RUN, CANDIDATE_RUN, RERUNS, CONFIG, paired_flips() and t95() are loaded for you.


def rerun_policy(flips, k, max_calls):
    """{"rerun": [...], "calls": n, "skipped": [...]}"""
    # TODO: regressions first, then fixes; each case costs 2 * k calls.
    pass


def case_rate(statuses):
    """(passes, n) with errors left out."""
    # TODO
    pass


def classify(base_statuses, cand_statuses):
    # TODO: "regression", "fix", "flaky", "stable" or "unknown"
    pass


def observations(first_run, reruns, version):
    """{case_id: [0/1, ...]} from the first run plus any reruns, errors left out."""
    # TODO
    pass


def clustered_rate(obs):
    # TODO
    pass


def paired_difference(base_obs, cand_obs):
    # TODO
    pass


def verdict(baseline, candidate, reruns, config):
    # TODO
    pass


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
