import json
from anthropic import _sim

# Stand-in for Claude on Halden Robotics' warranty inbox. Replies are keyed by email subject.
# Like Claude Opus 5.5, each reply starts with an (empty) thinking block before the JSON text.
_FIRST = {
    "Arm is dead": {"serial_number": "HX-204611", "sku": "HR-ARM-2", "failure_mode": "no_power",
                    "safety_issue": False, "requested_action": "replace", "evidence": "won't power on since Monday"},
    "Camera pictures are grainy": {"serial_number": None, "sku": "HR-CAM-1", "failure_mode": "sensor_fault",
                                   "safety_issue": False, "requested_action": "repair", "evidence": "gives very noisy images"},
    "URGENT gripper": {"serial_number": "HX-310077", "sku": "HR-GRP-3", "failure_mode": "overheating",
                       "safety_issue": True, "requested_action": "refund", "evidence": "smell like burning plastic"},
    # The serial is well-formed but invented: it isn't in the email.
    "Damaged on arrival": {"serial_number": "HX-104000", "sku": "HR-ARM-2", "failure_mode": "physical_damage",
                           "safety_issue": False, "requested_action": "replace", "evidence": "arrived with a cracked base plate"},
    # The evidence is a paraphrase, not a quote, and stays that way after the correction.
    "not great": {"serial_number": None, "sku": "unknown", "failure_mode": "other",
                  "safety_issue": False, "requested_action": "unclear", "evidence": "the whole thing is a letdown"},
}
_CORRECTED = {
    "Damaged on arrival": dict(_FIRST["Damaged on arrival"], serial_number=None),
}


def _subject(params):
    first = params["messages"][0]["content"]
    text = first if isinstance(first, str) else ""
    return text.split("<subject>", 1)[-1].split("</subject>", 1)[0]


def _responder(params):
    subject = _subject(params)
    reply = _FIRST.get(subject)
    if reply is None:
        return [_sim.thinking(), _sim.text(json.dumps({"serial_number": None, "sku": "unknown", "failure_mode": "other",
                                                       "safety_issue": False, "requested_action": "unclear", "evidence": ""}))]
    if len(params["messages"]) >= 3:
        reply = _CORRECTED.get(subject, reply)
    return [_sim.thinking(), _sim.text(json.dumps(reply))]


_sim.set_responder(_responder)
