import json
import re
from anthropic import _sim


def _judge(params):
    """A scripted judge: passes the answer if it mentions the word the rubric requires."""
    text = params["messages"][-1]["content"]
    rubric = re.search(r"Rubric:\n(.*?)\n\n", text, re.S)
    answer = re.search(r"Answer:\n(.*?)\n\nGrade the answer", text, re.S)
    if not rubric or not answer:
        return json.dumps({"pass": False, "reason": "I couldn't find the rubric and the answer in the expected format."})
    need = re.search(r"Must mention ([\w-]+)", rubric.group(1))
    ok = bool(need) and need.group(1).lower() in answer.group(1).lower()
    reason = f"The answer {'mentions' if ok else 'does not mention'} {need.group(1) if need else 'the required point'}."
    return json.dumps({"pass": ok, "reason": reason})


_sim.set_responder(_judge)
