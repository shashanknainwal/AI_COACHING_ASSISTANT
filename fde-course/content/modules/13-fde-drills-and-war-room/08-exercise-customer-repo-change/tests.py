import importlib as _il
import os as _os
import sys as _sys

_CSV = """name,email,phone
Ada Obi,ada@example.com,(555) 010-2000
Bo Lind,,555-010-3000
Cy Ruiz,cy@example.com,1-555-010-4000
Di Park,di@example.com,
Ed Moss,ed@example.com,010-4000
Fay Wu,fay@example.com,+1 555 010 5000
"""


def _fresh():
    for name in [m for m in _sys.modules if m == "tidewater" or m.startswith("tidewater.")]:
        del _sys.modules[name]
    _il.invalidate_caches()
    if REPO not in _sys.path:
        _sys.path.insert(0, REPO)
    importer = _il.import_module("tidewater.importer")
    store_mod = _il.import_module("tidewater.store")
    store = store_mod.MemoryStore()
    counts = importer.import_contacts(_CSV, store)
    return counts, store


def _repo_files():
    out = {}
    for root, dirs, files in _os.walk(REPO):
        for f in files:
            if f.endswith(".pyc"):
                continue
            p = _os.path.join(root, f)
            out[_os.path.relpath(p, REPO).replace("\\", "/")] = open(p).read()
    return out


def test_phones_are_e164():
    """Saved contacts have phones in +1XXXXXXXXXX form"""
    _, store = _fresh()
    assert store.saved.get("ada@example.com", {}).get("phone") == "+15550102000", "(555) 010-2000 becomes +15550102000"
    assert store.saved.get("cy@example.com", {}).get("phone") == "+15550104000", "a leading 1 is allowed"
    assert store.saved.get("fay@example.com", {}).get("phone") == "+15550105000"


def test_missing_email_goes_to_review():
    """Rows without an email go to manual review, not the store"""
    counts, store = _fresh()
    assert any(r.get("name") == "Bo Lind" for r in store.review), "Bo Lind has no email"
    assert "" not in store.saved, "a contact was saved under an empty email"


def test_blank_and_invalid_phones():
    """A blank phone is saved as None; an invalid phone goes to review"""
    counts, store = _fresh()
    assert "di@example.com" in store.saved and store.saved["di@example.com"].get("phone") is None
    assert any(r.get("name") == "Ed Moss" for r in store.review), "010-4000 isn't a valid US number"
    assert counts == {"saved": 4, "review": 2}, counts


def test_existing_hook_still_runs():
    """The existing audit_trail hook still runs on every saved contact"""
    _, store = _fresh()
    assert store.saved and all(r.get("source") == "csv_import" for r in store.saved.values()), \
        "keep audit_trail enabled"


def test_shared_code_untouched():
    """The importer, hooks, phone helper, store, audit and legacy_sync files are unchanged"""
    files = _repo_files()
    for rel in ("tidewater/importer.py", "tidewater/hooks.py", "tidewater/phone.py", "tidewater/store.py",
                "tidewater/audit.py", "tidewater/legacy_sync.py", "tidewater/__init__.py", "README.md"):
        assert files.get(rel) == _REPO_FILES[rel], f"{rel} changed; three customers share it. Use the extension point."


def test_settings_change_is_minimal():
    """settings.py changes only the hook lists"""
    text = _repo_files()["tidewater/settings.py"]
    orig = _REPO_FILES["tidewater/settings.py"].splitlines()
    new = text.splitlines()
    assert len(new) == len(orig), "change lines in settings.py, don't add or remove them"
    changed = [o for o, n in zip(orig, new) if o != n]
    assert all(o.startswith(("HOOK_MODULES", "ENABLED_HOOKS")) for o in changed), \
        "only HOOK_MODULES and ENABLED_HOOKS should change"


def test_at_most_one_new_file():
    """The change adds at most one new module"""
    new = sorted(set(_repo_files()) - set(_REPO_FILES))
    assert len(new) <= 1, f"new files: {new}; one hook module is enough"
    assert new, "add your rules as a hook module"


def test_reuses_the_phone_helper():
    """The new module reuses tidewater.phone instead of reimplementing it"""
    new = sorted(set(_repo_files()) - set(_REPO_FILES))
    assert new, "add your rules as a hook module"
    assert "normalize_us" in _repo_files()[new[0]], "the repo already has a phone normaliser; use it"
