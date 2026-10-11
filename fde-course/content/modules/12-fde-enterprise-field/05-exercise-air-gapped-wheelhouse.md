---
title: "Exercise: Plan an Air-Gapped Install"
type: exercise
minutes: 35
hints:
  - "`parse_requirements`: first join continuations with `text.replace(\"\\\\\\n\", \" \")`. Then for each line strip comments with `re.sub(r\"(^|\\s)#.*$\", \"\", raw).strip()` and skip blanks."
  - "Split a line on whitespace. The first token is the spec; the rest are options. Hashes are the tokens starting with `--hash=`; keep the part after `=` (for example `sha256:a1b2`) and sort them."
  - "`parse_wheel`: drop `.whl`, split on `-`. Five parts is `name-version-python-abi-platform`; six parts has a build tag after the version. Index the tags from the end: `parts[-3]`, `parts[-2]`, `parts[-1]`."
  - "`compatible`: each tag may be dotted (`py2.py3`, `manylinux_2_28_x86_64.manylinux_2_17_x86_64`). Split on `.` and accept if any piece is in the target's list. All three tags must pass."
  - "`plan`: for each requirement in sorted order, narrow the wheels step by step (same name, same version, compatible, hash allowed) and record the first step that leaves nothing."
---

Quarrybank's analytics enclave has no outbound network at all. Software gets in one way: you hand a reviewed bundle to Priit on the intake team, it's scanned, and two days later it appears at `/opt/wheelhouse`. If one package is missing, that's another two-day round trip. Sana has already had a vendor take four rounds to get a single install working.

You'll get it right in one round by checking the bundle against the lock file before you hand it over. Inside the enclave, the install will be:

```bash
pip install --no-index --find-links /opt/wheelhouse --require-hashes -r requirements.txt
```

`--no-index` means pip won't look anywhere else. `--require-hashes` means every requirement must be pinned with `==` and every file must match one of its listed hashes. Both are what a security team wants: nothing unreviewed gets in.

Package versions and hashes in this exercise are made up. Real sha256 hashes are 64 hex characters; these are shortened to keep the data readable.

## The data

- `REQUIREMENTS`: a lock file in the format `pip-compile --generate-hashes` writes, with backslash line continuations and comments.
- `WHEELHOUSE`: the files someone downloaded, each with its sha256.
- `TARGET`: the tags the enclave's Python accepts. On the real machine, `pip debug --verbose` prints them. A wheel built for Python 3.12, or on a Mac, won't install on Linux with Python 3.11.

`normalize(name)` is given. It applies PEP 503: lowercase, with runs of `-`, `_` and `.` turned into `-`, so `Pydantic_Core` and `pydantic-core` are the same package.

## Your task

**1. `parse_requirements(text)`** returns `(reqs, problems)`.
- Join backslash continuations, drop comments (whole-line and trailing) and blank lines.
- `reqs` maps the normalized name to `{"version": "1.2.0", "hashes": ["sha256:...", ...]}` with hashes sorted.
- A requirement without `==` adds `"<name>: not pinned with =="` to `problems`. A pinned requirement with no hashes adds `"<name>: no hashes"`. Neither goes into `reqs`.

**2. `parse_wheel(filename)`** returns `{"name", "version", "python", "abi", "platform"}`. The name is normalized. Wheel filenames have five dash-separated parts, or six when there's a build tag after the version. Anything else, or a file not ending in `.whl`, raises `ValueError`.

**3. `compatible(wheel, target)`** is true when the python tag, the abi tag and the platform tag each have at least one dotted piece in the target's `python_tags`, `abi_tags` and `platforms`.

**4. `plan(requirements_text, wheelhouse, target)`** returns:

```python
{"install": [{"name": ..., "file": ...}], "missing": [...], "wrong_version": [...],
 "incompatible": [...], "hash_mismatch": [...], "problems": [...], "extra": [...], "ready": bool}
```

For each requirement in `reqs`, in sorted order, record the **first** check that fails:

| Check | Fails into |
|---|---|
| No wheel with this name | `missing` (the name) |
| None at the pinned version | `wrong_version`: `"<name>==<version> (wheelhouse has <sorted versions, comma-separated>)"` |
| None of those is compatible with the target | `incompatible` (the name) |
| None of the compatible ones has an allowed hash | `hash_mismatch` (the name) |
| All pass | `install`: the first matching file in filename order |

`problems` comes from `parse_requirements`. `extra` lists, sorted, the wheel files whose package isn't named anywhere in the requirements (including the problem lines). `ready` is true only when `missing`, `wrong_version`, `incompatible`, `hash_mismatch` and `problems` are all empty. Don't modify the inputs.

## Example

Press **Run** on the demo data:

```
missing        ['sniffio']
wrong_version  ['anyio==4.9.0 (wheelhouse has 4.8.0)']
incompatible   ['numpy']                  # downloaded on a Mac
hash_mismatch  ['certifi']                # a different file from the one locked
problems       ['idna: not pinned with ==']
extra          ['tqdm-4.67.1-py3-none-any.whl']
```

Each line is a round trip you just saved. Build the wheelhouse on a machine that matches the target (same Python version and OS, often a container of the enclave's base image) with `pip download --only-binary=:all:` against the same lock file, then run this check before handing it to intake.

> **FDE tip:** Ask in week one whether the customer has an internal package mirror (Artifactory, Nexus or similar) and who approves new packages. A mirror turns this from a two-day round trip into a ticket. Ask the companion question at the same time: if the enclave can't reach the internet, how will it reach the model?
