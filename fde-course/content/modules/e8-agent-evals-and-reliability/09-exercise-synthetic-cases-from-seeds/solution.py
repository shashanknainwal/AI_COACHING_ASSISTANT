import random
import re

# SEEDS, TONES, CHANNELS and HELD_OUT are loaded for you.


def apply_tone(text, tone, account):
    if tone == "terse":
        sentences = re.split(r"(?<=[.?!])\s+", text)
        return next(s for s in sentences if account in s)
    return TONES[tone].format(text=text)


def apply_channel(text, channel):
    if channel == "email":
        return f"Subject: Moving house\n\nHello,\n\n{text}\n\nRegards"
    if channel == "sms":
        return re.sub(r"[.,!?;:]", "", text.lower())
    return text


def add_typo(text, rng):
    words = text.split(" ")
    candidates = [i for i, w in enumerate(words) if w.isalpha() and len(w) > 4]
    if not candidates:
        return text
    i = rng.choice(candidates)
    w = words[i]
    j = rng.randrange(len(w) - 1)
    words[i] = w[:j] + w[j + 1] + w[j] + w[j + 2:]
    return " ".join(words)


def generate(seeds, per_seed):
    cases = []
    for seed in seeds:
        for i in range(per_seed):
            rng = random.Random(f"{seed['id']}:{i}")
            account = "GN-" + "".join(rng.choice("0123456789") for _ in range(6))
            amount = rng.choice(seed["amounts"]) if seed["amounts"] else None
            tone = rng.choice(sorted(TONES))
            channel = rng.choice(CHANNELS)
            typo = rng.random() < 0.3
            text = seed["template"].format(account=account, amount=amount)
            text = apply_channel(apply_tone(text, tone, account), channel)
            if typo:
                text = add_typo(text, rng)
            cases.append({"id": f"{seed['id']}-s{i:02d}", "seed": seed["id"], "text": text,
                          "expected": {"intent": seed["intent"], "account": account, "amount": amount},
                          "axes": {"tone": tone, "channel": channel, "typo": typo}})
    return cases


def normalize(text):
    text = re.sub(r"\d+", "#", text.lower())
    text = re.sub(r"[^a-z# ]", " ", text)
    return " ".join(text.split())


def shingles(text, n=3):
    words = normalize(text).split()
    if len(words) < n:
        return {" ".join(words)}
    return {" ".join(words[i:i + n]) for i in range(len(words) - n + 1)}


def jaccard(a, b):
    sa, sb = shingles(a), shingles(b)
    return len(sa & sb) / len(sa | sb) if sa | sb else 1.0


def dedupe(cases, threshold=0.8):
    kept, dropped = [], []
    for c in cases:
        dup = next((k for k in kept if jaccard(c["text"], k["text"]) >= threshold), None)
        if dup:
            dropped.append((c["id"], dup["id"]))
        else:
            kept.append(c)
    return kept, dropped


def decontaminate(cases, held_out, threshold=0.8):
    kept, dropped = [], []
    for c in cases:
        if any(jaccard(c["text"], h) >= threshold for h in held_out):
            dropped.append(c["id"])
        else:
            kept.append(c)
    return kept, dropped


def coverage_gaps(cases):
    intents = sorted({c["expected"]["intent"] for c in cases})
    seen = {(c["expected"]["intent"], c["axes"]["tone"]) for c in cases}
    return [(i, t) for i in intents for t in sorted(TONES) if (i, t) not in seen]


def build_suite(seeds, per_seed, held_out, threshold=0.8):
    cases = generate(seeds, per_seed)
    cases, dupes = dedupe(cases, threshold)
    cases, contaminated = decontaminate(cases, held_out, threshold)
    return {"cases": cases, "dropped_duplicates": dupes, "dropped_contaminated": contaminated,
            "missing_coverage": coverage_gaps(cases)}


# --- Try it out (not graded) ---
suite = build_suite(SEEDS, 6, HELD_OUT)
if suite:
    print(f"{len(suite['cases'])} cases kept; {len(suite['dropped_duplicates'])} near-duplicates and "
          f"{len(suite['dropped_contaminated'])} test-set leaks dropped")
    for c in suite["cases"][:6]:
        print(f"  {c['id']} {c['axes']}  {c['text'][:90]!r}")
    print("missing (intent, tone) combinations:", suite["missing_coverage"])
