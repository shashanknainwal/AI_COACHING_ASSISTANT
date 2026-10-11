# Package Cindervale's exception playbook (PLAYBOOK_NOTES) as an Agent Skill.

SKILL_MD = """---
name: TODO
description: TODO
---

# Shipment exceptions

TODO
"""

CLASSIFY_PY = '''
def classify_exception(event):
    # TODO
    return {}
'''

SKILL_FILES = {
    "SKILL.md": SKILL_MD,
    # "references/....md": ...,
    "scripts/classify_exception.py": CLASSIFY_PY,
}


def run_trigger_eval(skill_files, cases):
    """Route every case with our skill plus the competing skills. Returns {"passed", "total", "failures"}."""
    # TODO
    return {"passed": 0, "total": len(cases), "failures": []}


def run_behaviour_eval(skill_files, cases):
    """Execute the packaged script and check it against each case. Returns {"passed", "total", "failures"}."""
    # TODO
    return {"passed": 0, "total": len(cases), "failures": []}


# --- Try it out (not graded) ---
meta, body = parse_skill_md(SKILL_FILES["SKILL.md"])
print("name:", meta.get("name"), "| description length:", len(meta.get("description", "")), "| body lines:", len(body.splitlines()))
print("trigger eval:", run_trigger_eval(SKILL_FILES, TRIGGER_CASES))
print("behaviour eval:", run_behaviour_eval(SKILL_FILES, BEHAVIOUR_CASES))
