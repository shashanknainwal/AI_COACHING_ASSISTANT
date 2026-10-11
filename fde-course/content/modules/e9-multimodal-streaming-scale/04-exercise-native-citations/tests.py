from anthropic import _sim

CUT = "Can a customer return cable that was cut to length?"
FEE = "Is there a restocking fee on unopened items?"
GLOVES = "What warranty do gloves have, and can I return them?"


def _fresh():
    _sim.calls.clear()
    _sim._queue.clear()


def _response(question):
    _fresh()
    docs = search(question)
    params = {"model": MODEL, "max_tokens": MAX_TOKENS, "messages": [{"role": "user", "content": [
        {"type": "document", "source": {"type": "text", "media_type": "text/plain", "data": d["text"]},
         "title": d["title"], "context": f"doc_id={d['id']}", "citations": {"enabled": True}} for d in docs
    ] + [{"type": "text", "text": question}]}]}
    return client.messages.create(**params), docs


def test_build_request_shape():
    """build_request() sends every document as a citable text document, then the question"""
    docs = search(CUT)
    req = build_request(CUT, docs)
    assert req.get("model") == MODEL and req.get("max_tokens") == MAX_TOKENS, f"model/max_tokens: {req}"
    assert req.get("output_config") == {"effort": "low"}, "set effort explicitly, and no format: it conflicts with citations"
    content = req["messages"][0]["content"]
    assert len(content) == len(docs) + 1, "one document block per doc, then the question"
    first = content[0]
    assert first.get("type") == "document" and first.get("citations") == {"enabled": True}, f"first block: {first}"
    assert first.get("source") == {"type": "text", "media_type": "text/plain", "data": docs[0]["text"]}, f"source: {first.get('source')}"
    assert first.get("title") == docs[0]["title"] and docs[0]["id"] in first.get("context", ""), "put the title in title and the doc id in context"
    assert content[-1] == {"type": "text", "text": CUT}


def test_check_request_rules():
    """check_request() rejects mixed citation settings and citations with structured output"""
    good = build_request(CUT, search(CUT))
    assert check_request(good) is None
    mixed = build_request(CUT, search(CUT))
    mixed["messages"][0]["content"][1]["citations"] = {"enabled": False}
    try:
        check_request(mixed)
        assert False, "citations on some documents but not others should raise ValueError"
    except ValueError:
        pass
    structured = build_request(CUT, search(CUT))
    structured["output_config"] = {"effort": "low", "format": {"type": "json_schema", "schema": {"type": "object"}}}
    try:
        check_request(structured)
        assert False, "citations plus output_config.format should raise ValueError (the API returns a 400)"
    except ValueError:
        pass
    plain = {"model": MODEL, "max_tokens": 10, "output_config": {"format": {"type": "json_schema", "schema": {}}},
             "messages": [{"role": "user", "content": "hi"}]}
    assert check_request(plain) is None, "structured output without citable documents is fine"


def test_render_markers_and_sources():
    """render() appends [n] markers after cited blocks and numbers sources by first appearance"""
    resp, docs = _response(CUT)
    out = render(resp, docs)
    assert out["answer"] == ("Cut-to-length cable can't be returned unless it has a manufacturing fault[1]. "
                             "If it is faulty, report it within 14 days of delivery with photos[2]."), f"answer was {out['answer']!r}"
    assert [s["n"] for s in out["sources"]] == [1, 2]
    assert out["sources"][0] == {"n": 1, "doc_id": "POL-RET-07", "title": "Returns policy v7",
                                 "quote": "Cable cut to customer length is non-returnable except for manufacturing faults."}, out["sources"][0]
    assert out["uncited"] == [], f"short connective text isn't a claim: {out['uncited']}"


def test_render_dedupes():
    """render() reuses a source number for a repeated quote and never repeats a marker in one block"""
    resp, docs = _response(GLOVES)
    out = render(resp, docs)
    assert out["answer"].endswith("within 30 days[2], and faulty ones must be reported within 14 days[3][1]."), f"answer was {out['answer']!r}"
    assert [(s["n"], s["doc_id"]) for s in out["sources"]] == [(1, "POL-WAR-03"), (2, "POL-RET-07"), (3, "POL-RET-07")], out["sources"]


def test_render_flags_uncited_claims():
    """render() lists uncited blocks of six or more words"""
    resp, docs = _response(FEE)
    out = render(resp, docs)
    assert out["uncited"] == ["Most customers get their refund within two working days."] or \
        out["uncited"] == [". Most customers get their refund within two working days."], out["uncited"]


def test_verify_catches_pipeline_bugs():
    """verify() passes real citations and catches a reordered or truncated document list"""
    resp, docs = _response(CUT)
    assert verify(resp, docs) == [], "these citations are valid against the documents that were sent"
    reordered = list(reversed(docs))
    probs = verify(resp, reordered)
    assert probs and all(p["kind"] == "text_mismatch" for p in probs), f"document_index refers to request order: {probs}"
    assert [p["block"] for p in probs] == [2, 4], f"report each cited block's index in response.content (the thinking block is index 0): {probs}"
    probs = verify(resp, docs[:0])
    assert [p["kind"] for p in probs] == ["bad_index", "bad_index"], probs


def test_answer_statuses():
    """answer() returns answered, needs_review, no_sources and refusal correctly"""
    _fresh()
    a = answer(client, CUT)
    assert a["status"] == "answered" and a["sources"] and a["problems"] == [], a
    sent = _sim.last_request()
    assert all(b.get("citations") == {"enabled": True} for b in sent["messages"][0]["content"][:-1]), "send citable documents"
    b = answer(client, FEE)
    assert b["status"] == "needs_review" and b["uncited"], b
    _fresh()
    c = answer(client, "Do you accept crypto?")
    assert c["status"] == "no_sources" and c["answer"] == INSUFFICIENT and not _sim.calls, "no documents: don't call Claude"
    _sim.queue(_sim.refusal("general_harms"))
    d = answer(client, CUT)
    assert d["status"] == "refusal" and d["answer"] == REFUSAL_MESSAGE, d
