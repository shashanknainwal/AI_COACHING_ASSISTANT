import anthropic
from anthropic import _sim


def _fresh():
    _sim.calls.clear()
    _sim._queue.clear()


DENTAL = "How many dental cleanings are covered each year?"
LEAVE = "How long is paid parental leave?"
FERTILITY = "Does the plan cover fertility treatment?"


def test_format_documents():
    """format_documents() wraps each chunk in indexed <document> tags with its source id"""
    docs = [{"id": "BEN-07", "title": "Vision coverage", "text": "One eye exam per year is covered."},
            {"id": "BEN-02", "title": "Prescription drugs", "text": "Generic drugs cost $10."}]
    expected = ('<documents>\n<document index="1">\n<source>BEN-07</source>\n<document_content>\n'
                'One eye exam per year is covered.\n</document_content>\n</document>\n'
                '<document index="2">\n<source>BEN-02</source>\n<document_content>\n'
                'Generic drugs cost $10.\n</document_content>\n</document>\n</documents>')
    got = format_documents(docs)
    assert got == expected, f"got:\n{got}"


def test_build_user_message():
    """build_user_message() puts documents first and the question last"""
    docs = [{"id": "BEN-07", "title": "Vision coverage", "text": "One eye exam per year is covered."}]
    got = build_user_message("Are eye exams covered?", docs)
    assert got == (format_documents(docs) or "") + "\n\n<question>\nAre eye exams covered?\n</question>", f"got:\n{got}"


def test_parse_citations():
    """parse_citations() splits sentences and pulls out their cited ids"""
    got = parse_citations("Two cleanings are covered [BEN-03]. Frames up to $150 [BEN-07][BEN-01]! Is that all? Yes.")
    assert got == [{"sentence": "Two cleanings are covered.", "ids": ["BEN-03"]},
                   {"sentence": "Frames up to $150!", "ids": ["BEN-07", "BEN-01"]},
                   {"sentence": "Is that all?", "ids": []},
                   {"sentence": "Yes.", "ids": []}], f"got {got}"
    got = parse_citations("Generic drugs cost $10. [BEN-02] Specialty drugs need approval. [BEN-02]")
    assert got == [{"sentence": "Generic drugs cost $10.", "ids": ["BEN-02"]},
                   {"sentence": "Specialty drugs need approval.", "ids": ["BEN-02"]}], \
        f"a citation placed after the period belongs to the sentence before it: {got}"
    assert parse_citations("  ") == []


def test_validate():
    """validate() reports uncited sentences and ids that were never retrieved"""
    claims = [{"sentence": "A.", "ids": ["BEN-05"]}, {"sentence": "B.", "ids": []},
              {"sentence": "C.", "ids": ["BEN-11", "BEN-05", "BEN-11"]}, {"sentence": "D.", "ids": ["BEN-99"]}]
    got = validate(claims, ["BEN-05", "BEN-06"])
    assert got == {"ok": False, "uncited": ["B."], "unknown_ids": ["BEN-11", "BEN-99"]}, f"got {got}"
    assert validate([{"sentence": "A.", "ids": ["BEN-06"]}], ["BEN-05", "BEN-06"]) == \
        {"ok": True, "uncited": [], "unknown_ids": []}


def test_feedback_message():
    """feedback_message() tells Claude exactly what failed"""
    got = feedback_message({"ok": False, "uncited": ["B."], "unknown_ids": ["BEN-11"]})
    expected = ("Your previous answer failed the citation check.\n- No citation: B.\n- Not in the documents: BEN-11\n"
                "Rewrite the answer using only the documents above. End every sentence with the id of a document "
                "that supports it. If the documents don't answer the question, reply with exactly INSUFFICIENT_CONTEXT.")
    assert got == expected, f"got:\n{got}"


def test_answer_grounded():
    """answer_question() retrieves, sends one grounded request and returns a cited answer"""
    _fresh()
    got = answer_question(anthropic.Anthropic(), DENTAL)
    assert isinstance(got, dict) and got.get("status") == "answered", f"got {got}"
    assert got == {"status": "answered",
                   "answer": "The plan covers two dental cleanings per year at no cost [BEN-03]. "
                             "Cleanings must be at least six months apart [BEN-03].",
                   "citations": ["BEN-03"], "attempts": 1, "problems": None}, f"got {got}"
    assert len(_sim.calls) == 1, f"one call when the first answer passes, got {len(_sim.calls)}"
    p = _sim.calls[0]["params"]
    assert p["model"] == MODEL and p["max_tokens"] >= 1024 and p.get("system") == SYSTEM_PROMPT
    assert p["messages"] == [{"role": "user", "content": build_user_message(DENTAL, search(DENTAL, 3))}], \
        "send build_user_message(question, search(question, k))"


def test_answer_retries_once_with_feedback():
    """An invented citation triggers one retry that carries the feedback"""
    _fresh()
    got = answer_question(anthropic.Anthropic(), LEAVE)
    assert isinstance(got, dict) and got.get("status") == "answered" and got.get("attempts") == 2, f"got {got}"
    assert got["citations"] == ["BEN-05", "BEN-06"]
    assert len(_sim.calls) == 2
    second = _sim.calls[1]["params"]["messages"]
    first_text = ("Birth and adoptive parents receive 16 weeks of paid leave at full salary [BEN-05]. "
                  "You can split the leave into two blocks [BEN-11].")
    assert len(second) == 3 and second[1] == {"role": "assistant", "content": first_text}, \
        "replay the first answer as the assistant turn"
    assert second[2] == {"role": "user", "content": feedback_message(
        {"ok": False, "uncited": [], "unknown_ids": ["BEN-11"]})}, "then send feedback_message(report) as the user turn"


def test_answer_flags_after_second_failure():
    """If the retry still fails, the answer is flagged, not shown as grounded"""
    _fresh()
    got = answer_question(anthropic.Anthropic(), FERTILITY)
    assert isinstance(got, dict) and got.get("status") == "flagged", f"got {got}"
    assert got["attempts"] == 2 and len(_sim.calls) == 2, f"stop after MAX_ATTEMPTS calls: {len(_sim.calls)}"
    assert got["problems"] == {"uncited": ["Most employees use the benefit within two years."], "unknown_ids": []}
    assert got["citations"] == ["BEN-04"]
    _fresh()
    _sim.queue("Leave lasts 20 weeks [BEN-99].", "Leave lasts 20 weeks [BEN-99].")
    got = answer_question(anthropic.Anthropic(), LEAVE)
    assert got["status"] == "flagged" and got["problems"] == {"uncited": [], "unknown_ids": ["BEN-99"]}, f"got {got}"


def test_answer_insufficient():
    """Claude's INSUFFICIENT_CONTEXT and an empty retrieval both return status insufficient"""
    _fresh()
    got = answer_question(anthropic.Anthropic(), "Is pet insurance included?")
    assert got == {"status": "insufficient", "answer": None, "citations": [], "attempts": 1, "problems": None}, f"got {got}"
    _fresh()
    got = answer_question(anthropic.Anthropic(), "What's the capital of France?")
    assert got == {"status": "insufficient", "answer": None, "citations": [], "attempts": 0, "problems": None}, f"got {got}"
    assert len(_sim.calls) == 0, "nothing retrieved means nothing to ground an answer in: don't call Claude"
