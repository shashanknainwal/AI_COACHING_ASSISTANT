# ILLUSTRATIVE capability table for the exercise. It is a simplified snapshot,
# loosely based on Anthropic's docs as checked in October 2026. It is NOT a
# source of truth: platforms change, and a real review re-checks every cell
# against current documentation. Your functions must work for ANY table in
# this shape, so never hard-code these values.
#
# "zdr" and "private_network" use "yes" | "confirm" | "no":
#   yes     -> documented and available
#   confirm -> depends on the cloud provider or isn't stated; needs checking
#   no      -> not available

PLATFORMS = {
    "claude_api": {
        "label": "Claude API (first-party)",
        "procurement": ["direct"],
        "processor": "anthropic",
        "geos": ["global", "us"],
        "features": [
            "prompt_caching", "web_search", "web_fetch", "code_execution",
            "agent_skills", "batches", "files_api", "mcp_connector", "managed_agents",
        ],
        "zdr": "yes",
        "private_network": "confirm",
    },
    "claude_platform_aws": {
        "label": "Claude Platform on AWS",
        "procurement": ["aws"],
        "processor": "anthropic",
        "geos": ["global", "us"],
        "features": [
            "prompt_caching", "web_search", "web_fetch", "code_execution",
            "agent_skills", "batches", "files_api", "mcp_connector", "managed_agents",
        ],
        "zdr": "yes",
        "private_network": "yes",
    },
    "bedrock": {
        "label": "Amazon Bedrock",
        "procurement": ["aws"],
        "processor": "cloud_provider",
        "geos": ["global", "us", "eu", "jp", "au"],
        "features": ["prompt_caching"],
        "zdr": "confirm",
        "private_network": "confirm",
    },
    "vertex": {
        "label": "Google Cloud Vertex AI",
        "procurement": ["gcp"],
        "processor": "cloud_provider",
        "geos": ["global", "us", "eu"],
        "features": ["prompt_caching", "web_search"],
        "zdr": "confirm",
        "private_network": "confirm",
    },
    "foundry_azure": {
        "label": "Microsoft Foundry (Hosted on Azure)",
        "procurement": ["azure"],
        "processor": "anthropic",
        "geos": ["global", "us"],
        "features": ["prompt_caching", "web_search", "web_fetch"],
        "zdr": "confirm",
        "private_network": "yes",
    },
}

# From Anthropic's "API and data retention" page: features that are not
# eligible for zero data retention (the API does not block them under ZDR).
NON_ZDR_FEATURES = [
    "batches", "files_api", "code_execution", "agent_skills", "mcp_connector", "managed_agents",
]
