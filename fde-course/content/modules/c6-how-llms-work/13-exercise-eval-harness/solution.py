import json
import math
import anthropic

client = anthropic.Anthropic()
JUDGE_MODEL = "claude-haiku-5-5"
JUDGE_MAX_TOKENS = 2000
JUDGE_SCHEMA = {
    "type": "object",
    "properties": {"pass": {"type": "boolean"}, "reason": {"type": "string"}},
    "required": ["pass", "reason"],
    "additionalProperties": False,
}

CASES = [
    {"id": "intent-1", "input": "Where is my order 4417?", "grader": "exact", "expected": "order_status"},
    {"id": "intent-2", "input": "I want my money back for the boots.", "grader": "exact", "expected": "refund"},
    {"id": "intent-3", "input": "Do you ship to Canada?", "grader": "exact", "expected": "shipping"},
    {"id": "reply-1", "input": "The jacket I got is torn. What can I do?", "grader": "judge",
     "rubric": "Must mention replacement. Polite, under 80 words."},
    {"id": "reply-2", "input": "Can I return a final-sale item?", "grader": "judge",
     "rubric": "Must mention final-sale. Says clearly that it cannot be returned."},
]


def system_under_test(text, run):
    """A stand-in for the system being evaluated. Like a real model, it is a little inconsistent."""
    if text.startswith("Where is"):
        return "Order_Status "
    if "money back" in text:
        return "refund" if run != 1 else "complaint"
    if "Canada" in text:
        return "shipping."
    if "torn" in text:
        return "Sorry about that! We can send a replacement right away."
    return "Most items can be returned within 30 days." if run == 0 else "Final-sale items cannot be returned, sorry."


def _normalize(text):
    return " ".join(str(text).lower().split()).rstrip(".!")


def exact_match(expected, got):
    """True if expected and got match after normalizing (lowercase, collapse whitespace, strip trailing . or !)."""
    if got is None:
        return False
    return _normalize(expected) == _normalize(got)


def judge(client, rubric, question, answer):
    """Ask the judge model for {"pass": bool, "reason": str} using structured outputs."""
    prompt = f"Rubric:\n{rubric}\n\nQuestion:\n{question}\n\nAnswer:\n{answer}\n\nGrade the answer against the rubric."
    response = client.messages.create(
        model=JUDGE_MODEL,
        max_tokens=JUDGE_MAX_TOKENS,
        output_config={"effort": "low", "format": {"type": "json_schema", "schema": JUDGE_SCHEMA}},
        messages=[{"role": "user", "content": prompt}],
    )
    if response.stop_reason != "end_turn":
        return {"pass": False, "reason": "judge_error"}
    text = "".join(b.text for b in response.content if b.type == "text")
    try:
        verdict = json.loads(text)
        return {"pass": bool(verdict["pass"]), "reason": str(verdict["reason"])}
    except (ValueError, KeyError, TypeError):
        return {"pass": False, "reason": "judge_error"}


def wilson_interval(k, n, z=1.96):
    """95% Wilson score interval for k passes out of n, as (low, high) rounded to 3."""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (round(max(0.0, centre - half), 3), round(min(1.0, centre + half), 3))


def run_eval(cases, generate, n_runs, client):
    """Run every case n_runs times. Returns trials, passes, pass_rate, per_case, flaky and interval."""
    per_case = {}
    for case in cases:
        passes = 0
        for run in range(n_runs):
            got = generate(case["input"], run)
            if case["grader"] == "exact":
                ok = exact_match(case["expected"], got)
            else:
                ok = judge(client, case["rubric"], case["input"], got)["pass"]
            passes += 1 if ok else 0
        per_case[case["id"]] = passes
    trials = len(cases) * n_runs
    total = sum(per_case.values())
    return {
        "trials": trials,
        "passes": total,
        "pass_rate": round(total / trials, 3) if trials else 0.0,
        "per_case": per_case,
        "flaky": [c["id"] for c in cases if 0 < per_case[c["id"]] < n_runs],
        "interval": wilson_interval(total, trials),
    }


# --- Try it out (not graded) ---
report = run_eval(CASES, system_under_test, 3, client)
if report:
    print(f"pass rate {report['pass_rate']} over {report['trials']} trials, 95% CI {report['interval']}")
    print("per case:", report["per_case"])
    print("flaky:", report["flaky"])
