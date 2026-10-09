class FlagService:
    """A feature-flag service. Timestamps only ever increase between calls.

    Read Level 1 on the left, then fill in the methods it asks for.
    Add the methods for each later level when it unlocks.
    """

    def __init__(self):
        pass

    def create_flag(self, timestamp, name, default):
        raise NotImplementedError

    def set_flag(self, timestamp, name, enabled):
        raise NotImplementedError

    def is_enabled(self, timestamp, name, user_id):
        raise NotImplementedError

    def delete_flag(self, timestamp, name):
        raise NotImplementedError
