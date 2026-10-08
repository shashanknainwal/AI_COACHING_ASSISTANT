class TemplateRegistry:
    """A prompt-template registry. Timestamps only ever increase between calls.

    Read Level 1 on the left, then fill in the methods it asks for.
    Add the methods for each later level when it unlocks.
    """

    def __init__(self):
        pass

    def add_version(self, timestamp, name, body):
        pass

    def render(self, timestamp, name, variables, version=None):
        pass

    def get_variables(self, timestamp, name, version=None):
        pass
