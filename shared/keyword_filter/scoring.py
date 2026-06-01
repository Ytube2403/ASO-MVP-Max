import math
import re

from .matcher import has_any_term, normalize_filter_text, tokenize


DEFAULT_VOLUME_SCORE_POLICY = {
    "search_popularity_floor": 5.0,
    "search_popularity_ceiling": 100.0,
    "exponential_curve_factor": 4.0,
    "current_volume_weight": 0.85,
    "historical_max_volume_weight": 0.15,
    "low_tier_threshold": 5.0,
    "low_tier_score_cap": 0.05,
    "exclude_low_tier_from_metadata_shortlist": True,
    "max_low_tier_consider_keywords": 3,
}

QUERY_PATTERNS = [
    r"\bwhat\s+is\b",
    r"\bhow\s+to\b",
    r"\bwhy\s+do\b",
    r"\bwhen\s+is\b",
    r"\bwhere\s+is\b",
]


def number(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def volume_score_policy(config=None):
    policy = dict(DEFAULT_VOLUME_SCORE_POLICY)
    policy.update((config or {}).get("volume_score_policy", {}) or {})
    return policy


def _normalize_search_popularity(value, policy):
    floor = number(policy.get("search_popularity_floor"), 5.0)
    ceiling = max(floor + 1.0, number(policy.get("search_popularity_ceiling"), 100.0))
    curve_factor = number(policy.get("exponential_curve_factor"), 4.0)
    popularity = min(ceiling, max(floor, number(value)))
    if popularity <= floor:
        return 0.0
    ratio = (popularity - floor) / (ceiling - floor)
    if curve_factor <= 0:
        return ratio
    return math.expm1(curve_factor * ratio) / math.expm1(curve_factor)


def calculate_volume_score(volume, max_volume=None, maximum_reach=0, max_maximum_reach=0, config=None):
    """Score AppTweak popularity without treating its exponential scale as raw traffic."""
    policy = volume_score_policy(config)
    current_volume = number(volume)
    historical_volume = max(current_volume, number(max_volume, current_volume))
    reach = max(0.0, number(maximum_reach))
    reach_ceiling = max(0.0, number(max_maximum_reach))
    current_score = min(1.0, reach / reach_ceiling) if reach > 0 and reach_ceiling > 0 else _normalize_search_popularity(current_volume, policy)
    historical_score = _normalize_search_popularity(historical_volume, policy)
    current_weight = max(0.0, number(policy.get("current_volume_weight"), 0.85))
    historical_weight = max(0.0, number(policy.get("historical_max_volume_weight"), 0.15))
    total_weight = current_weight + historical_weight
    score = current_score if total_weight <= 0 else ((current_weight * current_score) + (historical_weight * historical_score)) / total_weight
    if current_volume <= number(policy.get("low_tier_threshold"), 5.0):
        score = min(score, number(policy.get("low_tier_score_cap"), 0.05))
    return max(0.0, min(1.0, score))


def is_low_volume_tier(row, config=None):
    volume = row.get("Volume", 0) if hasattr(row, "get") else row
    return number(volume) <= number(volume_score_policy(config).get("low_tier_threshold"), 5.0)


def is_shortlist_volume_eligible(row, section, selected_low_tier_count=0, config=None):
    policy = volume_score_policy(config)
    if not is_low_volume_tier(row, config):
        return True
    if section in {"Core Intent Final", "Broad Expansion"}:
        return not bool(policy.get("exclude_low_tier_from_metadata_shortlist", True))
    if section == "Consider Keywords":
        return selected_low_tier_count < int(number(policy.get("max_low_tier_consider_keywords"), 3))
    return True


def has_core_intent(value, config):
    return has_any_term(value, config.get("intent_core_terms", [])) or has_any_term(value, config.get("intent_core_words", []))


def has_feature_intent(value, config):
    return has_any_term(value, config.get("feature_terms", []))


def has_style_intent(value, config):
    return has_any_term(value, config.get("style_terms", []))


def check_naturalness(value, config):
    en_text = value.get("EN", value.get("Keyword", "")) if hasattr(value, "get") and not isinstance(value, str) else value
    normalized = normalize_filter_text(en_text)
    words = tokenize(en_text)
    if not words:
        return "UNNATURAL", "Empty keyword"
    counts = {word: words.count(word) for word in set(words)}
    if len(words) > 2 and (max(counts.values()) / len(words)) > 0.5:
        return "STUFFING", "Too many repeated words"
    if len(words) > 6 and not (has_core_intent(value, config) or has_feature_intent(value, config)):
        return "TOO_LONG", f"Keyword has too many words ({len(words)})"
    if any(re.search(pattern, normalized) for pattern in QUERY_PATTERNS):
        return "UNNATURAL", "Fails structural validation"
    for word, count in counts.items():
        if count > 1 and len(words) <= 4 and f"{word} {word}" in normalized:
            return "UNNATURAL", "Repeated adjacent keyword token"
    return "OK", "Natural enough for keyword research"


def calculate_expansion(row, config):
    token_count = len(tokenize(row.get("Keyword", "")))
    score = 0.85 if token_count <= 1 else 0.75 if token_count == 2 else 0.55 if token_count == 3 else 0.35
    if has_core_intent(row, config):
        score += 0.10
    elif has_feature_intent(row, config):
        score += 0.05
    if row.get("is_competitor"):
        score = 0.10
    if has_style_intent(row, config) and not has_core_intent(row, config):
        score = min(score, 0.35)
    return max(0.0, min(1.0, score))


def get_language_bonus(row):
    group = str(row.get("LanguageGroup", "PRIMARY")).upper()
    return 0.02 if group == "PRIMARY" else 0.01 if group == "SECONDARY" else 0.0


def calculate_relevancy(row, config):
    score = float(config.get("relevancy_weights", {}).get("base", 0.30))
    if has_core_intent(row, config):
        score += 0.35
    if has_feature_intent(row, config):
        score += 0.20
    if has_style_intent(row, config):
        score += 0.15
    if row.get("is_competitor"):
        score -= 0.20
    if row.get("is_irrelevant"):
        score -= 0.25
    if str(row.get("LanguageGroup", "")).upper() == "FOREIGN":
        score -= 0.30
    score += float(row.get("CompetitorBoost", 0.0) or 0.0)
    return max(0.0, min(1.0, score))
