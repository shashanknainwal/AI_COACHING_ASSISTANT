# Gannet Home Energy (fictional): 60 failed conversations from last week's sample of
# 400 production traces, each annotated by a reviewer. Notes are free text, written
# fast, by three different people. Each note says at which agent step it happened.

# The codebook the reviewers agreed after the first 30 traces ("axial coding").
# Keywords are already normalized: lowercase, straight apostrophes, no punctuation.
CODEBOOK = {
    "identity_skipped": ["didn't verify", "no verification", "skipped verification", "unverified"],
    "missed_escalation": ["should have escalated", "didn't escalate", "no handoff", "vulnerable"],
    "false_completion": ["said done", "claimed", "not saved", "didn't actually"],
    "wrong_credit_amount": ["wrong credit", "credit amount", "over-credited", "under-credited"],
    "wrong_tariff_info": ["old price", "outdated price", "wrong unit rate", "stale tariff"],
    "tool_args_error": ["wrong account id", "bad date format", "invalid argument", "malformed"],
    "looping": ["loop", "repeated the same", "asked again"],
    "tone": ["rude", "curt", "robotic"],
}

# Estimated cost of one failure of each kind, in dollars, agreed with Gannet's ops and
# compliance leads: repeat contacts, refunds, complaints and regulatory exposure.
COST_PER_FAILURE = {
    "identity_skipped": 150, "missed_escalation": 220, "false_completion": 35,
    "wrong_credit_amount": 60, "wrong_tariff_info": 25, "tool_args_error": 12,
    "looping": 8, "tone": 5,
}

FIX_LIBRARY = {
    "identity_skipped": {"layer": "tool code",
                         "fix": "Write tools refuse to run until verify_identity has succeeded in this session.",
                         "eval": "Trajectory rule on every run: no write tool before a successful verify_identity."},
    "missed_escalation": {"layer": "prompt and routing",
                          "fix": "Add a vulnerability and over-limit checklist to the prompt and an escalate_to_human tool description that says when to call it.",
                          "eval": "Simulated-user episodes with vulnerable and over-limit customers; end state must show escalated=True."},
    "false_completion": {"layer": "tool results",
                         "fix": "Tools return the saved record; the prompt forbids 'Done:' unless a write returned ok.",
                         "eval": "End-state check after every episode; count 'claimed but failed' separately."},
    "wrong_credit_amount": {"layer": "tool code",
                            "fix": "Compute credits in the tool from the policy table instead of letting the model pick the amount.",
                            "eval": "End-state check on the credit field across the credit policy matrix."},
    "wrong_tariff_info": {"layer": "retrieval",
                          "fix": "Serve prices from the live tariff API instead of the prompt.",
                          "eval": "Code grader comparing quoted prices with the tariff API."},
    "tool_args_error": {"layer": "tool definitions",
                        "fix": "Tighten schemas with strict mode and formats; return actionable error text.",
                        "eval": "Tool-call accuracy on recorded inputs."},
    "looping": {"layer": "loop", "fix": "Detect repeated identical calls and stop early.", "eval": "Calls-per-run p95 on the suite."},
    "tone": {"layer": "prompt", "fix": "Add voice examples.", "eval": "Rubric judge on a sample."},
}

_PHRASES = {
    "identity_skipped": ["Didn’t verify identity before changing tariff", "NO verification - went straight to credit",
                         "Skipped verification!!", "Acted on an unverified caller"],
    "missed_escalation": ["Should have escalated: customer said they're on a medical device",
                          "Didn't escalate the over-limit refund", "No handoff despite 3 requests for a human",
                          "Vulnerable customer (prepay, no credit) - kept going"],
    "false_completion": ["Said done, reading not saved", "Claimed tariff switched; DB unchanged",
                         "Booking NOT SAVED but told customer it was", "Didn't actually submit the reading"],
    "wrong_credit_amount": ["Wrong credit: gave $50 for a $20 policy", "Credit amount off by 10x",
                            "Over-credited (applied twice)", "under-credited, ignored the second missed visit"],
    "wrong_tariff_info": ["Quoted the old price for Fixed 24", "Outdated price on EV Night",
                          "Wrong unit rate quoted (Sept rate)", "Stale tariff table in answer"],
    "tool_args_error": ["Wrong account ID passed to get_bill", "Bad date format (03/11) to book_engineer",
                        "Invalid argument: tariff='fixed'", "Malformed JSON in update_contact"],
    "looping": ["Loop: called check_slots 6 times", "Repeated the same question three times", "Asked again for the postcode it already had"],
    "tone": ["Rude reply to a complaint", "Curt and robotic"],
    None: ["Answered in Welsh", "Customer hung up, reason unclear"],
}

_ROOTS = (["false_completion"] * 14 + ["wrong_tariff_info"] * 12 + ["wrong_credit_amount"] * 8
          + ["tool_args_error"] * 7 + ["identity_skipped"] * 6 + ["missed_escalation"] * 5
          + ["looping"] * 4 + ["tone"] * 2 + [None] * 2)
_ORDER = [(i * 37) % 60 for i in range(60)]          # interleave so categories aren't in blocks

FAILURES = []
_seen = {}
for n, idx in enumerate(_ORDER, start=1):
    cat = _ROOTS[idx]
    k = _seen.get(cat, 0)
    _seen[cat] = k + 1
    phrases = _PHRASES[cat]
    notes = [{"step": 2 + k % 3, "note": phrases[k % len(phrases)]}]
    # Earlier mistakes cause later ones. Reviewers note both; only the first is the root cause.
    if cat == "tool_args_error" and k < 4:
        notes.append({"step": 6, "note": _PHRASES["false_completion"][k % 4]})
    if cat == "identity_skipped" and k < 3:
        notes.append({"step": 5, "note": _PHRASES["wrong_credit_amount"][k % 4]})
    if cat == "wrong_tariff_info" and k % 4 == 1:
        notes.insert(0, {"step": 1, "note": "Greeting fine, picked the right intent"})
        notes[1]["step"] = 3
    FAILURES.append({"id": f"F-{n:02d}", "notes": sorted(notes, key=lambda x: -x["step"])})
