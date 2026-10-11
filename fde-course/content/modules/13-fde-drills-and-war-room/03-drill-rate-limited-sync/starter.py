class SyncEngine:
    """Sync records from a customer's API into your store. Timestamps never decrease between calls.

    Read Level 1, then fill in the methods it asks for.
    Add the methods for each later level when it unlocks.
    """

    def __init__(self):
        pass

    def upsert(self, timestamp, record_id, updated_at, data):
        pass

    def sync(self, timestamp):
        pass

    def get(self, timestamp, record_id):
        pass

    def watermark(self, timestamp):
        pass

    def count(self, timestamp):
        pass
