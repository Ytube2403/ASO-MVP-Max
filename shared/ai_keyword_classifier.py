import json
import os
import sqlite3
import ssl
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import closing
from dataclasses import dataclass

from shared.keyword_filter.cache import config_hash
from shared.keyword_filter.hard_filters import evaluate_hard_filters
from shared.keyword_filter.matcher import has_any_term, normalize_filter_text, tokenize
from shared.keyword_filter.scoring import has_core_intent, has_feature_intent, has_style_intent
from shared.language_detector import detect_keyword_language, get_market_language_policy


class AIKeywordClassifierError(RuntimeError):
    pass


PROVIDER = "deepseek"
DEFAULT_MODEL = "deepseek-v4-flash"
DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_PROMPT_VERSION = "aso-keyword-classifier-v1"
DEFAULT_BATCH_SIZE = 50
DEFAULT_REQUESTS_PER_SECOND = 2.0
DEFAULT_REQUESTS_PER_SECOND_PER_KEY = 1.0
DEFAULT_MAX_WORKERS = 2
DEFAULT_TIMEOUT = 60
DOTENV_KEYS = {
    "DEEPSEEK_API_KEY",
    "DEEPSEEK_API_KEYS",
    "DEEPSEEK_BASE_URL",
    "DEEPSEEK_MAX_WORKERS",
    "DEEPSEEK_REQUESTS_PER_SECOND_PER_KEY",
}
DEFAULT_PRE_FILTER_CONFIG = {
    "enabled": True,
    "duplicate_strategy": "canonical_reuse",
    "preserve_if_matches_intent": True,
    "allow_possible_truncated_to_ai": True,
    "skip_rules": [
        "empty_keyword",
        "duplicate_keyword",
        "competitor_brand",
        "typo_blacklist",
        "truncated_keyword",
        "irrelevant_intent",
        "noise_only",
        "platform_affiliation",
        "platform_only",
    ],
}

LANGUAGE_GROUPS = {"PRIMARY", "SECONDARY", "MIXED", "FOREIGN", "UNKNOWN"}
SEMANTIC_BUCKETS = {
    "Core Intent Final",
    "Broad Expansion",
    "Feature Keywords",
    "Style Keywords",
    "Consider Keywords",
    "Generic Style Reserve",
    "Language Mismatch Audit",
    "Manual Review",
    "Dropped",
}

OUTPUT_COLUMNS = [
    "NeedsAI",
    "PreAIAction",
    "PreAIRule",
    "PreAIReason",
    "CanonicalKeyword",
    "DetectedLanguage",
    "LanguageGroup",
    "AISemanticBucket",
    "AIDecisionRule",
    "AIReason",
    "AIConfidence",
    "AIEnglishGloss",
    "AIStatus",
]


@dataclass(frozen=True)
class AIKeywordAnalysis:
    keyword: str
    detected_language: str
    language_group: str
    semantic_bucket: str
    decision_rule: str
    reason: str
    confidence: float
    english_gloss: str
    status: str = "AI_CLASSIFIED"


@dataclass
class PreAIItem:
    position: int
    row: dict
    keyword: str
    canonical_keyword: str
    needs_ai: bool
    action: str
    rule: str
    reason: str
    canonical_position: int | None = None


def enabled(config):
    classifier_config = (config or {}).get("ai_keyword_classifier", {})
    return bool(classifier_config.get("enabled", False))


def _project_env_paths():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    paths = [
        os.path.join(os.getcwd(), ".env"),
        os.path.join(project_root, ".env"),
    ]
    unique_paths = []
    seen = set()
    for path in paths:
        normalized = os.path.abspath(path)
        if normalized not in seen:
            unique_paths.append(normalized)
            seen.add(normalized)
    return unique_paths


def _strip_env_quotes(value):
    value = str(value or "").strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def load_project_env():
    """Load project-local .env secrets without overriding existing environment."""
    loaded = []
    for path in _project_env_paths():
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8") as env_file:
            for line in env_file:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                if key not in DOTENV_KEYS or os.environ.get(key):
                    continue
                os.environ[key] = _strip_env_quotes(value)
        loaded.append(path)
    return loaded


