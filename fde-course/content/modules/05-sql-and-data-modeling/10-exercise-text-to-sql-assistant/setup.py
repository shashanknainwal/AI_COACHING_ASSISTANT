import json
from anthropic import _sim

# Stand-in for Claude writing SQL from the schema in the system prompt.
_ANSWERS = [
    ("most visits", "SELECT l.name AS location, COUNT(*) AS visits FROM visits v JOIN locations l ON l.id = v.location_id "
                    "WHERE v.visited_at >= '2026-03-01' AND v.visited_at < '2026-04-01' GROUP BY l.name ORDER BY visits DESC LIMIT 1",
     "Counts March 2026 visits by the location where each visit happened and returns the top one."),
    ("premium", "SELECT COUNT(*) AS premium_members FROM subscriptions s JOIN plans p ON p.id = s.plan_id "
                "WHERE p.name = 'Premium' AND s.status = 'active'",
     "Counts active subscriptions on the Premium plan."),
    ("delete", "DELETE FROM members WHERE id IN (SELECT member_id FROM subscriptions WHERE status = 'cancelled')",
     "Deletes members whose subscription is cancelled."),
    ("trainer", "SELECT trainer_name, COUNT(*) FROM sessions GROUP BY trainer_name",
     "Counts sessions per trainer."),
]


def _responder(params):
    question = str(params["messages"][-1]["content"]).lower()
    for cue, sql, why in _ANSWERS:
        if cue in question:
            return json.dumps({"sql": sql, "explanation": why})
    return json.dumps({"sql": "SELECT NULL", "explanation": "This question can't be answered from the schema."})


_sim.set_responder(_responder)
