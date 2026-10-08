INDEPENDENT_KINDS = {"candidate", "guide", "news"}
RANK = {"official": 0, "reported": 1, "anecdotal": 2}


def label_claim(claim):
    """Return "official", "reported", "anecdotal" or "unsupported" for one claim."""
    sources = claim.get("sources", [])
    if any(s.get("kind") == "company" for s in sources):
        return "official"
    ids = {s.get("independent_id") for s in sources if s.get("kind") in INDEPENDENT_KINDS}
    if len(ids) >= 3:
        return "reported"
    if ids:
        return "anecdotal"
    return "unsupported"


def prep_priorities(claims):
    """Return claim texts to prepare for: official, then reported, then anecdotal."""
    labelled = [(label_claim(c), c["text"]) for c in claims]
    kept = [(label, text) for label, text in labelled if label in RANK]
    kept = sorted(kept, key=lambda pair: RANK[pair[0]])  # sorted() is stable
    return [text for _, text in kept]


notes = [
    {"text": "Live interviews are AI-free unless they say otherwise",
     "sources": [{"kind": "company", "independent_id": "careers-page"}]},
    {"text": "The online assessment is one problem with about four levels",
     "sources": [{"kind": "candidate", "independent_id": "forum-post-a"},
                 {"kind": "guide", "independent_id": "prep-blog-b"},
                 {"kind": "candidate", "independent_id": "forum-post-c"}]},
    {"text": "Interviewers like hearing about a favourite paper",
     "sources": [{"kind": "guide", "independent_id": "prep-blog-b"},
                 {"kind": "guide", "independent_id": "prep-blog-b"}]},
    {"text": "You must memorise the lab's essays",
     "sources": [{"kind": "friend", "independent_id": "my-cousin"}]},
]

for n in notes:
    print(label_claim(n), "-", n["text"])

print("Prep plan:")
for i, text in enumerate(prep_priorities(notes), 1):
    print(f"  {i}. {text}")
