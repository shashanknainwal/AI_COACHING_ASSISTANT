import re


def build_request(question, docs):
    """Keyword arguments for client.messages.create with citable documents."""
    # TODO: one document block per doc (citations enabled), then the question
    return {}


def check_request(params):
    """Raise ValueError if the request would be rejected for its citation settings."""
    # TODO: all-or-none, and no output_config.format alongside citations
    return None


def render(response, docs):
    """Rebuild the answer with [n] markers from the citation blocks."""
    # TODO
    return {"answer": "", "sources": [], "uncited": []}


def verify(response, docs):
    """Check every char_location citation against the documents you sent."""
    # TODO
    return []


def answer(client, question):
    # TODO: search, build, check, call, then render and verify
    return {"status": "answered", "answer": "", "sources": [], "uncited": [], "problems": []}


# --- Try it out (not graded) ---
if __name__ == "__main__":
    for q in ["Can a customer return cable that was cut to length?",
              "Is there a restocking fee on unopened items?",
              "What warranty do gloves have, and can I return them?",
              "Do you accept crypto?"]:
        print(answer(client, q))
