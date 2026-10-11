---
title: "Exercise: A Citation-Grounding Checker"
type: exercise
minutes: 35
hints:
  - "`split_sentences`: `re.split(r\"(?<=[.!?])\\s+\", text)` splits only where punctuation is followed by whitespace, so `4.5` survives. Strip each piece and drop empty ones."
  - "Citations: `re.findall(r\"\\[(\\d+)\\]\", sentence)` gives the numbers as strings. Convert to int and skip duplicates while keeping order."
  - "Content words: `re.findall(r\"[a-z0-9]+\", text.lower())`, minus `STOPWORDS`, as a set. Remove the `[n]` markers from the claim first. Overlap is |claim words that appear in the cited spans| / |claim words|."
  - "Numbers: `re.findall(r\"\\d+(?:[.,]\\d+)*\", text)` on the claim and on the joined cited spans. Every claim number must appear in the spans, or the claim is unsupported."
  - "Check in this order: no citations -> uncited; any citation not in spans -> bad_citation; then numbers and overlap decide supported or unsupported."
---

In Mira Vasquez's fundamentals round (she's this module's fictional interviewer), the hallucination question ends with: "Fine. You said you'd verify citations in code. Write it." This exercise is that code.

The setting is a support assistant for Quillmark Outfitters, a fictional retailer. Retrieval returned three policy spans, and the model wrote an answer with a citation after each claim. Some claims are real. Some cite a real span that doesn't say what the claim says. One changes a number. One cites a span that was never retrieved. Your checker flags each one before a customer sees it.

Word overlap is a deliberately simple, deterministic first line of defence. It catches invented facts and changed numbers cheaply. It misses well-paraphrased support, which is where an LLM faithfulness judge comes in (lesson 12).

## Your task

**1. `split_sentences(text)`** splits after `.`, `!` or `?` followed by whitespace, strips each piece and drops empty ones.

**2. `check_claim(sentence, spans, threshold=0.6)`** returns:

```python
{"sentence": sentence, "citations": [1, 2], "status": "supported", "overlap": 0.88}
```

- `citations`: the numbers in `[n]` markers, as ints, each listed once, in order of appearance.
- `status`, checked in this order:
  1. `"uncited"` if there are no citations (overlap `0.0`);
  2. `"bad_citation"` if any citation isn't a key of `spans` (overlap `0.0`);
  3. otherwise compare the claim (with the `[n]` markers removed) against **all cited spans joined together**:
     - content words = lowercase `[a-z0-9]+` words not in `STOPWORDS`;
     - `overlap` = share of the claim's content words that appear in the spans' content words, rounded to 2 (1.0 if the claim has no content words);
     - every number in the claim (`\d+(?:[.,]\d+)*`) must also appear in the spans;
     - `"supported"` if the numbers check passes and `overlap >= threshold`, else `"unsupported"`.

**3. `grounding_report(answer, spans, threshold=0.6)`** checks every sentence and returns:

```python
{"claims": [...], "supported": 3, "total": 7, "grounded_ratio": 0.43, "flagged": ["Return shipping is free ...", ...]}
```

`grounded_ratio` is `supported / total` rounded to 2, or `0.0` when there are no sentences. `flagged` lists every sentence that isn't `"supported"`, in order.

## Example

```text
supported     0.88  You can return unworn items within 30 days of delivery for a full refund [1].
supported     1.00  Refunds are issued within 5 business days after the item reaches the warehouse [2].
supported     1.00  Final sale items cannot be returned [3].
unsupported   0.00  Return shipping is free for loyalty members [2].
unsupported   0.38  Refunds for orders over $200 take 10 business days [2].
uncited       0.00  Exchanges are processed the same day.
bad_citation  0.00  Gift cards are refunded as store credit [4].
grounded ratio: 0.43
```

Press **Run** to print this table, then **Submit**.

## After you pass: the design answer

Say what you'd do with the flags in production: block the answer and regenerate with the flagged claims named, or strip unsupported sentences and show the rest with sources, and log every flag so the weekly faithfulness rate is a number, not an anecdote.

> **Interview tip:** Name the checker's blind spots before the interviewer does: paraphrase lowers overlap on true claims, and negation ("can" versus "cannot") barely moves it. That's why the deterministic check is the first layer, with a calibrated judge behind it.
