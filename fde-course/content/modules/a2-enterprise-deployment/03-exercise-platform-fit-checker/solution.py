def _status(value, code, label, reasons, open_items, gaps):
    """Sort a yes/confirm/no capability into reasons, open items or gaps."""
    if value == "yes":
        reasons.append(f"{code}: {label} documented")
    elif value == "confirm":
        open_items.append(f"{code}: {label} must be confirmed")
    else:
        gaps.append(f"{code}: {label} not available")


def check_platform(name, platform, requirements, non_zdr_features):
    """Check one platform against the customer's requirements."""
    reasons, gaps, open_items = [], [], []
    req = requirements

    procurement = req.get("procurement")
    if procurement:
        if procurement in platform["procurement"]:
            reasons.append(f"procurement: can be bought via {procurement}")
        else:
            gaps.append(f"procurement: needs {procurement}, platform is bought via {', '.join(platform['procurement'])}")

    processor = req.get("processor")
    if processor:
        if platform["processor"] == processor:
            reasons.append(f"processor: {processor} processes the data")
        else:
            gaps.append(f"processor: needs {processor}, platform processor is {platform['processor']}")

    geo = req.get("geo")
    if geo:
        if geo in platform["geos"]:
            reasons.append(f"geo: inference can be kept in {geo}")
        else:
            gaps.append(f"geo: needs {geo}, platform offers {', '.join(platform['geos'])}")

    for feature in req.get("features", []):
        if feature in platform["features"]:
            reasons.append(f"feature: {feature} available")
        else:
            gaps.append(f"feature: {feature} not available")

    if req.get("zdr"):
        _status(platform["zdr"], "zdr", "zero data retention", reasons, open_items, gaps)
        for feature in req.get("features", []):
            if feature in non_zdr_features:
                gaps.append(f"conflict: {feature} is not ZDR-eligible")

    if req.get("private_network"):
        _status(platform["private_network"], "network", "private networking", reasons, open_items, gaps)

    return {
        "platform": name,
        "eligible": not gaps,
        "reasons": reasons,
        "gaps": gaps,
        "open_items": open_items,
    }


def shortlist(platforms, requirements, non_zdr_features):
    """Return eligible platform names (best first) and the gaps that block the rest."""
    results = [check_platform(n, p, requirements, non_zdr_features) for n, p in platforms.items()]
    eligible = sorted(
        (r for r in results if r["eligible"]),
        key=lambda r: (len(r["open_items"]), r["platform"]),
    )
    return {
        "eligible": [r["platform"] for r in eligible],
        "blocked": {r["platform"]: r["gaps"] for r in results if not r["eligible"]},
    }


# --- Try it out (this part isn't graded) ---
granite_bank = {
    "procurement": "aws",
    "geo": "us",
    "features": ["prompt_caching", "batches"],
    "zdr": False,
    "private_network": True,
}

for name, platform in PLATFORMS.items():
    result = check_platform(name, platform, granite_bank, NON_ZDR_FEATURES)
    print(name, "eligible" if result["eligible"] else "blocked", result["gaps"], result["open_items"])

print(shortlist(PLATFORMS, granite_bank, NON_ZDR_FEATURES))
