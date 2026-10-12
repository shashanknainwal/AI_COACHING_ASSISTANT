import hashlib


class EvalLab:
    """Prompt hill-climbing with a dev split, a validation split and a frozen test split.

    Read Level 1 on the left, then fill in the methods it asks for.
    Add the methods for each later level when it unlocks.
    """

    def __init__(self, case_ids):
        self.case_ids = list(case_ids)

    def split(self):
        pass

    def fingerprint(self, name):
        pass


# --- Try it out (not graded) ---
lab = EvalLab(CASE_IDS)
parts = lab.split()
if parts:
    print({k: len(v) for k, v in parts.items()}, "test fingerprint", lab.fingerprint("test"))
