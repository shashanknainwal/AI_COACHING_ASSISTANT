import json


def iter_sse(chunks):
    """Yield (t_ms, event_name, data) for each complete event, as soon as it completes."""
    buffer = ""
    for t, chunk in chunks:
        buffer = (buffer + chunk).replace("\r\n", "\n")
        while "\n\n" in buffer:
            raw, buffer = buffer.split("\n\n", 1)
            name, data_lines = None, []
            for line in raw.split("\n"):
                if line.startswith(":"):
                    continue
                if line.startswith("event:"):
                    name = line[len("event:"):].strip()
                elif line.startswith("data:"):
                    data_lines.append(line[len("data:"):].lstrip(" "))
            if not data_lines:
                continue
            data = json.loads("\n".join(data_lines))
            yield t, name or data.get("type"), data


STATUS = {"end_turn": "complete", "stop_sequence": "complete", "tool_use": "tool_use",
          "refusal": "refusal", "max_tokens": "max_tokens"}


def consume(chunks, on_text=None, should_cancel=None):
    blocks, raw_json = {}, {}
    out = {"status": None, "text": "", "blocks": [], "stop_reason": None, "stop_details": None,
           "usage": {"input_tokens": 0, "output_tokens": 0}, "ttft_ms": None, "error": None}
    finished = False
    try:
        for t, name, data in iter_sse(chunks):
            kind = data.get("type")
            if kind == "message_start":
                u = data["message"].get("usage", {})
                out["usage"] = {"input_tokens": u.get("input_tokens", 0), "output_tokens": u.get("output_tokens", 0)}
            elif kind == "content_block_start":
                b = data["content_block"]
                i = data["index"]
                if b["type"] == "text":
                    blocks[i] = {"type": "text", "text": "", "citations": []}
                elif b["type"] == "thinking":
                    blocks[i] = {"type": "thinking", "thinking": "", "signature": ""}
                elif b["type"] == "tool_use":
                    blocks[i] = {"type": "tool_use", "id": b["id"], "name": b["name"], "input": None}
                    raw_json[i] = ""
                else:
                    blocks[i] = dict(b)
            elif kind == "content_block_delta":
                i, d = data["index"], data["delta"]
                if d["type"] == "text_delta":
                    if not d["text"]:
                        continue
                    blocks[i]["text"] += d["text"]
                    out["text"] += d["text"]
                    if out["ttft_ms"] is None:
                        out["ttft_ms"] = t
                    if on_text:
                        on_text(d["text"])
                    if should_cancel and should_cancel(out["text"]):
                        out["status"] = "cancelled"
                        break
                elif d["type"] == "thinking_delta":
                    blocks[i]["thinking"] += d["thinking"]
                elif d["type"] == "signature_delta":
                    blocks[i]["signature"] = d["signature"]
                elif d["type"] == "input_json_delta":
                    raw_json[i] += d["partial_json"]
                elif d["type"] == "citations_delta":
                    blocks[i]["citations"].append(d["citation"])
            elif kind == "content_block_stop":
                i = data["index"]
                if i in raw_json:
                    try:
                        blocks[i]["input"] = json.loads(raw_json[i]) if raw_json[i] else {}
                    except ValueError:
                        blocks[i]["input"] = None
            elif kind == "message_delta":
                out["stop_reason"] = data["delta"].get("stop_reason")
                out["stop_details"] = data["delta"].get("stop_details")
                if "output_tokens" in data.get("usage", {}):
                    out["usage"]["output_tokens"] = data["usage"]["output_tokens"]
            elif kind == "message_stop":
                finished = True
            elif kind == "error":
                out["status"] = "error"
                out["error"] = data["error"]
                break
    finally:
        if hasattr(chunks, "close"):
            chunks.close()

    out["blocks"] = [blocks[i] for i in sorted(blocks)]
    if out["status"] is None:
        if not finished:
            out["status"] = "error"
            out["error"] = {"type": "incomplete_stream", "message": "stream ended before message_stop"}
        else:
            out["status"] = STATUS.get(out["stop_reason"], "complete")
    if out["status"] == "refusal":
        out["text"] = ""
        out["blocks"] = [b for b in out["blocks"] if b["type"] != "text"]
    return out


# --- Try it out (not graded) ---
if __name__ == "__main__":
    for name in STREAMS:
        r = consume(stream_source(name), should_cancel=(lambda s: len(s) > 40) if name == "long" else None)
        print(f"{name:10} {r['status']:10} ttft={r['ttft_ms']} usage={r['usage']} text={r['text'][:50]!r}")
