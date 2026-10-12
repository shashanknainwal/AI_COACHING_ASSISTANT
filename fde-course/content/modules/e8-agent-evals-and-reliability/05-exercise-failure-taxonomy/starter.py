import re

# FAILURES, CODEBOOK, COST_PER_FAILURE and FIX_LIBRARY are loaded for you.


def normalize(note):
    # TODO: lowercase, straight apostrophes, keep only a-z 0-9 ' - and spaces, collapse whitespace.
    pass


def categorize(note):
    """First codebook category with a keyword in the normalized note, else None."""
    # TODO
    pass


def root_cause(failure):
    """(root category or "uncategorized", [downstream categories in step order])."""
    # TODO
    pass


def build_taxonomy(failures):
    """{"by_root": {category: [ids]}, "downstream": {category: count}}"""
    # TODO
    pass


def rank(taxonomy, costs, total):
    # TODO
    pass


def propose_fixes(ranked, taxonomy, top=2):
    # TODO
    pass


def analyze(failures, max_uncategorized=0.10):
    # TODO
    pass


# --- Try it out (not graded) ---
a = analyze(FAILURES)
if a:
    print(f"{'category':22}{'n':>4}{'share':>7}{'$ each':>8}{'impact':>8}{'cum':>7}")
    for r in a["ranked"]:
        print(f"{r['category']:22}{r['count']:>4}{r['share']:>7.3f}{r['cost_each']:>8}{r['impact']:>8}{r['cumulative_impact_share']:>7.3f}")
    print("most frequent:", a["most_frequent"], "| uncategorized:", a["uncategorized"], a["uncategorized_share"])
    print("downstream notes (not root causes):", a["downstream"])
    for f in a["fixes"]:
        print(f"FIX {f['category']} ({f['layer']}): {f['fix']}\n    EVAL: {f['eval']}  e.g. {f['examples']}")
