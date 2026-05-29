import hashlib
import os
import re
import unicodedata

try:
    from shared.language_detector import get_market_language_policy
except Exception:
    from language_detector import get_market_language_policy


DEFAULT_NOISE_TERMS = [
    "app", "apps", "free", "download", "android", "for android",
    "new", "best", "top", "2026", "2025",
]

QUERY_PATTERNS = [
    r"\bwhat\s+is\b",
    r"\bhow\s+to\b",
    r"\bwhy\s+do\b",
    r"\bwhen\s+is\b",
    r"\bwhere\s+is\b",
]


def normalize_filter_text(text):
    text = str(text or "").lower().strip()
    text = "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )
    text = re.sub(r"[-_]+", " ", text)
    text = re.sub(r"[^\w\s]+", " ", text, flags=re.UNICODE)
    return re.sub(r"\s+", " ", text).strip()


def tokenize(text):
    normalized = normalize_filter_text(text)
    return [t for t in normalized.split() if t]


def _term_pattern(term):
    term_norm = normalize_filter_text(term)
    if not term_norm:
        return None
    return re.compile(r"(?<!\w)" + re.escape(term_norm) + r"(?!\w)", re.UNICODE)


def has_term(text, terms):
    text_norm = normalize_filter_text(text)
    for term in terms or []:
        pattern = _term_pattern(term)
        if pattern and pattern.search(text_norm):
            return True
    return False


def has_core_intent(keyword, config):
    # Support dict/Series/row or string
    kw_str = keyword
    if isinstance(keyword, (dict, object)) and hasattr(keyword, 'get'):
        kw_str = keyword.get("EN", keyword.get("Keyword", ""))
    return has_term(kw_str, config.get("intent_core_terms", [])) or has_term(kw_str, config.get("intent_core_words", []))


def has_feature_intent(keyword, config):
    kw_str = keyword
    if isinstance(keyword, (dict, object)) and hasattr(keyword, 'get'):
        kw_str = keyword.get("EN", keyword.get("Keyword", ""))
    return has_term(kw_str, config.get("feature_terms", []))


def has_style_intent(keyword, config):
    kw_str = keyword
    if isinstance(keyword, (dict, object)) and hasattr(keyword, 'get'):
        kw_str = keyword.get("EN", keyword.get("Keyword", ""))
    return has_term(kw_str, config.get("style_terms", []))


def is_competitor_keyword(keyword, config):
    kw_str = keyword
    if isinstance(keyword, (dict, object)) and hasattr(keyword, 'get'):
        kw_str = keyword.get("Keyword", "")
        # Competitor brands could match either the raw keyword or its English translation
        return has_term(kw_str, config.get("competitor_brands", [])) or has_term(keyword.get("EN", ""), config.get("competitor_brands", []))
    return has_term(kw_str, config.get("competitor_brands", []))


def is_typo_keyword(keyword, config):
    kw_str = keyword
    if isinstance(keyword, (dict, object)) and hasattr(keyword, 'get'):
        # Typo matching should be done on the raw keyword only
        kw_str = keyword.get("Keyword", "")
    return has_term(kw_str, config.get("typo_blacklist", []))


def is_irrelevant_keyword(keyword, config):
    kw_str = keyword
    if isinstance(keyword, (dict, object)) and hasattr(keyword, 'get'):
        kw_str = keyword.get("EN", keyword.get("Keyword", ""))
    return has_term(kw_str, config.get("irrelevant_intent_terms", []))


def is_noise_only(keyword, config):
    kw_str = keyword
    en_kw = keyword
    if isinstance(keyword, (dict, object)) and hasattr(keyword, 'get'):
        kw_str = keyword.get("Keyword", "")
        en_kw = keyword.get("EN", kw_str)
    else:
        kw_str = keyword
        en_kw = keyword

    if has_core_intent(keyword, config) or has_feature_intent(keyword, config) or has_style_intent(keyword, config):
        return False

    tokens = tokenize(en_kw)
    if not tokens:
        return False

    noise_terms = config.get("noise_terms") or DEFAULT_NOISE_TERMS
    noise_tokens = set()
    noise_phrases = set()
    for term in noise_terms:
        term_norm = normalize_filter_text(term)
        if not term_norm:
            continue
        parts = term_norm.split()
        if len(parts) == 1:
            noise_tokens.add(parts[0])
        else:
            noise_phrases.add(term_norm)

    keyword_norm = normalize_filter_text(en_kw)
    if keyword_norm in noise_phrases:
        return True
    return all(token in noise_tokens for token in tokens)


