"""Hidden setup: 20 fictional carrier contracts for Cindervale Freight, and a scripted simulator.

Every carrier, clause and number here is made up.
"""
import json
import re

import anthropic
from anthropic import _sim

WORKER_MODEL = "claude-haiku-5-5"
LEAD_MODEL = "claude-opus-5-5"
WORKER_BUDGET = 6000  # max input tokens one worker may send
PRICES = {  # USD per million tokens (Haiku 5.5 rate applies to prompts up to 100K tokens)
    "claude-haiku-5-5": {"input": 0.10, "output": 0.50},
    "claude-opus-5-5": {"input": 4.00, "output": 20.00},
}

WORKER_SYSTEM = (
    "You extract terms from one carrier contract for Cindervale Freight's procurement team. "
    "Report only what the contract says. Use null for a term the contract doesn't state."
)
LEAD_SYSTEM = (
    "You write a short procurement briefing from structured contract findings. "
    "Name every contract that was not reviewed and say why."
)

REPORT_SCHEMA = {
    "type": "object",
    "properties": {
        "contract_id": {"type": "string"},
        "carrier": {"type": "string"},
        "liability_cap_eur": {"type": ["integer", "null"]},
        "termination_notice_days": {"type": ["integer", "null"]},
        "auto_renew": {"type": ["boolean", "null"]},
        "fuel_surcharge_cap_pct": {"type": ["number", "null"]},
    },
    "required": ["contract_id", "carrier", "liability_cap_eur", "termination_notice_days", "auto_renew", "fuel_surcharge_cap_pct"],
    "additionalProperties": False,
}

_CARRIERS = ["Brask Haulage", "Ostrander Lines", "Pellworth Cargo", "Verrin Transport", "Moll & Daske",
             "Tavish Road Freight", "Kordel Logistik", "Sablon Express", "Hartwick Rail", "Quenby Trucking"]
_FILLER = (
    "The Carrier shall perform the Services with due care and in accordance with applicable law. "
    "Proof of delivery shall be provided electronically within 24 hours. Claims for visible damage "
    "must be noted on the consignment note at delivery. "
)

TERMS = {}
CONTRACTS = {}
for i in range(20):
    cid = f"CC-{101 + i}"
    t = {
        "contract_id": cid,
        "carrier": _CARRIERS[i % 10],
        "liability_cap_eur": [250000, 40000, 120000, 75000, 30000][i % 5],
        "termination_notice_days": [30, 60, 120, 90, 45][(i * 2) % 5],
        "auto_renew": i % 3 == 0,
        "fuel_surcharge_cap_pct": [8.0, 12.5, 18.0, 10.0][i % 4],
    }
    TERMS[cid] = t
    text = (
        f"CARRIER SERVICES AGREEMENT {cid}\nBetween Cindervale Freight B.V. and {t['carrier']}.\n"
        + _FILLER * 3
        + f"\n4.2 Liability. The Carrier's aggregate liability per event is capped at EUR {t['liability_cap_eur']:,}.\n"
        + f"9.1 Term. Either party may terminate on {t['termination_notice_days']} days' written notice.\n"
        + ("9.3 Renewal. This Agreement renews automatically for successive 12-month terms.\n" if t["auto_renew"]
           else "9.3 Renewal. This Agreement expires at the end of the term unless renewed in writing.\n")
        + f"Schedule B. Fuel surcharge adjustments are capped at {t['fuel_surcharge_cap_pct']}% per quarter.\n"
        + _FILLER * 2
    )
    if cid == "CC-113":
        text += "\nAPPENDIX C: RATE TABLES\n" + ("Lane RTM-LYS 20ft EUR 1,840; 40ft EUR 2,310. " * 1400)
    CONTRACTS[cid] = text

RISK_RULES = "liability cap under EUR 50,000; notice over 90 days; auto-renew with notice over 60 days; fuel cap over 15%"

# The contracts that should be flagged under RISK_RULES (the answer key for the eval).
TRUTH_RISKY = sorted(
    cid for cid, t in TERMS.items()
    if t["liability_cap_eur"] < 50000 or t["termination_notice_days"] > 90
    or (t["auto_renew"] and t["termination_notice_days"] > 60) or t["fuel_surcharge_cap_pct"] > 15
)

_FAILING = "CC-117"          # its worker's API calls fail with 529 Overloaded every time
_BASELINE_MISSES = ["CC-109", "CC-110", "CC-111"]  # scripted: the long single-context run skips these


def _text_of(params):
    out = []
    for m in params["messages"]:
        c = m["content"]
        out.append(c if isinstance(c, str) else " ".join(b.get("text", "") for b in c if isinstance(b, dict)))
    return "\n".join(out)


def _respond(params):
    text = _text_of(params)
    ids = sorted(set(re.findall(r"CC-\d{3}", text)))
    if params["model"] == WORKER_MODEL:
        if len(ids) != 1:
            return json.dumps({"contract_id": "MIXED", "carrier": "unknown", "liability_cap_eur": None,
                               "termination_notice_days": None, "auto_renew": None, "fuel_surcharge_cap_pct": None})
        if ids[0] == _FAILING:
            return _sim.overloaded()
        return [_sim.thinking(""), _sim.text(json.dumps(TERMS[ids[0]]))]
    if len(ids) >= 15 and "<contract id=" in text:  # the single-agent baseline: all contracts in one context
        rows = [TERMS[c] for c in ids if c not in _BASELINE_MISSES]
        return [_sim.thinking(""), _sim.text(json.dumps(rows))]
    return [_sim.thinking(""), _sim.text(
        "Procurement briefing: flagged contracts are listed with the terms that triggered them. "
        "Contracts not reviewed are listed separately and need a manual check before renewal season.")]


_sim.set_responder(_respond)
client = anthropic.Anthropic()


def run_single_agent(client):
    """The baseline: one Opus 5.5 call with all 20 contracts in its context."""
    body = "\n\n".join(f"<contract id=\"{cid}\">\n{txt}\n</contract>" for cid, txt in CONTRACTS.items())
    r = client.messages.create(
        model=LEAD_MODEL, max_tokens=16000, system=WORKER_SYSTEM,
        output_config={"effort": "medium"},
        messages=[{"role": "user", "content": body + "\n\nReturn a JSON list with one report per contract."}],
    )
    text = "".join(b.text for b in r.content if b.type == "text")
    return {"reports": json.loads(text), "usage": {"input_tokens": r.usage.input_tokens, "output_tokens": r.usage.output_tokens}}
