class WebhookInbox:
    """Ingest for a payment provider's webhooks. Timestamps never decrease between calls.

    Read Level 1, then fill in the methods it asks for.
    Add the methods for each later level when it unlocks.
    """

    def __init__(self):
        pass

    def receive(self, timestamp, event_id, account, seq, kind, amount):
        pass

    def balance(self, timestamp, account):
        pass

    def event_count(self, timestamp, account):
        pass
