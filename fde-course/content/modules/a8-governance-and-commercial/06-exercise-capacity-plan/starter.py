# EXAMPLE_LIMITS, PRIORITY_RATES and BRACKENRIDGE_WORKLOAD are already defined
# for you (see the lesson). The limits are made-up placeholders: never
# hard-code them. Your functions receive everything as arguments.
import math

METRICS = ("rpm", "itpm", "otpm")


def capacity_plan(workload, peak_factor, limits, headroom=0.8):
    """Return one row per platform (sorted by name) with peak needs, utilization and flags."""
    # TODO: validate inputs, work out peak calls per minute, counted input
    # tokens per call, then compare with each platform's limits.
    pass


def priority_burndown(workload, peak_factor, commitment, rates):
    """Return how a peak minute burns a commitment measured in ITPM/OTPM."""
    # TODO
    pass


# --- Try it out (this part isn't graded) ---
for row in capacity_plan(BRACKENRIDGE_WORKLOAD, 3.0, EXAMPLE_LIMITS) or []:
    print(row["platform"], row["status"], row["utilization"], row["breaches"])

print(priority_burndown(BRACKENRIDGE_WORKLOAD, 3.0, {"itpm": 3_000_000, "otpm": 500_000}, PRIORITY_RATES))
