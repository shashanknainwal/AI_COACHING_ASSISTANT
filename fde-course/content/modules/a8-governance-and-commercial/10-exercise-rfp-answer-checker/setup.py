# ILLUSTRATIVE fact sheet, a simplified snapshot of Anthropic's public docs as
# checked in October 2026 (lessons 01, 05 and 09, and module A2). It is NOT a
# source of truth: re-check every row against current documentation before a
# real response. Your functions must work for ANY fact sheet in this shape.
#
# status: "yes" | "partial" | "no" | "unknown"
#   unknown -> not publicly documented, or a contract term: the answer is to_confirm
FACT_SHEET = {
    "us_only_inference": {
        "status": "yes",
        "note": "inference_geo 'us' on the Claude API and Claude Platform on AWS; 1.1x price on Claude 4.6 and later",
        "source": "platform.claude.com data residency",
    },
    "eu_only_inference": {
        "status": "partial",
        "note": "EU options on Amazon Bedrock and Google Vertex AI; not on the Claude API or Foundry",
        "source": "platform.claude.com data residency and platform pages",
    },
    "single_country_inference_germany": {
        "status": "no",
        "note": "no documented option pins current models to Germany",
        "source": "platform pages",
    },
    "model_retirement_notice": {
        "status": "yes",
        "note": "at least 60 days' notice for publicly released models on Anthropic-operated platforms",
        "source": "platform.claude.com model deprecations",
    },
    "batches_on_bedrock": {
        "status": "no",
        "note": "Message Batches API not available on Bedrock",
        "source": "platform availability",
    },
    "priority_tier_new_purchase": {
        "status": "no",
        "note": "Priority Tier commitments are no longer available for purchase",
        "source": "platform.claude.com service tiers",
    },
    "uptime_sla_with_credits": {"status": "unknown", "note": "contract term", "source": "account team / legal"},
    "ip_indemnity": {"status": "unknown", "note": "contract term", "source": "legal"},
    "customer_managed_keys": {"status": "unknown", "note": "depends on platform; confirm", "source": "account team"},
}

ROADMAP_PHRASES = ["roadmap", "coming soon", "planned", "will be available", "will support", "next release", "future release"]
HEDGE_WORDS = ["generally", "typically", "usually", "in most cases"]
