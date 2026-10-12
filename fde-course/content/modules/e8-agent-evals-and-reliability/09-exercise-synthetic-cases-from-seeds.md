---
title: "Exercise: Synthetic Cases from Real Seeds"
type: exercise
minutes: 40
hints:
  - "Create one `random.Random(f\"{seed['id']}:{i}\")` per case and draw everything for that case from it. A case then depends only on its seed and its index, so adding a seed or raising `per_seed` never changes existing cases."
  - "Order matters for the labels: fill the template first, so you know the account and amount, then apply the tone (terse needs the account to pick its sentence), then the channel, then the typo."
  - "For terse, `re.split(r\"(?<=[.?!])\\s+\", text)` splits into sentences and keeps the punctuation. Pick the first sentence containing the account. A typo must only touch purely alphabetic words, so slot values like `GN-204117` and `$38` survive."
  - "`normalize` replaces runs of digits with `#` before removing other characters, so two cases that differ only in their account numbers become identical."
  - "`dedupe` is a single pass: compare each case with the cases you've kept so far, not with all cases. `decontaminate` compares each case with every held-out text."
---

Teodora Kessler at Gannet Home Energy (fictional) is planning the eval for a new Home Move agent. "There's no traffic yet: the product isn't live. The support leads gave us eight real messages from the current queue, turned into templates with the account numbers and amounts taken out. I need a few dozen varied cases from them by Friday. They have to be reproducible, labelled correctly, and they must not overlap with the handful of real messages we've already frozen as the test set."

`SEEDS`, `TONES`, `CHANNELS` and `HELD_OUT` are loaded for you. Lesson 08 explains why you vary real seeds instead of asking a model to invent cases from the product description.

## Your task

**1. Perturbations.** Write three small transforms:

- `apply_tone(text, tone, account)`: for `"terse"`, return only the first sentence that contains `account`. Split sentences after `.`, `?` or `!` followed by whitespace. Otherwise return `TONES[tone].format(text=text)`.
- `apply_channel(text, channel)`: `"email"` wraps the text as `"Subject: Moving house\n\nHello,\n\n" + text + "\n\nRegards"`. `"sms"` lowercases it and removes `. , ! ? ; :`. `"chat"` leaves it unchanged.
- `add_typo(text, rng)`: swap two adjacent letters in one randomly chosen word that is purely alphabetic and longer than 4 letters. Return the text unchanged if there is no such word.

**2. `generate(seeds, per_seed)`.** For each seed and each `i` in `range(per_seed)`, use one `rng = random.Random(f"{seed_id}:{i}")` and draw an account (`"GN-"` + six random digits), an amount (one of `seed["amounts"]`, or `None`), a tone (from `sorted(TONES)`), a channel and a typo flag (true about 30% of the time). Fill the template, then apply tone, channel and typo, in that order. Each case is:

```python
{"id": "SD5-s03", "seed": "SD5", "text": "...",
 "expected": {"intent": "refund_balance", "account": "GN-482913", "amount": 38},
 "axes": {"tone": "angry", "channel": "sms", "typo": False}}
```

The tests check properties, not exact strings: the output is deterministic, varied, and every label is still true of its text.

**3. Similarity.** `normalize(text)` lowercases, replaces each run of digits with `#`, turns every other character that isn't `a-z`, `#` or a space into a space, and collapses whitespace. `shingles(text, n=3)` is the set of word 3-grams of the normalized text, or `{whole normalized text}` if it has fewer than 3 words. `jaccard(a, b)` is the size of the shingle intersection over the size of the union.

**4. `dedupe(cases, threshold=0.8)`** keeps a case unless its Jaccard similarity with an already kept case is at least the threshold. Return `(kept, dropped)`, where `dropped` lists `(dropped_id, kept_id)` pairs, using the first kept match.

**5. `decontaminate(cases, held_out, threshold=0.8)`** drops cases that are near-duplicates of any held-out text. Return `(kept, dropped_ids)`.

**6. `coverage_gaps(cases)`** lists the `(intent, tone)` pairs with no case, over the sorted intents present and `sorted(TONES)`.

**7. `build_suite(seeds, per_seed, held_out, threshold=0.8)`** runs generate, dedupe, then decontaminate, and returns `{"cases", "dropped_duplicates", "dropped_contaminated", "missing_coverage"}`.

## Example

```python
>>> jaccard("Please close GN-1, now.", "please CLOSE gn-999 now")
1.0
```

Press **Run** to see the suite, then **Submit**.

## What to notice

- **About one generated case in five is a near-duplicate.** A neutral, plain chat variant of a seed differs from the next one only in its digits. Without deduplication those cases quietly double-weight a few seeds.
- **Two cases would have leaked into the test set.** Synthetic variants of SD3 and SD5 are almost word for word the held-out messages they came from. If you train or tune a prompt on them, your test score measures memory.
- **Labels are only free when transforms preserve them.** The first version of "terse" (keep the first sentence) dropped the account number from SD1. A label you can't verify against the text is a wrong label waiting to happen, which is why the tests check that each slot value appears.
- **Synthetic cases go to a separate slice of the report.** Score them, but report real-seed cases and synthetic cases side by side, and replace synthetic cases with real traffic as soon as the product has some.
