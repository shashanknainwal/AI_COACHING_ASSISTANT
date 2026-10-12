import re


def _meta_body():
    return parse_skill_md(SKILL_FILES.get("SKILL.md", ""))


def test_frontmatter_rules():
    """SKILL.md frontmatter has a valid name and a description that says what and when"""
    meta, _ = _meta_body()
    name, desc = meta.get("name", ""), meta.get("description", "")
    assert name == SKILL_NAME, f"Name the skill {SKILL_NAME!r} (keep it the same as the skill's folder name). Got {name!r}"
    assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) and len(name) <= 64, \
        "name: lowercase letters, digits and single hyphens, at most 64 characters."
    assert desc and desc != "TODO", "Write a description: it's what the model reads to decide whether to load the skill."
    assert len(desc) <= 1024, f"description: at most 1024 characters. Got {len(desc)}."
    assert "<" not in desc and ">" not in desc, "description: no angle brackets."
    assert "use when" in desc.lower(), "Say when to use the skill in the description itself ('Use when ...'). The body is only read after the skill triggers."


def test_progressive_disclosure():
    """The body is short and points to reference files that hold the detail"""
    _, body = _meta_body()
    lines = body.splitlines()
    assert 8 <= len(lines) <= BODY_MAX_LINES, f"Keep the SKILL.md body between 8 and {BODY_MAX_LINES} lines (this course's rule). Got {len(lines)}."
    refs = [p for p in SKILL_FILES if p.startswith("references/") and p.endswith(".md")]
    assert len(refs) >= 2, "Move the detail into at least two reference files under references/."
    for p in refs:
        assert p in body, f"SKILL.md must tell the model when to read {p}: mention its path in the body."
        assert len(SKILL_FILES[p].strip().splitlines()) >= 8, f"{p} is too thin to be worth a file (at least 8 lines)."
    assert "scripts/classify_exception.py" in body, "Tell the model to run scripts/classify_exception.py."
    for detail in ("10,000", "10000", "48", "3 days"):
        assert detail not in body, f"The threshold {detail!r} belongs in a reference file, not the SKILL.md body."
    all_refs = " ".join(SKILL_FILES[p] for p in refs)
    assert ("10,000" in all_refs or "10000" in all_refs) and "48" in all_refs, "The escalation thresholds should live in a reference file."


def test_behaviour_eval():
    """The packaged script follows the playbook on every case"""
    r = run_behaviour_eval(SKILL_FILES, BEHAVIOUR_CASES)
    assert r.get("total") == len(BEHAVIOUR_CASES), "total is the number of cases."
    assert r.get("passed") == len(BEHAVIOUR_CASES), f"The script passed {r.get('passed')} of {len(BEHAVIOUR_CASES)} cases. First failures: {r.get('failures', [])[:2]}"
    ns = {"__name__": "x"}
    exec(SKILL_FILES["scripts/classify_exception.py"], ns)
    assert ns["classify_exception"]({"code": "DMG", "value_eur": 10000})["escalate"] is False, "Over EUR 10,000 means strictly greater."


def test_behaviour_eval_catches_a_broken_script():
    """run_behaviour_eval really runs the packaged script"""
    broken = dict(SKILL_FILES)
    broken["scripts/classify_exception.py"] = "def classify_exception(event):\n    return {'category': 'unknown', 'first_action': 'route_to_duty_manager', 'escalate': True}\n"
    r = run_behaviour_eval(broken, BEHAVIOUR_CASES)
    assert r.get("passed") == 1 and len(r.get("failures", [])) == 9, "Your eval should execute the script it's given and count failures."


def test_trigger_eval():
    """The skill triggers on exceptions and stays quiet otherwise"""
    r = run_trigger_eval(SKILL_FILES, TRIGGER_CASES)
    assert r.get("total") == len(TRIGGER_CASES), "total is the number of cases."
    fails = r.get("failures", [])
    assert r.get("passed") == len(TRIGGER_CASES) and not fails, \
        f"{r.get('passed')} of {len(TRIGGER_CASES)} cases routed correctly. First failure: {fails[:1]}. Tune the description, not the router."


def test_trigger_eval_catches_a_vague_description():
    """run_trigger_eval really uses the description it's given"""
    vague = dict(SKILL_FILES)
    vague["SKILL.md"] = "---\nname: shipment-exceptions\ndescription: Helps with logistics. Use when needed.\n---\nBody\n"
    r = run_trigger_eval(vague, TRIGGER_CASES)
    assert r.get("passed", 99) < len(TRIGGER_CASES), "A vague description should fail your trigger eval. Route with the description from skill_files."
