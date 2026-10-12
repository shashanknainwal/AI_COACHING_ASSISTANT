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


def exact_match(expected, got):
    """True if expected and got match after normalizing (lowercase, collapse whitespace, strip trailing . or !)."""
    # TODO
    pass


def judge(client, rubric, question, answer):
    """Ask the judge model for {"pass": bool, "reason": str} using structured outputs."""
    # TODO
    pass


def wilson_interval(k, n, z=1.96):
    """95% Wilson score interval for k passes out of n, as (low, high) rounded to 3."""
    # TODO
    pass


def run_eval(cases, generate, n_runs, client):
    """Run every case n_runs times. Returns trials, passes, pass_rate, per_case, flaky and interval."""
    # TODO
    pass


# --- Try it out (not graded) ---
report = run_eval(CASES, system_under_test, 3, client)
if report:
    print(f"pass rate {report['pass_rate']} over {report['trials']} trials, 95% CI {report['interval']}")
    print("per case:", report["per_case"])
    print("flaky:", report["flaky"])
