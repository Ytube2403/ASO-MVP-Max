import json
import os
import sqlite3
import ssl
import threading
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from dataclasses import dataclass

from shared.keyword_filter.matcher import normalize_filter_text


class TranslationUnavailableError(ConnectionError):
    pass


PROVIDER = "libretranslate_local"
TARGET_LANGUAGE = "en"
TRANSLATION_COLUMNS = ["TranslationStatus", "TranslationError"]
DEFAULT_BASE_URL = "http://127.0.0.1:5001"
DEFAULT_REQUESTS_PER_SECOND = 2
DEFAULT_MAX_WORKERS = 2


def normalize_source_language(source_language, market="", target_language=TARGET_LANGUAGE):
    language = str(source_language or "").strip().lower().replace("_", "-")
    target_language = str(target_language or TARGET_LANGUAGE).strip().lower()
    aliases = {
        "fil": "tl",
        "tagalog": "tl",
        "pt-br": "pt",
    }
    if not language or language == "unknown":
        return "auto"
    if "+" in language:
        parts = {
            aliases.get(part, part)
            for part in language.split("+")
            if part and part != target_language
        }
        language = next(iter(parts)) if len(parts) == 1 else "auto"
    else:
        language = aliases.get(language, language)
    if str(market or "").strip().upper().replace("-", "_") == "BR_PT_BR" and language == "pt":
        return "pb"
    return language


@dataclass(frozen=True)
class TranslationResult:
    text: str
    status: str
    error: str = ""


