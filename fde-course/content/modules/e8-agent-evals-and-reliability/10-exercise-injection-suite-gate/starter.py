import re
from urllib.parse import urlparse

# ATTACKS, BENIGN, TRANSCRIPTS, CANARY, CRITICAL_TOOLS, GATE_CONFIG and wilson() are loaded for you.


def extract_hosts(text):
    """Lowercase hosts of every http(s) URL in the text, in order, without duplicates."""
    # TODO
    pass


def attack_succeeded(attack, transcript):
    # TODO: one branch per goal type: tool, exfil, leak.
    pass


def benign_ok(transcript):
    # TODO
    pass


def score_defence(name, attacks, benign, transcripts):
    # TODO
    pass


def gate(score, baseline_benign_rate, config):
    # TODO
    pass


def compare(score_a, score_b, attacks):
    # TODO
    pass


# --- Try it out (not graded) ---
base = TRANSCRIPTS["none"]["benign"]
base_rate = sum(bool(benign_ok(base[b["id"]])) for b in BENIGN) / len(BENIGN)
scores = {}
for name in ("A-prompt-and-input-filter", "B-least-privilege-and-output-filter"):
    s = score_defence(name, ATTACKS, BENIGN, TRANSCRIPTS)
    if not s:
        continue
    scores[name] = s
    print(f"{name}: ASR {s['asr']:.3f} {s['asr_ci']}  benign {s['benign_ok_rate']:.3f}  successes {s['successes']}")
    print("   ", gate(s, base_rate, GATE_CONFIG))
if len(scores) == 2:
    print(compare(*scores.values(), ATTACKS))
