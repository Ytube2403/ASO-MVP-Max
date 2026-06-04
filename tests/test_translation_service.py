import io
import json
import os
import sqlite3
import ssl
import tempfile
import unittest
from contextlib import closing, redirect_stdout
from unittest.mock import patch

import pandas as pd

from shared.translation_service import (
    DEFAULT_MAX_WORKERS,
    DEFAULT_REQUESTS_PER_SECOND,
    PROVIDER,
    TranslationService,
    TranslationUnavailableError,
    normalize_source_language,
    translate_dataframe,
    translation_cache_count,
)


class FakeResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self.payload


class TranslationServiceTests(unittest.TestCase):
    def test_translate_uses_verified_tls_and_cache(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            contexts = []
            requests = []

            def opener(request, timeout, context):
                contexts.append(context)
                requests.append(request)
                if request.full_url.endswith("/health"):
                    return FakeResponse({"status": "ok"})
                return FakeResponse({"translatedText": "funny sounds"})

            service = TranslationService(
                os.path.join(temp_dir, "translations.sqlite3"),
                opener=opener,
                sleep=lambda _: None,
                requests_per_second=1000,
                base_url="https://translate.local:5001",
                api_key="secret",
            )
            first = service.translate("sonidos divertidos", "es")
            second = service.translate("sonidos divertidos", "es")
            self.assertEqual(first.status, "TRANSLATED")
            self.assertEqual(second.status, "CACHE_HIT")
            self.assertEqual(len(contexts), 2)
            self.assertTrue(all(context.verify_mode != ssl.CERT_NONE for context in contexts))
            self.assertEqual(requests[1].get_method(), "POST")
            self.assertNotIn("googleapis.com", requests[1].full_url)
            self.assertEqual(
                json.loads(requests[1].data.decode("utf-8")),
                {
                    "q": "sonidos divertidos",
                    "source": "es",
                    "target": "en",
                    "format": "text",
                    "api_key": "secret",
                },
            )

    def test_failed_health_check_stops_without_repeated_requests(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            calls = []

            def opener(*args, **kwargs):
                calls.append(1)
                raise OSError("offline")

            service = TranslationService(
                os.path.join(temp_dir, "translations.sqlite3"),
                opener=opener,
                sleep=lambda _: None,
                retries=3,
                requests_per_second=1000,
            )
            with self.assertRaises(TranslationUnavailableError) as context:
                service.translate("broma", "es")
            self.assertIn("LibreTranslate health check failed", str(context.exception))
            self.assertEqual(len(calls), 1)

    def test_source_language_mapping_uses_libretranslate_codes(self):
        self.assertEqual(normalize_source_language("fil"), "tl")
        self.assertEqual(normalize_source_language("tagalog"), "tl")
        self.assertEqual(normalize_source_language("unknown"), "auto")
        self.assertEqual(normalize_source_language(""), "auto")
        self.assertEqual(normalize_source_language("fil+en"), "tl")
        self.assertEqual(normalize_source_language("pt+en"), "pt")
        self.assertEqual(normalize_source_language("en+es"), "es")
        self.assertEqual(normalize_source_language("es+id"), "auto")
        self.assertEqual(normalize_source_language("pt", "BR_PT-BR"), "pb")
        self.assertEqual(normalize_source_language("es"), "es")

    def test_google_cache_is_not_reused_for_libretranslate(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_path = os.path.join(temp_dir, "translations.sqlite3")
            requests = []

            def opener(request, timeout, context):
                requests.append(request)
                if request.full_url.endswith("/health"):
                    return FakeResponse({"status": "ok"})
                return FakeResponse({"translatedText": "libre prank"})

            service = TranslationService(cache_path, opener=opener, sleep=lambda _: None)
            with closing(sqlite3.connect(cache_path)) as connection:
                connection.execute(
                    """
                    INSERT INTO translations (
                        provider, source_language, target_language, normalized_keyword, translated_text, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    ("google_gtx", "es", "en", "broma", "google prank", 1.0),
                )
                connection.commit()
            result = service.translate("broma", "es")
            self.assertEqual(PROVIDER, "libretranslate_local")
            self.assertEqual(result.text, "libre prank")
            self.assertEqual(result.status, "TRANSLATED")
            self.assertEqual(len(requests), 2)

    def test_libretranslate_cache_hit_works_while_service_is_offline(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            calls = []

            def opener(*args, **kwargs):
                calls.append(1)
                raise OSError("offline")

            service = TranslationService(os.path.join(temp_dir, "translations.sqlite3"), opener=opener)
            service._store_cached("broma", "es", "en", "prank")
            result = service.translate("broma", "es")
            self.assertEqual(result.text, "prank")
            self.assertEqual(result.status, "CACHE_HIT")
            self.assertEqual(calls, [])

    def test_endpoint_reads_environment_override(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(
                os.environ,
                {
                    "LIBRETRANSLATE_URL": "http://localhost:5999/",
                    "LIBRETRANSLATE_API_KEY": "env-key",
                },
            ):
                service = TranslationService(os.path.join(temp_dir, "translations.sqlite3"))
            self.assertEqual(service.base_url, "http://localhost:5999")
            self.assertEqual(service.api_key, "env-key")

    def test_environment_controls_default_request_rate(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(os.environ, {"ASO_TRANSLATION_RPS": "1.5"}):
                service = TranslationService(os.path.join(temp_dir, "translations.sqlite3"))
            self.assertEqual(DEFAULT_REQUESTS_PER_SECOND, 2)
            self.assertEqual(DEFAULT_MAX_WORKERS, 2)
            self.assertEqual(service.requests_per_second, 1.5)

    def test_translation_cache_count_only_counts_current_provider(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_path = os.path.join(temp_dir, "translations.sqlite3")
            service = TranslationService(cache_path)
            service._store_cached("broma", "es", "en", "prank")
            with closing(sqlite3.connect(cache_path)) as connection:
                connection.execute(
                    """
                    INSERT INTO translations (
                        provider, source_language, target_language, normalized_keyword, translated_text, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    ("google_gtx", "es", "en", "sonido", "sound", 1.0),
                )
                connection.commit()
            self.assertEqual(translation_cache_count(cache_path), 1)

    def test_rate_limit_reserves_global_request_slots(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            sleeps = []
            service = TranslationService(
                os.path.join(temp_dir, "translations.sqlite3"),
                sleep=sleeps.append,
                clock=lambda: 100.0,
                requests_per_second=2,
            )
            service._reserve_request()
            service._reserve_request()
            self.assertEqual(sleeps, [0.5])

    def test_dataframe_records_provided_and_not_required(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            frame = pd.DataFrame([
                {"Keyword": "prank", "DetectedLanguage": "en"},
                {"Keyword": "broma", "DetectedLanguage": "es"},
            ])
            translated = translate_dataframe(
                frame,
                provided_en=pd.Series(["", "prank"]),
                cache_path=os.path.join(temp_dir, "translations.sqlite3"),
            )
            self.assertEqual(list(translated["TranslationStatus"]), ["NOT_REQUIRED", "PROVIDED_EN"])

    def test_dataframe_stops_when_translation_is_unavailable(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            calls = []

            def opener(*args, **kwargs):
                calls.append(1)
                raise OSError("offline")

            frame = pd.DataFrame([
                {"Keyword": "broma", "DetectedLanguage": "es"},
                {"Keyword": "broma", "DetectedLanguage": "es"},
            ])
            service = TranslationService(os.path.join(temp_dir, "translations.sqlite3"), opener=opener)
            output = io.StringIO()
            with self.assertRaises(TranslationUnavailableError):
                with redirect_stdout(output):
                    translate_dataframe(frame, service=service)
            self.assertEqual(len(calls), 1)


if __name__ == "__main__":
    unittest.main()
