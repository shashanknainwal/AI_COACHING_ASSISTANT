SECTIONS = {"must have": "must", "nice to have": "nice", "logistics": "logistics"}
KIND_POINTS = {"work": 2, "project": 1, "course": 1}


def parse_posting(text):
    """Turn a posting's text into a list of requirement dicts, in order."""
    requirements = []
    section = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.endswith(":") and not line.startswith(("-", "*")):
            section = SECTIONS.get(line[:-1].strip().lower())
            continue
        if section is None or not line.startswith(("- ", "* ")):
            continue
        body = line[2:].strip()
        tag = None
        if body.endswith("]") and "[" in body:
            start = body.rindex("[")
            tag = body[start + 1:-1].strip().lower() or None
            body = body[:start].strip()
        requirements.append({"text": body, "tag": tag, "priority": section})
    return requirements


def score_evidence(item):
    """Score one piece of evidence from 0 to 3."""
    points = KIND_POINTS.get(item.get("kind"), 0)
    if points == 0:
        return 0
    if item.get("kind") == "project" and item.get("link"):
        points += 1
    if item.get("metric"):
        points += 1
    return min(points, 3)


def gap_report(requirements, evidence):
    """One row per requirement: its best evidence and a status."""
    report = []
    for req in requirements:
        row = {"requirement": req["text"], "priority": req["priority"], "status": None, "best": None}
        if req["priority"] == "logistics":
            row["status"] = "ask"
        elif req["tag"] is None:
            row["status"] = "review"
        else:
            best, best_score = None, 0
            for item in evidence:
                tags = [t.lower() for t in item.get("tags", [])]
                if req["tag"] in tags:
                    s = score_evidence(item)
                    if s > best_score:
                        best, best_score = item, s
            if best is not None:
                row["best"] = best["claim"]
            row["status"] = "green" if best_score == 3 else "amber" if best_score >= 1 else "red"
        report.append(row)
    return report


def focus_list(report):
    """Requirement texts to prepare, most urgent first."""
    order = [("must", "red"), ("must", "amber"), ("nice", "red")]
    return [row["requirement"] for p, s in order for row in report if row["priority"] == p and row["status"] == s]


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
for row in gap_report(reqs, evidence):
    print(f"{row['status']:7} {row['priority']:9} {row['requirement']}  <- {row['best']}")
print("Focus:", focus_list(gap_report(reqs, evidence)))
