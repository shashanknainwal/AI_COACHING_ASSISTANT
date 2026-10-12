# Thornbury Mutual (fictional insurer): claims-intake extraction proof of concept.
# The criteria were agreed in writing at kickoff and signed by the decision owner,
# Ruth Okafor (VP Claims Operations, fictional). Baselines come from two weeks of
# measuring today's manual process before any model was involved.
CRITERIA = [
    {"metric": "field_accuracy", "threshold": 0.95, "direction": "higher", "must_have": True,
     "baseline": 0.93, "how": "Share of 14 key fields correct on the 400-claim frozen test set, graded against adjudicated labels"},
    {"metric": "p95_latency_s", "threshold": 20, "direction": "lower", "must_have": True,
     "baseline": 14400, "how": "Seconds from claim upload to extracted record, 95th percentile (manual keying today: about 4 hours)"},
    {"metric": "pii_leaks", "threshold": 0, "direction": "lower", "must_have": True,
     "baseline": 0, "how": "Count of personal data fields written anywhere outside the claims system during the test"},
    {"metric": "straight_through_rate", "threshold": 0.60, "direction": "higher", "must_have": False,
     "baseline": 0.0, "how": "Share of claims needing no human correction"},
    {"metric": "cost_per_claim_usd", "threshold": 0.15, "direction": "lower", "must_have": False,
     "baseline": 4.80, "how": "Model and infrastructure cost per claim (manual keying today: $4.80 loaded labour)"},
    {"metric": "adjuster_hours_saved_per_week", "threshold": 120, "direction": "higher", "must_have": False,
     "baseline": 0, "how": "Measured in a two-week shadow run with one adjuster team"},
]

# Week 6 measurements. The shadow run never started (the adjuster team was pulled onto a storm surge),
# so adjuster_hours_saved_per_week has no number. Someone also added a demo survey score.
RESULTS = {
    "field_accuracy": 0.948,
    "p95_latency_s": 14.2,
    "pii_leaks": 0,
    "straight_through_rate": 0.52,
    "cost_per_claim_usd": 0.11,
    "demo_feedback_score": 9.1,
}
