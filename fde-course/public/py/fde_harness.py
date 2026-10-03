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
    for name in ("anthropic._sim", "fde_sim"):
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


def run(user_code, setup_code="", test_code="", mode="run"):
    """mode is "run" (just execute) or "submit" (execute, then grade)."""
    _reset_simulators()
    ns = {"__name__": "__main__"}
    out = io.StringIO()
    result = {"ok": True, "stdout": "", "error": None, "tests": [], "passed": None}

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
