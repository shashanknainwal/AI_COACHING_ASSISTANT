import json
from anthropic import _sim

DOCS = {d["doc_id"]: d for d in INBOX}


def _fresh():
    _sim.calls.clear()
    _sim._queue.clear()
    _uploads.clear()


def test_route_rejects_and_splits():
    """route() rejects unsupported, encrypted and oversized files and splits long PDFs"""
    assert route(DOCS["D5"])["action"] == "reject" and route(DOCS["D5"])["reason"] == "unsupported_type", f".docx: {route(DOCS['D5'])}"
    assert route(DOCS["D6"])["reason"] == "unsupported_type", f"HEIC isn't a supported image type: {route(DOCS['D6'])}"
    assert route(DOCS["D4"])["action"] == "reject" and route(DOCS["D4"])["reason"] == "encrypted", f"encrypted PDF: {route(DOCS['D4'])}"
    assert route(DOCS["D8"])["action"] == "split" and route(DOCS["D8"])["reason"] == "too_many_pages", f"812 pages: {route(DOCS['D8'])}"
    huge = dict(DOCS["D2"], width=9000, height=6000)
    assert route(huge)["reason"] == "image_too_large", "an image over 8000 px must be rejected"
    heavy = dict(DOCS["D2"], size_bytes=12_000_000)
    assert route(heavy)["reason"] == "image_too_large", "an image over 10 MB must be rejected"


def test_route_extract_fields():
    """route() picks the block, the source and citability for extractable files"""
    pdf = route(DOCS["D1"])
    assert pdf["action"] == "extract" and pdf["block"] == "document" and pdf["source"] == "base64", f"po-4471.pdf: {pdf}"
    assert pdf["citable"] is True and pdf["reason"] is None and pdf["est_visual_tokens"] is None, f"po-4471.pdf: {pdf}"
    scan = route(DOCS["D3"])
    assert scan["block"] == "document" and scan["citable"] is False, f"a PDF with no text layer can't be verified against text: {scan}"
    big = route(DOCS["D7"])
    assert big["source"] == "file", f"41 MB is over INLINE_LIMIT_BYTES, so upload it: {big}"
    photo = route(DOCS["D2"])
    assert photo["block"] == "image" and photo["citable"] is False and photo["source"] == "base64", f"photo: {photo}"


def test_image_token_estimate():
    """estimate_image_tokens() matches the documented high-resolution examples"""
    assert estimate_image_tokens(1000, 1000) == 1296, estimate_image_tokens(1000, 1000)
    assert estimate_image_tokens(1920, 1080) == 2691, estimate_image_tokens(1920, 1080)
    assert estimate_image_tokens(3840, 2160) == 4784, estimate_image_tokens(3840, 2160)
    assert estimate_image_tokens(4032, 3024) == 4784, "a 12 MP photo hits the 4,784-token cap"
    assert route(DOCS["D2"])["est_visual_tokens"] == 4784


