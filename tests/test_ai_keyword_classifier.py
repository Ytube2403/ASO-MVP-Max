import copy
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
import urllib.error

import pandas as pd


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from shared.ai_keyword_classifier import AIKeywordClassifier, AIKeywordClassifierError, analyze_dataframe


BASE_CONFIG = {
    "app_id": "com.example.app",
    "app_name": "Example App",
    "category": "Personalization",
    "market": "VN_VI",
    "market_language_policy": {
        "primary_languages": ["vi"],
        "secondary_languages": ["en"],
        "mixed_language_action": "manual_review",
    },
    "intent_core_terms": ["pin emoji", "thanh trạng thái"],
    "feature_terms": ["phím tắt"],
    "style_terms": ["dễ thương"],
    "visual_terms": [],
    "irrelevant_intent_terms": [],
    "ai_keyword_classifier": {
        "enabled": True,
        "provider": "deepseek",
        "model": "deepseek-v4-flash",
        "prompt_version": "test-v1",
        "batch_size": 2,
        "requests_per_second": 1000,
        "fail_on_api_error": True,
        "pre_filter": {
            "enabled": True,
            "duplicate_strategy": "canonical_reuse",
            "preserve_if_matches_intent": True,
            "allow_possible_truncated_to_ai": True,
        },
    },
}


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


