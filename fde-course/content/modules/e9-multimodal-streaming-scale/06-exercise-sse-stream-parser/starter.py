import json


def iter_sse(chunks):
    """Yield (t_ms, event_name, data) for each complete event, as soon as it completes."""
    buffer = ""
    for t, chunk in chunks:
        buffer += chunk
        # TODO: normalise line endings, split complete events on a blank line,
        # skip comment lines, parse the data JSON and yield
    return
    yield


def consume(chunks, on_text=None, should_cancel=None):
    """Rebuild the message from a stream of (t_ms, chunk) pairs."""
    out = {"status": None, "text": "", "blocks": [], "stop_reason": None, "stop_details": None,
           "usage": {"input_tokens": 0, "output_tokens": 0}, "ttft_ms": None, "error": None}
    for t, name, data in iter_sse(chunks):
        pass  # TODO: handle each event type
    return out


# --- Try it out (not graded) ---
if __name__ == "__main__":
    for name in STREAMS:
        r = consume(stream_source(name))
        print(f"{name:10} {r['status']} ttft={r['ttft_ms']} text={r['text'][:50]!r}")