def check_naturalness(keyword, config):
    kw_str = keyword
    en_kw = keyword
    if isinstance(keyword, (dict, object)) and hasattr(keyword, 'get'):
        kw_str = keyword.get("Keyword", "")
        en_kw = keyword.get("EN", kw_str)
    else:
        kw_str = keyword
        en_kw = keyword

    text_norm = normalize_filter_text(en_kw)
    words = tokenize(en_kw)
    if not words:
        return "UNNATURAL", "Empty keyword"

    counts = {}
    for word in words:
        counts[word] = counts.get(word, 0) + 1
    max_repeat = max(counts.values()) if counts else 0
    if len(words) > 2 and (max_repeat / len(words)) > 0.5:
        return "STUFFING", "Too many repeated words"

    if len(words) > 6 and not (has_core_intent(keyword, config) or has_feature_intent(keyword, config)):
        return "TOO_LONG", f"Keyword has too many words ({len(words)})"

    for pattern in QUERY_PATTERNS:
        if re.search(pattern, text_norm):
            return "UNNATURAL", "Fails structural validation"

    for word, count in counts.items():
        if count > 1 and len(words) <= 4:
            repeated = " ".join([word, word])
            if repeated in text_norm:
                return "UNNATURAL", "Repeated adjacent keyword token"

    return "OK", "Natural enough for keyword research"


def calculate_expansion(row, config):
    keyword = row.get("Keyword", "")
    tokens = tokenize(keyword)
    count = len(tokens)
    if count <= 1:
        score = 0.85
    elif count == 2:
        score = 0.75
    elif count == 3:
        score = 0.55
    else:
        score = 0.35

    if has_core_intent(keyword, config):
        score += 0.10
    elif has_feature_intent(keyword, config):
        score += 0.05

    if row.get("is_competitor"):
        score = 0.10
    if has_style_intent(keyword, config) and not has_core_intent(keyword, config):
        score = min(score, 0.35)

    return max(0.0, min(1.0, score))


def get_language_bonus(row):
    group = str(row.get("LanguageGroup", "PRIMARY")).upper()
    if group == "PRIMARY":
        return 0.02
    if group == "SECONDARY":
        return 0.01
    return 0.0


def _app_mode(config):
    slug = normalize_filter_text(config.get("category_slug") or config.get("app_name") or config.get("category") or "")
    if "game" in slug or "emulator" in slug or "gb4" in slug:
        return "game"
    if "ar" in slug or "filter" in slug or "camera" in slug or "dogy" in slug:
        return "ar_filter"
    return "generic"


