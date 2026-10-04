import json
import anthropic
from anthropic import _sim


def _fresh():
    _sim.calls.clear()
    _sim._queue.clear()


def test_schema_reasoning_first():
    """JUDGE_SCHEMA asks for reasoning before the verdict"""
    s = JUDGE_SCHEMA
    props = s.get("properties", {})
    assert list(props) == ["reasoning", "verdict"], f"put reasoning first so the verdict follows from it: {list(props)}"
    assert props["reasoning"].get("type") == "string"
    assert props["verdict"].get("type") == "string" and props["verdict"].get("enum") == ["pass", "fail"]
    assert s.get("required") == ["reasoning", "verdict"] and s.get("additionalProperties") is False and s.get("type") == "object"


def test_build_judge_prompt():
    """build_judge_prompt() lays out rubric, question, reference and candidate"""
    case = {"id": "x", "question": "Q?", "reference": "R.", "answer": "A.", "human": "pass"}
    expected = (f"<rubric>\n{RUBRIC}\n</rubric>\n\n<question>\nQ?\n</question>\n\n<reference_answer>\nR.\n</reference_answer>\n\n"
                "<candidate_answer>\nA.\n</candidate_answer>\n\n"
                "Grade the candidate answer against the rubric. Explain your reasoning first, then give the verdict.")
    got = build_judge_prompt(case)
    assert got == expected, f"got:\n{got}"


def test_judge_request_and_verdict():
    """judge() sends a structured-output request to JUDGE_MODEL and returns the verdict"""
    _fresh()
    got = judge(anthropic.Anthropic(), JUDGE_CASES[1])
    assert got == {"verdict": "fail", "reasoning": "The answer does not state: 14 days, $49."}, f"got {got}"
    p = _sim.last_request()
    assert p["model"] == JUDGE_MODEL and p["max_tokens"] >= 1024 and p.get("system") == JUDGE_SYSTEM
    assert p["messages"] == [{"role": "user", "content": build_judge_prompt(JUDGE_CASES[1])}]
    assert (p.get("output_config") or {}).get("format") == {"type": "json_schema", "schema": JUDGE_SCHEMA}


def test_judge_refusal():
    """A refusal becomes verdict "error" instead of a crash"""
    _fresh()
    _sim.queue(_sim.refusal())
    got = judge(anthropic.Anthropic(), JUDGE_CASES[0])
    assert isinstance(got, dict) and got.get("verdict") == "error", f"got {got}"


def test_agreement():
    """agreement() reports accuracy, Cohen's kappa and both error types"""
    judge_v = ["pass", "pass", "fail", "fail", "pass", "fail", "pass", "pass"]
    human_v = ["pass", "fail", "fail", "fail", "pass", "pass", "pass", "pass"]
    got = agreement(judge_v, human_v)
    # po = 6/8 = 0.75; judge pass 5/8, human pass 5/8; pe = 0.625^2 + 0.375^2 = 0.53125; kappa = 0.4667
    assert got == {"n": 8, "accuracy": 0.75, "kappa": 0.467, "false_pass": 1, "false_fail": 1, "errors": 0}, f"got {got}"


def test_agreement_edge_cases():
    """Judge errors are skipped and counted; identical constant labels give kappa 1"""
    got = agreement(["pass", "error", "fail"], ["pass", "pass", "fail"])
    assert got == {"n": 2, "accuracy": 1.0, "kappa": 1.0, "false_pass": 0, "false_fail": 0, "errors": 1}, f"got {got}"
    got = agreement(["pass", "pass"], ["pass", "pass"])
    assert got["kappa"] == 1.0 and got["accuracy"] == 1.0, "when chance agreement is 1, kappa is 1 for perfect agreement"
    got = agreement(["pass", "pass", "pass", "pass"], ["pass", "pass", "pass", "fail"])
    assert got["kappa"] == 0.0 and got["false_pass"] == 1, f"a judge that always says pass has no skill: {got}"


def test_calibrate():
    """calibrate() finds the judge's two disagreements with the support lead"""
    _fresh()
    got = calibrate(anthropic.Anthropic(), JUDGE_CASES)
    assert got == {"report": {"n": 12, "accuracy": 0.833, "kappa": 0.667, "false_pass": 1, "false_fail": 1, "errors": 0},
                   "disagreements": ["J-08", "J-10"]}, f"got {got}"
    assert len(_sim.calls) == 12, "one judge call per case"
