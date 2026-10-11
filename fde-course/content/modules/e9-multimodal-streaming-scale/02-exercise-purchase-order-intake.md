---
title: "Exercise: Purchase-Order Intake with an Abstain Path"
type: exercise
minutes: 45
hints:
  - "`route`: apply the table top to bottom and return as soon as a rule fires. Start from one dict with all six keys so every return has the same shape."
  - "`estimate_image_tokens`: the scale factor is `min(1, 2576 / long_edge)`. Round the scaled width and height, then `ceil(w / 28) * ceil(h / 28)`, then cap at 4,784. Check yourself against 3840 x 2160, which should give exactly 4,784."
  - "`build_request`: only two things vary between a PDF and a photo: the block `type` and the `source`. A `file` source has just `type` and `file_id`; a `base64` source has `type`, `media_type` and `data`."
  - "`validate_line`: order matters. No evidence, then unknown SKU, then (for citable documents) the quote-on-page and quote-contains-SKU checks, and only then the comparison with ERP. Normalise with `' '.join(s.split()).lower()` before any substring check."
  - "`process_inbox`: check `stop_reason` before you parse anything. A `max_tokens` reply holds half a JSON object and a refusal holds none; both go to review without touching `json.loads`."
---

Leo Martins here. Tallowmere Industrial Supply (fictional) wants its order desk to stop retyping purchase orders. Imani Ferrowell, their VP of Order Operations (also fictional), put it plainly on our call: "I'll take a system that says 'I'm not sure' twenty times a day. I won't take one that keys the wrong cable length once." Your job is the intake: decide how each file goes to Claude, extract the lines, and refuse to trust any line you can't back up.

The inbox has eight files: an ERP-exported PDF, a phone photo, a scan with no text layer, a locked PDF, a Word file, an iPhone HEIC photo, a 41 MB PDF with a catalog attached, and an 812-page archive. The simulated Claude returns the extraction as JSON (it was asked for `output_config.format`), with a page number and a verbatim quote for every line. Some quotes are wrong.

## Given

`INBOX` (each document has `doc_id`, `filename`, `media_type`, `size_bytes`, `data`, plus `pages`, `text_layer`, `encrypted` and `page_text` for PDFs, and `width` and `height` for images), `ERP_OPEN_POS` (`{po_number: {sku: {"qty", "unit_price"}}}`), `upload(doc)` (stands in for `client.files.upload` and returns a `file_id`), `client`, `MODEL`, `MAX_TOKENS`, `INSTRUCTIONS`, `EXTRACTION_SCHEMA`, and the limit constants named below.

## Your task

**1. `route(doc)`** returns `{"action", "block", "source", "citable", "est_visual_tokens", "reason"}`. Apply the first matching rule:

| Rule | action | reason |
|---|---|---|
| Not a PDF and not in `IMAGE_TYPES` | `"reject"` | `"unsupported_type"` |
| PDF with `encrypted` true | `"reject"` | `"encrypted"` |
| PDF with more than `MAX_PDF_PAGES` pages | `"split"` | `"too_many_pages"` |
| Image with a side over `MAX_IMAGE_EDGE` or over `MAX_IMAGE_BYTES` | `"reject"` | `"image_too_large"` |
| Anything else | `"extract"` | `None` |

For `"extract"`: `block` is `"document"` for a PDF or `"image"`; `source` is `"file"` when `size_bytes > INLINE_LIMIT_BYTES`, else `"base64"`; `citable` is true only for a PDF with a text layer; `est_visual_tokens` is `estimate_image_tokens(width, height)` for images and `None` for PDFs. Non-extract results keep `block`, `source` and `est_visual_tokens` as `None` and `citable` false.

**2. `estimate_image_tokens(width, height)`**: downscale (keeping the aspect ratio) so the long edge is at most `HIRES_LONG_EDGE`, round both sides, compute `ceil(w / 28) * ceil(h / 28)`, and cap at `HIRES_MAX_TOKENS`. This reproduces the documented examples for Claude 4.7 and later.

**3. `build_request(doc, file_id=None)`** returns keyword arguments for `client.messages.create`: `model`, `max_tokens`, `output_config={"effort": "low", "format": {"type": "json_schema", "schema": EXTRACTION_SCHEMA}}`, and one user message whose content is the file block **first**, then `{"type": "text", "text": INSTRUCTIONS}`. The file block is `{"type": "document" | "image", "source": ...}` with source `{"type": "file", "file_id": ...}` when a `file_id` is given, otherwise `{"type": "base64", "media_type": doc["media_type"], "data": doc["data"]}`.

**4. `validate_line(line, doc, erp_lines)`** returns `(status, reason)`. Check in this order:

1. `quote` is empty or `None`: `("abstain", "no_evidence")`.
2. `sku` not in `erp_lines`: `("abstain", "unknown_sku")`.
3. If `route(doc)["citable"]`: the normalised quote must appear in the normalised `page_text` of the cited `page`, else `("abstain", "quote_not_on_page")`; the normalised quote must contain the SKU, else `("abstain", "quote_does_not_support")`. Then `("accept", None)` if quantity and unit price match ERP, else `("discrepancy", "differs_from_erp")`.
4. Not citable: `("accept", None)` if quantity and unit price match ERP, else `("abstain", "unverified_mismatch")`.

Normalise by collapsing whitespace and lowercasing. Prices match when they differ by less than 0.005.

**5. `process_inbox(client, inbox, erp, upload)`** returns one dict per document, in inbox order: `{"doc_id", "action", "reason", "po", "lines", "auto_post"}`.

- Not `"extract"`: copy `action` and `reason` from `route`; `po` is `None`, `lines` is `[]`, `auto_post` is false.
- Otherwise call `upload(doc)` only when the source is `"file"`, then call Claude once with `build_request`.
- `stop_reason` other than `"end_turn"`: `action` `"review"`, `reason` the stop reason. A PO number missing from `erp`: `"review"`, `"unknown_po"`.
- Otherwise parse the JSON from the text blocks (skip thinking blocks), set `po`, and add `status` and `reason` to a copy of every line. `auto_post` is true only when every line is accepted.

## Why abstain on a photo but flag a discrepancy on a PDF?

On a PDF with a text layer you can prove the quote is really on that page. If that verified line says 150 metres and ERP says 100, the customer probably changed the order: that's a real **discrepancy** for a buyer to confirm. On a photo you can't verify anything. "8 vests" against an ERP line of 3 is more likely a misread "3" than a change, so you **abstain** and a person looks at the image. Same disagreement, different evidence, different action.

The JSON page-and-quote scheme here exists because you used structured outputs, and native citations can't be combined with `output_config.format`. The next two lessons show what native citations guarantee instead.

## Example

```python
>>> route(INBOX[1])["est_visual_tokens"]
4784
>>> [l["status"] for l in process_inbox(client, INBOX, ERP_OPEN_POS, upload)[0]["lines"]]
['accept', 'accept', 'discrepancy', 'abstain']
```

Press **Run** to see the routing for all eight files, then **Submit**.