def classify_keyword(row, config):
    keyword = row.get("Keyword", "")
    app_mode = _app_mode(config)
    has_core = has_core_intent(keyword, config)
    has_feature = has_feature_intent(keyword, config)
    has_style = has_style_intent(keyword, config)
    core_override = bool(config.get("risk_policy", {}).get("core_intent_override", False))

    if row.get("is_competitor"):
        return "Dropped", "competitor_brand", "Dropped: Competitor brand"
    if row.get("is_typo"):
        return "Dropped", "typo_truncated_broken", "Dropped: Typo, truncated, or broken"
    if row.get("is_irrelevant"):
        if core_override and has_core:
            return "Consider Keywords", "irrelevant_intent_core_override", "Consider: Core intent with broad irrelevant-risk term"
        return "Dropped", "irrelevant_intent", "Dropped: Irrelevant category/intent"
    if row.get("is_noise"):
        return "Dropped", "noise_only", "Dropped: Noise-only generic term"

    naturalness = str(row.get("NaturalnessFlag", "OK"))
    if naturalness != "OK":
        return "Dropped", "unnatural", f"Dropped: Unnatural phrase ({row.get('NaturalnessReason', '')})"

    language_group = str(row.get("LanguageGroup", "PRIMARY")).upper()
    if language_group == "FOREIGN":
        return "Language Mismatch Audit", "foreign_language_mismatch", "Foreign language mismatch"
    if language_group == "UNKNOWN":
        return "Manual Review", "manual_review", "Unknown language"
    if language_group == "MIXED":
        policy = get_market_language_policy(config.get("market", "US_EN"), config)
        if policy.get("mixed_allowed", False):
            return "Consider Keywords", "mixed_language_consider", "Mixed language allowed for this market"
        return "Manual Review", "manual_review", "Mixed language needs review"
    if language_group == "SECONDARY":
        return "Consider Keywords", "secondary_language_handling", "Secondary language handling"

    if has_term(keyword, config.get("risky_platform_terms", [])):
        return "Consider Keywords", "platform_style_risk", "Platform-style risk"

    if has_core:
        if app_mode == "game":
            return "Core Intent Final", "core_intent_final", "Strong core game emulator search intent"
        if app_mode == "ar_filter":
            return "Core Intent Final", "core_intent_final", "Strong core camera filter/effect search intent"
        return "Core Intent Final", "core_intent_final", "Strong core app search intent"

    if app_mode == "game":
        if has_style:
            generic_terms = ["retro games", "classic games", "gba games", "arcade games", "game emulator"]
            if has_term(keyword, generic_terms):
                return "Broad Expansion", "broad_expansion", "Generic game/emulator variant"
            return "Game Keywords", "game_keywords", "Game Title/Franchise candidate (Research Only)"
        if has_feature:
            return "System Keywords", "system_keywords", "System/Console candidate"
    elif app_mode == "ar_filter":
        if has_style and not has_feature and not has_core:
            return "Generic Style Reserve", "style_only", "Generic aesthetic/style-only terms held back from shortlist"
        if has_feature:
            return "Effect / Filter Type", "feature_keywords", "Specific effect/filter candidate"
        if has_style:
            return "User Intent / Content Use Case", "style_keywords", "User intent/content use case candidate"
    else:
        if has_style and not has_core and not has_feature:
            return "Generic Style Reserve", "style_only", "Generic aesthetic/style-only terms held back from shortlist"
        if has_feature:
            return "Feature Keywords", "feature_keywords", "Specific feature candidate"
        if has_style:
            return "Style Keywords", "style_keywords", "Aesthetic/theme candidate"

    if float(row.get("RelevancyScore", 0) or 0) < 0.45:
        return "Dropped", "dropped", "Dropped: Weak app intent after scoring"

    if app_mode == "game":
        return "Broad Expansion", "broad_expansion", "Moderately relevant emulator expansion"
    if app_mode == "ar_filter":
        return "Broad Expansion", "broad_expansion", "Broad camera filter expansion"
    return "Broad Expansion", "broad_expansion", "Broad app expansion"


def file_md5(path):
    try:
        hash_md5 = hashlib.md5()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception:
        return ""


def build_selection_cache_meta(input_path, market):
    return {
        "market": str(market or ""),
        "input_file": os.path.basename(str(input_path or "")),
        "input_hash": file_md5(input_path) if input_path else "",
    }


def unwrap_selection_payload(payload):
    if isinstance(payload, dict) and isinstance(payload.get("selection"), dict):
        return payload.get("selection"), payload.get("_cache_meta", {})
    return payload, {}


def is_selection_cache_valid(payload, expected_meta):
    _, meta = unwrap_selection_payload(payload)
    if not meta:
        return False
    return all(str(meta.get(k, "")) == str(v or "") for k, v in expected_meta.items())


def wrap_selection_payload(selection, meta):
    if not isinstance(selection, dict):
        return selection
    wrapped = dict(selection)
    wrapped["_cache_meta"] = meta
    wrapped["selection"] = {k: v for k, v in selection.items() if k != "_cache_meta"}
    return wrapped
