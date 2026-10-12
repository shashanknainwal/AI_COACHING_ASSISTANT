import json


def strip_cache_control(obj):
    """A copy of obj with every cache_control key removed, at any depth."""
    # TODO
    return obj


def segments(body):
    """[(path, serialized)] in cache order: tools, then system, then messages."""
    # TODO
    return []


def first_divergence(a, b):
    """Where request b stops sharing request a's prefix, or None."""
    # TODO
    return None


def diagnose(a, b):
    """Name the cause of the break."""
    # TODO
    return "none"


# --- Try it out (not graded) ---
if __name__ == "__main__":
    for name, (a, b) in PAIRS.items():
        print(f"{name:14} {diagnose(a, b):15} {first_divergence(a, b)}")
