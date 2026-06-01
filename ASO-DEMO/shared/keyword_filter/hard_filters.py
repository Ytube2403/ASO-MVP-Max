from .audit import AuditMatch
from .matcher import find_any_term, find_term, normalize_filter_text, row_texts, tokenize
from .runtime import DEFAULT_NOISE_TERMS, resolve_filter_runtime
from .scoring import has_core_intent, has_feature_intent, has_style_intent


def _raw_text(value):
    return value.get("Keyword", "") if hasattr(value, "get") and not isinstance(value, str) else value


def find_competitor_keyword(value, config):
    runtime = resolve_filter_runtime(config)
    return find_any_term(value, runtime.matchers["competitor_brands"], rule="competitor_brand")


def is_competitor_keyword(value, config):
    return bool(find_competitor_keyword(value, config))


def find_typo_keyword(value, config):
    runtime = resolve_filter_runtime(config)
    return find_term(_raw_text(value), runtime.matchers["typo_blacklist"], rule="typo_blacklist", source="raw")


def is_typo_keyword(value, config):
    return bool(find_typo_keyword(value, config))


def find_irrelevant_keyword(value, config):
    runtime = resolve_filter_runtime(config)
    return find_any_term(value, runtime.matchers["irrelevant_intent_terms"], rule="irrelevant_intent")


def is_irrelevant_keyword(value, config):
    return bool(find_irrelevant_keyword(value, config))


def _noise_match(text, runtime, source):
    tokens = tokenize(text)
    if not tokens:
        return None
    normalized_text = normalize_filter_text(text)
    if normalized_text in runtime.noise_phrases:
        return AuditMatch(rule="noise_only", term=normalized_text, source=source)
    if all(token in runtime.noise_tokens for token in tokens):
        return AuditMatch(rule="noise_only", term=normalized_text, source=source)
    return None


def find_noise_only(value, config):
    runtime = resolve_filter_runtime(config)
    config = runtime.config
    if has_core_intent(value, config) or has_feature_intent(value, config) or has_style_intent(value, config):
        return None
    for source, text in row_texts(value):
        match = _noise_match(text, runtime, source)
        if match:
            return match
    return None


def is_noise_only(value, config):
    return bool(find_noise_only(value, config))


def find_truncated_keyword(value, config):
    runtime = resolve_filter_runtime(config)
    config = runtime.config
    policy = config.get("truncation_policy", {}) or {}
    if policy.get("enabled", True) is False:
        return None
    raw = _raw_text(value)
    normalized = normalize_filter_text(raw)
    if normalized in runtime.truncation_allowlist:
        return None
    words = tokenize(raw)
    if len(words) < 2:
        return None
    prefix = words[-1]
    min_length = int(policy.get("min_prefix_length", 2) or 2)
    if len(prefix) < min_length:
        return None
    if not any(token in runtime.truncation_anchor_tokens for token in words[:-1]):
        return None
    for candidate in runtime.truncation_candidates:
        if len(candidate) > len(prefix) and candidate.startswith(prefix):
            return AuditMatch(rule="truncated_keyword", term=prefix, source="raw", completion=candidate)
    return None


def is_truncated_keyword(value, config):
    return bool(find_truncated_keyword(value, config))


def _platform_only(value, config, platform_match):
    return bool(platform_match and not has_core_intent(value, config) and not has_feature_intent(value, config))


def evaluate_hard_filters(value, config):
    runtime = resolve_filter_runtime(config)
    config = runtime.config
    matches = {
        "is_competitor": find_competitor_keyword(value, config),
        "is_typo": find_typo_keyword(value, config),
        "is_truncated": find_truncated_keyword(value, config),
        "is_irrelevant": find_irrelevant_keyword(value, config),
        "is_noise": find_noise_only(value, config),
        "is_platform_affiliation": find_any_term(value, runtime.matchers["platform_affiliation_terms"], rule="platform_affiliation"),
        "is_risky_ip": find_any_term(value, runtime.matchers["risky_ip_terms"], rule="risky_ip"),
        "is_ambiguous_brand": find_any_term(value, runtime.matchers["ambiguous_brand_terms"], rule="ambiguous_brand"),
        "is_platform_risk": find_any_term(value, runtime.matchers["risky_platform_terms"], rule="platform_context"),
    }
    matches["is_platform_only"] = matches["is_platform_risk"] if _platform_only(value, config, matches["is_platform_risk"]) else None
    priority = [
        "is_competitor", "is_typo", "is_truncated", "is_irrelevant", "is_noise",
        "is_platform_affiliation", "is_platform_only", "is_risky_ip",
        "is_ambiguous_brand", "is_platform_risk",
    ]
    primary = next((matches[key] for key in priority if matches.get(key)), None)
    result = {key: bool(match) for key, match in matches.items()}
    result.update({
        "HardFilterRule": primary.rule if primary else "",
        "HardFilterTerm": primary.term if primary else "",
        "HardFilterSource": primary.source if primary else "",
        "PolicyFlags": "; ".join(match.flag() for key, match in matches.items() if match),
    })
    return result
