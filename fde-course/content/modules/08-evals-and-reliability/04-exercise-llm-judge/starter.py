import json
import anthropic

client = anthropic.Anthropic()
JUDGE_MODEL = "claude-opus-5-5"
JUDGE_SYSTEM = "You are a strict grader of customer-support answers. Follow the rubric exactly."
RUBRIC = """Pass only if ALL of these are true:
1. The answer is correct: every fact in the reference answer that matters to the customer is stated.
2. The answer contains no claims that contradict the reference or that the reference doesn't support.
3. The answer directly addresses the question.
Length, tone and friendliness do not matter for this grade."""

# Answers from the help-center assistant, each labeled by a Brightway support lead.
JUDGE_CASES = [
    {"id": "J-01", "question": "Can I return a sofa?", "reference": "Yes, within 14 days of delivery, with a $49 pickup fee.",
     "answer": "Yes. Sofas can be returned within 14 days of delivery, and a $49 pickup fee applies.", "human": "pass"},
    {"id": "J-02", "question": "Can I return a sofa?", "reference": "Yes, within 14 days of delivery, with a $49 pickup fee.",
     "answer": "Yes, sofas can be returned within 30 days for free.", "human": "fail"},
    {"id": "J-03", "question": "What store credit do gold members get for a late order?",
     "reference": "$25, when the order arrives more than 5 business days late.",
     "answer": "Gold members get a $25 store credit if the order arrives more than 5 business days late.", "human": "pass"},
    {"id": "J-04", "question": "What store credit do gold members get for a late order?",
     "reference": "$25, when the order arrives more than 5 business days late.",
     "answer": "You'll get $20 in store credit.", "human": "fail"},
    {"id": "J-05", "question": "How fast do gift cards arrive?", "reference": "By email, within an hour.",
     "answer": "Within an hour, by email.", "human": "pass"},
    {"id": "J-06", "question": "Does store credit expire?", "reference": "No, store credit never expires.",
     "answer": "No, it never expires.", "human": "pass"},
    {"id": "J-07", "question": "Can I cancel an order that has already shipped?",
     "reference": "No. Once an order has shipped it can't be cancelled, but it can be returned.",
     "answer": "Yes, you can cancel any time before delivery.", "human": "fail"},
    {"id": "J-08", "question": "Can I return a sofa?", "reference": "Yes, within 14 days of delivery, with a $49 pickup fee.",
     "answer": "Great question! At Brightway we want every customer to love their furniture, so we make returns easy. "
               "Sofas can be returned within 30 days of delivery, just like everything else, and our team will happily "
               "arrange a convenient pickup time that works for you.", "human": "fail"},
    {"id": "J-09", "question": "How fast do gift cards arrive?", "reference": "By email, within an hour.",
     "answer": "It arrives by mail within 5-7 days.", "human": "fail"},
    {"id": "J-10", "question": "What store credit do gold members get for a late order?",
     "reference": "$25, when the order arrives more than 5 business days late.",
     "answer": "Gold members receive twenty-five dollars in store credit when an order is more than five business days late.",
     "human": "pass"},
    {"id": "J-11", "question": "Does store credit expire?", "reference": "No, store credit never expires.",
     "answer": "Store credit expires after one year.", "human": "fail"},
    {"id": "J-12", "question": "Can I cancel an order that has already shipped?",
     "reference": "No. Once an order has shipped it can't be cancelled, but it can be returned.",
     "answer": "No, once it has shipped it can't be cancelled, but you can return it under the returns policy.", "human": "pass"},
]

# TODO: reasoning (string) first, then verdict ("pass" or "fail")
JUDGE_SCHEMA = {}


def build_judge_prompt(case):
    """Rubric, question, reference answer and candidate answer, each in its own tags, then the instruction."""
    # TODO
    pass


def judge(client, case):
    """Ask the judge model for a verdict. Returns {"verdict", "reasoning"}; verdict "error" on a refusal."""
    # TODO
    pass


def agreement(judge_verdicts, human_verdicts):
    """{"n", "accuracy", "kappa", "false_pass", "false_fail", "errors"}, skipping judge errors."""
    # TODO
    pass


def calibrate(client, cases):
    """Judge every case and compare with the human labels: {"report", "disagreements"}."""
    # TODO
    pass


# --- Try it out (not graded) ---
result = calibrate(client, JUDGE_CASES)
if result:
    print("Judge vs. support lead:", result["report"])
    for case in JUDGE_CASES:
        if case["id"] in result["disagreements"]:
            verdict = judge(client, case)
            print(f"\n{case['id']}: human={case['human']} judge={verdict['verdict']}")
            print("   answer:   ", case["answer"][:90] + ("..." if len(case["answer"]) > 90 else ""))
            print("   reasoning:", verdict["reasoning"])
