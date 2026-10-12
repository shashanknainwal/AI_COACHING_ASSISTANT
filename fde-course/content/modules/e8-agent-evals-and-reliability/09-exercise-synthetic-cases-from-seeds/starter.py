import random
import re

# SEEDS, TONES, CHANNELS and HELD_OUT are loaded for you.


def apply_tone(text, tone, account):
    # TODO
    return text


def apply_channel(text, channel):
    # TODO
    return text


def add_typo(text, rng):
    # TODO: swap two adjacent letters in one alphabetic word longer than 4 letters.
    return text


def generate(seeds, per_seed):
    # TODO: one random.Random(f"{seed_id}:{i}") per case.
    pass


def normalize(text):
    # TODO
    pass


def shingles(text, n=3):
    # TODO
    pass


def jaccard(a, b):
    # TODO
    pass


def dedupe(cases, threshold=0.8):
    # TODO: return (kept, [(dropped_id, kept_id), ...])
    pass


def decontaminate(cases, held_out, threshold=0.8):
    # TODO: return (kept, [dropped_id, ...])
    pass


def coverage_gaps(cases):
    # TODO
    pass


def build_suite(seeds, per_seed, held_out, threshold=0.8):
    # TODO
    pass


# --- Try it out (not graded) ---
suite = build_suite(SEEDS, 6, HELD_OUT)
if suite:
    print(f"{len(suite['cases'])} cases kept; {len(suite['dropped_duplicates'])} near-duplicates and "
          f"{len(suite['dropped_contaminated'])} test-set leaks dropped")
    for c in suite["cases"][:6]:
        print(f"  {c['id']} {c['axes']}  {c['text'][:90]!r}")
    print("missing (intent, tone) combinations:", suite["missing_coverage"])
