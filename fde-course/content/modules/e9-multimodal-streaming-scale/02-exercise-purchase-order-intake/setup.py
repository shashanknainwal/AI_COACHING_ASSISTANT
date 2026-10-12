import json
import anthropic
from anthropic import _sim

MODEL = "claude-sonnet-5-5"
MAX_TOKENS = 4000

# Documented limits (vision and PDF support docs, Claude API) plus Tallowmere's own inline threshold.
MAX_PDF_PAGES = 600
MAX_IMAGE_EDGE = 8000
MAX_IMAGE_BYTES = 10_000_000
INLINE_LIMIT_BYTES = 5_000_000          # Tallowmere's rule: bigger files go through the Files API
IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
HIRES_LONG_EDGE = 2576                  # Claude 4.7 and later
HIRES_MAX_TOKENS = 4784

INSTRUCTIONS = (
    "Extract every order line from this purchase order. For each line give the SKU, quantity, "
    "unit price, the page number it appears on, and a short verbatim quote of the line as printed. "
    "If a line is illegible, set quote to null. Do not guess SKUs."
)

_LINE = {
    "type": "object",
    "properties": {
        "line_no": {"type": "integer"},
        "sku": {"type": "string"},
        "qty": {"type": "number"},
        "unit_price": {"type": "number"},
        "page": {"type": "integer"},
        "quote": {"type": ["string", "null"]},
    },
    "required": ["line_no", "sku", "qty", "unit_price", "page", "quote"],
    "additionalProperties": False,
}
EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {"po_number": {"type": "string"}, "lines": {"type": "array", "items": _LINE}},
    "required": ["po_number", "lines"],
    "additionalProperties": False,
}

PAGE_TEXT_4471 = {
    1: ("PURCHASE ORDER PO-4471  Harlow Plant Services  Ship to: Dock 3\n"
        "1  TS-HB-M8-50   Hex bolt M8 x 50 zinc        200 EA   0.42\n"
        "2  TS-NY-M8      Nylon lock nut M8            200 EA   0.11\n"),
    2: ("PO-4471 continued\n"
        "3  TS-CB-3C25    Cable 3-core 2.5mm2         150 M    1.85\n"
        "4  TS-GL-NIT-L   Nitrile gloves size L        20 BOX   6.90\n"
        "Terms: Net 30. Deliver by 2026-10-24.\n"),
}

INBOX = [
    {"doc_id": "D1", "filename": "po-4471.pdf", "media_type": "application/pdf", "size_bytes": 182_000,
     "pages": 2, "text_layer": True, "encrypted": False, "data": "JVBERi0xLjcK...po-4471", "page_text": PAGE_TEXT_4471},
    {"doc_id": "D2", "filename": "IMG_2093.jpg", "media_type": "image/jpeg", "size_bytes": 3_100_000,
     "width": 4032, "height": 3024, "data": "/9j/4AAQSkZJRg...img-2093"},
    {"doc_id": "D3", "filename": "scan-0912.pdf", "media_type": "application/pdf", "size_bytes": 940_000,
     "pages": 1, "text_layer": False, "encrypted": False, "data": "JVBERi0xLjQK...scan-0912", "page_text": {}},
    {"doc_id": "D4", "filename": "po-4520-locked.pdf", "media_type": "application/pdf", "size_bytes": 210_000,
     "pages": 1, "text_layer": True, "encrypted": True, "data": "JVBERi0xLjcK...locked", "page_text": {}},
    {"doc_id": "D5", "filename": "order-form.docx",
     "media_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
     "size_bytes": 64_000, "data": "UEsDBBQABgAI...docx"},
    {"doc_id": "D6", "filename": "IMG_2101.heic", "media_type": "image/heic", "size_bytes": 2_400_000,
     "width": 4032, "height": 3024, "data": "AAAAGGZ0eXBoZWlj...heic"},
    {"doc_id": "D7", "filename": "po-4533-with-catalog.pdf", "media_type": "application/pdf", "size_bytes": 41_000_000,
     "pages": 140, "text_layer": True, "encrypted": False, "data": "JVBERi0xLjcK...po-4533",
     "page_text": {1: "PURCHASE ORDER PO-4533\n1  TS-WT-ZIP-300  Cable ties 300mm black   50 PK   2.40\n"}},
    {"doc_id": "D8", "filename": "archive-2019-2024.pdf", "media_type": "application/pdf", "size_bytes": 3_900_000,
     "pages": 812, "text_layer": True, "encrypted": False, "data": "JVBERi0xLjcK...archive", "page_text": {}},
]

