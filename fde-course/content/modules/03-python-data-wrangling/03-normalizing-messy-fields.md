---
title: "Normalization: Dates, Money, Phones, IDs, and Text"
type: reading
minutes: 3
---

> **By the end of this lesson you will be able to:**
> - Parse dates from several formats, and spot the ones you can't parse safely
> - Turn money strings like `"(1,204.50)"` into correct numbers
> - Normalize phones, IDs and free text, and keep cleaning code trustworthy

Cobalt's orders export mixes three date formats, writes refunds as `(45.00)`, and has IDs that Excel stripped of leading zeros. Owen will put your totals in a board pack, so every number has to be one you can defend.

## Three rules for cleaning code

1. **Parse, don't guess.** Accept formats you know appear; everything else is invalid. A parser that "tries its best" quietly turns `03/04/2026` into the wrong month.
2. **Never silently drop data.** Every row you can't clean goes into a **reject list with a reason**. Rejects often reveal a whole category of problem.
3. **Keep the raw value** next to the cleaned one, so you can show where a value came from.

## Dates

```python
from datetime import datetime

DATE_FORMATS = ["%Y-%m-%d", "%m/%d/%Y", "%b %d %Y", "%d-%b-%Y"]

def parse_date(text):
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text.strip(), fmt).date()
        except ValueError:
            continue
    return None   # unknown format -> reject, don't guess
```

- **Ambiguity.** `03/04/2026` parses either way, so no error warns you. Ask which systems use which format. If any value has a first number above 12, that column is day-first.
- **Sentinel dates** like `1900-01-01` or `9999-12-31` usually mean "unknown". Treat out-of-range dates as missing.
- **Time zones.** Ask which zone each system stores; convert to UTC before comparing across systems.

## Money

| Raw | Meaning | Clean |
|---|---|---|
| `$1,204.50` | Symbol, thousands separator | `1204.50` |
| `USD 99` | Currency code prefix | `99.00` |
| `(45.00)` | Accounting notation for **negative** | `-45.00` |
| `1.204,50` | European: `.` thousands, `,` decimal | `1204.50` |
| `$-3` | Negative after the symbol | `-3.00` |

```python
import re

def parse_money(text):
    s = text.strip()
    negative = s.startswith("(") and s.endswith(")")
    s = s.strip("()").replace("$", "").replace("USD", "").replace(",", "").strip()
    if not re.fullmatch(r"-?\d+(\.\d+)?", s):
        return None
    value = float(s)
    return round(-value if negative else value, 2)
```

- **Locale.** Stripping commas breaks `1.204,50`. Handle European sources explicitly, per system.
- **Floating point.** `0.1 + 0.2 != 0.3`. For anything that must reconcile to the cent, use integer cents or `decimal.Decimal`.

## Phones, IDs and text

**Phones:** store as **E.164** (`+15551234567`). Cut off extensions (`x22`, `ext`), keep digits, check length (10 digits, or 11 starting with 1, for US). `123-4567` is invalid. For international data use the `phonenumbers` library.

**IDs** break joins quietly:
- Strip whitespace: `"A-1001 "` won't match `"A-1001"`.
- Pick one case (usually upper) for both sides of every join.
- Excel turns `00742` into `742`: pad back with `zfill(5)` and tell the customer about the Excel step.
- Excel's `1.23457E+11` is **unrecoverable**; ask for a fresh export from the source system.

**Text:** `" ".join(s.split())` collapses spaces; `casefold()` for comparisons; `unicodedata.normalize("NFKC", s)` fixes non-breaking spaces and full-width look-alikes. Map booleans (`Y`, `yes`, `TRUE`, `1`, `x`) explicitly and reject anything else.

## Collect every reason

```python
clean, rejects = [], []
for row in rows:
    reasons = []
    if parse_date(row["order_date"]) is None:
        reasons.append("bad date")
    # ... other fields ...
    if reasons:
        rejects.append({"order_id": row["order_id"], "reasons": reasons})
    else:
        clean.append({...})
```

Collecting all reasons, not just the first, lets the customer fix a row once. In pandas, `errors="coerce"` turns bad values into `NaT`/`NaN` without raising: convenient, and exactly how data gets silently dropped. Always count what was coerced.

> **Key takeaways**
> - Parse known formats; reject the rest. Never guess ambiguous dates.
> - Rejects carry all their reasons and go back to the customer.
> - Money: parentheses mean negative; use cents or `Decimal` when it must reconcile.
> - Phones to E.164, IDs stripped and one case, text stripped, casefolded, NFKC.
