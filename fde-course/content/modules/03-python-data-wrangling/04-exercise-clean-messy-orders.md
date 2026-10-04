---
title: "Exercise: Clean a Messy Orders File"
type: exercise
minutes: 30
hints:
  - "`parse_date`: return None for missing values. Then loop over `DATE_FORMATS`, try `datetime.strptime(text.strip(), fmt).date()`, and `continue` on `ValueError`. Check the parsed date is within `MIN_DATE`..`MAX_DATE` before returning `.isoformat()`."
  - "`parse_money`: detect `negative = s.startswith(\"(\") and s.endswith(\")\")`, then remove `(`, `)`, `$`, `USD`, commas and spaces. Validate with `re.fullmatch(r\"-?\\d+(\\.\\d+)?\", s)`."
  - "`normalize_phone`: cut the extension first with `re.split(r\"x|ext\", text.lower())[0]`, then keep digits with `re.sub(r\"\\D\", \"\", ...)`."
  - "In `clean_orders`, keep a `seen` set of order IDs that were **accepted**. A row whose ID is already in `seen` gets the reason \"duplicate order_id\"."
  - "Collect all reasons for a row before deciding. Only add the ID to `seen` when the row is accepted."
  - "A phone that's missing is fine (store None). A phone that's present but invalid is the reason \"bad phone\"."
---

Cobalt's order export comes from two systems that were merged years ago. You need clean orders to compute revenue per account, and a reject list to send back to Cobalt's finance team.

## Your task

**1. `parse_date(text)`** returns the date as an ISO string `"YYYY-MM-DD"`, or `None`.
- Return `None` for missing values (use `is_missing`, given in the starter).
- Try each format in `DATE_FORMATS`, in order.
- Dates before `MIN_DATE` or after `MAX_DATE` are sentinels or typos: return `None`.

**2. `parse_money(text)`** returns a float rounded to 2 decimals, or `None`.
- Missing → `None`.
- Wrapped in parentheses → negative: `"(45.00)"` → `-45.0`.
- Remove `$`, `USD`, commas, and spaces. What's left must match an optional minus sign, digits, and an optional decimal part. Otherwise return `None`.

**3. `normalize_phone(text)`** returns an E.164 US number like `"+15551234567"`, or `None`.
- Missing → `None`.
- Ignore everything from `x` or `ext` onward (case-insensitive).
- Keep the digits. 10 digits → `"+1"` + digits. 11 digits starting with `1` → `"+"` + digits. Anything else → `None`.

**4. `clean_orders(rows)`** returns a tuple `(clean, rejects)`.
- Each input row has `order_id`, `account_id`, `order_date`, `amount`, `phone`.
- Check each row and collect **all** reasons, in this order:
  - `"bad date"` if `parse_date` returns `None`
  - `"bad amount"` if `parse_money` returns `None`
  - `"bad phone"` if the phone is **present** (not missing) but `normalize_phone` returns `None`
  - `"duplicate order_id"` if an earlier row with the same (stripped) order ID was **accepted**
- Rejected rows become `{"order_id": <stripped id>, "reasons": [...]}`.
- Accepted rows become:

```python
{"order_id": "O-501", "account_id": "A-1001", "order_date": "2026-03-04", "amount": 1204.5, "phone": "+15551234567"}
```

with `order_id` stripped, `account_id` stripped and **uppercased**, and `phone` set to `None` when missing.

Press **Run** to clean Cobalt's sample, then **Submit**.

> **The reject list is a deliverable.** Send it to the customer's finance team with a one-line summary per reason ("4 orders have dates we couldn't read"). Fixing data at the source is always better than fixing it in your pipeline.
