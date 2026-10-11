import time


def build_requests(orders):
    """Return (requests, id_map) where id_map maps custom_id -> order_id."""
    # TODO: one request per order with a valid, unique custom_id
    return [], {}


def run_batch(client, requests, poll_seconds=60):
    """Submit, poll until ended, return (batch_id, {custom_id: result})."""
    # TODO
    return None, {}


def process(client, orders, max_rounds=3, poll_seconds=60):
    """Run the batch, retry what can be retried, report what failed."""
    # TODO
    return {"labels": {}, "failed": {}, "rounds": 0, "batch_ids": []}


# --- Try it out (not graded) ---
if __name__ == "__main__":
    report = process(client, ORDERS)
    print(report)
