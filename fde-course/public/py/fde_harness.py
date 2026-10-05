"""Runs learner code and hidden tests inside Pyodide.

The browser worker and the content validator (scripts/validate-content.mjs) both
call `run(...)` and get back a JSON string, so grading behaves identically in
both places.
"""

import contextlib
import io
import json
import sys
import traceback

_MAX_OUTPUT = 20_000


def _reset_simulators():
    import fde_clock

    fde_clock.install()
    fde_clock.reset()
    for name in ("anthropic._sim", "requests._sim"):
        mod = sys.modules.get(name)
        if mod is not None and hasattr(mod, "reset"):
            mod.reset()


def _exec(source, ns, filename):
    code = compile(source, filename, "exec")
    exec(code, ns)


def _format_user_error(exc):
    # Only show frames from the learner's own code, not the harness.
    tb = traceback.extract_tb(exc.__traceback__)
    frames = [f for f in tb if f.filename == "main.py"]
    lines = []
    for f in frames:
        lines.append(f'  File "main.py", line {f.lineno}, in {f.name}')
        if f.line:
            lines.append(f"    {f.line}")
    detail = "".join(traceback.format_exception_only(type(exc), exc)).strip()
    if lines:
        return "Traceback (most recent call last):\n" + "\n".join(lines) + "\n" + detail
    return detail


_TRACE_RUNS = 12
_TRACE_STEPS = 30
_TRACE_TEXT = 600


def _clip(value, limit=_TRACE_TEXT):
    text = value if isinstance(value, str) else json.dumps(value, default=str)
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _content_text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")
    return ""


def _build_trace():
    """Group the simulated Claude calls into agent runs for the console's Trace tab."""
    sim = sys.modules.get("anthropic._sim")
    if sim is None or not sim.calls:
        return []
    runs = []
    for call in sim.calls:
        params = call.get("params", {})
        messages = params.get("messages", [])
        if not runs or (len(messages) <= 1 and call.get("attempt", 0) == 0):
            if len(runs) >= _TRACE_RUNS:
                break
            first = messages[0].get("content") if messages else ""
            runs.append({"question": _clip(_content_text(first), 200), "steps": []})
        run = runs[-1]
        # Tool results sent in this request belong to the previous step.
        last = messages[-1] if messages else {}
        if run["steps"] and last.get("role") == "user" and isinstance(last.get("content"), list):
            results = [
                {"id": b.get("tool_use_id"), "is_error": bool(b.get("is_error")), "content": _clip(_content_text(b.get("content")) or str(b.get("content", "")), 300)}
                for b in last["content"]
                if isinstance(b, dict) and b.get("type") == "tool_result"
            ]
            if results and not run["steps"][-1].get("results"):
                run["steps"][-1]["results"] = results
        if len(run["steps"]) >= _TRACE_STEPS:
            continue
        response = call.get("response")
        step = {"model": params.get("model"), "attempt": call.get("attempt", 0), "error": call.get("error")}
        if response:
            step["stop_reason"] = response["stop_reason"]
            step["usage"] = response["usage"]
            step["blocks"] = [
                dict(b, input=_clip(b["input"], 300)) if b["type"] == "tool_use" else (dict(b, text=_clip(b["text"])) if b["type"] == "text" else b)
                for b in response["blocks"]
            ]
        run["steps"].append(step)
    return runs


def run(user_code, setup_code="", test_code="", mode="run"):
    """mode is "run" (just execute) or "submit" (execute, then grade)."""
    _reset_simulators()
    ns = {"__name__": "__main__"}
    out = io.StringIO()
    result = {"ok": True, "stdout": "", "error": None, "tests": [], "passed": None, "trace": []}

    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        try:
            if setup_code:
                _exec(setup_code, ns, "setup.py")
            _exec(user_code, ns, "main.py")
        except SystemExit:
            pass
        except BaseException as exc:  # noqa: BLE001 - learner code can raise anything
            result["ok"] = False
            result["error"] = _format_user_error(exc)

    try:
        result["trace"] = _build_trace()
    except Exception:  # noqa: BLE001 - the trace is a nice-to-have, never a reason to fail a run
        result["trace"] = []

    if mode == "submit" and test_code:
        tests = []
        if result["ok"]:
            test_ns = dict(ns)
            try:
                _exec(test_code, test_ns, "tests.py")
            except BaseException as exc:  # noqa: BLE001
                tests.append({"name": "load tests", "passed": False, "message": f"{type(exc).__name__}: {exc}"})
            for name, fn in list(test_ns.items()):
                if not (name.startswith("test_") and callable(fn)):
                    continue
                label = (fn.__doc__ or name).strip().splitlines()[0]
                try:
                    with contextlib.redirect_stdout(io.StringIO()):
                        fn()
                    tests.append({"name": label, "passed": True, "message": ""})
                except AssertionError as exc:
                    tests.append({"name": label, "passed": False, "message": str(exc) or "Assertion failed"})
                except BaseException as exc:  # noqa: BLE001
                    tests.append({"name": label, "passed": False, "message": f"{type(exc).__name__}: {exc}"})
        else:
            tests.append({"name": "Your code ran without errors", "passed": False, "message": "Fix the error above first."})
        result["tests"] = tests
        result["passed"] = bool(tests) and all(t["passed"] for t in tests)

    text = out.getvalue()
    if len(text) > _MAX_OUTPUT:
        text = text[:_MAX_OUTPUT] + "\n... output truncated ..."
    result["stdout"] = text
    return json.dumps(result)
