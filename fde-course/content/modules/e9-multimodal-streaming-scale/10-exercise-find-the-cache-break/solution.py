import json


def strip_cache_control(obj):
    if isinstance(obj, dict):
        return {k: strip_cache_control(v) for k, v in obj.items() if k != "cache_control"}
    if isinstance(obj, list):
        return [strip_cache_control(v) for v in obj]
    return obj


def _dumps(x):
    return json.dumps(x, ensure_ascii=False, separators=(",", ":"))


def segments(body):
    body = strip_cache_control(body)
    out = [(f"tools[{i}]", _dumps(t)) for i, t in enumerate(body.get("tools", []))]
    system = body.get("system")
    if isinstance(system, list):
        out += [(f"system[{j}]", _dumps(b)) for j, b in enumerate(system)]
    elif system is not None:
        out.append(("system", _dumps(system)))
    out += [(f"messages[{k}]", _dumps(m)) for k, m in enumerate(body.get("messages", []))]
    return out


def _first_diff(x, y):
    for i, (p, q) in enumerate(zip(x, y)):
        if p != q:
            return i
    return min(len(x), len(y))


def first_divergence(a, b):
    if a.get("model") != b.get("model"):
        return {"section": "model", "path": "model", "offset": 0, "a": a.get("model"), "b": b.get("model")}
    sa, sb = segments(a), segments(b)
    for (pa, ta), (pb, tb) in zip(sa, sb):
        if pa != pb or ta != tb:
            off = _first_diff(ta, tb) if pa == pb else 0
            return {"section": pa.split("[")[0], "path": pa, "offset": off,
                    "a": ta[off:off + 20], "b": tb[off:off + 20]}
    if len(sa) > len(sb):
        pa, ta = sa[len(sb)]
        return {"section": pa.split("[")[0], "path": pa, "offset": 0, "a": ta[:20], "b": ""}
    return None


def diagnose(a, b):
    div = first_divergence(a, b)
    if div is None:
        return "none"
    if div["section"] == "model":
        return "model_switch"
    if div["section"] == "tools":
        names_a = [t["name"] for t in a.get("tools", [])]
        names_b = [t["name"] for t in b.get("tools", [])]
        if sorted(names_a) != sorted(names_b):
            return "tools_changed"
        if names_a != names_b:
            return "tool_order"
        return "key_order"
    if div["section"] == "system":
        return "system_changed"
    return "history_edited"


# --- Try it out (not graded) ---
if __name__ == "__main__":
    for name, (a, b) in PAIRS.items():
        print(f"{name:14} {diagnose(a, b):15} {first_divergence(a, b)}")
