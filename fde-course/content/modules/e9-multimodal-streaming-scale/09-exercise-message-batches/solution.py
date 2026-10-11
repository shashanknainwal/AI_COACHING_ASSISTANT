import time


def build_requests(orders):
    """Return (requests, id_map) where id_map maps custom_id -> order_id."""
    requests, id_map = [], {}
    for i, order in enumerate(orders):
        cid = f"order-{i:05d}"
        id_map[cid] = order["order_id"]
        requests.append({"custom_id": cid, "params": {
            "model": MODEL,
            "max_tokens": MAX_TOKENS,
            "output_config": {"effort": "low"},
            "system": [{"type": "text", "text": SYSTEM_PROMPT,
                        "cache_control": {"type": "ephemeral", "ttl": "1h"}}],
            "messages": [{"role": "user", "content": order["text"]}],
        }})
    return requests, id_map


def run_batch(client, requests, poll_seconds=60):
    batch = client.messages.batches.create(requests=requests)
    while client.messages.batches.retrieve(batch.id).processing_status != "ended":
        time.sleep(poll_seconds)
    results = {r.custom_id: r for r in client.messages.batches.results(batch.id)}
    return batch.id, results


def process(client, orders, max_rounds=3, poll_seconds=60):
    requests, id_map = build_requests(orders)
    pending = {r["custom_id"]: r for r in requests}
    labels, failed, batch_ids, last_reason = {}, {}, [], {}
    rounds = 0
    while pending and rounds < max_rounds:
        rounds += 1
        batch_id, results = run_batch(client, list(pending.values()), poll_seconds)
        batch_ids.append(batch_id)
        retry = {}
        for cid, req in pending.items():
            res = results[cid].result
            oid = id_map[cid]
            if res.type == "succeeded":
                labels[oid] = next(b.text for b in res.message.content if b.type == "text").strip()
            elif res.type == "errored" and res.error.error.type == "invalid_request_error":
                failed[oid] = "invalid_request_error"
            else:
                last_reason[cid] = res.error.error.type if res.type == "errored" else res.type
                retry[cid] = req
        pending = retry
    for cid in pending:
        failed[id_map[cid]] = last_reason[cid]
    return {"labels": labels, "failed": failed, "rounds": rounds, "batch_ids": batch_ids}


# --- Try it out (not graded) ---
if __name__ == "__main__":
    report = process(client, ORDERS)
    print("rounds:", report["rounds"], "batches:", report["batch_ids"])
    print("labelled:", len(report["labels"]), "failed:", report["failed"])
    print("batch sizes:", [len(ids) for ids in client.messages.batches.created])
