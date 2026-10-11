def parse_posting(text):
    """Turn a posting's text into a list of requirement dicts, in order."""
    # TODO
    pass


def score_evidence(item):
    """Score one piece of evidence from 0 to 3."""
    # TODO
    pass


def gap_report(requirements, evidence):
    """One row per requirement: its best evidence and a status."""
    # TODO
    pass


def focus_list(report):
    """Requirement texts to prepare, most urgent first."""
    # TODO
    pass


# --- Try it out (this part isn't graded) ---
posting = """
Applied AI Engineer (practice posting, fictional)

Must have:
- 4+ years in a technical role [experience]
- Built evaluation frameworks for LLM systems [evals]
- Strong Python [python]
- Explains technical tradeoffs to customers [customer]

Nice to have:
- Retrieval or RAG systems in production [retrieval]
- Experience with agents and tool use [agents]

Logistics:
- Travel up to 25% to customer sites
"""

evidence = [
    {"claim": "6 years backend engineering at a logistics SaaS", "tags": ["experience", "python"], "kind": "work", "metric": True},
    {"claim": "Public eval harness repo for a support classifier", "tags": ["evals"], "kind": "project", "link": "github.com/you/evals", "metric": False},
    {"claim": "Completed course module on agents", "tags": ["agents"], "kind": "course"},
]

reqs = parse_posting(posting)
print("Requirements:", reqs)
report = gap_report(reqs, evidence)
print("Report:", report)
print("Focus:", focus_list(report))
