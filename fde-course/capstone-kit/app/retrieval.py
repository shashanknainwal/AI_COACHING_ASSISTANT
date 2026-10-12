"""A tiny lexical retriever (BM25) over Markdown files, plus recall@k.

Standard library only. It is deliberately simple so you can see every step
and so lab 2 has a baseline to beat. Swap in embeddings or a hybrid index for
your own capstone, and keep the same `search()` shape so the eval still runs.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

STOPWORDS = frozenset(
    "a an and are as at be but by can do does for from has have how i if in is it its "
    "my no not of on or our so that the their them then there this to was we what when "
    "where which who why will with you your".split()
)


def tokenize(text: str) -> list[str]:
    """Lowercase word tokens without stopwords. Keeps ids like QF-1042 as one token."""
    words = re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)*", text.lower())
    return [w for w in words if w not in STOPWORDS]


@dataclass(frozen=True)
class Chunk:
    id: str        # "<doc_id>#<n>"
    doc_id: str    # file stem, e.g. "returns-policy"
    title: str
    text: str


def chunk_markdown(doc_id: str, text: str, max_words: int = 120) -> list[Chunk]:
    """Split on `## ` headings, then cap each piece at about max_words words.

    The document title (first `# ` line) is prefixed to every chunk so a chunk
    still makes sense on its own.
    """
    lines = text.strip().splitlines()
    title = lines[0].lstrip("# ").strip() if lines and lines[0].startswith("# ") else doc_id
    body = "\n".join(lines[1:]) if lines and lines[0].startswith("# ") else text
    sections = [s.strip() for s in re.split(r"\n(?=## )", body) if s.strip()]
    chunks: list[Chunk] = []
    for section in sections or [body]:
        words = section.split()
        for start in range(0, max(len(words), 1), max_words):
            piece = " ".join(words[start:start + max_words])
            if piece:
                chunks.append(Chunk(f"{doc_id}#{len(chunks)}", doc_id, title, f"{title}. {piece}"))
    return chunks


def load_corpus(directory: str | Path, max_words: int = 120) -> list[Chunk]:
    """Chunk every .md file in a directory, in a stable (sorted) order."""
    chunks: list[Chunk] = []
    for path in sorted(Path(directory).glob("*.md")):
        chunks.extend(chunk_markdown(path.stem, path.read_text(encoding="utf-8"), max_words))
    return chunks


class BM25Index:
    """Okapi BM25 with the usual k1=1.5, b=0.75."""

    def __init__(self, chunks: list[Chunk], k1: float = 1.5, b: float = 0.75):
        self.chunks = chunks
        self.k1, self.b = k1, b
        self.tfs = [Counter(tokenize(c.text)) for c in chunks]
        self.lengths = [sum(tf.values()) for tf in self.tfs]
        self.avg_len = (sum(self.lengths) / len(self.lengths)) if chunks else 0.0
        df: Counter = Counter()
        for tf in self.tfs:
            df.update(tf.keys())
        n = len(chunks)
        self.idf = {t: math.log(1 + (n - d + 0.5) / (d + 0.5)) for t, d in df.items()}

    def search(self, query: str, k: int = 5) -> list[tuple[Chunk, float]]:
        terms = tokenize(query)
        scored = []
        for i, tf in enumerate(self.tfs):
            score = 0.0
            for t in terms:
                f = tf.get(t, 0)
                if not f:
                    continue
                norm = f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * self.lengths[i] / (self.avg_len or 1)))
                score += self.idf.get(t, 0.0) * norm
            if score > 0:
                scored.append((i, score))
        scored.sort(key=lambda pair: (-pair[1], pair[0]))  # ties broken by corpus order: deterministic
        return [(self.chunks[i], s) for i, s in scored[:k]]


def unique_docs(chunk_ids_or_doc_ids: list[str]) -> list[str]:
    """Map chunk ids to doc ids, keeping first-seen order and dropping repeats."""
    seen: list[str] = []
    for cid in chunk_ids_or_doc_ids:
        doc = cid.split("#", 1)[0]
        if doc not in seen:
            seen.append(doc)
    return seen


def recall_at_k(retrieved: list[str], relevant: list[str] | set[str], k: int) -> float:
    """Share of the relevant items that appear in the top k retrieved.

    Both lists use the same kind of id (doc ids in lab 2). An empty relevant
    set returns 1.0 only if nothing was expected; callers should avoid that case.
    """
    relevant = set(relevant)
    if not relevant:
        return 1.0
    return len(set(retrieved[:k]) & relevant) / len(relevant)


def reciprocal_rank(retrieved: list[str], relevant: list[str] | set[str]) -> float:
    """1/rank of the first relevant item, 0.0 if none was retrieved."""
    relevant = set(relevant)
    for rank, item in enumerate(retrieved, start=1):
        if item in relevant:
            return 1.0 / rank
    return 0.0
