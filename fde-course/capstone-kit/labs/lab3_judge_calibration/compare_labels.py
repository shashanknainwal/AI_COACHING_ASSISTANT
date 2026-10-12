"""Lab 3, step 2: compare your labels with the author's. No API calls.

    python -m labs.lab3_judge_calibration.compare_labels

Two humans rarely agree perfectly. The kappa between you and the author is a
ceiling of sorts for what you can expect from a judge on this rubric.
"""

from __future__ import annotations

from pathlib import Path

from evals.calibrate_judge import load_labels
from evals.stats import cohen_kappa, confusion

HERE = Path(__file__).parent


def main() -> int:
    mine = load_labels(HERE / "my_labels.csv")
    author = load_labels(HERE / "author_labels.jsonl")
    ids = sorted(author)
    missing = [i for i in ids if i not in mine]
    if missing:
        raise SystemExit(f"label every item in my_labels.csv first; missing: {', '.join(missing)}")
    a, b = [mine[i] for i in ids], [author[i] for i in ids]
    agree = sum(x == y for x, y in zip(a, b))
    print(f"you vs author: {agree}/{len(ids)} agree, kappa {cohen_kappa(a, b):.2f}")
    print(f"confusion (you/author): {confusion(a, b)}")
    print(f"items you disagree on: {[i for i in ids if mine[i] != author[i]] or 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