def _classifier_config(config):
    load_project_env()
    configured = dict((config or {}).get("ai_keyword_classifier", {}) or {})
    pre_filter_config = dict(DEFAULT_PRE_FILTER_CONFIG)
    pre_filter_config.update(dict(configured.get("pre_filter", {}) or {}))
    return {
        "provider": str(configured.get("provider", PROVIDER) or PROVIDER),
        "model": str(configured.get("model", DEFAULT_MODEL) or DEFAULT_MODEL),
        "prompt_version": str(configured.get("prompt_version", DEFAULT_PROMPT_VERSION) or DEFAULT_PROMPT_VERSION),
        "batch_size": int(configured.get("batch_size", DEFAULT_BATCH_SIZE) or DEFAULT_BATCH_SIZE),
        "cache_path": str(configured.get("cache_path", ".cache/ai_keyword_analysis.sqlite3") or ".cache/ai_keyword_analysis.sqlite3"),
        "fail_on_api_error": bool(configured.get("fail_on_api_error", True)),
        "requests_per_second": float(configured.get("requests_per_second", DEFAULT_REQUESTS_PER_SECOND) or DEFAULT_REQUESTS_PER_SECOND),
        "requests_per_second_per_key": float(
            configured.get(
                "requests_per_second_per_key",
                os.environ.get("DEEPSEEK_REQUESTS_PER_SECOND_PER_KEY", DEFAULT_REQUESTS_PER_SECOND_PER_KEY),
            )
            or DEFAULT_REQUESTS_PER_SECOND_PER_KEY
        ),
        "max_workers": int(
            configured.get("max_workers", os.environ.get("DEEPSEEK_MAX_WORKERS", DEFAULT_MAX_WORKERS))
            or DEFAULT_MAX_WORKERS
        ),
        "key_strategy": str(configured.get("key_strategy", "round_robin") or "round_robin"),
        "failover_on_key_error": bool(configured.get("failover_on_key_error", True)),
        "timeout": float(configured.get("timeout", DEFAULT_TIMEOUT) or DEFAULT_TIMEOUT),
        "retries": int(configured.get("retries", 3) or 3),
        "pre_filter": pre_filter_config,
    }


def _context_hash(config, app_profile=None):
    relevant = {
        "app_id": (config or {}).get("app_id", ""),
        "app_name": (config or {}).get("app_name", ""),
        "category": (config or {}).get("category", ""),
        "market": (config or {}).get("market", ""),
        "semantic_mode": (config or {}).get("semantic_mode", ""),
        "market_language_policy": (config or {}).get("market_language_policy", {}),
        "intent_core_terms": (config or {}).get("intent_core_terms", []),
        "intent_core_words": (config or {}).get("intent_core_words", []),
        "feature_terms": (config or {}).get("feature_terms", []),
        "style_terms": (config or {}).get("style_terms", []),
        "visual_terms": (config or {}).get("visual_terms", []),
        "noise_terms": (config or {}).get("noise_terms", []),
        "irrelevant_intent_terms": (config or {}).get("irrelevant_intent_terms", []),
        "profile_summary": (app_profile or {}).get("live_store_metadata", {}),
    }
    return config_hash(relevant)


def _cache_key(keyword, config, market, app_profile=None, classifier_config=None):
    classifier_config = classifier_config or _classifier_config(config)
    return (
        classifier_config["provider"],
        classifier_config["model"],
        classifier_config["prompt_version"],
        str((config or {}).get("app_id", "")),
        str(market or (config or {}).get("market", "")),
        _context_hash(config, app_profile),
        normalize_filter_text(keyword),
    )


def _pre_filter_config(classifier_config):
    configured = dict(classifier_config.get("pre_filter", {}) or {})
    merged = dict(DEFAULT_PRE_FILTER_CONFIG)
    merged.update(configured)
    merged["skip_rules"] = {
        str(rule or "").strip()
        for rule in (merged.get("skip_rules") or [])
        if str(rule or "").strip()
    }
    return merged


def _has_visual_intent(value, config):
    return has_any_term(value, (config or {}).get("visual_terms", []))


def _has_preserved_intent(value, config):
    return (
        has_core_intent(value, config)
        or has_feature_intent(value, config)
        or has_style_intent(value, config)
        or _has_visual_intent(value, config)
    )


