---
title: "Exercise: Help-Center Answers with Citations"
type: exercise
minutes: 40
hints:
  - "`chunk_articles`: split each article's text on `\"\\n\\n\"`, strip each paragraph, skip empty ones, and number from 1 with `enumerate(paragraphs, 1)`."
  - "`tokenize`: `re.findall(r\"[a-z0-9]+\", text.lower())`, skip words in `STOPWORDS`, and use `word[:-1]` when `len(word) > 3 and word.endswith(\"s\")`."
  - "`build_index`: tokenize `title + \" \" + text` into a set per chunk, count in how many sets each token appears (`df`), then `idf[t] = math.log(1 + n / df[t])`."
  - "`search`: `terms = set(tokenize(query))`; a chunk's score is `sum(idf[t] for t in terms & tokens)`. Keep scores > 0 as `dict(chunk, score=round(score, 3))`, sort by `-score` (Python's sort is stable, so ties keep their order), and slice `[:k]`."
  - "`answer`: if `search` returns nothing, return the NO_ANSWER dict straight away. Otherwise parse the JSON text block, keep citations that are in the retrieved IDs, and return NO_ANSWER if `answerable` is false or no valid citation is left."
---

Brightway's help center has eight articles. Customers ask the same questions every day, and the support team wants instant answers that link to the policy they came from. You'll build the whole retrieval-augmented generation (RAG) pipeline: chunking, a keyword index, search, a grounded prompt, structured answers, and citation checks.

The articles are in `brightway.KB_ARTICLES` (a list of `{"id", "title", "text"}`).

## Your task

**1. `chunk_articles(articles)`** returns one chunk per paragraph (paragraphs are separated by a blank line, `"\n\n"`): `{"id": "KB-01#1", "title": "Returns policy", "text": "..."}`. Strip whitespace, skip empty paragraphs, number from 1 within each article.

**2. `tokenize(text)`** returns the lowercase words and numbers (`[a-z0-9]+`), minus `STOPWORDS`. Words longer than 3 letters lose a trailing `s` (a crude stemmer: `sofas` → `sofa`, `days` → `day`).

**3. `build_index(chunks)`** returns `{"chunks": chunks, "tokens": [...], "idf": {...}}`:
- `tokens[i]` is the **set** of tokens in chunk `i`'s title plus text.
- `idf[t] = math.log(1 + N / df)`, where `N` is the number of chunks and `df` is how many chunks contain `t`. Rare words get high weights; common words get low weights.

**4. `search(index, query, k=3)`** scores each chunk as the sum of `idf` for the query tokens it contains. It returns up to `k` chunks with a score above 0, highest first (ties keep index order). Each result is a **copy** of the chunk plus `"score"` rounded to 3 decimals.

**5. `build_prompt(question, results)`** returns (lines joined with `"\n"`):

```
<documents>
<document id="KB-01#2" title="Returns policy">
Large furniture such as sofas ...
</document>
</documents>

<question>
Can I return a sofa?
</question>
```

**6. `ANSWER_SCHEMA`**: `answer` (string), `citations` (array of strings), `answerable` (boolean), all required, no extra properties.

**7. `answer(client, index, question)`**:
1. Search. If nothing is retrieved, return `{"answer": NO_ANSWER, "citations": [], "answerable": False}` **without calling Claude**.
2. Call Claude with `model=MODEL`, `max_tokens` ≥ 1024, `system=SYSTEM_PROMPT`, one user message `build_prompt(question, results)`, and `output_config={"format": {"type": "json_schema", "schema": ANSWER_SCHEMA}}`.
3. Parse the JSON. Keep only citations that match a **retrieved** chunk ID.
4. If Claude said `answerable: false`, or no valid citation is left, return the NO_ANSWER dict. Otherwise return `{"answer", "citations", "answerable": True}`.

Press **Run** to try four questions (one answered from two chunks, one the documents don't cover, one with nothing to retrieve), then **Submit**.
