from .classifier import DEFAULT_RISK_POLICY
from .matcher import normalize_filter_text


TERM_LIST_KEYS = [
    "intent_core_terms", "intent_core_words", "feature_terms", "style_terms",
    "visual_terms", "competitor_brands", "ambiguous_brand_terms",
    "risky_platform_terms", "platform_affiliation_terms", "risky_ip_terms",
    "noise_terms", "typo_blacklist", "irrelevant_intent_terms",
]
VALID_ACTIONS = {"drop", "consider", "reserve"}


class FilterConfigError(ValueError):
    pass


def _normalized_terms(config, key):
    return [normalize_filter_text(term) for term in config.get(key, []) or [] if normalize_filter_text(term)]


def validate_filter_config(config):
    errors = []
    warnings = []
    if not str(config.get("semantic_mode", "")).strip():
        errors.append("semantic_mode is required")

    for key in TERM_LIST_KEYS:
        normalized = _normalized_terms(config, key)
        duplicates = sorted({term for term in normalized if normalized.count(term) > 1})
        if duplicates:
            errors.append(f"{key} contains duplicate normalized terms: {duplicates}")

    competitors = set(_normalized_terms(config, "competitor_brands"))
    for key in ("feature_terms", "risky_platform_terms", "ambiguous_brand_terms", "platform_affiliation_terms"):
        overlap = sorted(competitors & set(_normalized_terms(config, key)))
        if overlap:
            errors.append(f"competitor_brands overlaps {key}: {overlap}")

    configured_policy = config.get("risk_policy", {}) or {}
    if "platform_style_action" in configured_policy:
        warnings.append("risk_policy.platform_style_action is deprecated; use platform_context_action")
    for key in DEFAULT_RISK_POLICY:
        if key.endswith("_action") and key in configured_policy and configured_policy[key] not in VALID_ACTIONS:
            errors.append(f"risk_policy.{key} must be one of {sorted(VALID_ACTIONS)}")
    if "platform_style_action" in configured_policy and configured_policy["platform_style_action"] not in VALID_ACTIONS:
        errors.append(f"risk_policy.platform_style_action must be one of {sorted(VALID_ACTIONS)}")
    if "rule_precedence" in config:
        warnings.append("rule_precedence is deprecated; precedence is fixed by the shared engine")
    if errors:
        raise FilterConfigError("; ".join(errors))
    return warnings
