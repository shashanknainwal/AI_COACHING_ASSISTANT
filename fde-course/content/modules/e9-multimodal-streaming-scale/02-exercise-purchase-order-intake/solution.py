import json
import math


def route(doc):
    """Decide how a document enters the pipeline."""
    out = {"action": "extract", "block": None, "source": None, "citable": False,
           "est_visual_tokens": None, "reason": None}
    mt = doc["media_type"]
    is_pdf = mt == "application/pdf"
    if not is_pdf and mt not in IMAGE_TYPES:
        return dict(out, action="reject", reason="unsupported_type")
    if is_pdf and doc.get("encrypted"):
        return dict(out, action="reject", reason="encrypted")
    if is_pdf and doc.get("pages", 0) > MAX_PDF_PAGES:
        return dict(out, action="split", reason="too_many_pages")
    if not is_pdf:
        if max(doc["width"], doc["height"]) > MAX_IMAGE_EDGE or doc["size_bytes"] > MAX_IMAGE_BYTES:
            return dict(out, action="reject", reason="image_too_large")
    out["block"] = "document" if is_pdf else "image"
    out["source"] = "file" if doc["size_bytes"] > INLINE_LIMIT_BYTES else "base64"
    out["citable"] = bool(is_pdf and doc.get("text_layer"))
    if not is_pdf:
        out["est_visual_tokens"] = estimate_image_tokens(doc["width"], doc["height"])
    return out


def estimate_image_tokens(width, height):
    scale = min(1.0, HIRES_LONG_EDGE / max(width, height))
    w, h = round(width * scale), round(height * scale)
    return min(math.ceil(w / 28) * math.ceil(h / 28), HIRES_MAX_TOKENS)


def build_request(doc, file_id=None):
    if file_id:
        source = {"type": "file", "file_id": file_id}
    else:
        source = {"type": "base64", "media_type": doc["media_type"], "data": doc["data"]}
    block_type = "document" if doc["media_type"] == "application/pdf" else "image"
    return {
        "model": MODEL,
        "max_tokens": MAX_TOKENS,
        "output_config": {"effort": "low", "format": {"type": "json_schema", "schema": EXTRACTION_SCHEMA}},
        "messages": [{"role": "user", "content": [
            {"type": block_type, "source": source},
            {"type": "text", "text": INSTRUCTIONS},
        ]}],
    }


def _norm(s):
    return " ".join(str(s).split()).lower()


def validate_line(line, doc, erp_lines):
    """Return (status, reason) for one extracted line."""
    quote = line.get("quote")
    if not quote or not str(quote).strip():
        return "abstain", "no_evidence"
    expected = erp_lines.get(line["sku"])
    if expected is None:
        return "abstain", "unknown_sku"
    matches = line["qty"] == expected["qty"] and abs(line["unit_price"] - expected["unit_price"]) < 0.005
    if route(doc)["citable"]:
        page_text = doc.get("page_text", {}).get(line["page"], "")
        if _norm(quote) not in _norm(page_text):
            return "abstain", "quote_not_on_page"
        if _norm(line["sku"]) not in _norm(quote):
            return "abstain", "quote_does_not_support"
        return ("accept", None) if matches else ("discrepancy", "differs_from_erp")
    return ("accept", None) if matches else ("abstain", "unverified_mismatch")


def process_inbox(client, inbox, erp, upload):
    results = []
    for doc in inbox:
        r = route(doc)
        entry = {"doc_id": doc["doc_id"], "action": r["action"], "reason": r["reason"],
                 "po": None, "lines": [], "auto_post": False}
        if r["action"] != "extract":
            results.append(entry)
            continue
        file_id = upload(doc) if r["source"] == "file" else None
        response = client.messages.create(**build_request(doc, file_id))
        if response.stop_reason != "end_turn":
            results.append(dict(entry, action="review", reason=response.stop_reason))
            continue
        text = "".join(b.text for b in response.content if b.type == "text")
        data = json.loads(text)
        entry["po"] = data["po_number"]
        erp_lines = erp.get(data["po_number"])
        if erp_lines is None:
            results.append(dict(entry, action="review", reason="unknown_po"))
            continue
        for line in data["lines"]:
            status, reason = validate_line(line, doc, erp_lines)
            entry["lines"].append(dict(line, status=status, reason=reason))
        entry["auto_post"] = all(l["status"] == "accept" for l in entry["lines"])
        results.append(entry)
    return results


# --- Try it out (not graded) ---
if __name__ == "__main__":
    for d in INBOX:
        print(d["filename"], route(d))
    for res in process_inbox(client, INBOX, ERP_OPEN_POS, upload):
        print(res["doc_id"], res["action"], res["reason"], "auto_post" if res["auto_post"] else "",
              [(l["sku"], l["status"], l["reason"]) for l in res["lines"]])
