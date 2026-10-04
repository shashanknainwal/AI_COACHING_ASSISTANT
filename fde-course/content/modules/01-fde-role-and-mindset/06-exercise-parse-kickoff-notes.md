---
title: "Exercise: Turn Kickoff Notes into Structured Data"
type: exercise
minutes: 25
hints:
  - "Split the text into lines with `text.splitlines()` and `.strip()` each one. Skip empty lines."
  - "Normalize a header by lowercasing it and removing spaces and the trailing colon: `line.lower().replace(\" \", \"\").rstrip(\":\")`. Then compare against `\"attendees\"`, `\"goals\"`, `\"risks\"`, `\"actionitems\"`."
  - "Keep a `section` variable that remembers which header you saw last. Bullet lines (starting with `-` or `*`) belong to the current section."
  - "For a stakeholder line like `Dana Ruiz (VP Operations) [sponsor]`, find the text between `(` and `)` for the title, and between `[` and `]` for the role. If there's no `[`, the role is `None`."
  - "For an action like `[Sam] Share sandbox credentials`, the owner is between the first `[` and `]`, and the task is everything after `]`, stripped."
  - "`missing_roles` should return the required roles in the order `[\"sponsor\", \"champion\"]`, keeping only those no stakeholder has."
---

Good FDEs take structured notes, and great FDEs turn them into structured **data**. Once your notes are data you can generate the engagement brief, track action items, and spot gaps (like a missing sponsor) automatically.

The customer's project manager just emailed you their notes from the Brightline Health kickoff. They roughly follow a template, but people typed them quickly: headers have inconsistent capitals and spacing, bullets use `-` or `*`, and there are stray blank lines.

```text
Customer: Brightline Health
Date: 2026-03-02

ATTENDEES:
- Dana Ruiz (VP Operations) [sponsor]
-   Sam Okafor (IT Director) [blocker]
* Priya Nair (Intake Lead) [Champion]
- Leo Park (Intake Specialist)

goals :
- Cut referral intake from 3 days to same-day
- Reduce manual data entry errors

Risks:
- EHR vendor API access needs ~6 weeks of approval

Action Items:
- [Sam] Share sandbox credentials by Friday
- [FDE]   Profile one month of fax referrals
```

## Your task

**1. `parse_notes(text)`** returns a dictionary with exactly these keys:

```python
{
    "customer": "Brightline Health",
    "date": "2026-03-02",
    "stakeholders": [
        {"name": "Dana Ruiz", "title": "VP Operations", "role": "sponsor"},
        {"name": "Sam Okafor", "title": "IT Director", "role": "blocker"},
        {"name": "Priya Nair", "title": "Intake Lead", "role": "champion"},
        {"name": "Leo Park", "title": "Intake Specialist", "role": None},
    ],
    "goals": ["Cut referral intake from 3 days to same-day", "Reduce manual data entry errors"],
    "risks": ["EHR vendor API access needs ~6 weeks of approval"],
    "actions": [
        {"owner": "Sam", "task": "Share sandbox credentials by Friday"},
        {"owner": "FDE", "task": "Profile one month of fax referrals"},
    ],
}
```

Rules:

- Section headers are `Attendees`, `Goals`, `Risks`, and `Action Items`, in **any capitalization**, with optional spaces before the colon. Sections can appear in any order and any section may be missing (use an empty list).
- Bullets start with `-` or `*`. Strip the bullet and surrounding whitespace.
- `Customer:` and `Date:` lines give single values (use `None` if missing). Their keys are also case-insensitive.
- A stakeholder's **role** is lowercased. If a stakeholder has no `[role]`, use `None`.

**2. `missing_roles(parsed)`** returns the list of required roles, `["sponsor", "champion"]`, that **no** stakeholder has, in that order. With the notes above it returns `[]`. If nobody is tagged sponsor it returns `["sponsor"]`.

> **Why this matters:** In the last lesson you learned that an engagement with a champion but no sponsor usually stalls. A tiny check like `missing_roles` is the kind of tooling FDE teams build to catch that in week one, not month three.
