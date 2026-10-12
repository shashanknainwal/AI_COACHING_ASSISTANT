# Integration point: the hook system (README and hooks.py say customer rules go there).
# Minimal change: one new hook module that reuses tidewater.phone, plus two list
# entries in settings.py. The importer, the phone helper and legacy_sync stay untouched.

write_file("tidewater/contact_rules.py", '''from tidewater.hooks import hook
from tidewater.phone import normalize_us


@hook("contact_rules")
def contact_rules(record):
    """Tidewater: no email means manual review; phones are stored in E.164."""
    if not record.get("email"):
        return None
    raw = record.get("phone", "")
    if not raw:
        record["phone"] = None
        return record
    phone = normalize_us(raw)
    if phone is None:
        return None
    record["phone"] = phone
    return record
''')

edit_file("tidewater/settings.py", 'HOOK_MODULES = ["tidewater.audit"]',
          'HOOK_MODULES = ["tidewater.audit", "tidewater.contact_rules"]')
edit_file("tidewater/settings.py", 'ENABLED_HOOKS = ["audit_trail"]',
          'ENABLED_HOOKS = ["audit_trail", "contact_rules"]')

if __name__ == "__main__":
    from tidewater.importer import import_contacts
    from tidewater.store import MemoryStore

    store = MemoryStore()
    print(import_contacts("name,email,phone\nAda,ada@example.com,(555) 010-2000\nBo,,555-010-3000\n", store))
    print(store.saved)
