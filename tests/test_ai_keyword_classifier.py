import copy
import io
import json
import os
import sys
import tempfile
import unittest

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
        previous_base_url = os.environ.pop("DEEPSEEK_BASE_URL", None)
        previous_cwd = os.getcwd()
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                try:
                    with open(os.path.join(temp_dir, ".env"), "w", encoding="utf-8") as env_file:
                        env_file.write("DEEPSEEK_API_KEY=env-file-key\nDEEPSEEK_BASE_URL=https://example.deepseek.local\n")
                    os.chdir(temp_dir)
                    service = AIKeywordClassifier(os.path.join(temp_dir, "ai.sqlite3"), BASE_CONFIG, market="VN_VI")
                    self.assertEqual(service.api_key, "env-file-key")
                    self.assertEqual(service.base_url, "https://example.deepseek.local")
                finally:
                    os.chdir(previous_cwd)
        finally:
            if previous_key is not None:
                os.environ["DEEPSEEK_API_KEY"] = previous_key
            else:
                os.environ.pop("DEEPSEEK_API_KEY", None)
            if previous_base_url is not None:
                os.environ["DEEPSEEK_BASE_URL"] = previous_base_url
            else:
                os.environ.pop("DEEPSEEK_BASE_URL", None)


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

        self.assertEqual(sent_keywords, ["theme pin", "phone personalization", "cute sta"])
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
