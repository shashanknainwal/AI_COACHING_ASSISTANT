import math

TEN = "w0 w1 w2 w3 w4 w5 w6 w7 w8 w9"


def _starts(chunks):
    return [c["start"] for c in chunks]


def test_chunk_text_windows():
    """chunk_text() makes overlapping word windows with the right starts"""
    got = chunk_text(TEN, 4, 1)
    assert got == [{"start": 0, "text": "w0 w1 w2 w3"}, {"start": 3, "text": "w3 w4 w5 w6"},
                   {"start": 6, "text": "w6 w7 w8 w9"}], f"size 4, overlap 1 on 10 words: got {got}"
    got = chunk_text(TEN + " w10", 4, 1)
    assert _starts(got or []) == [0, 3, 6, 9] and got[-1]["text"] == "w9 w10", \
        f"the last window can be shorter than size: got {got}"
    assert _starts(chunk_text(TEN, 5, 0) or []) == [0, 5], "overlap 0 means back-to-back windows"


def test_chunk_text_edges():
    """chunk_text() stops at the end, handles short and empty text, and rejects bad settings"""
    got = chunk_text(TEN, 10, 3)
    assert got == [{"start": 0, "text": TEN}], \
        f"a window that already reaches the last word is the final one; no duplicate tail chunk: {got}"
    assert chunk_text("just three words", 40, 10) == [{"start": 0, "text": "just three words"}]
    assert chunk_text("   \n  ", 40, 10) == [], "no words means no chunks"
    assert chunk_text("a  b\n\nc", 2, 0) == [{"start": 0, "text": "a b"}, {"start": 2, "text": "c"}], \
        "split on any whitespace and rejoin with single spaces"
    for size, overlap in [(4, 4), (4, 5), (0, 0), (4, -1)]:
        try:
            chunk_text(TEN, size, overlap)
        except ValueError:
            continue
        raise AssertionError(f"chunk_text(text, {size}, {overlap}) should raise ValueError")


def test_chunk_corpus():
    """chunk_corpus() gives every chunk a stable id and keeps its source"""
    chunks = chunk_corpus(RUNBOOKS, 40, 10)
    assert isinstance(chunks, list) and len(chunks) == 10, f"expected 10 chunks, got {None if chunks is None else len(chunks)}"
    assert [c["id"] for c in chunks][:4] == ["RB-01#1", "RB-01#2", "RB-02#1", "RB-02#2"]
    assert set(chunks[1]) == {"id", "doc_id", "title", "start", "text"}, f"keys: {set(chunks[1])}"
    assert chunks[1]["doc_id"] == "RB-01" and chunks[1]["title"] == "Rolling back a deploy" and chunks[1]["start"] == 30
    rb05 = [c["id"] for c in chunks if c["doc_id"] == "RB-05"]
    assert rb05 == ["RB-05#1"], f"RB-05 is exactly 40 words, so it is one chunk: {rb05}"


def test_tokenize():
    """tokenize() lowercases, keeps letters and digits, drops stopwords"""
    assert tokenize("Error E4012: token-expired, IS the host's clock OK?") == \
        ["error", "e4012", "token", "expired", "host", "s", "clock", "ok"], tokenize("Error E4012: token-expired, IS the host's clock OK?")
    assert tokenize("What is it?") == []


def test_bm25_statistics():
    """BM25 indexes title + text and uses the smoothed IDF"""
    index = BM25(chunk_corpus(RUNBOOKS, 40, 10))
    assert index.lengths == [32, 23, 34, 22, 35, 20, 28, 19, 31, 12], \
        f"lengths are token counts of title + text: {index.lengths}"
    assert abs(index.avgdl - 25.6) < 1e-9, f"avgdl: {index.avgdl}"
    n, df = 10, 2
    assert abs(index.idf["e4012"] - math.log(1 + (n - df + 0.5) / (df + 0.5))) < 1e-9, \
        "idf = log(1 + (N - df + 0.5) / (df + 0.5))"
    assert index.idf["token"] < index.idf["e4012"], "a term in more chunks gets a lower idf"


def test_bm25_saturation_and_length():
    """Term frequency saturates, and long chunks are normalised by b"""
    toy = [{"id": "one", "title": "", "text": "cache"},
           {"id": "ten", "title": "", "text": " ".join(["cache"] * 10)},
           {"id": "other", "title": "", "text": "queue"}]
    index = BM25(toy)
    one, ten = index.score("cache", 0), index.score("cache", 1)
    assert one > 0 and ten < 2 * one, f"ten mentions should score far less than 10x one mention: {one:.3f} vs {ten:.3f}"
    assert index.score("queue", 0) == 0, "a chunk without the query term scores 0"
    assert index.score("cache cache", 0) == one, "count each distinct query term once"
    chunks = chunk_corpus(RUNBOOKS, 40, 10)
    assert BM25(chunks, b=0).search("rollback", k=3) == [("RB-01#1", 1.5746), ("RB-01#2", 1.1451), ("RB-06#1", 1.1451)], \
        "with b=0 (no length normalisation), ties keep chunk order"
    assert BM25(chunks).search("rollback", k=3) == [("RB-01#1", 1.4711), ("RB-06#1", 1.4631), ("RB-01#2", 1.1948)], \
        "with b=0.75 the short handoff chunk moves up"


def test_search_ranking():
    """search() returns (id, score) pairs, best first, only positive scores, at most k"""
    got = INDEX.search("E4012 after rotation", k=3)
    assert got == [("RB-02#2", 4.6415), ("RB-02#1", 4.2696), ("RB-01#2", 0.9326)], f"got {got}"
    assert INDEX.search("replica lag after failover", k=2) == [("RB-04#1", 7.9162), ("RB-04#2", 2.1965)]
    assert INDEX.search("restart worker") == [("RB-02#1", 3.1982), ("RB-03#2", 1.888), ("RB-03#1", 1.8221)]
    assert INDEX.search("kubernetes") == [], "no matching terms means no results"
    assert len(INDEX.search("incident rollback token worker", k=4)) == 4