ERP_OPEN_POS = {
    "PO-4471": {
        "TS-HB-M8-50": {"qty": 200, "unit_price": 0.42},
        "TS-NY-M8": {"qty": 200, "unit_price": 0.11},
        "TS-CB-3C25": {"qty": 100, "unit_price": 1.85},
        "TS-GL-NIT-L": {"qty": 20, "unit_price": 6.90},
    },
    "PO-4502": {
        "TS-SG-CLR": {"qty": 24, "unit_price": 3.10},
        "TS-HV-VEST-XL": {"qty": 3, "unit_price": 4.75},
        "TS-EP-200": {"qty": 10, "unit_price": 0.95},
    },
    "PO-4510": {"TS-HB-M10-60": {"qty": 500, "unit_price": 0.58}},
    "PO-4533": {"TS-WT-ZIP-300": {"qty": 50, "unit_price": 2.40}},
}

_uploads = {}


def upload(doc):
    """Stand-in for client.files.upload(file=...). Returns a file_id."""
    file_id = f"file_sim_{doc['doc_id'].lower()}"
    _uploads[file_id] = doc["doc_id"]
    return file_id


def _line(n, sku, qty, price, page, quote):
    return {"line_no": n, "sku": sku, "qty": qty, "unit_price": price, "page": page, "quote": quote}


_EXTRACTIONS = {
    "D1": {"po_number": "PO-4471", "lines": [
        _line(1, "TS-HB-M8-50", 200, 0.42, 1, "TS-HB-M8-50 Hex bolt M8 x 50 zinc 200 EA 0.42"),
        _line(2, "TS-NY-M8", 200, 0.11, 1, "TS-NY-M8   Nylon lock nut M8  200 EA 0.11"),
        _line(3, "TS-CB-3C25", 150, 1.85, 2, "TS-CB-3C25 Cable 3-core 2.5mm2 150 M 1.85"),
        _line(4, "TS-GL-NIT-L", 20, 6.90, 1, "TS-GL-NIT-L Nitrile gloves size L 20 BOX 6.90"),
    ]},
    "D2": {"po_number": "PO-4502", "lines": [
        _line(1, "TS-SG-CLR", 24, 3.10, 1, "TS-SG-CLR safety glasses clear 24 3.10"),
        _line(2, "TS-HV-VEST-XL", 8, 4.75, 1, "TS-HV-VEST-XL hi-vis vest XL 8 4.75"),
        _line(3, "TS-EP-200", 10, 0.95, 1, None),
    ]},
    "D3": {"po_number": "PO-4510", "lines": [
        _line(1, "TS-HB-M10-60", 500, 0.58, 1, "TS-HB-M10-60 Hex bolt M10 x 60 500 EA 0.58"),
    ]},
    "D7": {"po_number": "PO-4533", "lines": [
        _line(1, "TS-WT-ZIP-300", 50, 2.40, 1, "TS-WT-ZIP-300 Cable ties 300mm black 50 PK 2.40"),
    ]},
}


def _doc_for_request(params):
    content = params["messages"][-1]["content"]
    if not isinstance(content, list):
        return None
    for block in content:
        if not isinstance(block, dict) or block.get("type") not in ("document", "image"):
            continue
        src = block.get("source", {})
        if src.get("type") == "file":
            return _uploads.get(src.get("file_id"))
        for d in INBOX:
            if src.get("data") == d["data"]:
                return d["doc_id"]
    return None


def _responder(params):
    doc_id = _doc_for_request(params)
    if doc_id not in _EXTRACTIONS:
        return _sim.text("I couldn't find a document in this request.")
    return [_sim.thinking(""), _sim.text(json.dumps(_EXTRACTIONS[doc_id]))]


_sim.set_responder(_responder)
client = anthropic.Anthropic()
