# Gannet Home Energy (fictional): one run of the 40-case golden set on the current
# agent (baseline) and on a candidate with a new model and prompt. The E4 gate said
# "review" for five categories: each lost exactly one case, below its two-regression
# minimum. RERUNS holds five more trials of each flipped case on both versions.

_CATS = ["billing", "credit", "meter", "tariff", "vulnerable"]
_FIRST_BASE = {"billing": "PPPPPPPF", "credit": "PPPPPPFP", "meter": "PPPPPPPP", "tariff": "PPPPPFPP", "vulnerable": "PPPPPPPF"}
_FIRST_CAND = {"billing": "FPPPPPPF", "credit": "PFPPPPPP", "meter": "PPFPPPPP", "tariff": "PPPFPPPP", "vulnerable": "PPPPFPPP"}
_CODE = {"P": "pass", "F": "fail", "E": "error"}


def _rows(spec):
    return [{"id": f"{c[:3].upper()}-{i:02d}", "category": c, "status": _CODE[s]}
            for c in _CATS for i, s in enumerate(spec[c], start=1)]


BASELINE_RUN = _rows(_FIRST_BASE)
CANDIDATE_RUN = _rows(_FIRST_CAND)

_R = lambda s: [_CODE[x] for x in s]
RERUNS = {
    "BIL-01": {"baseline": _R("PFPFP"), "candidate": _R("FPFPF")},
    "CRE-02": {"baseline": _R("PPPPP"), "candidate": _R("FFFFP")},
    "MET-03": {"baseline": _R("PPPPP"), "candidate": _R("PPPPP")},
    "TAR-04": {"baseline": _R("PPFPP"), "candidate": _R("PFPPF")},
    "VUL-05": {"baseline": _R("PPPPP"), "candidate": _R("FFFEF")},
    "TAR-06": {"baseline": _R("FFFFF"), "candidate": _R("PPPPP")},
    "CRE-07": {"baseline": _R("FPFFP"), "candidate": _R("PPPPP")},
    "VUL-08": {"baseline": _R("FFPFF"), "candidate": _R("PFPPF")},
}

CONFIG = {"k": 5, "max_calls": 80, "critical_categories": ["vulnerable"]}


def paired_flips(baseline, candidate):
    """From module E4/05: regressions and fixes in baseline order (errors are neither)."""
    cand = {r["id"]: r for r in candidate}
    out = {"regressions": [], "fixes": [], "missing": []}
    for b in baseline:
        c = cand.get(b["id"])
        if c is None:
            out["missing"].append(b["id"])
        elif b["status"] == "pass" and c["status"] == "fail":
            out["regressions"].append(b["id"])
        elif b["status"] == "fail" and c["status"] == "pass":
            out["fixes"].append(b["id"])
    return out


_T95 = [12.706, 4.303, 3.182, 2.776, 2.571, 2.447, 2.365, 2.306, 2.262, 2.228,
        2.201, 2.179, 2.160, 2.145, 2.131, 2.120, 2.110, 2.101, 2.093, 2.086,
        2.080, 2.074, 2.069, 2.064, 2.060, 2.056, 2.052, 2.048, 2.045, 2.042]


def t95(df):
    """Two-sided 95% critical value of Student's t; 1.96 above 30 degrees of freedom."""
    return _T95[df - 1] if df <= 30 else 1.96
