import csv
import os
import random

# Writes the results of Quarrybank's 50,000-ticket backfill to the virtual
# filesystem: one row per model call. Re-runs of tickets that hit max_tokens
# were appended at the end of the file, so a ticket's attempts can sit in
# different chunks.
RESULTS_PATH = "/data/backfill_results.csv"
_COLUMNS = ["ticket_id", "attempt", "month", "category", "stop_reason", "input_tokens", "output_tokens"]
_CATEGORIES = ["billing", "card", "fraud_report", "login", "transfer", "other"]
_WEIGHTS = [26, 22, 9, 17, 18, 8]
_MONTHS = [f"{y}-{m:02d}" for y in (2024, 2025) for m in range(1, 13)]


def _write():
    rng = random.Random(12)
    os.makedirs("/data", exist_ok=True)
    rows, retries = [], []
    for i in range(1, 50_001):
        tid = f"T{i:06d}"
        month = _MONTHS[min(23, int(rng.random() ** 0.8 * 24))]
        inp = rng.randint(700, 2600)
        roll = rng.random()
        if roll < 0.03:
            # First attempt hit max_tokens; a second attempt is appended later.
            rows.append([tid, 1, month, "", "max_tokens", inp, 256])
            final = rng.random()
            if final < 0.012:
                retries.append([tid, 2, month, "", "refusal", inp, 0])
            else:
                retries.append([tid, 2, month, rng.choices(_CATEGORIES, _WEIGHTS)[0], "end_turn", inp, rng.randint(200, 900)])
        elif roll < 0.042:
            rows.append([tid, 1, month, "", "refusal", inp, 0])
        else:
            rows.append([tid, 1, month, rng.choices(_CATEGORIES, _WEIGHTS)[0], "end_turn", inp, rng.randint(60, 420)])
    with open(RESULTS_PATH, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(_COLUMNS)
        w.writerows(rows)
        w.writerows(retries)


if not os.path.exists(RESULTS_PATH):
    _write()
