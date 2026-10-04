import json
from anthropic import _sim


def _responder(params):
    prompt = str(params["messages"][-1]["content"])
    facts = json.loads(prompt.split("<engagement_facts>", 1)[1].split("</engagement_facts>", 1)[0])
    b = facts["baseline"]
    return json.dumps({
        "problem_statement": f"NorthStar's ops team handles about {b['per_day']} shipment exceptions a day by hand; "
                             f"{b['breach_rate']:.0%} miss the customer's response SLA.",
        "executive_summary": f"A {facts['budget_days']}-day engagement to triage exceptions automatically and draft customer "
                             f"updates, with a weekly SLA report, SSO and an audit log.",
        "risks": ["Carrier event data quality", "Customer messages must never promise compensation"],
        "open_questions": ["Who approves carrier reroutes?", "Which SLA clock applies on weekends?"],
    })


_sim.set_responder(_responder)
