---
title: Data Modeling for Analytics and AI
type: reading
minutes: 6
---

> **By the end of this lesson you will be able to:**
> - State the **grain** of any table and use it to avoid double counting
> - Explain facts, dimensions and the star schema in plain language
> - Build a metrics layer so every dashboard and AI feature agrees
> - Shape data so LLM features work well

Pinecrest's revenue dashboard and the weekly email show different numbers for the same month, and Tom wants to know which one is right. You rarely design a customer's core database, but you build the views that dashboards and AI features read, and bad modeling there gives wrong numbers that look right.

## Grain: what one row represents

| Table | Grain |
|---|---|
| `visits` | One check-in |
| `payments` | One payment |
| `members` | One member |
| View `location_monthly` | One location per month |

State the grain before every query. Joining `payments` to `visits` through `member_id` creates one row per payment *per visit*. Aggregate each to a common grain first (say, location per month), then join.

## Facts, dimensions, star schema

- **Facts**: events you sum or count (visits, payments).
- **Dimensions**: things you filter and group by (members, locations, plans).

A **star schema** puts facts in the middle with dimensions around them; most warehouses are built this way. Operational systems are **normalized** (each fact stored once, safe for writes). For analytics and AI, build **denormalized views** on top: wide, well-named rows that are simple to read, at the cost of copies that can drift.

## History: the slowly changing dimension

If a member moves from Riverside to Downtown and `members.home_location_id` is overwritten, last quarter's Riverside numbers change on the next run. An SCD "type 2" table keeps a row per version with `valid_from` / `valid_to`. At minimum, **know whether the data overwrites history** and say so when you report trends.

## The metrics layer

When two people compute "revenue" differently, numbers disagree. A **metrics layer** defines each metric once:

```sql
CREATE VIEW v_location_monthly_revenue AS
SELECT l.name AS location, strftime('%Y-%m', p.paid_on) AS month, ROUND(SUM(p.amount), 2) AS revenue
FROM payments p
JOIN members m   ON m.id = p.member_id
JOIN locations l ON l.id = m.home_location_id
GROUP BY location, month;
```

Dashboard, email and AI assistant all read this view, so a definition change (exclude refunds) happens in one place. dbt models and semantic layers are the same idea at scale.

Habits: one view per grain, named for it (`v_location_monthly_*`); aggregate facts separately, then join; `NULLIF(denominator, 0)` so an empty month gives `NULL`, not an error; document every column's definition, source and owner.

## Modeling for AI features

- **Retrieval (Module 7):** one document per entity with context included. *"Maya Okafor, Riverside, Plus plan since Nov 2025, 3 visits in the last 60 days, cancelled Mar 2"* beats rows across six tables.
- **Text-to-SQL (lesson 9):** give the model clean named views. `v_location_kpis.revenue_per_visitor` is unambiguous; `pmt.amt` through three joins is not.
- **Features:** one row per entity at a point in time, so you never use future information.

> **Key takeaways**
> - State the grain; join only at a common grain.
> - Facts are events you aggregate; dimensions are things you group by.
> - A metrics layer defines each metric once, so every consumer agrees.
> - For AI: entity documents, clean named views, point-in-time rows.
