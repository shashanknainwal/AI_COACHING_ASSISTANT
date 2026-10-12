---
title: "Documents and Images as Input"
type: reading
minutes: 18
---

> **By the end of this lesson** you'll be able to send PDFs and images to Claude with the right content block, state the documented limits from memory, estimate what an image or a PDF page costs in tokens, choose between native PDF input, image input and an OCR step, and decide when to upload once with the Files API.

## Why this matters

Most enterprise data that customers want "AI on" isn't in a database. It's purchase orders sent as PDFs, delivery notes photographed on a phone, faxed invoices, scanned contracts. Document intake is one of the most common first projects an applied AI engineer or FDE gets, and it's where a pilot most often dies quietly: the demo used clean PDFs, production gets crooked photos.

This module's case file is **Tallowmere Industrial Supply** (a fictional distributor of fasteners, cable and safety gear). Its order desk receives about 3,000 purchase orders a week. Roughly 60% arrive as PDFs exported from the customer's ERP, 30% as phone photos of printed forms, and 10% as scans with no text layer. Imani Ferrowell, VP of Order Operations (fictional), wants order lines keyed automatically, with a human only where the system isn't sure.

## Two content blocks, three ways to supply the bytes

Claude reads files through two content block types in a user message:

| Block | Accepts | Notes |
|---|---|---|
| `image` | JPEG, PNG, GIF, WebP | Animated GIFs: only the first frame is used |
| `document` | PDF, plain text, or "custom content" (a list of text blocks you chunk yourself) | `.docx` and `.xlsx` are not supported: convert to PDF or text first |

Each block takes a `source`, which can be:

1. **`base64`**: the bytes inline in the request body.
2. **`url`**: a link the API fetches.
3. **`file`**: a `file_id` from the Files API (upload once, reference many times).

On Amazon Bedrock and Google Cloud, only base64 sources are currently available (Official, vision and PDF docs).

```python
import anthropic, base64
client = anthropic.Anthropic()

pdf_b64 = base64.standard_b64encode(open("po-4471.pdf", "rb").read()).decode()

response = client.messages.create(
    model="claude-sonnet-5-5",
    max_tokens=4000,                       # covers thinking and the answer
    output_config={"effort": "low"},       # Sonnet 5.5 defaults to high
    messages=[{
        "role": "user",
        "content": [
            {"type": "document",
             "source": {"type": "base64", "media_type": "application/pdf", "data": pdf_b64}},
            {"type": "text", "text": "List every order line: SKU, quantity, unit price, and the page it is on."},
        ],
    }],
)
```

Put the document or image **before** the question. The docs recommend this ordering for both images and PDFs, the same way long documents go before the query in text prompts. When you send several images, label them in text ("Image 1:", "Image 2:") so you and the model can refer to them.

## How a PDF is actually read

When you send a PDF, the API converts **each page into an image** and also extracts **each page's text**, then gives the model both (Official, PDF support docs). Three consequences follow:

- Claude can read charts, stamps, tables and handwriting in the margin, not only the text layer.
- A PDF costs **text tokens plus image tokens for every page**. The docs say text typically runs 1,500 to 3,000 tokens per page, depending on density, and each page image is costed like any other image.
- A scanned PDF with no text layer is still readable (the page image is there), but it has no extracted text. That matters for citations (next lessons).

Use `client.messages.count_tokens(...)` on real samples before you quote a price. Page density varies far more than people expect.

## Limits you should know without looking up

