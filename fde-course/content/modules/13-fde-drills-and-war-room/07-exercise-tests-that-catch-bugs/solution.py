def R(*pairs):
    return [{"id": i, "size": s} for i, s in pairs]


def check_empty_input(plan_batches):
    assert plan_batches([], 3, 100) == {"batches": [], "oversized": []}


def check_byte_limit_is_inclusive(plan_batches):
    out = plan_batches(R(("a", 60), ("b", 40), ("c", 1)), 10, 100)
    assert out["batches"] == [["a", "b"], ["c"]], out


def check_record_limit(plan_batches):
    out = plan_batches(R(("a", 1), ("b", 1), ("c", 1), ("d", 1), ("e", 1)), 2, 100)
    assert out["batches"] == [["a", "b"], ["c", "d"], ["e"]], out


def check_order_is_kept(plan_batches):
    out = plan_batches(R(("z", 1), ("a", 1), ("m", 1)), 10, 100)
    assert out["batches"] == [["z", "a", "m"]], out


def check_duplicates_keep_first(plan_batches):
    out = plan_batches(R(("a", 1), ("b", 1), ("a", 1), ("c", 1)), 2, 100)
    assert out["batches"] == [["a", "b"], ["c"]], out


def check_oversized_skipped_and_reported(plan_batches):
    out = plan_batches(R(("a", 10), ("big", 101), ("edge", 100), ("b", 10)), 10, 100)
    assert out["oversized"] == ["big"], out
    assert out["batches"] == [["a"], ["edge"], ["b"]], out


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("check_"):
            fn(plan_batches)
            print("ok", name)
