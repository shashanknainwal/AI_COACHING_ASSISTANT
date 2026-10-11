import re

# FAILURES, CODEBOOK, COST_PER_FAILURE and FIX_LIBRARY are loaded for you.


def normalize(note):
    text = note.lower().replace("’", "'").replace("‘", "'")
    text = re.sub(r"[^a-z0-9' \-]", "", text)
    return " ".join(text.split())


def categorize(note):
    """First codebook category with a keyword in the normalized note, else None."""
    text = normalize(note)
    for category, keywords in CODEBOOK.items():
        if any(k in text for k in keywords):
            return category
    return None


def root_cause(failure):
    """(root category or "uncategorized", [downstream categories in step order])."""
    cats = [categorize(n["note"]) for n in sorted(failure["notes"], key=lambda n: n["step"])]
    cats = [c for c in cats if c]
    if not cats:
        return "uncategorized", []
    return cats[0], cats[1:]


def build_taxonomy(failures):
    tax = {}
    downstream = {}
    for f in failures:
        root, later = root_cause(f)
        tax.setdefault(root, []).append(f["id"])
        for c in later:
            downstream[c] = downstream.get(c, 0) + 1
    return {"by_root": tax, "downstream": downstream}


def rank(taxonomy, costs, total):
    rows = []
    for cat, ids in taxonomy["by_root"].items():
        if cat == "uncategorized":
            continue
        rows.append({"category": cat, "count": len(ids), "share": round(len(ids) / total, 3),
                     "cost_each": costs[cat], "impact": len(ids) * costs[cat]})
    rows.sort(key=lambda r: (-r["impact"], r["category"]))
    all_impact = sum(r["impact"] for r in rows)
    running = 0
    for r in rows:
        running += r["impact"]
        r["cumulative_impact_share"] = round(running / all_impact, 3)
    return rows


def propose_fixes(ranked, taxonomy, top=2):
    out = []
    for r in ranked[:top]:
        lib = FIX_LIBRARY[r["category"]]
        out.append({"category": r["category"], "impact": r["impact"], "layer": lib["layer"],
                    "fix": lib["fix"], "eval": lib["eval"], "examples": taxonomy["by_root"][r["category"]][:3]})
    return out


def analyze(failures, max_uncategorized=0.10):
    tax = build_taxonomy(failures)
    ranked = rank(tax, COST_PER_FAILURE, len(failures))
    unc = len(tax["by_root"].get("uncategorized", [])) / len(failures)
    by_count = sorted(ranked, key=lambda r: (-r["count"], r["category"]))
    return {
        "ranked": ranked,
        "most_frequent": by_count[0]["category"],
        "uncategorized": tax["by_root"].get("uncategorized", []),
        "uncategorized_share": round(unc, 3),
        "codebook_saturated": unc <= max_uncategorized,
        "downstream": dict(sorted(tax["downstream"].items())),
        "fixes": propose_fixes(ranked, tax),
    }


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
