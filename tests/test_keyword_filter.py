import os
import sys
import tempfile
import unittest


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from shared import keyword_filter


BASE_CONFIG = {
    "market": "US_EN",
    "market_language_policy": {
        "primary_languages": ["en"],
        "secondary_languages": ["es", "es-MX"],
        "mixed_language_action": "manual_review",
    },
    "risk_policy": {"core_intent_override": True},
    "intent_core_terms": ["prank sounds"],
    "intent_core_words": ["prank"],
    "feature_terms": ["hair clipper", "filter"],
    "style_terms": ["funny"],
    "noise_terms": ["app", "apps", "free", "download", "android", "for android", "best", "top"],
    "irrelevant_intent_terms": ["game", "calculator"],
    "risky_platform_terms": ["ios", "iphone"],
    "competitor_brands": ["picsart"],
    "typo_blacklist": ["editer"],
}


def row(keyword, language_group="PRIMARY", **overrides):
    data = {
        "Keyword": keyword,
        "LanguageGroup": language_group,
        "NaturalnessFlag": "OK",
        "NaturalnessReason": "Natural enough for keyword research",
        "is_competitor": False,
        "is_typo": False,
        "is_irrelevant": False,
        "is_noise": False,
        "RelevancyScore": 0.7,
    }
    data.update(overrides)
    return data


class KeywordFilterTests(unittest.TestCase):
    def test_non_latin_is_not_naturalness_language_bleed(self):
        self.assertEqual(keyword_filter.check_naturalness("เสียงตลก", BASE_CONFIG)[0], "OK")
        self.assertEqual(keyword_filter.check_naturalness("面白いフィルター", BASE_CONFIG)[0], "OK")

    def test_mixed_philippines_goes_to_consider(self):
        config = dict(BASE_CONFIG, market="PH_FIL")
        self.assertEqual(
            keyword_filter.classify_keyword(row("tunog prank", "MIXED"), config),
            ("Consider Keywords", "mixed_language_consider", "Mixed language allowed for this market"),
        )

    def test_foreign_and_secondary_language_buckets(self):
        self.assertEqual(
            keyword_filter.classify_keyword(row("sonidos de broma", "FOREIGN"), dict(BASE_CONFIG, market="PH_FIL"))[0],
            "Language Mismatch Audit",
        )
        self.assertEqual(
            keyword_filter.classify_keyword(row("sonidos de broma", "SECONDARY"), dict(BASE_CONFIG, market="US_EN"))[0],
            "Consider Keywords",
        )

    def test_noise_only_respects_phrases_and_core_intent(self):
        self.assertTrue(keyword_filter.is_noise_only("free", BASE_CONFIG))
        self.assertTrue(keyword_filter.is_noise_only("download", BASE_CONFIG))
        self.assertTrue(keyword_filter.is_noise_only("for android", BASE_CONFIG))
        self.assertFalse(keyword_filter.is_noise_only("free prank sounds", BASE_CONFIG))

    def test_core_intent_override_prevents_irrelevant_hard_drop(self):
        item = row("prank sounds game", is_irrelevant=True)
        self.assertEqual(
            keyword_filter.classify_keyword(item, BASE_CONFIG),
            ("Consider Keywords", "irrelevant_intent_core_override", "Consider: Core intent with broad irrelevant-risk term"),
        )

    def test_translated_en_text_can_drive_primary_market_core_intent(self):
        item = row("maquina de cortar cabelo", "PRIMARY", EN="hair clipper prank")
        self.assertEqual(keyword_filter.classify_keyword(item, BASE_CONFIG)[0], "Core Intent Final")
        self.assertGreaterEqual(keyword_filter.calculate_relevancy(item, BASE_CONFIG), 0.65)

    def test_selection_cache_requires_matching_metadata(self):
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"Keyword,Volume\nprank sounds,100\n")
            tmp_path = tmp.name
        try:
            meta = keyword_filter.build_selection_cache_meta(tmp_path, "PH_FIL")
            wrapped = keyword_filter.wrap_selection_payload({"core_keywords": ["prank sounds"]}, meta)
            self.assertTrue(keyword_filter.is_selection_cache_valid(wrapped, meta))
            self.assertFalse(keyword_filter.is_selection_cache_valid(wrapped, dict(meta, market="US_EN")))
            selection, _ = keyword_filter.unwrap_selection_payload(wrapped)
            self.assertEqual(selection["core_keywords"], ["prank sounds"])
        finally:
            os.unlink(tmp_path)


if __name__ == "__main__":
    unittest.main()