def test_build_request_pdf():
    """build_request() puts the document block first and asks for structured output with low effort"""
    req = build_request(DOCS["D1"])
    assert req.get("model") == MODEL and req.get("max_tokens") == MAX_TOKENS, f"model/max_tokens: {req}"
    oc = req.get("output_config", {})
    assert oc.get("effort") == "low", "set effort explicitly: Sonnet 5.5 defaults to high"
    assert oc.get("format") == {"type": "json_schema", "schema": EXTRACTION_SCHEMA}, "use output_config.format with EXTRACTION_SCHEMA"
    content = req["messages"][0]["content"]
    assert content[0] == {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": DOCS["D1"]["data"]}}, f"first block: {content[0]}"
    assert content[-1] == {"type": "text", "text": INSTRUCTIONS}, "the instructions come after the document"


def test_build_request_image_and_file():
    """build_request() builds image blocks and file_id sources"""
    img = build_request(DOCS["D2"])["messages"][0]["content"][0]
    assert img == {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": DOCS["D2"]["data"]}}, f"image block: {img}"
    f = build_request(DOCS["D7"], file_id="file_abc")["messages"][0]["content"][0]
    assert f == {"type": "document", "source": {"type": "file", "file_id": "file_abc"}}, f"file source: {f}"


def test_validate_citable_document():
    """validate_line() checks the quote against the cited page before trusting a PDF line"""
    erp = ERP_OPEN_POS["PO-4471"]
    lines = _EXTRACTIONS["D1"]["lines"]
    assert validate_line(lines[0], DOCS["D1"], erp) == ("accept", None), validate_line(lines[0], DOCS["D1"], erp)
    assert validate_line(lines[1], DOCS["D1"], erp) == ("accept", None), "compare quotes with whitespace and case normalised"
    assert validate_line(lines[2], DOCS["D1"], erp) == ("discrepancy", "differs_from_erp"), "verified evidence that disagrees with ERP is a discrepancy for the buyer"
    assert validate_line(lines[3], DOCS["D1"], erp) == ("abstain", "quote_not_on_page"), "the gloves line is on page 2, not page 1"
    stray = dict(lines[0], sku="TS-XX-999")
    assert validate_line(stray, DOCS["D1"], erp) == ("abstain", "unknown_sku")
    wrong_sku = dict(lines[0], sku="TS-NY-M8", qty=200, unit_price=0.11)
    assert validate_line(wrong_sku, DOCS["D1"], erp) == ("abstain", "quote_does_not_support"), "the quote must contain the SKU it supports"


def test_validate_uncitable_document():
    """validate_line() abstains on any mismatch it can't verify (photos and scans)"""
    erp = ERP_OPEN_POS["PO-4502"]
    lines = _EXTRACTIONS["D2"]["lines"]
    assert validate_line(lines[0], DOCS["D2"], erp) == ("accept", None)
    assert validate_line(lines[1], DOCS["D2"], erp) == ("abstain", "unverified_mismatch"), "8 vs 3 on a photo is more likely a misread than a change"
    assert validate_line(lines[2], DOCS["D2"], erp) == ("abstain", "no_evidence"), "a null quote means illegible"


def test_process_inbox_end_to_end():
    """process_inbox() calls Claude only for extractable files and uploads only large ones"""
    _fresh()
    out = process_inbox(client, INBOX, ERP_OPEN_POS, upload)
    assert isinstance(out, list) and len(out) == len(INBOX), "one result per document, in inbox order"
    by = {r["doc_id"]: r for r in out}
    assert len(_sim.calls) == 4, f"4 documents are extractable; you made {len(_sim.calls)} calls"
    assert list(_uploads.values()) == ["D7"], f"only the 41 MB PDF should be uploaded, got {list(_uploads.values())}"
    assert by["D1"]["po"] == "PO-4471" and [l["status"] for l in by["D1"]["lines"]] == ["accept", "accept", "discrepancy", "abstain"], by["D1"]
    assert by["D1"]["auto_post"] is False
    assert [l["status"] for l in by["D2"]["lines"]] == ["accept", "abstain", "abstain"], by["D2"]
    assert by["D3"]["auto_post"] is True and by["D7"]["auto_post"] is True, "fully accepted orders can post automatically"
    assert by["D5"]["action"] == "reject" and by["D5"]["lines"] == [] and by["D5"]["auto_post"] is False
    assert by["D8"]["action"] == "split"
    line = by["D1"]["lines"][0]
    assert line["sku"] == "TS-HB-M8-50" and line["reason"] is None, "keep the extracted fields and add status and reason"


def test_process_inbox_handles_stop_reasons():
    """process_inbox() sends refused, truncated and unknown-PO documents to review"""
    _fresh()
    _sim.queue(_sim.message(_sim.text('{"po_number": "PO-44'), stop_reason="max_tokens"))
    _sim.queue(_sim.refusal("general_harms"))
    _sim.queue(json.dumps({"po_number": "PO-9999", "lines": []}))
    out = process_inbox(client, [DOCS["D1"], DOCS["D2"], DOCS["D3"]], ERP_OPEN_POS, upload)
    assert [(r["action"], r["reason"]) for r in out] == [("review", "max_tokens"), ("review", "refusal"), ("review", "unknown_po")], out
    assert all(r["auto_post"] is False for r in out)