| Limit | Value (Claude API) |
|---|---|
| Request size | 32 MB for standard endpoints (lower on some partner platforms, such as Bedrock and Google Cloud) |
| PDF pages per request | 600 (100 when the request's context window is under 1M tokens) |
| Images per request | 600 (100 for models with a 200K-token context window) |
| Image dimensions | 8000 x 8000 px maximum |
| More than 20 images in one request | A stricter per-image dimension limit applies. Keep each image's long edge at 2000 px or less, or send 20 or fewer image and document blocks |
| Image size | 10 MB base64 on the Claude API, 5 MB on Bedrock and Google Cloud |
| PDF format | Standard PDF, no passwords or encryption |

All Official, from the vision and PDF support pages (checked 2026-10-11). Two practical notes. The request limits cover the **whole payload**, so a 25 MB PDF plus a few photos can fail even though each file is under its own limit. And dense PDFs can fill the context window before they reach the page limit; split them.

## What an image costs

Claude sees images in **28 x 28 pixel patches**. An image costs `ceil(width / 28) x ceil(height / 28)` visual tokens, after any downscaling. Each model has a maximum native resolution:

| Tier | Models | Max long edge | Max visual tokens |
|---|---|---|---|
| High resolution | Claude 4.7 and later | 2576 px | 4,784 |
| Standard | Other models | 1568 px | 1,568 |

Larger images are downscaled (aspect ratio kept) until they fit both limits. Some documented examples on the high-resolution tier: a 1000 x 1000 image costs 1,296 tokens; 1920 x 1080 costs 2,691; a 3840 x 2160 image is downscaled to 2576 x 1449 and costs the 4,784 maximum (Official, vision docs).

**Worked example.** Tallowmere's phone photos are 4032 x 3024 (12 megapixels). On Claude Sonnet 5.5 (high-resolution tier) each photo is downscaled and hits the 4,784-token cap. The request:

| Line | Tokens | Price (Sonnet 5.5) |
|---|---|---|
| Photo | 4,784 | $2.00 / MTok input |
| Instructions and schema | 1,200 | $2.00 / MTok input |
| Thinking at `effort: "low"` (assumed; measure yours) | ~300 | $10.00 / MTok output |
| Extracted lines as JSON | ~500 | $10.00 / MTok output |

Input: 5,984 x $2 / 1M = $0.0120. Output: 800 x $10 / 1M = $0.0080. About **$0.02 per photo**, or about $18 a week for 900 photos. The photo is the biggest single line. High-resolution images can use up to about three times the visual tokens of the standard tier, so if a downsampled photo stays legible on your samples, downsample it before sending. Test legibility, don't assume it: small print on a crumpled form is exactly what downsampling destroys.

## Native, image, or OCR first?

| Approach | You get | You lose | Use when |
|---|---|---|---|
| **Native PDF** (`document` block) | Text layer plus page images; layout, tables and stamps understood; page-numbered citations possible when the PDF has extractable text | Pays for page images as well as text | ERP-exported PDFs, contracts, reports |
| **Image block** (photo or scan) | Visual understanding of a photo | No text layer. Native citations can't point into images | Phone photos, screenshots |
| **OCR first, then text** | A deterministic text layer you control, word bounding boxes from the OCR engine, text you can cite with character offsets | An extra vendor, latency and cost; OCR errors become "facts"; layout cues flatten | Regulated workflows that need a stored text layer, very high volume of clean scans, or when you must highlight exact boxes on the original |
| **Hybrid** | Claude reads the image; your code checks the result against OCR text or a system of record | Two pipelines to maintain | High-stakes extraction where you need evidence for every field |

The interview-ready point: native input isn't "better OCR". It's a different trade. The question to ask the customer is **what evidence a human needs to trust each extracted field**, because that decides whether you need a verifiable text layer.

Claude's documented vision limitations apply to every route: it can misread low-quality, rotated or very small images (under 200 px), counting many small objects is approximate, and outputs need verification for high-stakes use. Rotate pages upright and keep text legible before you send them.

## The Files API: upload once

For a file you'll use in more than one request, upload it and reference the `file_id`:

```python
from pathlib import Path

uploaded = client.files.upload(file=Path("po-4471.pdf"))   # client.beta.files on older SDKs
block = {"type": "document", "source": {"type": "file", "file_id": uploaded.id}}
```

Facts to know (Official, Files API docs, checked 2026-10-11):

- **It's out of beta.** Current SDKs use `client.files` with no beta header. Older code that sends `files-api-2025-04-14` keeps working with the older response shapes.
- **Limits:** 500 MB per file, 1 TB per organization. File operations are free; file content used in a message is billed as input tokens. File calls are rate limited to about 500 requests per minute.
- **Why bother:** in a multi-turn conversation every request resends the full history. Base64 images ride along on every turn; a `file_id` keeps the payload small however many files pile up.
- **Files are workspace-scoped, not user-scoped.** Any API key in the workspace can read any file in it. Never accept a `file_id` from an end user. Keep your own user-to-file mapping, and for multi-tenant products use a workspace per tenant (up to 100 per organization by default).
- **Lifecycle:** files persist until deleted, or until an optional expiry you set at upload (`expires_in_seconds`, from 1 hour to 90 days). Files you upload can't be downloaded again; only files created by skills or code execution can.
- **Availability:** the Claude API and Claude Platform on AWS; on Microsoft Foundry only for Hosted on Anthropic deployments. Not on Amazon Bedrock or Google Vertex AI.
- **Retention:** the Files API page lists the feature as not eligible for zero data retention. If a customer has a ZDR agreement, check the current data-retention docs before you design around uploaded files.

## Scaling the intake

Two levers from other modules apply directly. For repeated questions over the same document, put `cache_control` on the document block (caching basics are in E5). For a backlog that doesn't need answers now, the Message Batches API accepts vision and PDF requests at half price (lesson 7 of this module).

## How this comes up in interviews

Design rounds that involve "documents" are common in applied AI loops (Reported; see E6 for the prompts candidates describe). Interviewers probe whether you know the input actually costs tokens per page, what happens with scans, and how a human verifies a field. A practice prompt in the style of these rounds:

- "A logistics customer receives 50,000 delivery notes a month, half as phone photos. Design the extraction pipeline. What does one note cost, what's your accuracy target, and what does the reviewer see when the system isn't sure?"

> **Key takeaways**
>
> - Images go in `image` blocks; PDFs, text and custom-chunked content go in `document` blocks. Put them before the question.
> - A PDF page is read as text plus an image, so it costs both. Count tokens on real samples.
> - Know the limits: 32 MB per request, 600 pages or images (100 on smaller-context requests), 8000 px per image, 10 MB per image on the API, stricter sizes above 20 images.
> - Image tokens are `ceil(w/28) x ceil(h/28)` after downscaling, capped at 4,784 on Claude 4.7 and later. A 12 MP photo hits the cap.
> - Native PDF, image input and OCR-first are different trades. Decide by what evidence a reviewer needs per field.
> - The Files API saves resending bytes, but files are workspace-scoped: never take a `file_id` from a user, and check availability (no Bedrock or Vertex) and retention terms.
