class ToolGate:
    """Decides which tools an agent (or person) may call. Timestamps never decrease between calls.

    Read Level 1, then fill in the methods it asks for.
    Add the methods for each later level when it unlocks.
    """

    def __init__(self):
        pass

    def add_tool(self, timestamp, name, scope):
        pass

    def grant(self, timestamp, principal, scope):
        pass

    def revoke(self, timestamp, principal, scope):
        pass

    def call(self, timestamp, principal, tool):
        pass
