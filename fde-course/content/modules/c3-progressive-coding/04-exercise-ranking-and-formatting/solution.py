def _fmt(name, value):
    return f"{name}({value})"


def leaderboard(events, n):
    """Return up to n users as "name(total)", ranked by total (highest first),
    then by the time they reached that total (earliest first), then by name."""
    if n <= 0:
        return []
    totals = {}
    reached = {}
    for e in events:
        user = e["user"]
        totals[user] = totals.get(user, 0) + e["points"]
        reached[user] = max(reached.get(user, e["t"]), e["t"])
    ranked = sorted(totals, key=lambda u: (-totals[u], reached[u], u))
    return [_fmt(u, totals[u]) for u in ranked[:n]]


def window_totals(events, start, end):
    """Return {user: total points} for events with start <= t < end."""
    totals = {}
    for e in events:
        if start <= e["t"] < end:
            totals[e["user"]] = totals.get(e["user"], 0) + e["points"]
    return totals


# --- Try it out (not graded) ---
events = [
    {"user": "maya", "points": 30, "t": 1},
    {"user": "leo", "points": 50, "t": 2},
    {"user": "maya", "points": 20, "t": 4},
    {"user": "ana", "points": 50, "t": 5},
    {"user": "leo", "points": 10, "t": 9},
]

print("Top 3:", leaderboard(events, 3))
print("Window [2, 5):", window_totals(events, 2, 5))
