---
title: "Exercise: A Demo Backend With Its Own Scoreboard"
type: exercise
minutes: 45
hints:
  - "Read the response by block type: `text = \"\".join(b.text for b in response.content if b.type == \"text\")`. On current models a thinking block usually comes first, so `content[0].text` fails."
  - "Check `response.stop_reason == \"refusal\"` before you touch `content`. A refusal arrives as a normal response with empty content and a `stop_details.category`."
  - "Structured outputs: `output_config={\"effort\": \"low\", \"format\": {\"type\": \"json_schema\", \"schema\": SCHEMA}}`. Each field is an object with `value` and `quote`, both nullable (`\"type\": [\"string\", \"null\"]`), and every object sets `\"additionalProperties\": False`."
  - "In `ground`, run three loops of checks in order: any `value` that is None (missing), then any `quote` not found verbatim in the invoice (unsupported), then a shipment reference that isn't in `shipments` (unknown). Only then compare `total - agreed` with `max(5.0, 0.01 * agreed)`."
  - "In `scoreboard`, a case is correct when its verdict equals its label, so a justified abstain counts. `answered` is verdicts in (match, overcharge). `n` is always `len(cases)`: refusals and errors stay in."
---

Grace Liu, the principal architect who coaches this track (a fictional character), drops a folder in your inbox.

"Halberd Freight Group wants to see Claude audit carrier invoices. Their freight-audit team checks about 30,000 invoices a month against agreed rates, by hand. Imogen Pryce, the COO, will be in the room on Thursday, with Bas Achterberg, who runs freight audit. Bas sent us twenty real invoices from his backlog, anonymised, with the answer his team gave for each. Build the demo on those, not on anything we wrote. Three endpoints: **extract** the fields, **ground** them against the invoice and Halberd's records in code, **cite** the line each value came from. Then a **scoreboard** over all twenty. The scoreboard goes on screen next to the demo. If it says 85%, we show 85%, and we show the three it got wrong."

Halberd Freight Group, Imogen Pryce, Bas Achterberg and the carriers are fictional. `CASES` (20 labelled invoices), `SHIPMENTS` (Halberd's agreed rates by shipment reference), `FIELDS`, `MODEL` and `client` (the simulated `anthropic` SDK) are loaded for you. The simulator behaves like a real model on these documents: mostly right, sometimes wrong, and once it refuses.

## The data

Each case is `{"id": "H02", "invoice_text": "CARRIER INVOICE\nCarrier: ...", "label": "overcharge"}`. Labels are `"match"`, `"overcharge"` or `"abstain"` (the auditors couldn't answer from this document either). `SHIPMENTS["HFG-88240"]` is `{"agreed_eur": 2480.0, "lane": "Hamburg -> Prague"}`.

`FIELDS` is `["invoice_number", "shipment_ref", "total_eur"]`. The model returns each field as `{"value": ..., "quote": "the exact invoice line"}`.

## Your task

**1. `extract(client, invoice_text)`** calls `client.messages.create` with:

- the invoice text in the user message;
- `output_config` with an explicit `effort` and a `json_schema` `format` (no prefill, no forced `tool_choice`: both return 400 on current models);
- `max_tokens` of at least 1024, because it covers thinking as well as the answer.

It returns `{"status": "refused", "category": ...}` when `stop_reason` is `"refusal"`, `{"status": "error", "detail": ...}` if the stop reason isn't `"end_turn"` or the text isn't a JSON object, and otherwise `{"status": "ok", "fields": {...}}`.

**2. `ground(fields, invoice_text, shipments)`** is plain code. It returns `{"verdict", "reason", "difference_eur"}`. Run the checks in this order and stop at the first that applies:

- a field whose `value` is None: `abstain`, reason `"missing <field>"`;
- a field whose `quote` is empty or not found verbatim in the invoice: `abstain`, `"unsupported <field>"`;
- a shipment reference not in `shipments`: `abstain`, `"unknown shipment <ref>"`.

Otherwise `difference_eur` is `round(total - agreed, 2)`. If it is above `max(5.0, 0.01 * agreed)` the verdict is `overcharge` with reason `"invoiced 2760.00 vs agreed 2480.00"`, else `match` with reason `"within tolerance"`. `difference_eur` is None on every abstain.

**3. `cite(fields, invoice_text)`** returns `[{"field", "line", "quote"}]` in `FIELDS` order, with the 1-based number of the first line containing the quote (None if not found). Skip fields with no quote.

**4. `run_case(client, case, shipments)`** returns `{"id", "verdict", "reason", "citations"}`. A refusal gives verdict `"refused"`. An `anthropic.APIError` or an extract error gives `"error"`. Neither crashes the demo.

**5. `scoreboard(client, cases, shipments)`** returns:

| Key | Meaning |
|---|---|
| `n` | every case, always |
| `correct`, `accuracy` | verdict equals label (a justified abstain counts); `accuracy` is `round(correct / n, 3)` |
| `answered`, `answered_correct`, `precision_answered` | verdicts of match or overcharge, how many were right, and `round(right / answered, 3)` (None if nothing was answered) |
| `abstained`, `abstain_justified` | abstains, and abstains on cases labelled abstain |
| `refused`, `errors` | counts |
| `wrong` | ids where verdict differs from label, in case order |
| `rows` | one `run_case` result per case |
| `headline` | `"17/20 correct (85%); answered 15, abstained 4, refused 1, errors 0"` |

## Example

```python
>>> run_case(client, CASES[1], SHIPMENTS)["verdict"]
'overcharge'
>>> scoreboard(client, CASES, SHIPMENTS)["wrong"]
['H13', 'H14', 'H15']
```

Press **Run** to see the demo case and the board, then **Submit**.

## Before Thursday

Look at the three wrong cases. H13 is a refusal on a dangerous-goods lane. H14 is the dangerous one: the model quoted a real line (the line-haul subtotal), so grounding passed and the verdict was wrong. H15 abstained when it could have answered. Write down, in one sentence each, what you'd say about H14 in the room and what you'd change before a pilot. That is the "show a failure and its handling" moment from lesson 01, and the next lesson puts you in that room.
