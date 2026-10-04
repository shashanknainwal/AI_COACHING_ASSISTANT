"""Pinecrest Fitness: a small gym-chain database used in Module 5.

`connect()` returns an in-memory SQLite connection with six tables:

    locations(id, name, city, opened_on)
    plans(id, name, monthly_price)
    members(id, first_name, last_name, email, phone, home_location_id, joined_on)
    subscriptions(id, member_id, plan_id, start_date, end_date, status)
    payments(id, member_id, amount, paid_on)
    visits(id, member_id, location_id, visited_at)

The data is generated with a tiny deterministic generator (not `random`), so it
is identical in every Python version and every browser.
"""

import sqlite3
from datetime import date, timedelta

SCHEMA = """
CREATE TABLE locations (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    opened_on TEXT NOT NULL
);
CREATE TABLE plans (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    monthly_price REAL NOT NULL
);
CREATE TABLE members (
    id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    home_location_id INTEGER REFERENCES locations(id),
    joined_on TEXT NOT NULL
);
CREATE TABLE subscriptions (
    id INTEGER PRIMARY KEY,
    member_id INTEGER NOT NULL REFERENCES members(id),
    plan_id INTEGER NOT NULL REFERENCES plans(id),
    start_date TEXT NOT NULL,
    end_date TEXT,
    status TEXT NOT NULL CHECK (status IN ('active', 'cancelled'))
);
CREATE TABLE payments (
    id INTEGER PRIMARY KEY,
    member_id INTEGER NOT NULL REFERENCES members(id),
    amount REAL NOT NULL,
    paid_on TEXT NOT NULL
);
CREATE TABLE visits (
    id INTEGER PRIMARY KEY,
    member_id INTEGER NOT NULL REFERENCES members(id),
    location_id INTEGER NOT NULL REFERENCES locations(id),
    visited_at TEXT NOT NULL
);
CREATE INDEX idx_visits_member ON visits(member_id);
CREATE INDEX idx_payments_member ON payments(member_id);
"""

LOCATIONS = [
    (1, "Downtown", "Portland", "2019-05-01"),
    (2, "Riverside", "Portland", "2020-09-15"),
    (3, "Northgate", "Vancouver", "2022-03-01"),
    (4, "Lakeshore", "Beaverton", "2025-10-01"),
]
PLANS = [(1, "Basic", 29.0), (2, "Plus", 49.0), (3, "Premium", 79.0)]

_FIRST = ["Ava", "Ben", "Chloe", "Dev", "Elena", "Femi", "Grace", "Hiro", "Isla", "Jon",
          "Kara", "Leo", "Maya", "Nate", "Olu", "Priya", "Quinn", "Rosa", "Sam", "Tara"]
_LAST = ["Nguyen", "Smith", "Garcia", "Okafor", "Kim", "Patel", "Brown", "Silva", "Cohen", "Ito",
         "Lopez", "Walsh", "Moreau", "Haddad", "Novak"]

START = date(2025, 10, 1)
END = date(2026, 3, 31)


class _Gen:
    """Linear congruential generator: same numbers on every platform."""

    def __init__(self, seed):
        self.state = seed

    def next(self):
        self.state = (self.state * 1103515245 + 12345) % 2147483648
        return self.state

    def below(self, n):
        return self.next() % n

    def chance(self, pct):
        return self.below(100) < pct


def _month_starts(first, last):
    d = date(first.year, first.month, 1)
    while d <= last:
        yield d
        d = date(d.year + (d.month == 12), d.month % 12 + 1, 1)


def _build_rows():
    g = _Gen(20260310)
    members, subscriptions, payments, visits = [], [], [], []
    location_weights = [1, 1, 1, 2, 2, 2, 3, 3, 4]   # Lakeshore is new and smaller
    for mid in range(1, 121):
        loc = location_weights[g.below(len(location_weights))]
        opened = date.fromisoformat(LOCATIONS[loc - 1][3])
        joined = START + timedelta(days=g.below((END - START).days - 20))
        if joined < opened:
            joined = opened + timedelta(days=g.below(30))
        first, last = _FIRST[g.below(len(_FIRST))], _LAST[g.below(len(_LAST))]
        email = f"{first.lower()}.{last.lower()}{mid}@example.com" if not g.chance(6) else None
        phone = f"503-555-{1000 + g.below(9000):04d}" if not g.chance(10) else None
        members.append((mid, first, last, email, phone, loc, joined.isoformat()))

        plan = 1 + (g.below(10) >= 5) + (g.below(10) >= 8)
        # Riverside has a churn problem: its members cancel much more often.
        churn_pct = 45 if loc == 2 else 15
        cancelled = g.chance(churn_pct)
        end = None
        if cancelled:
            end = joined + timedelta(days=30 + g.below(80))
            if end > END:
                end, cancelled = None, False
        subscriptions.append((mid, mid, plan, joined.isoformat(), end.isoformat() if end else None,
                              "cancelled" if cancelled else "active"))

        price = PLANS[plan - 1][2]
        last_day = end or END
        for m in _month_starts(joined, last_day):
            pay_day = max(m, joined)
            if pay_day <= last_day:
                payments.append((len(payments) + 1, mid, price, pay_day.isoformat()))

        if g.chance(8):
            continue   # signed up, never came in
        per_week = 1 + g.below(4) if loc != 2 else g.below(3)
        d = joined
        while d <= last_day:
            for _ in range(per_week):
                day = d + timedelta(days=g.below(7))
                if day <= last_day:
                    where = loc if not g.chance(10) else 1 + g.below(4)
                    if date.fromisoformat(LOCATIONS[where - 1][3]) > day:
                        where = loc
                    visits.append((len(visits) + 1, mid, where, f"{day.isoformat()} {6 + g.below(15):02d}:{g.below(60):02d}"))
            d += timedelta(days=7)
    visits.sort(key=lambda v: (v[3], v[1]))
    visits = [(i + 1, m, l, t) for i, (_, m, l, t) in enumerate(visits)]
    return members, subscriptions, payments, visits


_ROWS = None


def connect():
    """A fresh in-memory copy of the Pinecrest database."""
    global _ROWS
    if _ROWS is None:
        _ROWS = _build_rows()
    members, subscriptions, payments, visits = _ROWS
    con = sqlite3.connect(":memory:")
    con.executescript(SCHEMA)
    con.executemany("INSERT INTO locations VALUES (?, ?, ?, ?)", LOCATIONS)
    con.executemany("INSERT INTO plans VALUES (?, ?, ?)", PLANS)
    con.executemany("INSERT INTO members VALUES (?, ?, ?, ?, ?, ?, ?)", members)
    con.executemany("INSERT INTO subscriptions VALUES (?, ?, ?, ?, ?, ?)", subscriptions)
    con.executemany("INSERT INTO payments VALUES (?, ?, ?, ?)", payments)
    con.executemany("INSERT INTO visits VALUES (?, ?, ?, ?)", visits)
    con.commit()
    return con
