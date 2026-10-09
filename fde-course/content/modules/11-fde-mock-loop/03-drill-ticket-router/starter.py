class TicketRouter:
    """A ticket-routing service. Timestamps only ever increase between calls.

    Read Level 1 on the left, then fill in the methods it asks for.
    Add the methods for each later level when it unlocks.
    """

    def __init__(self):
        pass

    def add_rule(self, timestamp, keyword, queue):
        pass

    def ingest(self, timestamp, ticket_id, subject):
        pass

    def get_ticket(self, timestamp, ticket_id):
        pass

    def close(self, timestamp, ticket_id):
        pass

    def list_queue(self, timestamp, queue):
        pass


# --- Try it out (not graded) ---
r = TicketRouter()
r.add_rule(1, "invoice", "billing")
print(r.ingest(2, "T1", "Invoice is wrong"))   # should print billing
print(r.get_ticket(3, "T1"))                    # should print billing:open
