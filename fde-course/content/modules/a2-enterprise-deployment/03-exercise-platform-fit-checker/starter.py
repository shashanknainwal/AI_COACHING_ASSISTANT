# PLATFORMS and NON_ZDR_FEATURES are already defined for you (see the lesson).
# They are an ILLUSTRATIVE capability table, so don't hard-code their values:
# your functions receive the table as an argument.


def check_platform(name, platform, requirements, non_zdr_features):
    """Return {"platform", "eligible", "reasons", "gaps", "open_items"} for one platform."""
    # TODO: run the checks in this order: procurement, processor, geo,
    # features, zdr (+ conflicts), private_network.
    pass


def shortlist(platforms, requirements, non_zdr_features):
    """Return {"eligible": [names, best first], "blocked": {name: gaps}}."""
    # TODO
    pass


# --- Try it out (this part isn't graded) ---
granite_bank = {
    "procurement": "aws",
    "geo": "us",
    "features": ["prompt_caching", "batches"],
    "zdr": False,
    "private_network": True,
}

for name, platform in PLATFORMS.items():
    print(name, check_platform(name, platform, granite_bank, NON_ZDR_FEATURES))

print(shortlist(PLATFORMS, granite_bank, NON_ZDR_FEATURES))
