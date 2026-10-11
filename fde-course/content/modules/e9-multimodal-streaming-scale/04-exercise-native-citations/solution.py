import re


def build_request(question, docs):
    blocks = [
        {"type": "document",
         "source": {"type": "text", "media_type": "text/plain", "data": d["text"]},
         "title": d["title"],
         "context": f"doc_id={d['id']}",
         "citations": {"enabled": True}}
        for d in docs
    ]
    return {
        "model": MODEL,
        "max_tokens": MAX_TOKENS,
        "output_config": {"effort": "low"},
        "messages": [{"role": "user", "content": blocks + [{"type": "text", "text": question}]}],
    }


def check_request(params):
    docs = []
    for m in params.get("messages", []):
        if isinstance(m.get("content"), list):
            docs += [b for b in m["content"] if isinstance(b, dict) and b.get("type") == "document"]
    enabled = [bool((b.get("citations") or {}).get("enabled")) for b in docs]
    if any(enabled) and not all(enabled):
        raise ValueError("citations must be enabled on all documents or none")
    if any(enabled) and "format" in (params.get("output_config") or {}):
        raise ValueError("citations can't be combined with output_config.format")


def _words(text):
    return re.findall(r"[A-Za-z0-9']+", text)


def render(response, docs):
    answer, sources, uncited, seen = "", [], [], {}
    for block in response.content:
        if block.type != "text":
            continue
        answer += block.text
        cites = getattr(block, "citations", None) or []
        if not cites:
            if len(_words(block.text)) >= MIN_UNCITED_WORDS:
                uncited.append(block.text.strip())
            continue
        markers = []
        for c in cites:
            doc = docs[c.document_index]
            key = (doc["id"], c.cited_text)
            if key not in seen:
                seen[key] = len(sources) + 1
                sources.append({"n": seen[key], "doc_id": doc["id"], "title": doc["title"], "quote": c.cited_text})
            if seen[key] not in markers:
                markers.append(seen[key])
        answer += "".join(f"[{n}]" for n in markers)
    return {"answer": answer, "sources": sources, "uncited": uncited}


def verify(response, docs):
    problems = []
    for i, block in enumerate(response.content):
        for c in (getattr(block, "citations", None) or []) if block.type == "text" else []:
            if c.type != "char_location":
                continue
            if not 0 <= c.document_index < len(docs):
                problems.append({"block": i, "kind": "bad_index"})
            elif docs[c.document_index]["text"][c.start_char_index:c.end_char_index].strip() != c.cited_text.strip():
                problems.append({"block": i, "kind": "text_mismatch"})
    return problems


def answer(client, question):
    docs = search(question, k=3)
    if not docs:
        return {"status": "no_sources", "answer": INSUFFICIENT, "sources": [], "uncited": [], "problems": []}
    params = build_request(question, docs)
    check_request(params)
    response = client.messages.create(**params)
    if response.stop_reason == "refusal":
        return {"status": "refusal", "answer": REFUSAL_MESSAGE, "sources": [], "uncited": [], "problems": []}
    out = render(response, docs)
    out["problems"] = verify(response, docs)
    out["status"] = "needs_review" if out["uncited"] or out["problems"] else "answered"
    return out


# --- Try it out (not graded) ---
if __name__ == "__main__":
    for q in ["Can a customer return cable that was cut to length?",
              "Is there a restocking fee on unopened items?",
              "What warranty do gloves have, and can I return them?",
              "Do you accept crypto?"]:
        r = answer(client, q)
        print(r["status"], "|", r["answer"])
        for s in r["sources"]:
            print(f"   [{s['n']}] {s['doc_id']}: {s['quote']}")
        if r["uncited"]:
            print("   uncited:", r["uncited"])