class AIKeywordClassifierTests(unittest.TestCase):
    def test_analyze_dataframe_calls_api_for_misses_and_reuses_cache(self):
        requests = []

        def opener(request, timeout=None, context=None):
            requests.append(request)
            body = json.loads(request.data.decode("utf-8"))
            user_content = body["messages"][1]["content"]
            prompt_payload = json.loads(user_content.split("Input:\n", 1)[1])
            items = []
            for item in prompt_payload["keywords"]:
                items.append({
                    "id": item["id"],
                    "keyword": item["keyword"],
                    "detected_language": "vi",
                    "language_group": "PRIMARY",
                    "semantic_bucket": "Core Intent Final",
                    "decision_rule": "ai_core_intent",
                    "reason": "Relevant local-market ASO keyword.",
                    "confidence": 0.91,
                    "english_gloss": "battery status",
                })
            return FakeResponse({"choices": [{"message": {"content": json.dumps({"items": items})}}]})

        with tempfile.TemporaryDirectory() as temp_dir:
            df = pd.DataFrame({"Keyword": ["phím tắt", "thanh trạng thái", "pin dễ thương"], "Volume": [1, 2, 3], "Rank": ["", "", ""]})
            cache_path = os.path.join(temp_dir, "ai.sqlite3")
            service = AIKeywordClassifier(cache_path, BASE_CONFIG, market="VN_VI", api_key="secret", opener=opener, sleep=lambda _: None)
            first = analyze_dataframe(df, BASE_CONFIG, cache_path=cache_path, market="VN_VI", service=service)
            self.assertEqual(len(requests), 2)
            self.assertEqual(first["AISemanticBucket"].tolist(), ["Core Intent Final"] * 3)

            offline_service = AIKeywordClassifier(cache_path, BASE_CONFIG, market="VN_VI", api_key="", opener=opener, sleep=lambda _: None)
            second = analyze_dataframe(df, BASE_CONFIG, cache_path=cache_path, market="VN_VI", service=offline_service)
            self.assertEqual(len(requests), 2)
            self.assertEqual(second["AIStatus"].tolist(), ["AI_CACHE_HIT"] * 3)

    def test_missing_key_fails_fast_for_uncached_keywords(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            df = pd.DataFrame({"Keyword": ["phím tắt"], "Volume": [1], "Rank": [""]})
            service = AIKeywordClassifier(os.path.join(temp_dir, "ai.sqlite3"), BASE_CONFIG, market="VN_VI", api_key="")
            with self.assertRaises(AIKeywordClassifierError):
                analyze_dataframe(df, BASE_CONFIG, cache_path=service.cache_path, market="VN_VI", service=service)

    def test_loads_deepseek_credentials_from_project_env_file(self):
        previous_key = os.environ.pop("DEEPSEEK_API_KEY", None)
        previous_keys = os.environ.pop("DEEPSEEK_API_KEYS", None)
        previous_workers = os.environ.pop("DEEPSEEK_MAX_WORKERS", None)
        previous_rps = os.environ.pop("DEEPSEEK_REQUESTS_PER_SECOND_PER_KEY", None)
        previous_base_url = os.environ.pop("DEEPSEEK_BASE_URL", None)
        previous_cwd = os.getcwd()
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                try:
                    with open(os.path.join(temp_dir, ".env"), "w", encoding="utf-8") as env_file:
                        env_file.write(
                            "DEEPSEEK_API_KEYS=env-file-key-1,env-file-key-2\n"
                            "DEEPSEEK_BASE_URL=https://example.deepseek.local\n"
                            "DEEPSEEK_MAX_WORKERS=3\n"
                            "DEEPSEEK_REQUESTS_PER_SECOND_PER_KEY=4.0\n"
                        )
                    os.chdir(temp_dir)
                    service = AIKeywordClassifier(os.path.join(temp_dir, "ai.sqlite3"), BASE_CONFIG, market="VN_VI")
                    self.assertEqual(service.api_keys, ["env-file-key-1", "env-file-key-2"])
                    self.assertEqual(service.api_key, "env-file-key-1")
                    self.assertEqual(service.base_url, "https://example.deepseek.local")
                    self.assertEqual(service.classifier_config["max_workers"], 3)
                    self.assertEqual(service.classifier_config["requests_per_second_per_key"], 4.0)
                finally:
                    os.chdir(previous_cwd)
        finally:
            if previous_key is not None:
                os.environ["DEEPSEEK_API_KEY"] = previous_key
            else:
                os.environ.pop("DEEPSEEK_API_KEY", None)
            if previous_keys is not None:
                os.environ["DEEPSEEK_API_KEYS"] = previous_keys
            else:
                os.environ.pop("DEEPSEEK_API_KEYS", None)
            if previous_workers is not None:
                os.environ["DEEPSEEK_MAX_WORKERS"] = previous_workers
            else:
                os.environ.pop("DEEPSEEK_MAX_WORKERS", None)
            if previous_rps is not None:
                os.environ["DEEPSEEK_REQUESTS_PER_SECOND_PER_KEY"] = previous_rps
            else:
                os.environ.pop("DEEPSEEK_REQUESTS_PER_SECOND_PER_KEY", None)
            if previous_base_url is not None:
                os.environ["DEEPSEEK_BASE_URL"] = previous_base_url
            else:
                os.environ.pop("DEEPSEEK_BASE_URL", None)

    def test_parallel_batches_round_robin_across_key_pool(self):
        config = copy.deepcopy(BASE_CONFIG)
        config["ai_keyword_classifier"].update({
            "batch_size": 1,
            "max_workers": 2,
            "requests_per_second_per_key": 1000,
        })
        auth_headers = []

        def opener(request, timeout=None, context=None):
            auth_headers.append(request.headers["Authorization"])
            body = json.loads(request.data.decode("utf-8"))
            prompt_payload = json.loads(body["messages"][1]["content"].split("Input:\n", 1)[1])
            keyword = prompt_payload["keywords"][0]["keyword"]
            item = {
                "id": 1,
                "keyword": keyword,
                "detected_language": "en",
                "language_group": "SECONDARY",
                "semantic_bucket": "Broad Expansion",
                "decision_rule": "ai_broad_related",
                "reason": "Relevant broad ASO keyword.",
                "confidence": 0.9,
                "english_gloss": keyword,
            }
            return FakeResponse({"choices": [{"message": {"content": json.dumps({"items": [item]})}}]})

        with tempfile.TemporaryDirectory() as temp_dir:
            df = pd.DataFrame({"Keyword": ["kw one", "kw two", "kw three", "kw four"], "Volume": [1, 1, 1, 1], "Rank": ["", "", "", ""]})
            service = AIKeywordClassifier(
                os.path.join(temp_dir, "ai.sqlite3"),
                config,
                market="VN_VI",
                api_key=None,
                opener=opener,
                sleep=lambda _: None,
            )
            service.api_keys = ["key-a", "key-b"]
            service.api_key = "key-a"
            analyze_dataframe(df, config, cache_path=service.cache_path, market="VN_VI", service=service)

        self.assertEqual(len(auth_headers), 4)
        self.assertIn("Bearer key-a", auth_headers)
        self.assertIn("Bearer key-b", auth_headers)
        self.assertEqual(service.stats["api_batches"], 4)
        self.assertEqual(service.stats["max_workers"], 2)

    def test_failover_retries_batch_with_next_key_without_logging_secret(self):
        config = copy.deepcopy(BASE_CONFIG)
        config["ai_keyword_classifier"].update({
            "batch_size": 1,
            "max_workers": 1,
            "requests_per_second_per_key": 1000,
            "retries": 1,
            "failover_on_key_error": True,
        })
        auth_headers = []

        def opener(request, timeout=None, context=None):
            auth_headers.append(request.headers["Authorization"])
            if request.headers["Authorization"] == "Bearer bad-key":
                raise urllib.error.HTTPError(request.full_url, 429, "rate limited", hdrs=None, fp=None)
            body = json.loads(request.data.decode("utf-8"))
            prompt_payload = json.loads(body["messages"][1]["content"].split("Input:\n", 1)[1])
            keyword = prompt_payload["keywords"][0]["keyword"]
            item = {
                "id": 1,
                "keyword": keyword,
                "detected_language": "en",
                "language_group": "SECONDARY",
                "semantic_bucket": "Broad Expansion",
                "decision_rule": "ai_broad_related",
                "reason": "Relevant broad ASO keyword.",
                "confidence": 0.9,
                "english_gloss": keyword,
            }
            return FakeResponse({"choices": [{"message": {"content": json.dumps({"items": [item]})}}]})

        with tempfile.TemporaryDirectory() as temp_dir:
            df = pd.DataFrame({"Keyword": ["kw one"], "Volume": [1], "Rank": [""]})
            service = AIKeywordClassifier(os.path.join(temp_dir, "ai.sqlite3"), config, market="VN_VI", api_key=None, opener=opener, sleep=lambda _: None)
            service.api_keys = ["bad-key", "good-key"]
            service.api_key = "bad-key"
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                output = analyze_dataframe(df, config, cache_path=service.cache_path, market="VN_VI", service=service)

        self.assertEqual(output.loc[0, "AIStatus"], "AI_CLASSIFIED")
        self.assertEqual(auth_headers, ["Bearer bad-key", "Bearer good-key"])
        self.assertEqual(service.stats["rate_limit_errors"], 1)
        log_output = stdout.getvalue()
        self.assertIn("key=key_1", log_output)
        self.assertIn("key=key_2", log_output)
        self.assertNotIn("bad-key", log_output)
        self.assertNotIn("good-key", log_output)

    def test_rate_limiter_uses_separate_lane_per_key(self):
        config = copy.deepcopy(BASE_CONFIG)
        config["ai_keyword_classifier"].update({
            "requests_per_second_per_key": 1.0,
        })
        with tempfile.TemporaryDirectory() as temp_dir:
            service = AIKeywordClassifier(os.path.join(temp_dir, "ai.sqlite3"), config, market="VN_VI", api_key=None, sleep=lambda _: None, clock=lambda: 100.0)
            service.api_keys = ["key-a", "key-b"]
            service._reserve_request(0)
            service._reserve_request(1)
            connection = service._connect()
            try:
                rows = connection.execute(
                    "SELECT provider, next_request_at FROM ai_keyword_rate_limit ORDER BY provider"
                ).fetchall()
            finally:
                connection.close()

        self.assertEqual(rows, [
            ("deepseek:key_1", 101.0),
            ("deepseek:key_2", 101.0),
        ])

    def test_pre_ai_filter_skips_waste_preserves_broad_terms_and_reuses_duplicates(self):
        config = copy.deepcopy(BASE_CONFIG)
        config.update({
            "intent_core_terms": ["pin", "battery"],
            "intent_core_words": ["pin", "battery"],
            "feature_terms": ["status bar", "battery status"],
            "style_terms": ["cute"],
            "visual_terms": ["theme", "icon"],
            "competitor_brands": ["duolingo"],
            "typo_blacklist": ["batterry"],
            "irrelevant_intent_terms": ["recipe"],
            "noise_terms": ["free"],
            "truncation_policy": {
                "enabled": True,
                "min_prefix_length": 2,
                "low_confidence_action": "manual_review",
            },
        })
        sent_keywords = []

        def opener(request, timeout=None, context=None):
            body = json.loads(request.data.decode("utf-8"))
            user_content = body["messages"][1]["content"]
            prompt_payload = json.loads(user_content.split("Input:\n", 1)[1])
            items = []
            for item in prompt_payload["keywords"]:
                sent_keywords.append(item["keyword"])
                items.append({
                    "id": item["id"],
                    "keyword": item["keyword"],
                    "detected_language": "en",
                    "language_group": "SECONDARY",
                    "semantic_bucket": "Broad Expansion",
                    "decision_rule": "ai_broad_related",
                    "reason": "Relevant broad ASO keyword.",
                    "confidence": 0.88,
                    "english_gloss": item["keyword"],
                })
            return FakeResponse({"choices": [{"message": {"content": json.dumps({"items": items})}}]})

        rows = [
            "theme pin",
            "phone personalization",
            "free",
            "duolingo battery",
            "batterry",
            "battery sta",
            "recipe maker",
            "theme pin",
            "cute sta",
            "",
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            df = pd.DataFrame({"Keyword": rows, "Volume": [1] * len(rows), "Rank": [""] * len(rows)})
            service = AIKeywordClassifier(os.path.join(temp_dir, "ai.sqlite3"), config, market="VN_VI", api_key="secret", opener=opener, sleep=lambda _: None)
            output = analyze_dataframe(df, config, cache_path=service.cache_path, market="VN_VI", service=service)

        self.assertCountEqual(sent_keywords, ["theme pin", "phone personalization", "cute sta"])
        self.assertEqual(output["AIStatus"].tolist(), [
            "AI_CLASSIFIED",
            "AI_CLASSIFIED",
            "AI_SKIPPED_PREFILTER",
            "AI_SKIPPED_PREFILTER",
            "AI_SKIPPED_PREFILTER",
            "AI_SKIPPED_PREFILTER",
            "AI_SKIPPED_PREFILTER",
            "AI_REUSED_CANONICAL",
            "AI_CLASSIFIED",
            "AI_SKIPPED_PREFILTER",
        ])
        self.assertEqual(output.loc[7, "AISemanticBucket"], "Broad Expansion")
        self.assertEqual(output.loc[8, "PreAIRule"], "needs_ai")


if __name__ == "__main__":
    unittest.main()
