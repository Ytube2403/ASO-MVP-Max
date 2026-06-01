FILTER_POLICY = {
    "semantic_mode": "personalization_widget",
    "risky_ip_terms": ["assistive touch", "dynamic island"],
    "ambiguous_brand_terms": ["sidebar"],
    "platform_affiliation_terms": [],
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
