# Write checks for plan_batches (its code is in setup.py and already loaded).
# Each check takes the function under test as its only argument and uses assert.
# Name them check_... (not test_...). Press Run to try them against the real function.


def check_returns_a_dict(plan_batches):
    out = plan_batches([{"id": "a", "size": 1}], 2, 10)
    assert isinstance(out, dict)


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("check_"):
            fn(plan_batches)
            print("ok", name)
