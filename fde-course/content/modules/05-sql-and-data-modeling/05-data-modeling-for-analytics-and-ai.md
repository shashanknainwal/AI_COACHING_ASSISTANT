---
title: Data Modeling for Analytics and AI
type: reading
minutes: 16
---

> **By the end of this lesson you will be able to:**
> - State the **grain** of any table, and use it to avoid double counting
> - Explain facts, dimensions, and the star schema in plain language
> - Build a "metrics layer" so every dashboard and AI feature uses the same definitions
> - Shape data so LLM features (retrieval, text-to-SQL) work well

## Why an FDE needs to think about modeling

You'll rarely design a customer's core database. But you'll constantly create *derived* tables and views: for a pilot dashboard, for an AI assistant's retrieval index, for the weekly metrics email. Bad modeling here produces wrong numbers that look right, and every downstream AI feature inherits them.

## Grain: the most important word in data modeling

The **grain** of a table is what one row represents. Say it out loud before you write any query:

| Table | Grain |
|---|---|
| `visits` | One row per check-in |
| `payments` | One row per payment |
| `members` | One row per member |
| A view `location_monthly` | One row per location per month |

Most double-counting bugs come from joining tables of different grains without noticing. Joining `payments` (per payment) to `visits` (per visit) through `member_id` creates one row per payment *per visit*. Aggregate each to a common grain first (for example, per location per month), then join.

## Facts and dimensions

Analytical models usually split data into two kinds of tables:

- **Facts** record events or measurements: visits, payments, orders, tickets. They're long, they grow fast, and they hold numbers you sum or count.
- **Dimensions** describe the things involved: members, locations, plans, products. They're shorter and hold attributes you filter and group by.

A **star schema** puts fact tables in the middle and dimensions around them:

```
               ┌──────────┐
               │  plans   │
               └────┬─────┘
┌───────────┐  ┌────┴─────┐  ┌──────────┐
│ locations ├──┤ payments ├──┤ members  │
└───────────┘  └──────────┘  └──────────┘
        \                      /
         └──── visits (fact) ─┘
```

Pinecrest's database is already close to this. Most warehouses (Snowflake, BigQuery, Redshift) are organized this way, often built with a tool like dbt.

## Normalized vs. denormalized

| | Normalized | Denormalized |
|---|---|---|
| Shape | Each fact stored once; join to get context | Context copied into wide rows |
| Good for | Applications that write data (no inconsistency) | Analytics and AI (fast, simple reads) |
| Risk | Complex queries | Copies drift out of date |

Operational systems are normalized. For analytics and AI features, it's common to build **denormalized views** on top: one wide, well-named row per entity or per period.

## History: the slowly changing dimension

When a member moves from Riverside to Downtown, do last year's visits count for Riverside or Downtown? If `members.home_location_id` is simply overwritten, history silently changes: last quarter's Riverside numbers shift the next time you run the report.

The standard fix (an SCD "type 2" table) keeps a row per version with `valid_from` and `valid_to` dates. You don't need to build one in every pilot, but you must **know whether the customer's data overwrites history**, and say so when you report trends.

## The metrics layer

The worst meeting in analytics is "your number doesn't match my number." It happens when two people compute "active members" or "revenue" slightly differently.

A **metrics layer** defines each metric once, in one place, and everything reads from it:

```sql
CREATE VIEW v_location_monthly_revenue AS
SELECT l.name AS location, strftime('%Y-%m', p.paid_on) AS month, ROUND(SUM(p.amount), 2) AS revenue
FROM payments p
JOIN members m   ON m.id = p.member_id
JOIN locations l ON l.id = m.home_location_id
GROUP BY location, month;
```

Now the dashboard, the weekly email, and the AI assistant all use `v_location_monthly_revenue`. If the definition changes (say, refunds should be excluded), you change it in one place. In larger setups the same idea appears as dbt models or a "semantic layer," but plain SQL views are a perfectly good start.

Good metrics-layer habits:

- **One view per grain**, named for it: `v_location_monthly_*`, `v_member_daily_*`.
- **Aggregate facts separately**, then join the aggregates (no fan-out).
- **Handle division by zero** with `NULLIF(denominator, 0)`, so an empty month gives `NULL` instead of an error or an infinite value.
- **Document every column** in a data dictionary: definition, source, owner.

## Modeling for AI features

LLM features have their own modeling needs:

**For retrieval (RAG, Module 7),** build one document per entity or per meaningful unit, with context included. A member-history document like *"Maya Okafor, Riverside, Plus plan since Nov 2025, 3 visits in the last 60 days, cancelled Mar 2"* retrieves far better than raw rows split across six tables.

**For text-to-SQL (later in this module),** give the model clean, well-named views rather than raw operational tables. `v_location_kpis.revenue_per_visitor` is unambiguous; `pmt.amt` joined through three tables is not. Fewer, clearer tables mean fewer wrong queries.

**For features and scoring,** build one row per entity at a clear point in time (for example, "member as of the 1st of the month") so you never accidentally use future information.

> **Key takeaways**
> - Always state the grain; join tables only at a common grain.
> - Facts are events you aggregate; dimensions describe things you group by.
> - A metrics layer (views) defines each metric once, so every consumer agrees.
> - For AI: entity documents for retrieval, clean named views for text-to-SQL, point-in-time rows for features.
