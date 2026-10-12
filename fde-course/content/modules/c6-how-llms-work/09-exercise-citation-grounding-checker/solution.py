import re

STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "of", "to", "in", "on", "for", "with", "at", "by",
    "from", "is", "are", "was", "were", "be", "been", "it", "its", "this", "that", "these", "those",
    "as", "can", "will", "may", "do", "does", "you", "your", "we", "our", "they", "their", "within",
}

# Retrieved spans for one question, keyed by citation number (Quillmark Outfitters is fictional).
SPANS = {
    1: "Unworn items can be returned within 30 days of delivery for a full refund to the original payment method.",
    2: "Refunds are issued within 5 business days after the returned item reaches our warehouse.",
    3: "Sale items marked final sale cannot be returned or exchanged.",
}

ANSWER = (
    "You can return unworn items within 30 days of delivery for a full refund [1]. "
    "Refunds are issued within 5 business days after the item reaches the warehouse [2]. "
    "Final sale items cannot be returned [3]. "
    "Return shipping is free for loyalty members [2]. "
    "Refunds for orders over $200 take 10 business days [2]. "
    "Exchanges are processed the same day. "
    "Gift cards are refunded as store credit [4]."
)

_CITE = re.compile(r"\[(\d+)\]")
_NUM = re.compile(r"\d+(?:[.,]\d+)*")


def _words(text):
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOPWORDS}


def split_sentences(text):
    """Split text into sentences after . ! or ? followed by whitespace. Drop empty pieces."""
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def check_claim(sentence, spans, threshold=0.6):
    """Return {"sentence", "citations", "status", "overlap"} for one sentence."""
    citations = []
    for n in _CITE.findall(sentence):
        if int(n) not in citations:
            citations.append(int(n))
    result = {"sentence": sentence, "citations": citations, "status": "", "overlap": 0.0}
    if not citations:
        result["status"] = "uncited"
        return result
    if any(c not in spans for c in citations):
        result["status"] = "bad_citation"
        return result
    claim = _CITE.sub("", sentence)
    source = " ".join(spans[c] for c in citations)
    claim_words = _words(claim)
    source_words = _words(source)
    overlap = 1.0 if not claim_words else len(claim_words & source_words) / len(claim_words)
    result["overlap"] = round(overlap, 2)
    numbers_ok = set(_NUM.findall(claim)) <= set(_NUM.findall(source))
    result["status"] = "supported" if numbers_ok and overlap >= threshold else "unsupported"
    return result


def grounding_report(answer, spans, threshold=0.6):
    """Check every sentence. Return {"claims", "supported", "total", "grounded_ratio", "flagged"}."""
    claims = [check_claim(s, spans, threshold) for s in split_sentences(answer)]
    supported = sum(1 for c in claims if c["status"] == "supported")
    total = len(claims)
    return {
        "claims": claims,
        "supported": supported,
        "total": total,
        "grounded_ratio": round(supported / total, 2) if total else 0.0,
        "flagged": [c["sentence"] for c in claims if c["status"] != "supported"],
    }


# --- Try it out (not graded) ---
report = grounding_report(ANSWER, SPANS)
if report:
    for c in report["claims"]:
        print(f"{c['status']:13} {c['overlap']:.2f}  {c['sentence']}")
    print("grounded ratio:", report["grounded_ratio"])
