---
title: "Tokenization: How Text Becomes Tokens"
type: reading
minutes: 15
---

> **By the end of this lesson** you'll be able to explain byte-pair encoding (BPE), say why the same meaning costs more tokens in some languages and in code, and explain why token counts change between model generations.

## Why interviewers ask about it

Tokenization explains a surprising number of production puzzles: why a Hindi-language support bot costs more than the English one, why a model miscounts letters in a word, why a migration changed the bill with no traffic change. Some candidates describe tokenization coming up in domain or coding questions for applied roles (**Anecdotal**). Even when it isn't asked directly, it's the "why" behind cost questions in every design round.

## From text to integers

A model can't read characters. It reads integers from a fixed **vocabulary**, typically tens of thousands to a few hundred thousand entries. A **tokenizer** maps text to those integers and back. Three designs you should be able to compare:

| Approach | Vocabulary | Problem |
|---|---|---|
| One token per word | Huge, and still misses new words, typos, names | Unknown words have no token |
| One token per character or byte | Tiny | Sequences get very long, so attention and cost blow up |
| **Subword (BPE and relatives)** | Medium | A compromise: common words are one token, rare words split into pieces |

Most current LLMs use a subword scheme. Many work on **bytes** rather than characters, so any string, in any script, can be encoded: in the worst case, one token per byte.

## Byte-pair encoding in five steps

BPE was adapted for neural models in ["Neural Machine Translation of Rare Words with Subword Units"](https://arxiv.org/abs/1508.07909) (Sennrich et al., 2016). The training algorithm is short enough to code in an interview:

1. Start with the training text as a sequence of base symbols (here, UTF-8 bytes, ids 0 to 255).
2. Count every adjacent pair of symbols.
3. Take the most frequent pair, give it a new id (256, 257, ...) and replace every occurrence.
4. Repeat until you've done the number of merges you want, or no pair appears twice.
5. Save the ordered list of merges. That list is the tokenizer.

To **encode** new text, convert it to bytes and replay the merges in the order they were learned. To **decode**, expand each id back into its bytes and decode as UTF-8.

```text
"aaabdaaabac"  bytes: a a a b d a a a b a c
merge 1 (a,a)   -> X : X a b d X a b a c
merge 2 (X,a)   -> Y : Y b d Y b a c
merge 3 (Y,b)   -> Z : Z d Z a c        11 symbols became 5
```

Production tokenizers add details you can mention without implementing: they pre-split text on spaces and punctuation so merges don't cross word boundaries, they add special tokens (for roles, tool calls and end of turn), and their training corpus decides which merges exist.

## Why costs skew by language and content

The merges come from the training corpus. Whatever is common there gets long, efficient tokens. Whatever is rare stays in small pieces.

- **Non-Latin scripts.** A Devanagari or Thai character takes 3 bytes in UTF-8. If the corpus has relatively little of that script, few merges cover it, and a sentence can need several times more tokens than its English equivalent. Same meaning, higher bill, more context used, slower output.
- **Code.** Indentation, brackets, identifiers in `snake_case` and long numbers tokenize differently from prose. Whitespace-heavy code can be token-hungry.
- **Numbers and spelling.** Digits are often grouped in odd chunks, and words aren't seen letter by letter. That's one reason models historically stumbled on "how many r's in strawberry" or long arithmetic, and why you hand exact arithmetic to code or a tool.

You'll measure all three in the next exercise with a toy BPE trained only on English. The skew is exaggerated compared with a real tokenizer trained on many languages, but the mechanism is the same.

## Tokenizers change between generations

A tokenizer belongs to a model family. When a provider trains a new generation, it may ship a new tokenizer. Anthropic's migration guidance says the tokenizer introduced with Claude Opus 4.7 and used by newer models produces roughly 30% more tokens for the same text than older models (it varies by content, roughly 1x to 1.35x). The practical consequences:

- **Cost baselines shift** even at a lower per-token price, in either direction.
- **Limits shift.** A `max_tokens` value tuned on an older model can truncate equivalent output. A context budget holds less text.
- **Measure per model.** The Claude API's token-counting endpoint (`POST /v1/messages/count_tokens`, `client.messages.count_tokens(...)` in the Python SDK) takes the model ID, so you count with the exact tokenizer you'll be billed on. Another vendor's tokenizer library gives the wrong count for Claude, often badly on code and non-English text.

```python
# Illustrative: Anthropic Python SDK
count = client.messages.count_tokens(
    model="claude-sonnet-5-5",
    messages=[{"role": "user", "content": hindi_ticket}],
)
print(count.input_tokens)
```

## Practice (say it out loud)

- "Our Japanese and Hindi customers cost about three times more per conversation than English ones, at the same message lengths. Why, and what would you do?"
- "We migrated models and our token usage went up 25% with identical traffic. Is something broken?"
- "Walk me through how a BPE tokenizer is trained. Then write `encode`."

> **Key takeaways**
>
> - Tokenizers map text to integer ids. Subword schemes like BPE balance vocabulary size against sequence length.
> - BPE training repeatedly merges the most frequent adjacent pair. Encoding replays the merges in order; decoding expands ids back to bytes.
> - Whatever is rare in the tokenizer's training corpus costs more tokens: many non-Latin scripts, some code, odd numbers.
> - Token counts change between model generations (about 30% more on Claude's newer tokenizer). Re-measure with `count_tokens` on the model you'll use.
