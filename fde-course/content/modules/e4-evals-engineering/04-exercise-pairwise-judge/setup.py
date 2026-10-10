import json
from anthropic import _sim

# Stand-in for the judge model. It checks the facts a lawyer needs from each clause, but when both
# summaries cover the same number of facts it simply prefers whichever one it read first.
# Real judges show the same position bias, which is why you run both orders.
_FACTS = {
    "Either party may terminate": ["90 days", "written notice", "uncured breach"],
    "Supplier's total liability": ["12 months", "fees paid", "gross negligence"],
    "Customer shall pay": ["30 days", "1.5%", "disputed"],
    "Each party shall keep": ["5 years", "legally required", "return or destroy"],
    "This Agreement renews": ["12-month", "60 days", "5%"],
    "Supplier shall maintain": ["99.9%", "service credit", "scheduled maintenance"],
    "Neither party shall solicit": ["12 months", "general job postings"],
    "Customer may audit": ["once per year", "30 days' notice", "customer's cost"],
    "All disputes shall": ["Ostrava", "arbitration", "injunctive relief"],
    "Supplier may subcontract": ["prior written consent", "remains responsible"],
}


def _section(prompt, tag):
    return prompt.split(f"<{tag}>", 1)[-1].split(f"</{tag}>", 1)[0].strip()


def _facts_for(clause):
    for start, facts in _FACTS.items():
        if clause.startswith(start):
            return facts
    return []


def _responder(params):
    prompt = str(params["messages"][-1]["content"])
    facts = _facts_for(_section(prompt, "clause"))
    first, second = _section(prompt, "response_1"), _section(prompt, "response_2")
    s1 = sum(f.lower() in first.lower() for f in facts)
    s2 = sum(f.lower() in second.lower() for f in facts)
    if s1 > s2:
        out = {"winner": "first", "rationale": f"The first summary keeps {s1} of {len(facts)} key terms; the second keeps {s2}."}
    elif s2 > s1:
        out = {"winner": "second", "rationale": f"The second summary keeps {s2} of {len(facts)} key terms; the first keeps {s1}."}
    else:
        out = {"winner": "first", "rationale": "Both summaries cover the key terms. The first is clear and well organised."}
    return json.dumps(out)


_sim.set_responder(_responder)