class TranslationService:
    def __init__(
        self,
        cache_path,
        requests_per_second=None,
        retries=3,
        timeout=5,
        opener=None,
        sleep=None,
        clock=None,
        base_url=None,
        api_key=None,
        market="",
    ):
        self.cache_path = os.path.abspath(cache_path)
        configured_rps = (
            requests_per_second
            if requests_per_second is not None
            else os.environ.get("ASO_TRANSLATION_RPS", DEFAULT_REQUESTS_PER_SECOND)
        )
        self.requests_per_second = max(float(configured_rps), 0.1)
        self.retries = max(int(retries), 1)
        self.timeout = float(timeout)
        self.opener = opener or urllib.request.urlopen
        self.sleep = sleep or time.sleep
        self.clock = clock or time.time
        self.market = str(market or "")
        self.base_url = str(
            base_url or os.environ.get("LIBRETRANSLATE_URL") or DEFAULT_BASE_URL
        ).rstrip("/")
        self.api_key = str(
            api_key if api_key is not None else os.environ.get("LIBRETRANSLATE_API_KEY", "")
        ).strip()
        self._health_lock = threading.Lock()
        self._health_checked = False
        self._health_error = ""
        self._initialize_cache()

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
                CREATE TABLE IF NOT EXISTS translations (
                    provider TEXT NOT NULL,
                    source_language TEXT NOT NULL,
                    target_language TEXT NOT NULL,
                    normalized_keyword TEXT NOT NULL,
                    translated_text TEXT NOT NULL,
                    updated_at REAL NOT NULL,
                    PRIMARY KEY (provider, source_language, target_language, normalized_keyword)
                )
                """
            )
            connection.commit()
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS rate_limit (
                    provider TEXT PRIMARY KEY,
                    next_request_at REAL NOT NULL
                )
                """
            )
            connection.commit()

    def _cache_key(self, keyword, source_language, target_language):
        return (
            PROVIDER,
            normalize_source_language(source_language, self.market, target_language),
            str(target_language or TARGET_LANGUAGE).lower(),
            normalize_filter_text(keyword),
        )

    def _get_cached(self, keyword, source_language, target_language):
        key = self._cache_key(keyword, source_language, target_language)
        with closing(self._connect()) as connection:
            row = connection.execute(
                """
                SELECT translated_text FROM translations
                WHERE provider = ? AND source_language = ? AND target_language = ? AND normalized_keyword = ?
                """,
                key,
            ).fetchone()
        return row[0] if row else None

    def _store_cached(self, keyword, source_language, target_language, translated_text):
        key = self._cache_key(keyword, source_language, target_language)
        with closing(self._connect()) as connection:
            connection.execute(
                """
                INSERT INTO translations (
                    provider, source_language, target_language, normalized_keyword, translated_text, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(provider, source_language, target_language, normalized_keyword)
                DO UPDATE SET translated_text = excluded.translated_text, updated_at = excluded.updated_at
                """,
                (*key, str(translated_text), self.clock()),
            )
            connection.commit()

    def _reserve_request(self):
        interval = 1.0 / self.requests_per_second
        with closing(self._connect()) as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT next_request_at FROM rate_limit WHERE provider = ?",
                (PROVIDER,),
            ).fetchone()
            now = self.clock()
            request_at = max(now, row[0] if row else now)
            connection.execute(
                """
                INSERT INTO rate_limit(provider, next_request_at) VALUES (?, ?)
                ON CONFLICT(provider) DO UPDATE SET next_request_at = excluded.next_request_at
                """,
                (PROVIDER, request_at + interval),
            )
            connection.commit()
        wait_time = request_at - self.clock()
        if wait_time > 0:
            self.sleep(wait_time)

    def _ensure_healthy(self):
        if self._health_checked:
            if self._health_error:
                raise TranslationUnavailableError(self._health_error)
            return
        with self._health_lock:
            if self._health_checked:
                if self._health_error:
                    raise TranslationUnavailableError(self._health_error)
                return
            request = urllib.request.Request(f"{self.base_url}/health")
            context = ssl.create_default_context()
            try:
                with self.opener(request, timeout=self.timeout, context=context) as response:
                    response.read()
            except Exception as exc:
                self._health_error = (
                    f"LibreTranslate health check failed at {self.base_url}: "
                    f"{type(exc).__name__}: {exc}"
                )
                self._health_checked = True
                raise TranslationUnavailableError(self._health_error) from exc
            self._health_checked = True

    def _fetch(self, keyword, source_language, target_language):
        self._ensure_healthy()
        self._reserve_request()
        payload = {
            "q": str(keyword),
            "source": normalize_source_language(source_language, self.market, target_language),
            "target": str(target_language or TARGET_LANGUAGE).lower(),
            "format": "text",
        }
        if self.api_key:
            payload["api_key"] = self.api_key
        request = urllib.request.Request(
            f"{self.base_url}/translate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        context = ssl.create_default_context()
        with self.opener(request, timeout=self.timeout, context=context) as response:
            data = json.loads(response.read().decode("utf-8"))
        translated = str(data.get("translatedText", ""))
        if not translated:
            raise ValueError("Translation provider returned an empty response")
        return translated

    def translate(self, keyword, source_language="auto", target_language=TARGET_LANGUAGE, market=""):
        keyword = str(keyword or "")
        if market:
            self.market = str(market)
        source_language = normalize_source_language(source_language, self.market, target_language)
        if source_language == target_language.lower():
            return TranslationResult(keyword, "NOT_REQUIRED")
        cached = self._get_cached(keyword, source_language, target_language)
        if cached is not None:
            return TranslationResult(cached, "CACHE_HIT")
        errors = []
        for attempt in range(self.retries):
            try:
                translated = self._fetch(keyword, source_language, target_language)
                self._store_cached(keyword, source_language, target_language, translated)
                return TranslationResult(translated, "TRANSLATED")
            except TranslationUnavailableError:
                raise
            except Exception as exc:
                errors.append(f"{type(exc).__name__}: {exc}")
                if self._health_error:
                    break
                if attempt + 1 < self.retries:
                    self.sleep(0.5 * (2 ** attempt))
        return TranslationResult(keyword, "FAILED_RAW_FALLBACK", " | ".join(errors)[-1000:])


def translation_cache_count(cache_path, provider=PROVIDER):
    if not os.path.exists(cache_path):
        return 0
    try:
        with closing(sqlite3.connect(cache_path, timeout=30)) as connection:
            row = connection.execute(
                "SELECT COUNT(*) FROM translations WHERE provider = ?",
                (provider,),
            ).fetchone()
        return int(row[0]) if row else 0
    except sqlite3.Error:
        return 0


def translate_dataframe(df, provided_en=None, cache_path=None, max_workers=None, service=None, market=""):
    import pandas as pd

    if cache_path is None:
        cache_path = os.path.join(os.getcwd(), ".cache", "translations.sqlite3")
    service = service or TranslationService(cache_path, market=market)
    if market:
        service.market = str(market)
    configured_workers = (
        max_workers
        if max_workers is not None
        else os.environ.get("ASO_TRANSLATION_MAX_WORKERS", DEFAULT_MAX_WORKERS)
    )
    provided = provided_en if provided_en is not None else pd.Series("", index=df.index)
    tasks = {}
    results = {}
    for index, row in df.iterrows():
        keyword = str(row.get("Keyword", "") or "")
        source_language = str(row.get("DetectedLanguage", "auto") or "auto").lower()
        supplied = str(provided.get(index, "") or "").strip()
        if supplied:
            results[index] = TranslationResult(supplied, "PROVIDED_EN")
        elif source_language == TARGET_LANGUAGE:
            results[index] = TranslationResult(keyword, "NOT_REQUIRED")
        else:
            tasks.setdefault((keyword, source_language), []).append(index)

    def worker(task):
        keyword, source_language = task
        return task, service.translate(keyword, source_language)

    with ThreadPoolExecutor(max_workers=max(1, int(configured_workers))) as executor:
        for task, result in executor.map(worker, tasks):
            for index in tasks[task]:
                results[index] = result
    ordered = [results[index] for index in df.index]
    fallback_results = [result for result in ordered if result.status == "FAILED_RAW_FALLBACK"]
    status_counts = {}
    for result in ordered:
        status_counts[result.status] = status_counts.get(result.status, 0) + 1
    auto_sources = sum(
        len(indexes)
        for (_, source_language), indexes in tasks.items()
        if normalize_source_language(source_language, service.market) == "auto"
    )
    if tasks:
        print(
            "Translation summary: "
            f"provider={PROVIDER}, cache_hit={status_counts.get('CACHE_HIT', 0)}, "
            f"translated={status_counts.get('TRANSLATED', 0)}, auto_source={auto_sources}, "
            f"raw_fallback={len(fallback_results)}"
        )
    if fallback_results:
        print(
            "Warning: LibreTranslate kept raw text for "
            f"{len(fallback_results)} keyword(s). Check local service at {service.base_url}. "
            f"First error: {fallback_results[0].error[:300]}"
        )
    return pd.DataFrame(
        {
            "EN": [result.text for result in ordered],
            "TranslationStatus": [result.status for result in ordered],
            "TranslationError": [result.error for result in ordered],
        },
        index=df.index,
    )
