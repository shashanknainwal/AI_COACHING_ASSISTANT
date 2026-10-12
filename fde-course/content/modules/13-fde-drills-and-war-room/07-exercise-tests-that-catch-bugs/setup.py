# The function under test. This is the correct version, already in production at
# Marram. Your job is to write checks that would catch someone breaking it.


def plan_batches(records, max_records, max_bytes):
    """Split records into upload batches for the client's bulk API.

    records: list of {"id": str, "size": int} in the order they must be sent.
    Returns {"batches": [[id, ...], ...], "oversized": [id, ...]}.
    """
    seen = set()
    batches, oversized = [], []
    current, current_bytes = [], 0
    for r in records:
        if r["id"] in seen:
            continue
        seen.add(r["id"])
        if r["size"] > max_bytes:
            oversized.append(r["id"])
            continue
        if current and (len(current) + 1 > max_records or current_bytes + r["size"] > max_bytes):
            batches.append(current)
            current, current_bytes = [], 0
        current.append(r["id"])
        current_bytes += r["size"]
    if current:
        batches.append(current)
    return {"batches": batches, "oversized": oversized}
