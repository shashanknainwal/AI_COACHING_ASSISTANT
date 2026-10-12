---
title: "Exercise: Rebuild a Grounded Answer on Native Citations"
type: exercise
minutes: 40
hints:
  - "`build_request`: a text document's source is `{\"type\": \"text\", \"media_type\": \"text/plain\", \"data\": ...}`. The doc id goes in `context` (passed to the model, never cited), and the question goes last."
  - "`check_request`: collect every block with `type == \"document\"` across all messages first. Then two questions: are citations on for some but not all? Are they on at all while `output_config` has a `format`?"
  - "`render`: keep a dict from `(doc_id, cited_text)` to its source number, so a repeated quote reuses its number. Build each block's markers in citation order, skipping numbers already added to that block."
  - "`render`: count words with `re.findall(r\"[A-Za-z0-9']+\", text)`. Only blocks with no citations can be uncited claims. Skip blocks whose `type` isn't `\"text\"` (the thinking block)."
  - "`verify`: `document_index` points into the list of documents you sent, in the order you sent them. Slice the source text with the start and end indices (end is exclusive) and compare after `strip()`."
---

Leo again. Tallowmere's order desk wants an assistant that answers staff questions about returns, warranty and freight from the policy documents. Last quarter a contractor built one with the bracket-ID scheme you know from E3, and it worked until someone re-sorted the retrieval results before rendering: every footnote pointed at the wrong policy for a week. Imani's ask is simple: "Use the API's own citations, and show me the answer can't point at the wrong document without us knowing."

The simulated Claude behaves like the real Citations API. Its response is a list of text blocks; blocks that make a sourced claim have a `citations` list of `char_location` objects (`cited_text`, `document_index`, `document_title`, `start_char_index`, `end_char_index`). Read them with attribute access, as with the real SDK. Some answers include a claim with no citation.

## Given

`POLICY_DOCS`, `search(question, k=3)` (returns up to `k` docs `{"id", "title", "text"}`, best first, or `[]`), `client`, `MODEL`, `MAX_TOKENS`, `MIN_UNCITED_WORDS = 6`, `INSUFFICIENT` and `REFUSAL_MESSAGE`.

## Your task

**1. `build_request(question, docs)`** returns keyword arguments for `client.messages.create`: `model`, `max_tokens`, `output_config={"effort": "low"}`, and one user message containing one document block per doc, in order, followed by `{"type": "text", "text": question}`. Each document block:

```python
{"type": "document",
 "source": {"type": "text", "media_type": "text/plain", "data": doc["text"]},
 "title": doc["title"],
 "context": f"doc_id={doc['id']}",
 "citations": {"enabled": True}}
```

**2. `check_request(params)`** raises `ValueError` when the API would reject the request for its citation settings, and returns `None` otherwise:

- citations enabled on some document blocks but not all (across every message), or
- citations enabled and `output_config` contains `"format"`.

**3. `render(response, docs)`** returns `{"answer", "sources", "uncited"}`:

- `answer`: the text blocks concatenated in order. After each block that has citations, append its markers, such as `[1]` or `[3][1]`.
- Sources are numbered from 1 in order of first appearance. A source is the pair `(doc_id, cited_text)`, where `doc_id = docs[c.document_index]["id"]`. A repeated pair reuses its number, and a block never shows the same marker twice.
- `sources`: `[{"n", "doc_id", "title", "quote"}]` in number order; `quote` is the `cited_text`.
- `uncited`: for each text block **without** citations that has at least `MIN_UNCITED_WORDS` words, its text with surrounding whitespace stripped.

**4. `verify(response, docs)`** returns a list of problems, one per bad citation, as `{"block": i, "kind": ...}` where `i` is the block's index in `response.content`:

- `"bad_index"`: `document_index` isn't a valid index into `docs`.
- `"text_mismatch"`: `docs[idx]["text"][start:end].strip() != cited_text.strip()`.

Check only `char_location` citations.

**5. `answer(client, question)`** returns `{"status", "answer", "sources", "uncited", "problems"}`:

- `search` returns nothing: status `"no_sources"`, answer `INSUFFICIENT`, and **don't call Claude**.
- Build the request, run `check_request`, call Claude once.
- `stop_reason == "refusal"`: status `"refusal"`, answer `REFUSAL_MESSAGE`.
- Otherwise render and verify against the **same** `docs` list you sent. Status is `"needs_review"` if there are uncited claims or problems, else `"answered"`. Empty lists for anything not computed.

## What changed from the ID scheme

You never parse brackets, and you never check that a quote exists: the API extracted it. What you still own:

- **Coverage.** The restocking answer ends with an uncited sentence about refund timing. Nothing in the API stops that. Your `uncited` check does.
- **Your own pipeline.** `document_index` is a position in the list you sent. If you re-sort or filter that list before rendering, every footnote shifts. `verify` turns that bug into a visible problem instead of a quiet wrong answer.
- **Support.** A valid citation proves the quote is in the document, not that it backs the claim. That belongs in your eval set, with a judge or human labels (E4).

And one thing you gave up: no `output_config.format` in the same request. If the order desk also needs JSON fields from the same question, make a second call.

## Example

```python
>>> r = answer(client, "Can a customer return cable that was cut to length?")
>>> r["answer"]
"Cut-to-length cable can't be returned unless it has a manufacturing fault[1]. If it is faulty, report it within 14 days of delivery with photos[2]."
>>> r["sources"][0]["doc_id"], r["status"]
('POL-RET-07', 'answered')
```

Press **Run** to see all four questions answered, then **Submit**.
