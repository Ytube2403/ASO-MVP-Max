import json
import os
import ssl
import tempfile
import unittest

import pandas as pd

from shared.translation_service import TranslationService, translate_dataframe


class FakeResponse:
    def __init__(self, translated):
        self.payload = json.dumps([[[translated]]]).encode("utf-8")

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

            def opener(request, timeout, context):
                contexts.append(context)
                return FakeResponse("funny sounds")

            service = TranslationService(
                os.path.join(temp_dir, "translations.sqlite3"),
                opener=opener,
                sleep=lambda _: None,
                requests_per_second=1000,
            )
            first = service.translate("sonidos divertidos", "es")
            second = service.translate("sonidos divertidos", "es")
            self.assertEqual(first.status, "TRANSLATED")
            self.assertEqual(second.status, "CACHE_HIT")
            self.assertEqual(len(contexts), 1)
            self.assertNotEqual(contexts[0].verify_mode, ssl.CERT_NONE)

    def test_failed_translation_keeps_raw_with_audit(self):
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
            result = service.translate("broma", "es")
            self.assertEqual(result.text, "broma")
            self.assertEqual(result.status, "FAILED_RAW_FALLBACK")
            self.assertEqual(len(calls), 3)

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


if __name__ == "__main__":
    unittest.main()
