---
title: "Exercise: Grounded Answers With Verified Citations"
type: exercise
minutes: 40
hints:
  - "`format_documents`: build a list of lines. For each doc, `enumerate(docs, 1)` and add `<document index=\"{i}\">`, `<source>{id}</source>`, `<document_content>`, the text, `</document_content>`, `</document>`. Join with `\"\\n\"`."
  - "`parse_citations`: split with `re.split(r\"(?<=[.!?])\\s+\", text.strip())`. For each piece, first peel off any citations at the very start (`re.match(r\"(\\s*\\[[A-Z]+-\\d+\\])+\", piece)`) and add them to the previous claim. Then `CITATION.findall(piece)` gives the ids and `re.sub(r\"\\s*\\[[A-Z]+-\\d+\\]\", \"\", piece).strip()` gives the sentence."
  - "`validate`: `uncited` is every sentence whose `ids` is empty. For `unknown_ids`, walk the claims in order and append each id that isn't in `retrieved_ids` and isn't already in the list."
  - "`answer_question`: return the insufficient dict with `attempts: 0` before calling Claude when `search` returns nothing. Then loop `for attempt in range(1, MAX_ATTEMPTS + 1)`, joining the text blocks of each response."
  - "On a failed check before the last attempt, extend the conversation: `messages + [{\"role\": \"assistant\", \"content\": text}, {\"role\": \"user\", \"content\": feedback_message(report)}]`. After the loop, return `flagged` with the last text, its cited ids and the last report's `uncited` and `unknown_ids`."
---

**Kestrel Benefits** (fictional) runs benefits for mid-sized employers. Their employee assistant answers questions like "How long is paid parental leave?" from plan documents. Their legal team has one non-negotiable rule: **every sentence the assistant shows must point to the plan document that supports it.** Last month the pilot told an employee they could "split the leave into two blocks" and cited a document that was never retrieved. Nobody noticed until HR did.

Leo's brief: "Prompting Claude to cite is step one. Step two is code that refuses to trust the citations. I want a pipeline where an invented source or an unsupported sentence can't reach an employee without a flag."

Available to your code: `PLAN_DOCS`, and `search(question, k=3)`, which returns up to `k` chunks `{"id", "title", "text"}`, best first. `MODEL`, `MAX_ATTEMPTS = 2`, `INSUFFICIENT` and `SYSTEM_PROMPT` are given. Read the system prompt: it asks for citations in square brackets before each sentence's period, like `Cleanings are covered [BEN-03].`

## Your task

**1. `format_documents(docs)`** returns (lines joined with `"\n"`):

```
<documents>
<document index="1">
<source>BEN-03</source>
<document_content>
The plan covers two dental cleanings per year at no cost. ...
</document_content>
</document>
</documents>
```

**2. `build_user_message(question, docs)`** returns `format_documents(docs)`, a blank line, then `<question>`, the question and `</question>` on their own lines. Documents first, question last.

**3. `parse_citations(text)`** returns one `{"sentence", "ids"}` per sentence:

- Split sentences where `.`, `!` or `?` is followed by whitespace.
- `ids` are the `[ABC-12]` tags in that sentence, in order. `sentence` is the text with the tags (and the space before each) removed, stripped.
- Models don't always follow the format. A citation written **after** the period (`cost $10. [BEN-02] Next...`) belongs to the sentence **before** it.

**4. `validate(claims, retrieved_ids)`** returns `{"ok", "uncited", "unknown_ids"}`: the sentences with no citation, and the cited ids that weren't retrieved (each once, in order of first appearance). `ok` is True only when both lists are empty.

**5. `feedback_message(report)`** returns these lines joined with `"\n"`: the header, one line per problem, then the instruction:

```
Your previous answer failed the citation check.
- No citation: <sentence>
- Not in the documents: <id>
Rewrite the answer using only the documents above. End every sentence with the id of a document that supports it. If the documents don't answer the question, reply with exactly INSUFFICIENT_CONTEXT.
```

**6. `answer_question(client, question, k=3)`**:

1. `docs = search(question, k)`. If it's empty, return `insufficient` with `attempts: 0` **without calling Claude**.
2. Call `client.messages.create` with `model=MODEL`, `max_tokens` ≥ 1024, `system=SYSTEM_PROMPT` and one user message, `build_user_message(question, docs)`.
3. Join the text blocks. If the text is exactly `INSUFFICIENT_CONTEXT`, return `insufficient`.
4. Parse and validate against the retrieved ids. If it passes, return `answered`.
5. If it fails and you have attempts left, append the answer as an `assistant` turn and `feedback_message(report)` as a `user` turn, and call again. After `MAX_ATTEMPTS` failures, return `flagged`.

Every return value has the same shape:

```python
{"status": "answered" | "insufficient" | "flagged",
 "answer": text or None,          # None when insufficient
 "citations": ["BEN-05", ...],    # unique ids cited in the final text, first-appearance order
 "attempts": 1,                   # calls made
 "problems": None}                # flagged only: {"uncited": [...], "unknown_ids": [...]}
```

## Why it's built this way

- **Indexed documents with a `<source>` tag** follow the structure Anthropic's prompting guidance suggests for long documents. The id in `<source>` is what Claude cites, and it is what your validator checks.
- **Retry once, with specific feedback, then flag.** One retry fixes most format slips cheaply. A second failure is a signal, not bad luck: show the employee a fallback and route the question to a human or a review queue.
- **A flag is not a fix.** The validator proves a cited id was retrieved. It does not prove the document supports the sentence. That needs a groundedness check (an LLM judge or a human sample), which is measured in lesson 4 and in E4.
- **Built-in alternative.** The Messages API has a citations feature: send documents as `document` content blocks with citations enabled, and the response carries the exact passages each claim relies on. It can't be combined with structured outputs (the API returns a 400), which is one reason teams sometimes keep an ID-based scheme like this one.

Press **Run** to see one clean answer, one fixed on retry, one flagged, and two insufficient. Then **Submit**.

> **Interview angle.** In the style of a deep-dive question: "How do you know your RAG system isn't hallucinating?" Weak answer: "the prompt tells it to only use the documents." Strong answer: layered checks. Retrieval recall measured offline; citations required and verified in code; unsupported or uncited sentences flagged; a groundedness judge on a sample; abstention tested with questions the corpus can't answer; and a metric for each in production.
