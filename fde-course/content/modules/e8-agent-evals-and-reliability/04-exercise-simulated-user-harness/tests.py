from anthropic import _sim

_P = {"opening": "Hi, I need to submit a meter reading.", "patience": 4,
      "facts": {"account": "GN-204117", "postcode": "BS1 4DJ", "reading": "4821"}}


def _fresh():
    _sim.calls.clear()
    _sim._queue.clear()
    reset_db()


def test_simulator_reveals_only_what_is_asked():
    """UserSimulator answers only the facts the agent asked for"""
    sim = UserSimulator(_P)
    assert sim.opening() == _P["opening"] and sim.turns == 1, "the opening is the first user turn"
    got = sim.respond("Can I take your account number, please?")
    assert got == "It's GN-204117.", f"reveal only the account number, nothing else: got {got!r}"
    got = sim.respond("Thanks. What's your postcode, and the reading on your meter?")
    assert got == "It's BS1 4DJ, 4821.", f"two facts asked: both, in FACT_KEYWORDS order: got {got!r}"
    assert sim.turns == 3


def test_simulator_unknowns_statements_and_endings():
    """UserSimulator handles unknown questions, statements, Done: and patience"""
    sim = UserSimulator(_P)
    sim.opening()
    assert sim.respond("What's your date of birth?") == "Sorry, I don't know that."
    assert sim.respond("Which supplier were you with before?") == "Sorry, I don't know that.", \
        "a question with no known keyword is unknown too"
    assert sim.unknown_questions == 2
    assert sim.respond("I've passed this to a colleague.") == "Is that sorted, then?"
    assert sim.turns == 4
    assert sim.respond("Anything else?") is None and sim.ended == "gave_up", "patience 4 is used up"
    sim2 = UserSimulator(_P)
    sim2.opening()
    assert sim2.respond("Done: I've recorded reading 4821.") is None and sim2.ended == "satisfied", \
        "'Done:' ends the conversation even though the text mentions a reading"


def test_episode_drives_the_agent():
    """run_episode() alternates turns and keeps the history append-only"""
    _fresh()
    ep = run_episode(client, SCENARIOS[0]["persona"])
    assert ep and ep["ended"] == "satisfied" and ep["agent_turns"] == 4, f"got {ep and {k: ep[k] for k in ('ended', 'agent_turns')}}"
    reqs = _sim.requests()
    assert len(reqs) == 4, f"one API call per agent turn, got {len(reqs)}"
    for r in reqs:
        assert r["model"] == AGENT_MODEL and r["system"] == AGENT_SYSTEM and r["max_tokens"] == MAX_TOKENS, \
            "send model, max_tokens and the system prompt on every call"
    for prev, cur in zip(reqs, reqs[1:]):
        assert cur["messages"][:len(prev["messages"])] == prev["messages"], "history must be append-only"
        assert len(cur["messages"]) == len(prev["messages"]) + 2, "each round adds one assistant and one user message"
    second = reqs[1]["messages"][1]["content"]
    assert isinstance(second, list) and second[0]["type"] == "thinking", \
        "append response.content unchanged, thinking block included"
    roles = [m["role"] for m in reqs[-1]["messages"]]
    assert roles == ["user", "assistant"] * 3 + ["user"], f"roles alternate: {roles}"
    assert ep["transcript"][0] == ("user", SCENARIOS[0]["persona"]["opening"])
    assert ep["transcript"][-1] == ("assistant", "Done: I've recorded reading 4821 on GN-204117.")


def test_episode_errors_and_turn_cap():
    """API errors end the episode as 'error'; the cap ends it as 'max_turns'"""
    _fresh()
    ep = run_episode(client, SCENARIOS[5]["persona"])
    assert ep and ep["ended"] == "error" and ep["agent_turns"] == 0, f"catch anthropic.APIError: got {ep}"
    _fresh()
    ep = run_episode(client, dict(SCENARIOS[4]["persona"], patience=50), max_agent_turns=3)
    assert ep["ended"] == "max_turns" and ep["agent_turns"] == 3, f"got {ep['ended']}, {ep['agent_turns']}"


def test_suite_scores_end_state_not_claims():
    """run_suite() checks the sandbox, so a false 'Done:' is a failure"""
    _fresh()
    rows = run_suite(client, SCENARIOS)
    assert rows and [r["id"] for r in rows] == [s["id"] for s in SCENARIOS]
    got = {r["id"]: (r["ended"], r["agent_turns"], r["success"], r["claimed_but_failed"]) for r in rows}
    assert got == {
        "S1-meter": ("satisfied", 4, True, False),
        "S2-meter-all-in-one": ("satisfied", 1, True, False),
        "S3-tariff-no-space": ("satisfied", 3, False, True),
        "S4-tariff-lowercase": ("satisfied", 3, True, False),
        "S5-moving-house": ("gave_up", 5, False, False),
        "S6-outage": ("error", 0, None, False),
        "S7-impatient": ("gave_up", 2, False, False),
    }, f"got {got}"


def test_summarize():
    """summarize() reports success, turns and the episodes to read"""
    _fresh()
    s = summarize(run_suite(client, SCENARIOS))
    assert s == {"episodes": 7, "errors": 1, "success_rate": 0.5, "mean_turns_success": 2.67,
                 "claimed_but_failed": ["S3-tariff-no-space"], "gave_up": ["S5-moving-house", "S7-impatient"],
                 "check_simulator": ["S5-moving-house"]}, f"got {s}"
