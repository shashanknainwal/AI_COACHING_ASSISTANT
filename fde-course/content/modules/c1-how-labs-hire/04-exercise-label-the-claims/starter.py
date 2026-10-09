def label_claim(claim):
    """Return "official", "reported", "anecdotal" or "unsupported" for one claim."""
    # TODO
    pass


def prep_priorities(claims):
    """Return claim texts to prepare for: official, then reported, then anecdotal."""
    # TODO
    pass


# --- Try it out (this part isn't graded) ---
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
print(prep_priorities(notes))