def _pre_ai_skip_reason(row, config, pre_filter):
    keyword = str(row.get("Keyword", "") or "")
    canonical = normalize_filter_text(keyword)
    tokens = tokenize(keyword)
    skip_rules = pre_filter["skip_rules"]
    if "empty_keyword" in skip_rules and (not canonical or not tokens):
        return "empty_keyword", "Empty or invalid keyword"

    hard = evaluate_hard_filters(row, config)
    rule = str(hard.get("HardFilterRule", "") or "")
    if rule == "possible_truncated_keyword" and pre_filter.get("allow_possible_truncated_to_ai", True):
        return "", ""
    if not rule or rule not in skip_rules:
        return "", ""

    protected_rules = {"irrelevant_intent", "noise_only", "platform_affiliation", "platform_only"}
    if (
        bool(pre_filter.get("preserve_if_matches_intent", True))
        and rule in protected_rules
        and _has_preserved_intent(row, config)
    ):
        return "", ""

    term = str(hard.get("HardFilterTerm", "") or "")
    if rule == "competitor_brand":
        reason = f"Competitor brand match: {term}" if term else "Competitor brand match"
    elif rule == "typo_blacklist":
        reason = f"Typo blacklist match: {term}" if term else "Typo blacklist match"
    elif rule == "truncated_keyword":
        reason = f"Hard truncated keyword: {term}" if term else "Hard truncated keyword"
    elif rule == "irrelevant_intent":
        reason = f"Clearly irrelevant intent: {term}" if term else "Clearly irrelevant intent"
    elif rule == "noise_only":
        reason = f"Noise-only keyword: {term}" if term else "Noise-only keyword"
    elif rule == "platform_affiliation":
        reason = f"Platform affiliation without app intent: {term}" if term else "Platform affiliation without app intent"
    elif rule == "platform_only":
        reason = f"Platform-only keyword without app intent: {term}" if term else "Platform-only keyword without app intent"
    else:
        reason = f"Pre-AI hard filter match: {rule}"
    return rule, reason


def _build_pre_ai_items(rows, config, classifier_config):
    pre_filter = _pre_filter_config(classifier_config)
    if not bool(pre_filter.get("enabled", True)):
        return [
            PreAIItem(
                position=index,
                row=row,
                keyword=str(row.get("Keyword", "") or ""),
                canonical_keyword=normalize_filter_text(row.get("Keyword", "")),
                needs_ai=True,
                action="send_to_ai",
                rule="pre_filter_disabled",
                reason="Pre-AI filter disabled",
            )
            for index, row in enumerate(rows)
        ]

    items = []
    canonical_first = {}
    duplicate_strategy = str(pre_filter.get("duplicate_strategy", "canonical_reuse") or "canonical_reuse").strip().lower()
    skip_duplicates = duplicate_strategy == "canonical_reuse" and "duplicate_keyword" in pre_filter["skip_rules"]

    for index, row in enumerate(rows):
        keyword = str(row.get("Keyword", "") or "")
        canonical = normalize_filter_text(keyword)
        rule, reason = _pre_ai_skip_reason(row, config, pre_filter)
        if rule:
            item = PreAIItem(
                position=index,
                row=row,
                keyword=keyword,
                canonical_keyword=canonical,
                needs_ai=False,
                action="skip_ai",
                rule=rule,
                reason=reason,
            )
            items.append(item)
            if canonical and canonical not in canonical_first:
                canonical_first[canonical] = index
            continue

        if canonical and skip_duplicates and canonical in canonical_first:
            canonical_position = canonical_first[canonical]
            item = PreAIItem(
                position=index,
                row=row,
                keyword=keyword,
                canonical_keyword=canonical,
                needs_ai=False,
                action="reuse_canonical",
                rule="duplicate_keyword",
                reason=f"Duplicate normalized keyword; reused row {canonical_position + 1}",
                canonical_position=canonical_position,
            )
            items.append(item)
            continue

        item = PreAIItem(
            position=index,
            row=row,
            keyword=keyword,
            canonical_keyword=canonical,
            needs_ai=True,
            action="send_to_ai",
            rule="needs_ai",
            reason="Eligible for cache lookup or AI classification",
        )
        items.append(item)
        if canonical and canonical not in canonical_first:
            canonical_first[canonical] = index
    return items


def _empty_analysis(keyword, status, decision_rule="", reason=""):
    return AIKeywordAnalysis(
        keyword=keyword,
        detected_language="unknown",
        language_group="UNKNOWN",
        semantic_bucket="",
        decision_rule=decision_rule,
        reason=reason,
        confidence=0.0,
        english_gloss="",
        status=status,
    )


def _dedupe_ordered(values):
    output = []
    seen = set()
    for value in values:
        value = str(value or "").strip()
        if value and value not in seen:
            output.append(value)
            seen.add(value)
    return output


def _parse_api_keys(explicit_key=None):
    if explicit_key is not None:
        return _dedupe_ordered([explicit_key])
    configured_keys = []
    for item in str(os.environ.get("DEEPSEEK_API_KEYS", "") or "").replace("\n", ",").split(","):
        configured_keys.append(_strip_env_quotes(item))
    configured_keys.append(os.environ.get("DEEPSEEK_API_KEY", ""))
    return _dedupe_ordered(configured_keys)


def _key_label(index):
    return f"key_{index + 1}"


def _is_rate_limit_error(exc):
    return isinstance(exc, urllib.error.HTTPError) and getattr(exc, "code", None) == 429


def _is_timeout_error(exc):
    name = type(exc).__name__.lower()
    message = str(exc).lower()
    return "timeout" in name or "timed out" in message or "timeout" in message


