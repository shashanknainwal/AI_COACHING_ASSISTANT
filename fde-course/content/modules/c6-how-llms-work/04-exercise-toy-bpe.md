---
title: "Exercise: Build a Toy BPE Tokenizer"
type: exercise
minutes: 40
hints:
  - "Start every function from bytes: `list(text.encode(\"utf-8\"))` gives integers 0 to 255. Write a helper `_merge(ids, pair, new_id)` that scans left to right and replaces each non-overlapping occurrence of the pair."
  - "`learn_merges`: in each round, count pairs with `zip(ids, ids[1:])` into a plain dict. `max(counts, key=counts.get)` returns the first pair it saw among the ties, which is exactly the tie rule. Stop early if the best count is below 2."
  - "`encode`: convert to bytes, then call `_merge` once per learned merge, in order. Don't re-learn anything."
  - "`decode`: build `vocab = {i: bytes([i]) for i in range(256)}`, then for each merge `vocab[new_id] = vocab[a] + vocab[b]`. Join the bytes and `.decode(\"utf-8\", errors=\"replace\")`."
---

Mira Vasquez, the module's fictional fundamentals interviewer, likes one question because it can't be bluffed: "Implement a tiny BPE tokenizer. Then tell me why our Hindi customers cost more." You'll do both. The first part is the classic algorithm. The second part turns it into the cost argument you'd make in a design round.

The tokenizer you build is trained only on a short English text, so it exaggerates the skew a real multilingual tokenizer would show. That's the point: you'll see the mechanism clearly.

## Your task

Work on **UTF-8 bytes**: `list(text.encode("utf-8"))`. Base ids are 0 to 255; each new merged token gets the next id, starting at 256.

**1. `learn_merges(text, num_merges)`** returns a list of `((a, b), new_id)` in the order learned. Each round:

- count every adjacent pair in the current sequence;
- pick the most frequent pair. **Ties go to the pair that appears first** in the current sequence;
- if its count is below 2, stop early;
- replace every non-overlapping occurrence, scanning left to right, with `256 + round_number`.

**2. `encode(text, merges)`** turns text into bytes, then replays each merge in order. Returns a list of ints.

**3. `decode(ids, merges)`** maps ids back to bytes and decodes UTF-8 (use `errors="replace"`).

**4. `compare(samples, merges)`** returns, for each name in `samples`:

```python
{"chars": len(text), "tokens": len(encode(text, merges)), "tokens_per_char": round(tokens / chars, 2)}
```

`TRAINING_TEXT` and `SAMPLES` (English, Python code and Hindi) are given at the top of the file.

## Example

```python
learn_merges("aaabdaaabac", 10)
# [((97, 97), 256), ((256, 97), 257), ((257, 98), 258)]   then no pair appears twice
encode("aaabdaaabac", _)   # [258, 100, 258, 97, 99]

merges = learn_merges(TRAINING_TEXT, 150)
compare(SAMPLES, merges)
# english  ~0.5 tokens per char
# code     ~0.7 tokens per char
# hindi    ~2.6 tokens per char   (each Devanagari character is 3 bytes, and no merges cover them)
```

Press **Run** to see the table, then **Submit**.

## After you pass: say the cost argument

Write two sentences you could say in an interview: why Hindi costs more here, and what changes with a real tokenizer. A strong version: "The merges come from the training corpus, so scripts that are rare there stay close to one token per byte, and Devanagari is 3 bytes a character. Production tokenizers train on many languages so the gap is smaller, but it doesn't vanish, so I'd measure real traffic per language with the provider's token counter and price each market separately."

> **Interview tip:** If you're asked to code BPE live, say the tie-break rule and the stopping rule out loud before you start. Most bugs in this problem are an unclear tie or merging overlapping pairs like "aaa".
