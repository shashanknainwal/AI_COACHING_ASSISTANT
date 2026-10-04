---
title: "Normalization: Dates, Money, Phones, IDs, and Text"
type: reading
minutes: 18
---

> **By the end of this lesson you will be able to:**
> - Parse dates from several formats safely, and spot the ones you can't parse safely
> - Turn money strings like `"(1,204.50)"` into correct numbers
> - Normalize phone numbers, IDs, and free text into consistent forms
> - Follow the three rules that keep cleaning code trustworthy

## Three rules for cleaning code

Before the techniques, the principles. They matter more than any regex.

1. **Parse, don't guess.** Accept the formats you *know* appear, and treat everything else as invalid. A parser that "tries its best" will quietly turn `03/04/2026` into the wrong month and nobody will notice for weeks.
2. **Never silently drop data.** Every row you can't clean goes into a **reject list with a reason**. The customer needs to know what was excluded, and rejects often reveal a whole category of problem.
3. **Keep the raw value.** Store the cleaned value alongside the original (or keep the raw file untouched). When someone asks "why is this order dated March 4th?", you can show exactly what you started from.

## Dates

Dates are the most common and most dangerous mess.

**Multiple formats.** One export can contain `2026-03-04`, `03/04/2026`, `Mar 4 2026`, and `04-Mar-2026`, because different systems or users entered them. Handle this with an explicit list of formats, tried in order:

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

**Ambiguity.** Is `03/04/2026` March 4th (US) or April 3rd (most of the world)? Code can't know. Ask the customer which systems produce which format. You can also check the data: if any value in the column has a first number above 12 (`13/04/2026`), that column is day-first.

**Sentinel dates.** Values like `1900-01-01`, `1970-01-01` or `9999-12-31` usually mean "unknown," inserted by a system that didn't allow blanks. Treat dates outside a plausible range as missing.

**Time zones.** Timestamps without a time zone are a classic source of off-by-hours bugs. Ask which zone the system stores, and convert to UTC for any calculation across systems.

## Money

Money strings come with symbols, separators, and conventions:

| Raw | Meaning | Clean |
|---|---|---|
| `$1,204.50` | Dollar sign, thousands separator | `1204.50` |
| `USD 99` | Currency code prefix | `99.00` |
| `(45.00)` | Accounting notation for **negative** | `-45.00` |
| `1.204,50` | European format: `.` thousands, `,` decimal | `1204.50` |
| `$-3` | Negative after the symbol | `-3.00` |

The safe approach: detect parentheses (negative), remove known symbols and currency codes, remove thousands separators, then check that what's left is a valid number. If it isn't, reject.

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

Watch out for two things:

- **Locale.** Removing commas breaks European formats (`1.204,50` becomes `1.20450`). If a customer has European data, handle it explicitly, per source system.
- **Floating point.** `0.1 + 0.2` isn't exactly `0.3` in binary floating point. For reports, rounding to cents is fine. For anything that must reconcile to the cent (invoices, payments), use integer cents or Python's `decimal.Decimal`.

## Phone numbers

Store phones in **E.164** format: `+` then country code then number, digits only: `+15551234567`.

```
(555) 123-4567     -> +15551234567
555.123.4567       -> +15551234567
1-555-123-4567     -> +15551234567
555-123-4567 x22   -> +15551234567   (extension handled separately)
123-4567           -> invalid (too short)
```

The approach: cut off any extension (`x`, `ext`), keep only digits, then check the length (10 digits for US numbers, or 11 starting with 1). For international data, use a dedicated library (`phonenumbers` on your own machine); phone formats are very complex worldwide.

## IDs and keys

IDs look simple and break joins in subtle ways:

- **Whitespace:** `"A-1001 "` won't match `"A-1001"`. Always strip.
- **Case:** `a-1001` vs `A-1001`. Decide on one (usually uppercase) and apply it to both sides of every join.
- **Leading zeros:** Excel turns `00742` into `742`. If IDs are numeric strings, pad them back (`"742".zfill(5)`) and tell the customer about the Excel step in their export process.
- **Scientific notation:** Excel also turns long numbers into `1.23457E+11`. Those IDs are **unrecoverable** from that file; ask for a fresh export straight from the source system.

## Free text

- **Whitespace:** strip ends, and collapse runs of spaces: `" ".join(s.split())`.
- **Case:** use `s.casefold()` for comparisons (a stronger `lower()` that handles more languages).
- **Unicode look-alikes:** non-breaking spaces, curly quotes, and full-width characters look identical but don't compare equal. `unicodedata.normalize("NFKC", s)` fixes most of them.
- **Booleans in disguise:** `Y`, `yes`, `TRUE`, `1`, `x` all mean true. Map them explicitly, and reject anything unexpected.

## Putting it together: a cleaning function

A good cleaning function processes each row, collects every problem it finds, and returns two lists:

```python
clean, rejects = [], []
for row in rows:
    reasons = []
    date = parse_date(row["order_date"])
    if date is None:
        reasons.append("bad date")
    # ... other fields ...
    if reasons:
        rejects.append({"order_id": row["order_id"], "reasons": reasons})
    else:
        clean.append({...})
```

Collecting *all* reasons (not stopping at the first one) makes your reject report far more useful: the customer can fix a row once instead of three times.

### The same in pandas

```python
df["order_date"] = pd.to_datetime(df["order_date"], format="%Y-%m-%d", errors="coerce")
df["amount"] = pd.to_numeric(df["amount"].str.replace(r"[$,]", "", regex=True), errors="coerce")
rejects = df[df["order_date"].isna() | df["amount"].isna()]
```

`errors="coerce"` turns unparseable values into missing values (`NaT`/`NaN`) instead of raising. That's convenient, but it's exactly how data gets silently dropped. Always count and inspect what was coerced.

> **Key takeaways**
> - Parse known formats explicitly; reject the rest. Never guess ambiguous dates.
> - Never silently drop rows: collect rejects with *all* their reasons.
> - Money: handle parentheses, symbols and separators, and use integer cents or `Decimal` when it must reconcile exactly.
> - Normalize phones to E.164, IDs to stripped/uppercase, and text with strip, casefold, and NFKC.
