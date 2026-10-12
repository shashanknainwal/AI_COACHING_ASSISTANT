---
title: "Design It: Multimodal Document Intake for a Customs Broker"
type: written
minutes: 45
diagram: true
sections:
  - key: requirements
    label: 1. Requirements and assumptions
    prompt: "What you'd ask, what you assume, and the numbers you design for: volume, document types and formats, the fields that matter, the cost of a wrong value, turnaround."
    words: [80, 250]
  - key: architecture
    label: 2. Architecture
    prompt: "The intake flow from arrival to a filing a broker approves. How each input type reaches the model (native PDF, image, text, spreadsheet), which model does which step, how you get structured fields, how each value is traced to its source page, and where humans come in."
    words: [150, 450]
  - key: quality
    label: 3. Evals and the quality bar
    prompt: "The labelled set, how you score fields, the release gate, and what you monitor after launch."
    words: [80, 300]
  - key: risks
    label: 4. Failure modes, cost and latency
    prompt: "What breaks (bad scans, wrong document type, conflicting documents, injected text), how you'd detect it, and a cost per shipment with the arithmetic."
    words: [80, 300]
rubric:
  - name: Scoping
    points: 15
    lookFor: "Asks or states the questions that change the design: the document mix and formats (native PDFs, scans, phone photos, spreadsheets, emails), languages, the fields that drive duty and compliance, the penalty for a wrong value, turnaround, and volume with peaks. Commits to numbers."
  - name: Multimodal architecture
    points: 25
    lookFor: "Classifies each document first, then routes by type and format. Sends PDFs and images to the model natively where that works, with a reason for any OCR step (for example spreadsheets parsed in code, very poor scans). Extracts to a fixed schema with structured outputs and a 'not sure' value per field. Traces every value to a document and page. Considers the Files API to avoid re-uploading the same file across calls, or explains why not. Cross-checks documents against each other in code (invoice totals versus packing list, weights, counts). Puts a broker approval step before anything is filed."
  - name: Evals and quality bar
    points: 20
    lookFor: "A labelled set from past shipments with the filings brokers actually submitted, stratified by document type, format and scan quality. Field-level accuracy on duty-relevant fields with intervals, a separate abstain rate, must-pass cases, and a gate on every prompt or model change. Online: broker correction rate per field, sampled audits."
  - name: Failure modes and safety
    points: 25
    lookFor: "Names realistic failures (illegible scans, rotated or multi-document PDFs, the wrong document type, documents that disagree, text in a document that tries to instruct the model, a value hallucinated from an empty field) with detection and a response. Treats document text as untrusted data. Knows that citations and structured outputs can't be combined in one request and designs around it (for example, structured fields plus a page reference field validated in code, or a second call)."
  - name: Cost and latency math
    points: 15
    lookFor: "A cost per shipment from estimated tokens per page (or measured with count_tokens), model prices, and the effort level stated or thinking counted as output. Uses a cheap model for classification and a stronger one only where needed, caches the stable instructions with cache_control, and considers batch processing for documents nobody is waiting on, checking platform availability."
