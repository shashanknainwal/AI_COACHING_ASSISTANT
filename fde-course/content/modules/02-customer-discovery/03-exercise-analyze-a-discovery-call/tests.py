SMALL = """FDE: How does it work today?
Ana: We type everything by hand.
It takes about 3 hours a day.

FDE: Do you like it? Why not?
Ana: No. Nobody does!
"""


def test_parse_basic():
    """parse_transcript() splits lines into (speaker, text) turns"""
    turns = parse_transcript("FDE: Hello there\nAna: Hi")
    assert turns == [("FDE", "Hello there"), ("Ana", "Hi")], f"got {turns!r}"


def test_parse_continuation_and_blank_lines():
    """Wrapped lines join the previous turn; blank lines are skipped"""
    turns = parse_transcript(SMALL)
    assert len(turns) == 4, f"expected 4 turns, got {len(turns)}: {turns!r}"
    assert turns[1] == ("Ana", "We type everything by hand. It takes about 3 hours a day."), \
        f"the wrapped line should be appended with one space; got {turns[1]!r}"


def test_parse_keeps_colons_in_text():
    """Only the first ': ' separates speaker from text"""
    turns = parse_transcript("Joan (VP): Ratio: 3 to 1")
    assert turns == [("Joan (VP)", "Ratio: 3 to 1")], f"got {turns!r}"


def test_parse_sample():
    """The Lumen Insurance transcript parses into 12 turns"""
    turns = parse_transcript(TRANSCRIPT)
    assert len(turns) == 12, f"expected 12 turns, got {len(turns)}"
    assert turns[1][0] == "Marcus (Claims Ops)", f"speaker should be 'Marcus (Claims Ops)', got {turns[1][0]!r}"
    assert turns[1][1].endswith("keys it into ClaimsPro by hand."), "the wrapped line wasn't joined to Marcus's first turn"


def test_talk_ratio():
    """talk_ratio() is the speaker's share of words, rounded to 2 decimals"""
    turns = [("FDE", "one two"), ("Ana", "one two three four five six")]
    got = talk_ratio(turns)
    assert got == 0.25, f"FDE said 2 of 8 words, expected 0.25, got {got!r}"
    got = talk_ratio(turns, speaker="Ana")
    assert got == 0.75, f"with speaker='Ana' expected 0.75, got {got!r}"


def test_talk_ratio_sample_and_empty():
    """talk_ratio() works on the sample and returns 0.0 with no words"""
    got = talk_ratio(parse_transcript(TRANSCRIPT))
    assert got == 0.34, f"expected 0.34 for the sample, got {got!r}"
    assert talk_ratio([]) == 0.0, "an empty transcript should give 0.0"


def test_question_counts_small():
    """question_counts() finds every question and classifies open vs closed"""
    got = question_counts(parse_transcript(SMALL))
    assert got == {"open": 2, "closed": 1}, f"'How does…?' and 'Why not?' are open, 'Do you like it?' is closed; got {got!r}"


def test_question_counts_phrases_anywhere():
    """'walk me through' / 'tell me about' anywhere make a question open"""
    got = question_counts([("FDE", "Could you walk me through it? Can you tell me about Tuesday? Is it slow?")])
    assert got == {"open": 2, "closed": 1}, f"got {got!r}"


def test_question_counts_only_speaker():
    """Only the chosen speaker's questions are counted"""
    got = question_counts(parse_transcript(TRANSCRIPT))
    assert got == {"open": 3, "closed": 2}, f"expected {{'open': 3, 'closed': 2}} for the FDE, got {got!r}"


def test_quantified_pains():
    """quantified_pains() returns customer sentences containing digits"""
    got = quantified_pains(parse_transcript(SMALL))
    assert got == ["It takes about 3 hours a day."], f"got {got!r}"
    got = quantified_pains(parse_transcript(TRANSCRIPT))
    assert len(got) == 6, f"expected 6 quantified sentences in the sample, got {len(got)}: {got!r}"
    assert got[2] == "About 18% of claims get sent back because a field was keyed wrong.", f"third pain: got {got[2]!r}"
