def test_learn_merges_toy_example():
    """learn_merges() reproduces the classic aaabdaaabac example"""
    got = learn_merges("aaabdaaabac", 10)
    expected = [((97, 97), 256), ((256, 97), 257), ((257, 98), 258)]
    assert got == expected, f"expected {expected} (then stop: no pair appears twice), got {got!r}"


def test_learn_merges_respects_limit_and_ties():
    """learn_merges() stops at num_merges, needs a pair seen twice, and breaks ties by first appearance"""
    assert learn_merges("aaabdaaabac", 1) == [((97, 97), 256)], "with num_merges=1 return only the first merge"
    assert learn_merges("abcd", 5) == [], "no pair appears twice, so there are no merges"
    got = learn_merges("cdab cdab abcd", 1)
    assert got == [((99, 100), 256)], f"'cd' and 'ab' both appear 3 times; 'cd' appears first, so it wins. Got {got!r}"


def test_encode_replays_merges():
    """encode() applies the merges in the order they were learned"""
    merges = [((97, 97), 256), ((256, 97), 257), ((257, 98), 258)]
    got = encode("aaabdaaabac", merges)
    assert got == [258, 100, 258, 97, 99], f"expected [258, 100, 258, 97, 99], got {got!r}"
    assert encode("dc", merges) == [100, 99], "text with no matching merges stays as raw bytes"
    got = encode("aaaa", merges)
    assert got == [256, 256], f"merge 1 turns 'aaaa' into [256, 256], scanning left to right without overlaps; got {got!r}"
    assert encode("", merges) == [], "empty text encodes to an empty list"


def test_round_trip_all_scripts():
    """decode(encode(text)) gives back the original text, including Hindi and code"""
    merges = learn_merges(TRAINING_TEXT, 150)
    for name, text in SAMPLES.items():
        ids = encode(text, merges)
        back = decode(ids, merges)
        assert back == text, f"round trip failed for {name}: got {back!r}"
    assert decode([], merges) == "", "decode([]) should be an empty string"


def test_merges_compress_training_text():
    """Merges make English text much shorter than raw bytes"""
    first = learn_merges(TRAINING_TEXT, 100)
    assert len(first) == 100, f"the training text has plenty of repeated pairs; expected 100 merges, got {len(first)}"
    assert [m[1] for m in first] == list(range(256, 356)), "new ids must run 256, 257, ... in order"
    merges = learn_merges(TRAINING_TEXT, 150)
    assert merges[:100] == first, "asking for more merges must not change the first ones"
    raw = len(TRAINING_TEXT.encode("utf-8"))
    assert len(encode(TRAINING_TEXT, merges)) < raw / 2.5, "the training text should shrink to well under half its byte length"


def test_compare_shows_the_language_skew():
    """compare() reports chars, tokens and tokens_per_char, and Hindi costs far more per character"""
    merges = learn_merges(TRAINING_TEXT, 150)
    report = compare(SAMPLES, merges)
    assert isinstance(report, dict) and set(report) == set(SAMPLES), f"one row per sample, got {report!r}"
    row = report["english"]
    assert set(row) == {"chars", "tokens", "tokens_per_char"}, f"row keys: {sorted(row)}"
    assert row["chars"] == len(SAMPLES["english"]), "chars is len(text)"
    assert row["tokens"] == len(encode(SAMPLES["english"], merges)), "tokens is len(encode(text, merges))"
    assert row["tokens_per_char"] == round(row["tokens"] / row["chars"], 2), "tokens_per_char is rounded to 2 decimals"
    assert report["hindi"]["tokens_per_char"] > 4 * report["english"]["tokens_per_char"], \
        f"a tokenizer trained only on English should spend far more tokens per Hindi character: {report}"
