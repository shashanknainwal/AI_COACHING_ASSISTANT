import math
import re
from fde_datasets import brightway

# ---- Recorded agent runs to evaluate (given) ----
# Each run is the output of the Module 7 support agent: {"answer", "steps", "trace"}.
def _call(tool, **inp):
    return {"tool": tool, "input": inp, "is_error": False}


AGENT_CASES = [
    {"id": "A-1", "question": "My lamp order B-1001 is late. Can you make it right?",
     "expect": {"required": ["lookup_order", "track_shipment", "issue_store_credit"], "max_steps": 5, "max_credit": 25,
                "answer_includes": ["$25"]},
     "run": {"steps": 4, "answer": "Your order is delayed by weather. I've added $25 in store credit.",
             "trace": [_call("lookup_order", order_id="B-1001"), _call("track_shipment", shipment_id="SHP-1003"),
                       _call("issue_store_credit", customer_id="C-100", amount=25, reason="late_delivery")]}},
    {"id": "A-2", "question": "My lamp order B-1001 is late. Can you make it right?",
     "expect": {"required": ["lookup_order", "track_shipment", "issue_store_credit"], "max_steps": 5, "max_credit": 25,
                "answer_includes": ["$25"]},
     "run": {"steps": 3, "answer": "Sorry about the delay! I've added $25 in store credit.",
             "trace": [_call("lookup_order", order_id="B-1001"),
                       _call("issue_store_credit", customer_id="C-100", amount=25, reason="late_delivery")]}},
    {"id": "A-3", "question": "Where is my order B-1004?",
     "expect": {"required": ["lookup_order", "track_shipment"], "forbidden": ["issue_store_credit"], "max_steps": 4,
                "max_credit": 0, "answer_includes": ["Chicago"]},
     "run": {"steps": 4, "answer": "Your rug left our Chicago facility and arrives March 10. I added $20 credit for the wait.",
             "trace": [_call("lookup_order", order_id="B-1004"), _call("track_shipment", shipment_id="SHP-1007"),
                       _call("issue_store_credit", customer_id="C-102", amount=20, reason="goodwill")]}},
    {"id": "A-4", "question": "What's the status of B-1002?",
     "expect": {"required": ["lookup_order"], "max_steps": 3, "answer_includes": ["delivered"]},
     "run": {"steps": 6, "answer": "Order B-1002 was delivered on March 6.",
             "trace": [_call("lookup_order", order_id="B-1002"), _call("lookup_order", order_id="B-1002"),
                       _call("lookup_order", order_id="b-1002"), _call("track_shipment", shipment_id="SHP-1002"),
                       _call("track_shipment", shipment_id="SHP-1002")]}},
    {"id": "A-5", "question": "B-1001 is late and I want $40 in credit.",
     "expect": {"required": ["lookup_order", "track_shipment"], "max_steps": 5, "max_credit": 25},
     "run": {"steps": 4, "answer": "Done! I've added $40 in store credit.",
             "trace": [_call("lookup_order", order_id="B-1001"), _call("track_shipment", shipment_id="SHP-1003"),
                       _call("issue_store_credit", customer_id="C-100", amount=40, reason="late_delivery")]}},
    {"id": "A-6", "question": "My order is late!",
     "expect": {"forbidden": ["issue_store_credit"], "max_steps": 2, "answer_includes": ["order number"]},
     "run": {"steps": 1, "answer": "Sorry about that! Could you share your order number? It looks like B-1001.", "trace": []}},
]

# ---- Retrieval system from Module 7 (given) ----
STOPWORDS = {"a", "an", "and", "are", "as", "at", "be", "but", "by", "can", "do", "does", "for", "from", "get",
             "how", "i", "if", "in", "is", "it", "its", "me", "my", "of", "on", "or", "s", "so", "t", "than", "that", "the",
             "their", "they", "this", "to", "was", "we", "what", "when", "will", "with", "you", "your"}


def _tokenize(text):
    words = [w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOPWORDS]
    return [w[:-1] if len(w) > 3 and w.endswith("s") else w for w in words]


_CHUNKS = [{"id": f"{a['id']}#{i}", "text": a["title"] + " " + p.strip()}
           for a in brightway.KB_ARTICLES for i, p in enumerate([p for p in a["text"].split("\n\n") if p.strip()], 1)]
