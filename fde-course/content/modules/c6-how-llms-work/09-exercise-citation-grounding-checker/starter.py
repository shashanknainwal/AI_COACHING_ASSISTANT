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


def split_sentences(text):
    """Split text into sentences after . ! or ? followed by whitespace. Drop empty pieces."""
    # TODO
    pass


def check_claim(sentence, spans, threshold=0.6):
    """Return {"sentence", "citations", "status", "overlap"} for one sentence."""
    # TODO
    pass


def grounding_report(answer, spans, threshold=0.6):
    """Check every sentence. Return {"claims", "supported", "total", "grounded_ratio", "flagged"}."""
    # TODO
    pass


# --- Try it out (not graded) ---
report = grounding_report(ANSWER, SPANS)
if report:
    for c in report["claims"]:
        print(f"{c['status']:13} {c['overlap']:.2f}  {c['sentence']}")
    print("grounded ratio:", report["grounded_ratio"])
