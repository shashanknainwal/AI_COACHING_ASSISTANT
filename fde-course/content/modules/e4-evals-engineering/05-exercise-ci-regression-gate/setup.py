# Kestrel Mobile (fictional) eval results for the intent router, one row per golden case.
# Baseline: v3 in production. Candidate: v4, a rewritten prompt on a cheaper model.
# status is "pass", "fail" or "error" (the call failed, so the case wasn't scored).
_PREFIX = {"billing": "B", "network_outage": "N", "plan_change": "PC", "device_support": "D",
           "cancel": "C", "roaming": "R", "sim_swap_fraud": "S"}
_CODES = {"P": "pass", "F": "fail", "E": "error"}

_BASELINE = {
    "billing": "PPPPPPPPFF", "network_outage": "PPPPPPFF", "plan_change": "PPPPFP",
    "device_support": "PPPPPF", "cancel": "PPPP", "roaming": "PPF", "sim_swap_fraud": "PFP",
}
_CANDIDATE = {
    "billing": "PPPPPPPPPP", "network_outage": "PPPPPPPF", "plan_change": "PPPPPP",
    "device_support": "PPPPEF", "cancel": "PPFP", "roaming": "PFF", "sim_swap_fraud": "PPP",
}


def _rows(spec):
    rows = []
    for category, codes in spec.items():
        for i, code in enumerate(codes, start=1):
            rows.append({"id": f"{_PREFIX[category]}-{i:02d}", "category": category, "status": _CODES[code]})
    return rows


BASELINE_RUN = _rows(_BASELINE)
CANDIDATE_RUN = _rows(_CANDIDATE)
