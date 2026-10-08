import math
import re
from collections import Counter

STOPWORDS = {"a", "an", "and", "are", "as", "at", "be", "by", "can", "do", "for", "from", "how", "i", "if", "in",
             "is", "it", "its", "my", "of", "on", "or", "so", "that", "the", "then", "to", "what", "when", "why",
             "with"}


def chunk_text(text, size, overlap):
    if size < 1 or overlap < 0 or overlap >= size:
        raise ValueError("need size >= 1 and 0 <= overlap < size")
    words = text.split()
    step = size - overlap
    chunks = []
    start = 0
    while start < len(words):
        chunks.append({"start": start, "text": " ".join(words[start:start + size])})
        if start + size >= len(words):
            break
        start += step
    return chunks


def chunk_corpus(docs, size, overlap):
    chunks = []
    for doc in docs:
        for n, piece in enumerate(chunk_text(doc["text"], size, overlap), 1):
            chunks.append({"id": f"{doc['id']}#{n}", "doc_id": doc["id"], "title": doc["title"],
                           "start": piece["start"], "text": piece["text"]})
    return chunks


def tokenize(text):
    return [w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOPWORDS]


class BM25:
    def __init__(self, chunks, k1=1.2, b=0.75):
        self.chunks = chunks
        self.k1 = k1
        self.b = b
        self.tfs = [Counter(tokenize(c["title"] + " " + c["text"])) for c in chunks]
        self.lengths = [sum(tf.values()) for tf in self.tfs]
        n = len(chunks)
        self.avgdl = sum(self.lengths) / n if n else 0.0
        df = Counter()
        for tf in self.tfs:
            df.update(tf.keys())
        self.idf = {t: math.log(1 + (n - d + 0.5) / (d + 0.5)) for t, d in df.items()}

    def score(self, query, i):
        tf = self.tfs[i]
        norm = self.k1 * (1 - self.b + self.b * self.lengths[i] / self.avgdl)
        total = 0.0
        for term in sorted(set(tokenize(query))):
            f = tf.get(term, 0)
            if f:
                total += self.idf[term] * f * (self.k1 + 1) / (f + norm)
        return total

    def search(self, query, k=5):
        scored = [(c["id"], round(self.score(query, i), 4)) for i, c in enumerate(self.chunks)]
        hits = [h for h in scored if h[1] > 0]
        hits.sort(key=lambda h: -h[1])
        return hits[:k]


CHUNKS = chunk_corpus(RUNBOOKS, size=40, overlap=10)
INDEX = BM25(CHUNKS)

# --- Try it out (not graded) ---
print(len(CHUNKS) if CHUNKS else 0, "chunks")
for q in ["E4012 after rotation", "undo a bad deploy", "replica lag after failover", "kubernetes"]:
    hits = INDEX.search(q, k=3) if INDEX and CHUNKS else None
    print(f"{q!r:40} -> {hits}")
