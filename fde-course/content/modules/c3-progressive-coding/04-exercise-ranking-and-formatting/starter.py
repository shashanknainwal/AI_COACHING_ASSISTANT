def leaderboard(events, n):
    """Return up to n users as "name(total)", ranked by total (highest first),
    then by the time they reached that total (earliest first), then by name."""
    # TODO
    pass


def window_totals(events, start, end):
    """Return {user: total points} for events with start <= t < end."""
    # TODO
    pass


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
