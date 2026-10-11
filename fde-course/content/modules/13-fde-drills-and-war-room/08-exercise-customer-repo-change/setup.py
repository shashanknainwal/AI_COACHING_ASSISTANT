# Writes Tidewater Supply's contact-import repo to the virtual filesystem and gives
# you three helpers: tree(), show(path) and the two editing tools edit_file / write_file.
import importlib as _importlib
import os as _os
import sys as _sys

REPO = "/tmp/tidewater_repo"

_REPO_FILES = {
    "tidewater/__init__.py": '"""Tidewater Supply: contact import service."""\n',
    "tidewater/settings.py": '''# Deployment settings. Ops edits this file per environment.
SOURCE_ENCODING = "utf-8"
STORE_BACKEND = "memory"

# Modules that register hooks (imported at start-up, in this order).
HOOK_MODULES = ["tidewater.audit"]

# Hooks that run, in this order, before a contact is saved.
ENABLED_HOOKS = ["audit_trail"]
''',
    "tidewater/hooks.py": '''"""Extension points. Customer-specific rules belong in hooks, not in the importer."""
import importlib

from tidewater import settings

_HOOKS = {}


def hook(name):
    """Register fn as the hook called `name`. A hook takes a record dict and returns
    the record (possibly changed) or None to send the row to manual review."""
    def register(fn):
        _HOOKS[name] = fn
        return fn
    return register


def load():
    for module in settings.HOOK_MODULES:
        importlib.import_module(module)


def run_before_save(record):
    for name in settings.ENABLED_HOOKS:
        fn = _HOOKS.get(name)
        if fn is None:
            raise KeyError(f"hook {name!r} is enabled but no module registered it")
        record = fn(record)
        if record is None:
            return None
    return record
''',
    "tidewater/audit.py": '''from tidewater.hooks import hook


@hook("audit_trail")
def audit_trail(record):
    record["source"] = "csv_import"
    return record
''',
    "tidewater/phone.py": '''import re


def normalize_us(raw):
    """Return a US number in E.164 form (+1 and 10 digits), or None if it isn't one."""
    digits = re.sub(r"\\D", "", raw or "")
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) != 10:
        return None
    return "+1" + digits
''',
    "tidewater/store.py": '''class MemoryStore:
    def __init__(self):
        self.saved = {}     # email -> record
        self.review = []    # raw rows a person must look at

    def save(self, record):
        self.saved[record["email"]] = record
''',
    "tidewater/importer.py": '''import csv
import io

from tidewater import hooks


def parse_csv(text):
    rows = []
    for row in csv.DictReader(io.StringIO(text)):
        rows.append({k.strip(): (v or "").strip() for k, v in row.items()})
    return rows


def import_contacts(text, store):
    """Import contacts from CSV text into store. Returns counts."""
    hooks.load()
    counts = {"saved": 0, "review": 0}
    for row in parse_csv(text):
        # TODO(2025): phone numbers arrive in every format under the sun
        record = hooks.run_before_save(dict(row))
        if record is None:
            store.review.append(row)
            counts["review"] += 1
        else:
            store.save(record)
            counts["saved"] += 1
    return counts
''',
    "tidewater/legacy_sync.py": '''"""Nightly sync to the old CRM. Frozen: the old CRM is retired next quarter."""


def to_legacy(record):
    return {"EMAIL": record.get("email", ""), "TEL": record.get("phone", "")}
''',
    "README.md": '''# tidewater

Imports contacts from CSV exports into the store.

Customer-specific rules go in a hook module (see tidewater/hooks.py and
tidewater/audit.py for an example), registered in settings.py. Please don't put
customer rules in the importer: three customers share it.
''',
}


def _purge():
    for name in [m for m in _sys.modules if m == "tidewater" or m.startswith("tidewater.")]:
        del _sys.modules[name]
    _importlib.invalidate_caches()


def _reset_repo():
    if _os.path.isdir(REPO):
        for root, dirs, files in _os.walk(REPO, topdown=False):
            for f in files:
                _os.remove(_os.path.join(root, f))
            for d in dirs:
                _os.rmdir(_os.path.join(root, d))
    for rel, text in _REPO_FILES.items():
        path = _os.path.join(REPO, rel)
        _os.makedirs(_os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(text)


def tree():
    """Print every file in the repo."""
    for root, dirs, files in _os.walk(REPO):
        dirs.sort()
        for f in sorted(files):
            print(_os.path.relpath(_os.path.join(root, f), REPO))


def show(rel):
    """Print a repo file with line numbers."""
    with open(_os.path.join(REPO, rel)) as f:
        for i, line in enumerate(f.read().splitlines(), 1):
            print(f"{i:3} {line}")


def edit_file(rel, old, new):
    """Replace the one occurrence of `old` with `new` in a repo file (like a one-hunk patch)."""
    path = _os.path.join(REPO, rel)
    with open(path) as f:
        text = f.read()
    if text.count(old) != 1:
        raise ValueError(f"{rel}: expected exactly one match for the old text, found {text.count(old)}")
    with open(path, "w") as f:
        f.write(text.replace(old, new))
    _purge()


def write_file(rel, text):
    """Create (or overwrite) a repo file."""
    path = _os.path.join(REPO, rel)
    _os.makedirs(_os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)
    _purge()


_purge()
_reset_repo()
if REPO not in _sys.path:
    _sys.path.insert(0, REPO)
