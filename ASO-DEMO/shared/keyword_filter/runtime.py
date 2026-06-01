from collections import OrderedDict

from .cache import config_hash
from .matcher import compile_terms, normalize_filter_text, tokenize


TERM_KEYS = [
    "competitor_brands",
    "typo_blacklist",
    "irrelevant_intent_terms",
    "platform_affiliation_terms",
    "risky_ip_terms",
    "ambiguous_brand_terms",
    "risky_platform_terms",
]
DEFAULT_NOISE_TERMS = [
    "app", "apps", "free", "download", "android", "for android",
    "new", "best", "top", "2026", "2025",
]
_RUNTIME_CACHE = OrderedDict()
_MAX_RUNTIME_CACHE_SIZE = 128


class FilterRuntime:
    def __init__(self, config):
        self.config = config
        self.config_hash = config_hash(config)
        self.matchers = {key: compile_terms(config.get(key, [])) for key in TERM_KEYS}
        noise_terms = config.get("noise_terms") or DEFAULT_NOISE_TERMS
        normalized_noise = {normalize_filter_text(term) for term in noise_terms if normalize_filter_text(term)}
        self.noise_phrases = {term for term in normalized_noise if " " in term}
        self.noise_tokens = {term for term in normalized_noise if " " not in term}
        truncation_policy = config.get("truncation_policy", {}) or {}
        candidate_sources = truncation_policy.get("candidate_sources") or [
            "intent_core_terms", "intent_core_words", "feature_terms", "visual_terms",
        ]
        self.truncation_candidates = sorted({
            token
            for source in candidate_sources
            for term in config.get(source, []) or []
            for token in tokenize(term)
        })
        self.truncation_anchor_tokens = {
            token
            for source in ("intent_core_terms", "intent_core_words", "feature_terms")
            for term in config.get(source, []) or []
            for token in tokenize(term)
        }
        allowlist = set(truncation_policy.get("allowlist", []) or [])
        allowlist.update((config.get("user_overrides", {}) or {}).get("do_not_auto_drop_terms", []) or [])
        self.truncation_allowlist = {normalize_filter_text(term) for term in allowlist}


def build_filter_runtime(config):
    key = config_hash(config)
    runtime = _RUNTIME_CACHE.get(key)
    if runtime is not None:
        _RUNTIME_CACHE.move_to_end(key)
        return runtime
    runtime = FilterRuntime(config)
    _RUNTIME_CACHE[key] = runtime
    if len(_RUNTIME_CACHE) > _MAX_RUNTIME_CACHE_SIZE:
        _RUNTIME_CACHE.popitem(last=False)
    return runtime


def resolve_filter_runtime(config_or_runtime):
    if isinstance(config_or_runtime, FilterRuntime):
        return config_or_runtime
    return build_filter_runtime(config_or_runtime)