class AIKeywordClassifier:
    def __init__(
        self,
        cache_path,
        config=None,
        app_profile=None,
        market="",
        api_key=None,
        base_url=None,
        opener=None,
        sleep=None,
        clock=None,
    ):
        self.config = config or {}
        load_project_env()
        self.classifier_config = _classifier_config(self.config)
        self.app_profile = app_profile or {}
        self.market = str(market or self.config.get("market", ""))
        self.cache_path = os.path.abspath(cache_path)
        self.api_keys = _parse_api_keys(api_key)
        self.api_key = self.api_keys[0] if self.api_keys else ""
        self.base_url = str(base_url or os.environ.get("DEEPSEEK_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
        self.opener = opener or urllib.request.urlopen
        self.sleep = sleep or time.sleep
        self.clock = clock or time.time
        self._request_lock = threading.Lock()
        self._key_lock = threading.Lock()
        self._stats_lock = threading.Lock()
        self._key_cursor = 0
        self.stats = {}
        self._initialize_cache()

    def _reset_stats(self, total_rows=0):
        self.stats = {
            "total_rows": int(total_rows),
            "cache_hit": 0,
            "api_candidates": 0,
            "api_batches": 0,
            "key_pool_size": len(self.api_keys),
            "max_workers": 0,
            "batch_seconds": [],
            "retries": 0,
            "rate_limit_errors": 0,
            "timeout_errors": 0,
            "failed_batches": 0,
            "total_ai_seconds": 0.0,
        }

    def _record_batch_stat(self, elapsed, retries=0, rate_limit_errors=0, timeout_errors=0, failed=False):
        with self._stats_lock:
            self.stats.setdefault("batch_seconds", []).append(float(elapsed))
            self.stats["retries"] = int(self.stats.get("retries", 0)) + int(retries)
            self.stats["rate_limit_errors"] = int(self.stats.get("rate_limit_errors", 0)) + int(rate_limit_errors)
            self.stats["timeout_errors"] = int(self.stats.get("timeout_errors", 0)) + int(timeout_errors)
            if failed:
                self.stats["failed_batches"] = int(self.stats.get("failed_batches", 0)) + 1

    def _next_key_index(self):
        with self._key_lock:
            index = self._key_cursor % max(len(self.api_keys), 1)
            self._key_cursor += 1
            return index

    def _candidate_key_indices(self, primary_index):
        if not self.api_keys:
            return []
        indices = [primary_index]
        if self.classifier_config.get("failover_on_key_error", True):
            indices.extend(index for index in range(len(self.api_keys)) if index != primary_index)
        return indices

    def _connect(self):
        connection = sqlite3.connect(self.cache_path, timeout=30)
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA busy_timeout=30000")
        return connection

    def _initialize_cache(self):
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        with closing(self._connect()) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS ai_keyword_analysis (
                    provider TEXT NOT NULL,
                    model TEXT NOT NULL,
                    prompt_version TEXT NOT NULL,
                    app_id TEXT NOT NULL,
                    market TEXT NOT NULL,
                    context_hash TEXT NOT NULL,
                    normalized_keyword TEXT NOT NULL,
                    keyword TEXT NOT NULL,
                    detected_language TEXT NOT NULL,
                    language_group TEXT NOT NULL,
                    semantic_bucket TEXT NOT NULL,
                    decision_rule TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    english_gloss TEXT NOT NULL,
                    raw_json TEXT NOT NULL,
                    updated_at REAL NOT NULL,
                    PRIMARY KEY (
                        provider, model, prompt_version, app_id, market,
                        context_hash, normalized_keyword
                    )
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS ai_keyword_rate_limit (
                    provider TEXT PRIMARY KEY,
                    next_request_at REAL NOT NULL
                )
                """
            )
            connection.commit()

    def _get_cached(self, keyword):
        key = _cache_key(keyword, self.config, self.market, self.app_profile, self.classifier_config)
        with closing(self._connect()) as connection:
            row = connection.execute(
                """
                SELECT keyword, detected_language, language_group, semantic_bucket,
                       decision_rule, reason, confidence, english_gloss
                FROM ai_keyword_analysis
                WHERE provider = ? AND model = ? AND prompt_version = ?
                  AND app_id = ? AND market = ? AND context_hash = ?
                  AND normalized_keyword = ?
                """,
                key,
            ).fetchone()
        if not row:
            return None
        return AIKeywordAnalysis(
            keyword=row[0],
            detected_language=row[1],
            language_group=row[2],
            semantic_bucket=row[3],
            decision_rule=row[4],
            reason=row[5],
            confidence=float(row[6]),
            english_gloss=row[7],
            status="AI_CACHE_HIT",
        )

    def _store_cached(self, result, raw_json):
        key = _cache_key(result.keyword, self.config, self.market, self.app_profile, self.classifier_config)
        with closing(self._connect()) as connection:
            connection.execute(
                """
                INSERT INTO ai_keyword_analysis (
                    provider, model, prompt_version, app_id, market, context_hash,
                    normalized_keyword, keyword, detected_language, language_group,
                    semantic_bucket, decision_rule, reason, confidence, english_gloss,
                    raw_json, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(provider, model, prompt_version, app_id, market, context_hash, normalized_keyword)
                DO UPDATE SET
                    keyword = excluded.keyword,
                    detected_language = excluded.detected_language,
                    language_group = excluded.language_group,
                    semantic_bucket = excluded.semantic_bucket,
                    decision_rule = excluded.decision_rule,
                    reason = excluded.reason,
                    confidence = excluded.confidence,
                    english_gloss = excluded.english_gloss,
                    raw_json = excluded.raw_json,
                    updated_at = excluded.updated_at
                """,
                (
                    *key,
                    result.keyword,
                    result.detected_language,
                    result.language_group,
                    result.semantic_bucket,
                    result.decision_rule,
                    result.reason,
                    result.confidence,
                    result.english_gloss,
                    json.dumps(raw_json, ensure_ascii=False, sort_keys=True),
                    self.clock(),
                ),
            )
            connection.commit()

    def _reserve_request(self, key_index):
        interval = 1.0 / max(float(self.classifier_config["requests_per_second_per_key"]), 0.1)
        rate_limit_key = f"{PROVIDER}:{_key_label(key_index)}"
        with self._request_lock:
            with closing(self._connect()) as connection:
                connection.execute("BEGIN IMMEDIATE")
                row = connection.execute(
                    "SELECT next_request_at FROM ai_keyword_rate_limit WHERE provider = ?",
                    (rate_limit_key,),
                ).fetchone()
                now = self.clock()
                request_at = max(now, row[0] if row else now)
                connection.execute(
                    """
                    INSERT INTO ai_keyword_rate_limit(provider, next_request_at) VALUES (?, ?)
                    ON CONFLICT(provider) DO UPDATE SET next_request_at = excluded.next_request_at
                    """,
                    (rate_limit_key, request_at + interval),
                )
                connection.commit()
        wait_time = request_at - self.clock()
        if wait_time > 0:
            self.sleep(wait_time)

    def _build_prompt_payload(self, keywords):
        policy = get_market_language_policy(self.market or self.config.get("market", "US_EN"), self.config)
        competitors = []
        for competitor in (self.app_profile or {}).get("competitors", [])[:6]:
            competitors.append({
                "title": competitor.get("title", ""),
                "short_description": competitor.get("short_description", ""),
                "overlap_keywords": competitor.get("overlap_keywords", []),
            })
        return {
            "app": {
                "app_id": self.config.get("app_id", ""),
                "app_name": self.config.get("app_name", ""),
                "category": self.config.get("category", ""),
                "semantic_mode": self.config.get("semantic_mode", ""),
                "market": self.market or self.config.get("market", ""),
                "primary_languages": policy.get("primary", []),
                "secondary_languages": policy.get("secondary", []),
                "core_intents": self.config.get("intent_core_terms", []),
                "core_words": self.config.get("intent_core_words", []),
                "feature_terms": self.config.get("feature_terms", []),
                "style_terms": self.config.get("style_terms", []),
                "visual_terms": self.config.get("visual_terms", []),
                "irrelevant_terms": self.config.get("irrelevant_intent_terms", []),
                "competitors": competitors,
            },
            "keywords": [
                {
                    "id": index + 1,
                    "keyword": str(item.get("Keyword", "") or ""),
                    "volume": item.get("Volume", 0),
                    "rank": str(item.get("Rank", "")),
                }
                for index, item in enumerate(keywords)
            ],
        }

    def _messages(self, prompt_payload):
        return [
            {
                "role": "system",
                "content": (
                    "You are an ASO keyword classifier. Return only valid JSON. "
                    "Classify each keyword for the target market and app. "
                    "Do not use Python-style comments or markdown. "
                    "Use only these language_group values: PRIMARY, SECONDARY, MIXED, FOREIGN, UNKNOWN. "
                    "Use only these semantic_bucket values: Core Intent Final, Broad Expansion, "
                    "Feature Keywords, Style Keywords, Consider Keywords, Generic Style Reserve, "
                    "Language Mismatch Audit, Manual Review, Dropped. "
                    "Prefer semantic relevance over literal English word matching. "
                    "For mixed local-language plus English app terms, keep the keyword eligible for "
                    "Core/Feature/Style/Broad when the intent is relevant."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Return JSON with this exact shape: "
                    "{\"items\":[{\"id\":1,\"keyword\":\"...\",\"detected_language\":\"vi\","
                    "\"language_group\":\"PRIMARY\",\"semantic_bucket\":\"Core Intent Final\","
                    "\"decision_rule\":\"ai_core_intent\",\"reason\":\"short audit reason\","
                    "\"confidence\":0.0,\"english_gloss\":\"short English gloss\"}]}. "
                    "Classify every keyword exactly once. Input:\n"
                    + json.dumps(prompt_payload, ensure_ascii=False)
                ),
            },
        ]

    def _fetch_batch(self, keyword_rows):
        if not self.api_keys:
            raise AIKeywordClassifierError("Missing DEEPSEEK_API_KEYS or DEEPSEEK_API_KEY for uncached AI keyword classification")
        primary_index = self._next_key_index()
        errors = []
        for key_index in self._candidate_key_indices(primary_index):
            try:
                return self._fetch_batch_with_key(keyword_rows, key_index)
            except AIKeywordClassifierError as exc:
                errors.append(f"{_key_label(key_index)}: {exc}")
                if not self.classifier_config.get("failover_on_key_error", True):
                    break
        raise AIKeywordClassifierError(f"DeepSeek keyword classification failed on all configured keys: {' | '.join(errors)[-1000:]}")

    def _fetch_batch_with_key(self, keyword_rows, key_index):
        api_key = self.api_keys[key_index]
        key_label = _key_label(key_index)
        started_at = self.clock()
        self._reserve_request(key_index)
        prompt_payload = self._build_prompt_payload(keyword_rows)
        body = {
            "model": self.classifier_config["model"],
            "messages": self._messages(prompt_payload),
            "response_format": {"type": "json_object"},
            "stream": False,
            "temperature": 0,
            "thinking": {"type": "disabled"},
            "max_tokens": int((self.config.get("ai_keyword_classifier", {}) or {}).get("max_tokens", 8192)),
        }
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            method="POST",
        )
        errors = []
        retry_count = 0
        rate_limit_errors = 0
        timeout_errors = 0
        for attempt in range(max(1, int(self.classifier_config["retries"]))):
            try:
                with self.opener(request, timeout=self.classifier_config["timeout"], context=ssl.create_default_context()) as response:
                    response_data = json.loads(response.read().decode("utf-8"))
                break
            except Exception as exc:
                if _is_rate_limit_error(exc):
                    rate_limit_errors += 1
                if _is_timeout_error(exc):
                    timeout_errors += 1
                errors.append(f"{type(exc).__name__}: {exc}")
                if attempt + 1 < max(1, int(self.classifier_config["retries"])):
                    retry_count += 1
                    self.sleep(1.0 * (2 ** attempt))
        else:
            elapsed = self.clock() - started_at
            self._record_batch_stat(
                elapsed,
                retries=retry_count,
                rate_limit_errors=rate_limit_errors,
                timeout_errors=timeout_errors,
                failed=True,
            )
            print(
                "AI batch completed: "
                f"key={key_label}, rows={len(keyword_rows)}, seconds={elapsed:.2f}, status=error"
            )
            raise AIKeywordClassifierError(f"DeepSeek keyword classification failed: {' | '.join(errors)[-1000:]}")
        try:
            content = response_data["choices"][0]["message"]["content"]
            parsed = json.loads(content)
        except Exception as exc:
            elapsed = self.clock() - started_at
            self._record_batch_stat(
                elapsed,
                retries=retry_count,
                rate_limit_errors=rate_limit_errors,
                timeout_errors=timeout_errors,
                failed=True,
            )
            print(
                "AI batch completed: "
                f"key={key_label}, rows={len(keyword_rows)}, seconds={elapsed:.2f}, status=error"
            )
            raise AIKeywordClassifierError(f"DeepSeek returned invalid JSON content: {type(exc).__name__}: {exc}") from exc
        results = self._validate_batch(keyword_rows, parsed)
        elapsed = self.clock() - started_at
        self._record_batch_stat(
            elapsed,
            retries=retry_count,
            rate_limit_errors=rate_limit_errors,
            timeout_errors=timeout_errors,
        )
        print(
            "AI batch completed: "
            f"key={key_label}, rows={len(keyword_rows)}, seconds={elapsed:.2f}, status=ok"
        )
        return results, parsed

    def _validate_batch(self, keyword_rows, parsed):
        items = parsed.get("items") if isinstance(parsed, dict) else None
        if not isinstance(items, list):
            raise AIKeywordClassifierError("DeepSeek response missing items list")
        by_id = {int(item.get("id")): item for item in items if isinstance(item, dict) and str(item.get("id", "")).isdigit()}
        if len(by_id) != len(keyword_rows):
            raise AIKeywordClassifierError(f"DeepSeek response item count mismatch: expected {len(keyword_rows)}, got {len(by_id)}")
        results = []
        for index, row in enumerate(keyword_rows, 1):
            item = by_id.get(index)
            if not item:
                raise AIKeywordClassifierError(f"DeepSeek response missing keyword id {index}")
            keyword = str(row.get("Keyword", "") or "")
            response_keyword = str(item.get("keyword", "") or "")
            if normalize_filter_text(response_keyword) != normalize_filter_text(keyword):
                raise AIKeywordClassifierError(f"DeepSeek response keyword mismatch for id {index}: {response_keyword!r} != {keyword!r}")
            detected_language = str(item.get("detected_language", "") or "unknown").strip().lower()
            language_group = str(item.get("language_group", "") or "").strip().upper()
            semantic_bucket = str(item.get("semantic_bucket", "") or "").strip()
            if language_group not in LANGUAGE_GROUPS:
                raise AIKeywordClassifierError(f"Invalid language_group for {keyword!r}: {language_group!r}")
            if semantic_bucket not in SEMANTIC_BUCKETS:
                raise AIKeywordClassifierError(f"Invalid semantic_bucket for {keyword!r}: {semantic_bucket!r}")
            try:
                confidence = max(0.0, min(1.0, float(item.get("confidence", 0.0))))
            except (TypeError, ValueError):
                confidence = 0.0
            results.append(
                AIKeywordAnalysis(
                    keyword=keyword,
                    detected_language=detected_language,
                    language_group=language_group,
                    semantic_bucket=semantic_bucket,
                    decision_rule=str(item.get("decision_rule", "") or "ai_semantic_classification"),
                    reason=str(item.get("reason", "") or "AI semantic classification"),
                    confidence=confidence,
                    english_gloss=str(item.get("english_gloss", "") or ""),
                )
            )
        return results

    def analyze_rows(self, rows):
        started_at = self.clock()
        self._reset_stats(total_rows=len(rows))
        results = {}
        missing = []
        for row in rows:
            keyword = str(row.get("Keyword", "") or "")
            cached = self._get_cached(keyword)
            if cached is not None:
                results[keyword] = cached
                self.stats["cache_hit"] += 1
            else:
                missing.append(row)
        self.stats["api_candidates"] = len(missing)
        batch_size = max(1, int(self.classifier_config["batch_size"]))
        batches = [missing[start:start + batch_size] for start in range(0, len(missing), batch_size)]
        self.stats["api_batches"] = len(batches)
        effective_workers = min(
            max(1, int(self.classifier_config.get("max_workers", DEFAULT_MAX_WORKERS) or DEFAULT_MAX_WORKERS)),
            max(1, len(self.api_keys) * 2),
            max(1, len(batches)),
        )
        self.stats["max_workers"] = effective_workers if batches else 0

        def fetch_and_store(batch):
            batch_results, raw_json = self._fetch_batch(batch)
            stored = {}
            for result in batch_results:
                self._store_cached(result, raw_json)
                stored[result.keyword] = result
            return stored

        if batches:
            with ThreadPoolExecutor(max_workers=effective_workers) as executor:
                futures = [executor.submit(fetch_and_store, batch) for batch in batches]
                for future in as_completed(futures):
                    results.update(future.result())
        self.stats["total_ai_seconds"] = self.clock() - started_at
        return results


def _fallback_dataframe(df, config, english_vocab=None, market=""):
    import pandas as pd

    rows = []
    for _, row in df.iterrows():
        lang, group = detect_keyword_language(row.get("Keyword", ""), market or config.get("market", "US_EN"), config, english_vocab=english_vocab)
        rows.append({
            "NeedsAI": False,
            "PreAIAction": "ai_disabled",
            "PreAIRule": "ai_disabled",
            "PreAIReason": "AI classifier disabled; used heuristic language detector",
            "CanonicalKeyword": normalize_filter_text(row.get("Keyword", "")),
            "DetectedLanguage": lang,
            "LanguageGroup": group,
            "AISemanticBucket": "",
            "AIDecisionRule": "",
            "AIReason": "",
            "AIConfidence": 0.0,
            "AIEnglishGloss": "",
            "AIStatus": "AI_DISABLED_HEURISTIC",
        })
    return pd.DataFrame(rows, index=df.index)


def analyze_dataframe(df, config, app_profile=None, cache_path=None, market="", english_vocab=None, service=None):
    import pandas as pd

    if not enabled(config):
        return _fallback_dataframe(df, config, english_vocab=english_vocab, market=market)
    classifier_config = _classifier_config(config)
    if cache_path is None:
        configured_path = classifier_config["cache_path"]
        cache_path = configured_path if os.path.isabs(configured_path) else os.path.join(os.getcwd(), configured_path)
    service = service or AIKeywordClassifier(cache_path, config=config, app_profile=app_profile, market=market)
    rows = [row.to_dict() for _, row in df.iterrows()]
    pre_ai_items = _build_pre_ai_items(rows, config, classifier_config)
    ai_rows = [item.row for item in pre_ai_items if item.needs_ai]
    try:
        result_by_keyword = service.analyze_rows(ai_rows) if ai_rows else {}
    except AIKeywordClassifierError:
        if classifier_config["fail_on_api_error"]:
            raise
        return _fallback_dataframe(df, config, english_vocab=english_vocab, market=market)

    result_by_position = {}
    for item in pre_ai_items:
        if item.needs_ai:
            result = result_by_keyword.get(item.keyword)
            if result is None:
                raise AIKeywordClassifierError(f"Missing AI classification result for {item.keyword!r}")
            result_by_position[item.position] = result
        elif item.action == "skip_ai":
            result_by_position[item.position] = _empty_analysis(
                item.keyword,
                "AI_SKIPPED_PREFILTER",
                decision_rule=item.rule,
                reason=item.reason,
            )

    for item in pre_ai_items:
        if item.action != "reuse_canonical":
            continue
        canonical_result = result_by_position.get(item.canonical_position)
        if canonical_result is None:
            raise AIKeywordClassifierError(f"Missing canonical AI classification result for {item.keyword!r}")
        result_by_position[item.position] = AIKeywordAnalysis(
            keyword=item.keyword,
            detected_language=canonical_result.detected_language,
            language_group=canonical_result.language_group,
            semantic_bucket=canonical_result.semantic_bucket,
            decision_rule=canonical_result.decision_rule,
            reason=canonical_result.reason,
            confidence=canonical_result.confidence,
            english_gloss=canonical_result.english_gloss,
            status="AI_REUSED_CANONICAL",
        )

    output = []
    for item in pre_ai_items:
        result = result_by_position.get(item.position)
        if result is None:
            raise AIKeywordClassifierError(f"Missing AI classification result for {item.keyword!r}")
        output.append({
            "NeedsAI": item.needs_ai,
            "PreAIAction": item.action,
            "PreAIRule": item.rule,
            "PreAIReason": item.reason,
            "CanonicalKeyword": item.canonical_keyword,
            "DetectedLanguage": result.detected_language,
            "LanguageGroup": result.language_group,
            "AISemanticBucket": result.semantic_bucket,
            "AIDecisionRule": result.decision_rule,
            "AIReason": result.reason,
            "AIConfidence": result.confidence,
            "AIEnglishGloss": result.english_gloss,
            "AIStatus": result.status,
        })
    frame = pd.DataFrame(output, index=df.index)
    status_counts = frame["AIStatus"].value_counts().to_dict()
    stats = getattr(service, "stats", {}) or {}
    batch_seconds = list(stats.get("batch_seconds", []) or [])
    avg_batch_seconds = (sum(batch_seconds) / len(batch_seconds)) if batch_seconds else 0.0
    slowest_batch_seconds = max(batch_seconds) if batch_seconds else 0.0
    print(
        "AI keyword classification summary: "
        f"provider={PROVIDER}, model={classifier_config['model']}, "
        f"total_rows={len(df)}, "
        f"cache_hit={status_counts.get('AI_CACHE_HIT', 0)}, "
        f"classified={status_counts.get('AI_CLASSIFIED', 0)}, "
        f"reused={status_counts.get('AI_REUSED_CANONICAL', 0)}, "
        f"pre_skipped={status_counts.get('AI_SKIPPED_PREFILTER', 0)}, "
        f"api_candidates={stats.get('api_candidates', 0)}, "
        f"api_batches={stats.get('api_batches', 0)}, "
        f"key_pool_size={stats.get('key_pool_size', 0)}, "
        f"max_workers={stats.get('max_workers', 0)}, "
        f"avg_batch_seconds={avg_batch_seconds:.2f}, "
        f"slowest_batch_seconds={slowest_batch_seconds:.2f}, "
        f"retries={stats.get('retries', 0)}, "
        f"rate_limit_errors={stats.get('rate_limit_errors', 0)}, "
        f"timeout_errors={stats.get('timeout_errors', 0)}, "
        f"total_ai_seconds={float(stats.get('total_ai_seconds', 0.0)):.2f}"
    )
    return frame
