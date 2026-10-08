import math
import re
from collections import Counter

STOPWORDS = {"a", "an", "and", "are", "as", "at", "be", "by", "can", "do", "for", "from", "how", "i", "if", "in",
             "is", "it", "its", "my", "of", "on", "or", "so", "that", "the", "then", "to", "what", "when", "why",
             "with"}


def chunk_text(text, size, overlap):
    """Split text into word windows of `size` words that share `overlap` words.

    Returns [{"start": word_offset, "text": "..."}]. Raises ValueError unless size >= 1 and 0 <= overlap < size.
    """
    # TODO
    pass


def chunk_corpus(docs, size, overlap):
    """Chunk every doc: {"id": "RB-01#1", "doc_id", "title", "start", "text"}, numbered from 1 per doc."""
    # TODO
    pass


def tokenize(text):
    """Lowercase [a-z0-9]+ words, minus STOPWORDS."""
    # TODO
    pass


class BM25:
    def __init__(self, chunks, k1=1.2, b=0.75):
        """Index title + text of each chunk: self.tfs, self.lengths, self.avgdl, self.idf."""
        self.chunks = chunks
        self.k1 = k1
        self.b = b
        # TODO: self.tfs (Counter per chunk), self.lengths, self.avgdl, self.idf

    def score(self, query, i):
        """BM25 score of chunk i for the query (each distinct query term counted once)."""
        # TODO
        pass

    def search(self, query, k=5):
        """Up to k (chunk_id, score rounded to 4 places) with score > 0, best first, ties in chunk order."""
        # TODO
        pass


CHUNKS = chunk_corpus(RUNBOOKS, size=40, overlap=10)
INDEX = BM25(CHUNKS)

# --- Try it out (not graded) ---
print(len(CHUNKS) if CHUNKS else 0, "chunks")
for q in ["E4012 after rotation", "undo a bad deploy", "replica lag after failover", "kubernetes"]:
    hits = INDEX.search(q, k=3) if INDEX and CHUNKS else None
    print(f"{q!r:40} -> {hits}")
