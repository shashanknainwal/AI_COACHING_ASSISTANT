import hashlib

# Gannet Home Energy (fictional): 100 golden cases for the tariff-question prompt,
# and per-case results (True = pass) for three prompt variants.
CASE_IDS = [f"G-{i:03d}" for i in range(1, 101)]


def _bucket(cid):
    return int(hashlib.sha256(cid.encode()).hexdigest(), 16) % 100


def _split_of(cid):
    b = _bucket(cid)
    return "dev" if b < 60 else "val" if b < 80 else "test"


_v0 = {cid: (i % 4 != 0) for i, cid in enumerate(CASE_IDS)}           # baseline, about 75%

# v1: someone pasted the dev-set failures into the prompt as few-shot examples.
# Every dev failure now passes; elsewhere the long, oddly specific prompt breaks things.
_v1 = {}
for i, cid in enumerate(CASE_IDS):
    if _split_of(cid) == "dev":
        _v1[cid] = True
    else:
        _v1[cid] = _v0[cid] and i % 3 != 1

# v2: one general instruction ("read the tariff name back before quoting a price").
# It fixes about half of the failures everywhere and breaks nothing.
_v2 = {cid: _v0[cid] or i % 8 == 0 for i, cid in enumerate(CASE_IDS)}

RESULTS = {"v0-baseline": _v0, "v1-pasted-examples": _v1, "v2-read-back-rule": _v2}