passScore: 70
graderNotes: "Score the diagram with the sections: it should show classification, per-type routing, extraction, cross-document checks, the source trace and the broker approval. If anything is filed with customs without a broker's approval, cap 'Multimodal architecture' at 10. If the design assumes every document is clean text (no plan for scans or photos), cap 'Multimodal architecture' at 12. If there's no per-field 'not sure' path and no source trace, cap 'Failure modes and safety' at 12. If the candidate claims citations and structured outputs work together in one request, deduct 5 from 'Failure modes and safety'. If the cost estimate ignores image or PDF page tokens entirely, or ignores thinking, cap 'Cost and latency math' at 7. Specific numeric limits (pages per request, file sizes) stated as fact without 'check the current docs' are not an error if roughly right, but don't reward them; reward a plan to measure. Do not reward length."
anchors:
  - label: weak
    expect: [0, 45]
    answer: "Requirements: lots of documents a day. Architecture: OCR everything with a cloud OCR service, send the text to Claude Opus, ask for JSON with the fields and file it with customs automatically. Evals: test on some examples and check they look right. Risks: OCR errors, we can retry. Cost: Claude is cheap enough."
  - label: strong
    expect: [75, 100]
    answer: "Requirements: 8,000 shipments a day, peak 2x on Mondays; per shipment a commercial invoice, packing list and bill of lading, sometimes a certificate of origin. 55% native PDF, 30% scans, 10% phone photos, 5% spreadsheets; English, Spanish, Mandarin. Duty-relevant fields (description, quantity, value, currency, country of origin) carry penalties if wrong; filing within 4 hours. Architecture: a queue per shipment; Haiku 5.5 at low effort classifies each file and page range; spreadsheets are parsed in code; PDFs and photos go to Sonnet 5.5 natively, uploaded once with the Files API where the platform supports it and referenced by file_id across the classification and extraction calls. Extraction uses structured outputs with a 'not sure' value and a source_page field per value; code checks the page exists and the value appears in that page's text where text is available, and cross-checks invoice totals against the packing list. Conflicts and 'not sure' fields go to a broker; nothing is filed without broker approval. Evals: 1,200 past shipments with the submitted filings as labels, stratified by format and scan quality; field accuracy with Wilson intervals, the gate requires the lower bound above 97% on duty fields plus must-pass cases. Risks: rotated scans, multi-document PDFs, injected instructions in a document (treated as data; no tools that act), empty fields filled with guesses (abstain path). Cost: about 9 pages a shipment; I'd measure tokens per page with count_tokens, assume roughly 2,000 per page, so about 18,000 input plus 2,000 output including thinking at low effort on Sonnet 5.5: roughly $0.056 a shipment, about $450 a day before caching the instructions.\nDiagram: email/portal -> queue -> classifier (Haiku 5.5) -> spreadsheet parser | extractor (Sonnet 5.5, native PDF/image) -> code checks (page trace, cross-document) -> broker review -> customs filing"
---

Most enterprise documents are PDFs, scans and phone photos, so document intake is a realistic shape for a design prompt and a common first project with customers. The doc-QA prompt in lesson 04 touched scanned PDFs; this one makes multimodal input the core of the problem. The prompt is original and is not a real interview question.

The company is fictional.

## The prompt

> Corvid Customs Brokerage files import declarations for about 400 business clients. Every shipment arrives as an email or portal upload with a commercial invoice, a packing list and a bill of lading, sometimes a certificate of origin. Brokers retype the fields into the customs filing system. They want Claude to prepare each filing for a broker to approve. Design it.

Answer in the four sections on the right, and keep the diagram box up to date as you write. The diagram is graded with your answer.

## How to approach it

1. **Find out what the documents really look like.** Native PDF, scanned PDF, phone photo, spreadsheet, email body? Which languages? A design that assumes clean text fails on the first faxed invoice.
2. **Route before you extract.** Classify each file (and each document inside a multi-document PDF), then send each type down the path that suits it. Spreadsheets are data: parse them in code.
3. **Trace every value to its source.** A broker, and the customs authority, will ask where a number came from. Plan a document-and-page reference per value and check it in code.
4. **Check documents against each other.** The invoice total, the packing list's quantities and the bill of lading's weight should agree. Code can check that; a disagreement goes to a human.
5. **Do the math per page.** PDFs and images cost tokens per page or per image. Estimate, then say you'd measure with token counting.

## Facts you can use

- Claude reads PDFs and images natively; PDF input is supported on the Claude API, Claude Platform on AWS, Amazon Bedrock, Google Vertex AI and Microsoft Foundry. Page and file-size limits change: check the current docs rather than quoting a number.
- The Files API lets you upload a file once and reference it by `file_id` in later requests. It's a beta on the Claude API and Claude Platform on AWS, and isn't available on Bedrock or Vertex. It saves re-uploading the same bytes; it doesn't make a page cost fewer tokens.
- The Citations feature returns quoted spans from the documents you send, but it can't be combined with structured outputs (`output_config.format`) in the same request.
- Prices per million tokens: Haiku 5.5 $0.10 / $0.50 (prompts up to 100K tokens), Sonnet 5.5 $2 / $10, Opus 5.5 $4 / $20. All three think by default (Opus 5.5 and Haiku 5.5 at effort `medium`, Sonnet 5.5 at `high`), and thinking is billed as output, so state the effort you'd set. Caching needs a `cache_control` marker. Message Batches halves the price but isn't available on Bedrock, Vertex or Foundry.

When you submit, Claude grades your design against the rubric below.
