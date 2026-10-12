import re

# The enclave's interpreter and OS, as reported by `pip debug --verbose` on the target.
TARGET = {
    "python_tags": ["cp311", "py311", "py3"],
    "abi_tags": ["cp311", "none"],
    "platforms": ["manylinux_2_28_x86_64", "manylinux_2_17_x86_64", "manylinux2014_x86_64", "any"],
}

# Versions and hashes below are illustrative, not real releases.
REQUIREMENTS = """\
# generated with pip-compile --generate-hashes
anthropic==1.2.0 \\
    --hash=sha256:a1b2c3d4
httpx2==2.1.0 \\
    --hash=sha256:b0b0b0b0 \\
    --hash=sha256:b2c3d4e5
Pydantic_Core==2.30.1 --hash=sha256:c3d4e5f6
certifi==2026.9.1 --hash=sha256:d4e5f6a7
numpy==2.3.0 --hash=sha256:e5f6a7b8
anyio==4.9.0 --hash=sha256:f6a7b8c9
sniffio==1.3.1 --hash=sha256:0a1b2c3d
idna>=3.7  # someone forgot to pin this
"""

WHEELHOUSE = [
    {"file": "anthropic-1.2.0-py3-none-any.whl", "sha256": "a1b2c3d4"},
    {"file": "httpx2-2.1.0-py3-none-any.whl", "sha256": "b2c3d4e5"},
    {"file": "pydantic_core-2.30.1-cp312-cp312-manylinux_2_17_x86_64.whl", "sha256": "99999999"},
    {"file": "pydantic_core-2.30.1-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", "sha256": "c3d4e5f6"},
    {"file": "certifi-2026.9.1-py3-none-any.whl", "sha256": "deadbeef"},
    {"file": "numpy-2.3.0-cp311-cp311-macosx_14_0_arm64.whl", "sha256": "e5f6a7b8"},
    {"file": "anyio-4.8.0-py3-none-any.whl", "sha256": "f6a7b8c0"},
    {"file": "tqdm-4.67.1-py3-none-any.whl", "sha256": "12345678"},
]


def normalize(name):
    """PEP 503 name normalization (given)."""
    return re.sub(r"[-_.]+", "-", name).lower()


def parse_requirements(text):
    """Return (reqs, problems). reqs maps normalized name -> {"version", "hashes"}."""
    joined = text.replace("\\\n", " ")
    reqs, problems = {}, []
    for raw in joined.splitlines():
        line = re.sub(r"(^|\s)#.*$", "", raw).strip()
        if not line:
            continue
        tokens = line.split()
        spec = tokens[0]
        hashes = sorted(t.split("=", 1)[1] for t in tokens[1:] if t.startswith("--hash="))
        if "==" not in spec:
            name = normalize(re.split(r"[<>=!~ ]", spec, maxsplit=1)[0])
            problems.append(f"{name}: not pinned with ==")
            continue
        name, version = spec.split("==", 1)
        name = normalize(name)
        if not hashes:
            problems.append(f"{name}: no hashes")
            continue
        reqs[name] = {"version": version, "hashes": hashes}
    return reqs, problems


def parse_wheel(filename):
    """Split a wheel filename into name, version and its three tags."""
    if not filename.endswith(".whl"):
        raise ValueError(f"not a wheel: {filename}")
    parts = filename[:-4].split("-")
    if len(parts) not in (5, 6):
        raise ValueError(f"not a wheel: {filename}")
    return {
        "name": normalize(parts[0]),
        "version": parts[1],
        "python": parts[-3],
        "abi": parts[-2],
        "platform": parts[-1],
    }


def compatible(wheel, target):
    """True if any python, abi and platform tag of the wheel suits the target."""
    def ok(tags, allowed):
        return any(t in allowed for t in tags.split("."))
    return (ok(wheel["python"], target["python_tags"])
            and ok(wheel["abi"], target["abi_tags"])
            and ok(wheel["platform"], target["platforms"]))


def plan(requirements_text, wheelhouse, target):
    """Match every pinned requirement to one wheel, and list what blocks the install."""
    reqs, problems = parse_requirements(requirements_text)
    wheels = [dict(parse_wheel(w["file"]), file=w["file"], sha256=w["sha256"]) for w in wheelhouse]
    result = {"install": [], "missing": [], "wrong_version": [], "incompatible": [],
              "hash_mismatch": [], "problems": problems, "extra": []}

    for name in sorted(reqs):
        want = reqs[name]
        candidates = [w for w in wheels if w["name"] == name]
        if not candidates:
            result["missing"].append(name)
            continue
        same = [w for w in candidates if w["version"] == want["version"]]
        if not same:
            have = ", ".join(sorted({w["version"] for w in candidates}))
            result["wrong_version"].append(f"{name}=={want['version']} (wheelhouse has {have})")
            continue
        fits = [w for w in same if compatible(w, target)]
        if not fits:
            result["incompatible"].append(name)
            continue
        hashed = sorted((w for w in fits if "sha256:" + w["sha256"] in want["hashes"]), key=lambda w: w["file"])
        if not hashed:
            result["hash_mismatch"].append(name)
            continue
        result["install"].append({"name": name, "file": hashed[0]["file"]})

    required = set(reqs) | {p.split(":", 1)[0] for p in problems}
    result["extra"] = sorted(w["file"] for w in wheels if w["name"] not in required)
    blocking = ("missing", "wrong_version", "incompatible", "hash_mismatch", "problems")
    result["ready"] = not any(result[k] for k in blocking)
    return result


# --- Try it out (not graded) ---
report = plan(REQUIREMENTS, WHEELHOUSE, TARGET)
if report:
    for key in ("install", "missing", "wrong_version", "incompatible", "hash_mismatch", "problems", "extra", "ready"):
        print(f"{key:<14}", report[key])
    print("\nInside the enclave: pip install --no-index --find-links /opt/wheelhouse --require-hashes -r requirements.txt")
