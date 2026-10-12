---
title: "Native Citations: What the API Guarantees"
type: reading
minutes: 15
---

> **By the end of this lesson** you'll be able to turn on the Citations API, read the citation objects it returns for text, PDF and custom-content documents, say exactly what it guarantees and what it doesn't, and choose between native citations and a home-made ID scheme, including when you also need structured output.

## The problem it solves

In E3 you built grounded answers by asking Claude to write source IDs in brackets, then wrote code to check every ID. That works, and it taught you not to trust citations blindly. But the model *generates* those IDs and any quotes, so your validator has to catch invented sources and paraphrased "quotes".

Native citations move that work into the API. You mark documents as citable, and the response comes back as text blocks with structured pointers into your documents. The quoted text in each pointer is **extracted from your document by the API**, not written by the model.

## Turning it on

```python
response = client.messages.create(
    model="claude-sonnet-5-5",
    max_tokens=2000,
    output_config={"effort": "low"},          # no "format" here: see the conflict below
    messages=[{
        "role": "user",
        "content": [
            {"type": "document",
             "source": {"type": "text", "media_type": "text/plain", "data": returns_policy_text},
             "title": "Returns policy v7",
             "context": "doc_id=POL-RET-07; owner=Order Ops",   # passed to the model, never cited
             "citations": {"enabled": True}},
            {"type": "text", "text": "Can a customer return cable that was cut to length?"},
        ],
    }],
)
```

Rules from the docs (Official, Citations page, checked 2026-10-11):

- Set `citations.enabled` on **every** document in the request or on none. Mixing returns an error.
- Only text can be cited. Image citations aren't supported, so a **scanned PDF with no extractable text isn't citable**, and neither is a photo.
- `title` and `context` are given to the model but are never cited from. `context` is a good place for your own document ID or metadata.
- Supported on all active models, and on the Claude API, Claude Platform on AWS, Bedrock, Google Cloud and Foundry.

## Three document types, three pointer formats

| Document type | Chunking | Citation object `type` | Location fields |
|---|---|---|---|
| Plain text | Sentences | `char_location` | `start_char_index`, `end_char_index` (0-indexed, end exclusive) |
| PDF | Sentences of the extracted text | `page_location` | `start_page_number`, `end_page_number` (1-indexed, end exclusive) |
| Custom content | None: your blocks are the units | `content_block_location` | `start_block_index`, `end_block_index` (0-indexed, end exclusive) |

Every citation also carries `cited_text`, `document_index` (0-indexed across **all** document blocks in the request, in order, across messages) and `document_title`.

**Custom content** documents (`source: {"type": "content", "content": [{"type": "text", "text": ...}, ...]}`) are the one to remember for RAG. If each retrieved chunk or each record is one block, Claude can only cite whole blocks, and the block index maps straight back to your chunk ID. Use plain text documents instead when you want sentence-level quotes.

## What the response looks like

The answer is split into several text blocks. Blocks that make a sourced claim carry a `citations` list:

```json
{"content": [
  {"type": "text", "text": "Cut-to-length cable "},
  {"type": "text", "text": "can't be returned unless it is faulty",
   "citations": [{"type": "char_location",
                  "cited_text": "Cable cut to customer length is non-returnable except for manufacturing faults.",
                  "document_index": 0, "document_title": "Returns policy v7",
                  "start_char_index": 412, "end_char_index": 491}]},
  {"type": "text", "text": ". Restocking is free for unopened stock items."}
]}
```

Read that last block carefully. It's a claim with **no citation**. Nothing in the API forces every sentence to be cited. Your renderer has to notice.

When streaming, each citation arrives as a `citations_delta` inside a `content_block_delta` event and is appended to the current text block's list. Lesson 5 covers the event stream.

## What's guaranteed, and what isn't

| Property | Native citations | Your own ID scheme (E3) |
|---|---|---|
| Pointer refers to a real document you sent | **Guaranteed** (Official: "guaranteed to contain valid pointers to the provided documents") | You must validate every ID |
| Quoted text really is in the source | **Yes**: `cited_text` is extracted, not generated | Only if you check the quote |
| Every claim carries a citation | **No**. Uncited text blocks are normal | No, unless you enforce it |
| The cited text actually supports the claim | **No**. It's the most relevant passage the model chose, not proof of entailment | No |
| Works with structured outputs | **No** (400 error, see below) | Yes |
| Cites images or scanned pages | No | Only if you OCR first and cite the OCR text |
| Output cost of quotes | `cited_text` doesn't count toward output tokens, and isn't counted as input when you send it back in later turns | Every quoted character is output you pay for |
| Input cost | Slightly higher: system additions and chunking | Your tags and IDs |

Anthropic also reports that in its evaluations the feature picks more relevant quotes than prompt-based citing (Official, vendor evaluation; measure on your own data). The two guarantees that matter for an FDE conversation are the first two. The two gaps that matter are "uncited claims exist" and "a citation isn't proof". Your code still checks coverage, and your eval still measures support.

## The conflict with structured outputs

If any document has citations enabled and the request also sets `output_config.format` (or the deprecated `output_format`), the API returns a **400**. Citations interleave pointers with text blocks, which can't satisfy a strict JSON schema. That's why the purchase-order extraction in the last exercise asked for `page` and `quote` fields in its own schema instead.

Ways through it, in rough order of preference:

1. **Split the jobs.** A cited prose answer for the human, and a separate structured call for the machine-readable fields. Feed the second call the first call's text if it needs it.
2. **Custom content with one block per record**, and no structured output: the block index becomes your record ID, and you build the JSON yourself from the citations.
3. **Keep the ID or quote scheme** where you truly need one schema-valid object with evidence per field, and validate quotes against the source yourself (exactly what you did for the purchase orders).

## Costs and caching

Citations work with prompt caching, token counting and the Message Batches API. The citation blocks in a response can't be cached, but the source documents can: put `cache_control` on the top-level document blocks. A practical consequence for a support assistant: the policy corpus is cached once, every question pays cache-read rates on it, and quotes in answers cost no output tokens.

## How this comes up in interviews

Grounding is a standard follow-up in RAG design rounds (Reported, see E3 and E6). A strong answer distinguishes "the pointer is valid" from "the claim is supported", and says how each is measured. Practice prompts in the style of those rounds:

- "Your legal customer wants every sentence traceable to a clause. Would you use native citations or your own scheme? What would you still have to check in code?"
- "You need both a cited answer and a JSON object of extracted fields from the same contract. How do you design the calls?"

> **Key takeaways**
>
> - Enable citations on every document or none. Only text is citable: no images, no scanned pages without a text layer.
> - Text documents cite character ranges, PDFs cite pages (1-indexed), custom content cites your own blocks. `document_index` counts all documents in request order.
> - Guaranteed: pointers are valid and `cited_text` is extracted from your source. Not guaranteed: every claim is cited, or the cited text supports the claim.
> - `cited_text` costs no output tokens. Input rises slightly. Cache the documents, not the citations.
> - Citations plus `output_config.format` is a 400. Split the calls, use custom-content blocks as IDs, or keep a validated ID scheme.
