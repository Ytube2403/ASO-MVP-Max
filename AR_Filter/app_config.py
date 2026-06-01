FILTER_POLICY = {
    "semantic_mode": "ar_filter",
    "risky_ip_terms": [],
    "ambiguous_brand_terms": ["snow"],
    "platform_affiliation_terms": ["official snapchat", "official tiktok", "official instagram", "snapchat filter"],
    "truncation_policy": {
        "enabled": True,
        "min_prefix_length": 2,
        "allowed_partial_terms": [],
    },
    "risk_policy": {
        "competitor_brand_action": "drop",
        "ambiguous_brand_action": "consider",
        "risky_ip_action": "consider",
        "platform_context_action": "consider",
        "platform_only_action": "drop",
        "platform_affiliation_action": "drop",
        "style_only_action": "reserve",
        "core_intent_override": True,
    },
}