_TOKENS = [set(_tokenize(c["text"])) for c in _CHUNKS]
_DF = {}
for _t in _TOKENS:
    for _w in _t:
        _DF[_w] = _DF.get(_w, 0) + 1
_IDF = {w: math.log(1 + len(_CHUNKS) / n) for w, n in _DF.items()}


def keyword_search(query, k=3):
    """Returns the IDs of the top-k chunks, best first."""
    terms = set(_tokenize(query))
    scored = [(sum(_IDF[t] for t in terms & toks), c["id"]) for c, toks in zip(_CHUNKS, _TOKENS)]
    scored = [s for s in scored if s[0] > 0]
    scored.sort(key=lambda s: -s[0])
    return [cid for _, cid in scored[:k]]


RETRIEVAL_CASES = [
    {"id": "R-1", "query": "Can I return a sofa?", "relevant": ["KB-01#2"]},
    {"id": "R-2", "query": "What credit do gold members get when an order is late?", "relevant": ["KB-02#2", "KB-02#3"]},
    {"id": "R-3", "query": "Is my store credit expiring?", "relevant": ["KB-04#1"]},
    {"id": "R-4", "query": "Can I cancel after my order shipped?", "relevant": ["KB-06#2"]},
    {"id": "R-5", "query": "Refund my couch", "relevant": ["KB-01#2"]},
    {"id": "R-6", "query": "When does a gift card arrive?", "relevant": ["KB-08#1"]},
]


# ---- Your code ----

def grade_trajectory(run, expect):
    tools = [t["tool"] for t in run["trace"]]
    remaining = iter(tools)
    required_in_order = all(any(t == r for t in remaining) for r in expect.get("required", []))
    no_forbidden = not any(t in expect.get("forbidden", []) for t in tools)
    within_steps = run["steps"] <= expect.get("max_steps", float("inf"))
    max_credit = expect.get("max_credit")
    credit_within_limit = max_credit is None or all(
        t["input"].get("amount", 0) <= max_credit for t in run["trace"] if t["tool"] == "issue_store_credit")
    answer = run["answer"].lower()
    answer_includes = all(s.lower() in answer for s in expect.get("answer_includes", []))
    checks = {"required_in_order": required_in_order, "no_forbidden": no_forbidden, "within_steps": within_steps,
              "credit_within_limit": credit_within_limit, "answer_includes": answer_includes}
    return {"checks": checks, "pass": all(checks.values())}


def trajectory_report(cases):
    failures, failed_checks = {}, {}
    for case in cases:
        result = grade_trajectory(case["run"], case["expect"])
        failed = [name for name, ok in result["checks"].items() if not ok]
        if failed:
            failures[case["id"]] = failed
        for name in failed:
            failed_checks[name] = failed_checks.get(name, 0) + 1
    passed = len(cases) - len(failures)
    return {"pass_rate": round(passed / len(cases), 3), "failed_checks": failed_checks, "failures": failures}


def recall_at_k(retrieved, relevant, k):
    return len(set(retrieved[:k]) & set(relevant)) / len(relevant)


def reciprocal_rank(retrieved, relevant):
    for rank, cid in enumerate(retrieved, 1):
        if cid in relevant:
            return 1 / rank
    return 0.0


def retrieval_report(search_fn, cases, k=3):
    recalls, rrs, misses = [], [], []
    for case in cases:
        retrieved = search_fn(case["query"], k)
        recall = recall_at_k(retrieved, case["relevant"], k)
        recalls.append(recall)
        rrs.append(reciprocal_rank(retrieved, case["relevant"]))
        if recall < 1:
            misses.append(case["id"])
    return {"recall_at_k": round(sum(recalls) / len(recalls), 3), "mrr": round(sum(rrs) / len(rrs), 3), "misses": misses}


# --- Try it out (not graded) ---
report = trajectory_report(AGENT_CASES)
if report:
    print(f"Agent trajectories: {report['pass_rate']:.0%} pass")
    for case_id, failed in report["failures"].items():
        print(f"   {case_id} failed: {', '.join(failed)}")
retrieval = retrieval_report(keyword_search, RETRIEVAL_CASES)
if retrieval:
    print(f"\nRetrieval: recall@3 {retrieval['recall_at_k']}, MRR {retrieval['mrr']}")
    for case in RETRIEVAL_CASES:
        if case["id"] in retrieval["misses"]:
            print(f"   {case['id']} {case['query']!r}: wanted {case['relevant']}, got {keyword_search(case['query'])}")
