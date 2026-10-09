import re
from anthropic import _sim

# Kestrel Benefits plan documents (fictional), already chunked. Available to your code as PLAN_DOCS.
PLAN_DOCS = {
    "BEN-01": {"title": "Medical plan overview",
               "text": "The Standard medical plan has a $1,500 individual deductible. Preventive care is covered in full before the deductible."},
    "BEN-02": {"title": "Prescription drugs",
               "text": "Generic drugs cost $10 per prescription. Specialty drugs require prior approval from the plan."},
    "BEN-03": {"title": "Dental coverage",
               "text": "The plan covers two dental cleanings per year at no cost. Cleanings must be at least six months apart."},
    "BEN-04": {"title": "Fertility benefits",
               "text": "IVF and egg freezing are covered up to a lifetime maximum of $20,000. A referral from a specialist is required."},
    "BEN-05": {"title": "Paid parental leave",
               "text": "Birth and adoptive parents receive 16 weeks of paid leave at full salary."},
    "BEN-06": {"title": "Taking parental leave",
               "text": "Parental leave must be taken within 12 months of the birth or adoption. Tell your manager at least 30 days before leave starts."},
    "BEN-07": {"title": "Vision coverage",
               "text": "One eye exam per year is covered. Frames are covered up to $150 every two years."},
    "BEN-08": {"title": "Voluntary benefits",
               "text": "Employees can buy extra life insurance and accident insurance through payroll deduction."},
}

# Stand-in for Kestrel's retriever: which chunks come back for each question, best first.
_RETRIEVAL = {
    "How many dental cleanings are covered each year?": ["BEN-03", "BEN-01", "BEN-07"],
    "How long is paid parental leave?": ["BEN-05", "BEN-06"],
    "Does the plan cover fertility treatment?": ["BEN-04", "BEN-02"],
    "Is pet insurance included?": ["BEN-08"],
}


def search(question, k=3):
    """Retrieve up to k chunks for the question: [{"id", "title", "text"}], best first."""
    return [dict(PLAN_DOCS[i], id=i) for i in _RETRIEVAL.get(question, [])[:k]]


# Stand-in for Claude answering from the <documents> it was given.
_FIRST = {
    "dental cleanings": "The plan covers two dental cleanings per year at no cost [BEN-03]. "
                        "Cleanings must be at least six months apart [BEN-03].",
    "parental leave": "Birth and adoptive parents receive 16 weeks of paid leave at full salary [BEN-05]. "
                      "You can split the leave into two blocks [BEN-11].",
    "fertility": "IVF and egg freezing are covered up to a lifetime maximum of $20,000 [BEN-04]. "
                 "Most employees use the benefit within two years.",
}
_RETRY = {
    "parental leave": "Birth and adoptive parents receive 16 weeks of paid leave at full salary [BEN-05]. "
                      "The leave must be taken within 12 months of the birth or adoption [BEN-06].",
    "fertility": "IVF and egg freezing are covered up to a lifetime maximum of $20,000 [BEN-04]. "
                 "Most employees use the benefit within two years.",
}


def _responder(params):
    first = params["messages"][0]["content"]
    question = first.split("<question>", 1)[-1].split("</question>", 1)[0].strip().lower()
    table = _RETRY if len(params["messages"]) > 1 else _FIRST
    for cue, reply in table.items():
        if cue in question:
            needed = re.findall(r"\[([A-Z]+-\d+)\]", _FIRST[cue])
            sources = re.findall(r"<source>([^<]+)</source>", first)
            if any(n in sources for n in needed):
                return reply
    return "INSUFFICIENT_CONTEXT"


_sim.set_responder(_responder)
