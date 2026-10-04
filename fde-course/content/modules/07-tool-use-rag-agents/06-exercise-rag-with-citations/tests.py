import json
import math
import anthropic
from anthropic import _sim
from fde_datasets import brightway


def _fresh():
    _sim.calls.clear()
    _sim._queue.clear()


def _ids(results):
    return [r["id"] for r in results]


def test_chunk_articles():
    """chunk_articles() makes one stripped chunk per paragraph with stable IDs"""
    chunks = chunk_articles(brightway.KB_ARTICLES)
    assert isinstance(chunks, list) and len(chunks) == 18, f"expected 18 chunks, got {None if chunks is None else len(chunks)}"
    assert chunks[0] == {"id": "KB-01#1", "title": "Returns policy",
                         "text": "You can return most items within 30 days of delivery for a full refund to the original payment method."}
    assert [c["id"] for c in chunks if c["id"].startswith("KB-05")] == ["KB-05#1", "KB-05#2"]
    odd = chunk_articles([{"id": "X", "title": "T", "text": "  one  \n\n\n\n two\n\n   "}])
    assert odd == [{"id": "X#1", "title": "T", "text": "one"}, {"id": "X#2", "title": "T", "text": "two"}], \
        f"strip paragraphs and skip empty ones: {odd}"


def test_tokenize():
    """tokenize() lowercases, drops stopwords and strips plural s"""
    assert tokenize("What's the Gold membership?") == ["gold", "membership"], tokenize("What's the Gold membership?")
    assert tokenize("Late by 6 DAYS, two sofas!") == ["late", "6", "day", "two", "sofa"]
    assert tokenize("bus gas") == ["bus", "gas"], "only strip s from words longer than 3 letters"
    assert tokenize("Is it in my order?") == ["order"]


def test_build_index():
    """build_index() stores token sets (title included) and IDF weights"""
    chunks = chunk_articles(brightway.KB_ARTICLES)
    index = build_index(chunks)
    assert set(index) == {"chunks", "tokens", "idf"}, f"keys: {set(index)}"
    assert index["chunks"] is chunks or index["chunks"] == chunks
    assert isinstance(index["tokens"][0], set) and {"return", "policy", "refund"} <= index["tokens"][0], \
        "each token set includes the title's tokens"
    assert abs(index["idf"]["gift"] - math.log(1 + 18 / 2)) < 1e-9, "idf = log(1 + N / df)"
    assert index["idf"]["sofa"] > index["idf"]["credit"], "rarer terms get higher weights"


def test_search():
    """search() ranks chunks by summed IDF and returns the top k"""
    hits = search(INDEX, "Can I return a sofa?")
    assert _ids(hits) == ["KB-01#2", "KB-01#1", "KB-01#3"], f"got {_ids(hits or [])}"
    assert set(hits[0]) == {"id", "title", "text", "score"} and hits[0]["score"] == 4.47, f"got {hits[0]}"
    assert "score" not in INDEX["chunks"][1], "return copies; don't add score to the indexed chunks"
    assert _ids(search(INDEX, "My order is 6 business days late. What credit do gold members get?")) == ["KB-02#2", "KB-02#3", "KB-05#1"]
    assert _ids(search(INDEX, "Can I return a sofa?", k=1)) == ["KB-01#2"]
    assert search(INDEX, "What's the weather in Denver?") == [], "no matching terms means no results"


def test_build_prompt():
    """build_prompt() puts documents first, then the question"""
    doc = {"id": "KB-08#1", "title": "Gift cards", "text": "Gift cards arrive within an hour.", "score": 4.6}
    got = build_prompt("When does it arrive?", [doc])
    expected = ('<documents>\n<document id="KB-08#1" title="Gift cards">\nGift cards arrive within an hour.\n</document>\n'
                '</documents>\n\n<question>\nWhen does it arrive?\n</question>')
    assert got == expected, f"got:\n{got}"


def test_answer_schema():
    """ANSWER_SCHEMA is strict: answer, citations, answerable"""
    s = ANSWER_SCHEMA
    assert s.get("type") == "object" and s.get("additionalProperties") is False
    props = s.get("properties", {})
    assert props.get("answer", {}).get("type") == "string" and props.get("answerable", {}).get("type") == "boolean"
    assert props.get("citations", {}).get("type") == "array" and props["citations"].get("items", {}).get("type") == "string"
    assert sorted(s.get("required", [])) == ["answer", "answerable", "citations"]


def test_answer_grounded():
    """answer() sends the retrieved documents and returns a cited answer"""
    _fresh()
    q = "My order is 6 business days late. What credit do gold members get?"
    got = answer(anthropic.Anthropic(), INDEX, q)
    assert got == {"answer": "Gold members get a $25 store credit when an order arrives more than 5 business days late.",
                   "citations": ["KB-02#2", "KB-02#3"], "answerable": True}, f"got {got}"
    assert len(_sim.calls) == 1
    p = _sim.calls[0]["params"]
    assert p["model"] == MODEL and p["max_tokens"] >= 1024 and p.get("system") == SYSTEM_PROMPT
    assert p["messages"] == [{"role": "user", "content": build_prompt(q, search(INDEX, q))}], "send build_prompt(question, results)"
    fmt = (p.get("output_config") or {}).get("format", {})
    assert fmt.get("type") == "json_schema" and fmt.get("schema") == ANSWER_SCHEMA, "use output_config with ANSWER_SCHEMA"


def test_answer_skips_claude_without_documents():
    """With nothing retrieved, answer() returns NO_ANSWER without calling Claude"""
    _fresh()
    got = answer(anthropic.Anthropic(), INDEX, "What's the weather in Denver?")
    assert got == {"answer": NO_ANSWER, "citations": [], "answerable": False}, f"got {got}"
    assert len(_sim.calls) == 0, "don't pay for a call when there is nothing to ground the answer in"


def test_answer_not_answerable():
    """When Claude says the documents don't answer it, return NO_ANSWER"""
    _fresh()
    got = answer(anthropic.Anthropic(), INDEX, "Do you price match competitors?")
    assert got == {"answer": NO_ANSWER, "citations": [], "answerable": False}, f"got {got}"
    assert len(_sim.calls) == 1


def test_answer_validates_citations():
    """Invented citations are dropped; an answer with no valid citation is not shown"""
    _fresh()
    _sim.queue(json.dumps({"answer": "Sofas: 14 days, $49 pickup.", "citations": ["KB-99#9", "KB-01#2"], "answerable": True}))
    got = answer(anthropic.Anthropic(), INDEX, "Can I return a sofa?")
    assert got == {"answer": "Sofas: 14 days, $49 pickup.", "citations": ["KB-01#2"], "answerable": True}, f"got {got}"
    _fresh()
    _sim.queue(json.dumps({"answer": "Sofas are free to return forever.", "citations": ["KB-04#1"], "answerable": True}))
    got = answer(anthropic.Anthropic(), INDEX, "Can I return a sofa?")
    assert got == {"answer": NO_ANSWER, "citations": [], "answerable": False}, \
        f"KB-04#1 wasn't retrieved, so the answer is unsupported: {got}"
