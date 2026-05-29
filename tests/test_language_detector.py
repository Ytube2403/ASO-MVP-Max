import os
import sys
import unittest


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from shared.language_detector import detect_keyword_language, get_market_language_policy


BASE_CONFIG = {
    "market_language_policy": {
        "enabled": True,
        "required": True,
        "primary_languages": ["en"],
        "secondary_languages": ["es", "es-MX"],
        "mixed_language_action": "manual_review",
    },
    "intent_core_terms": ["prank sounds", "photo editor"],
    "feature_terms": ["hair clipper", "filter"],
    "style_terms": [],
    "visual_terms": [],
    "noise_terms": ["free", "download"],
}


class LanguageDetectorTests(unittest.TestCase):
    def test_ph_fil_uses_filipino_primary_and_english_secondary(self):
        self.assertEqual(
            get_market_language_policy("PH_FIL", BASE_CONFIG)["primary"],
            ["fil"],
        )
        self.assertEqual(
            detect_keyword_language("prank sounds", "PH_FIL", BASE_CONFIG),
            ("en", "SECONDARY"),
        )
        self.assertEqual(
            detect_keyword_language("nakakatawang tunog", "PH_FIL", BASE_CONFIG),
            ("fil", "PRIMARY"),
        )

    def test_ph_fil_allows_natural_english_filipino_mixed(self):
        self.assertEqual(
            detect_keyword_language("tunog prank", "PH_FIL", BASE_CONFIG),
            ("fil+en", "MIXED"),
        )

    def test_ph_fil_does_not_treat_spanish_as_secondary(self):
        self.assertEqual(
            detect_keyword_language("sonidos de broma", "PH_FIL", BASE_CONFIG),
            ("es", "FOREIGN"),
        )
        self.assertEqual(
            detect_keyword_language("sonidos de broma", "PH_FIL", BASE_CONFIG, english_vocab={"de"}),
            ("es", "FOREIGN"),
        )

    def test_us_en_keeps_spanish_secondary(self):
        self.assertEqual(
            detect_keyword_language("prank sounds", "US_EN", BASE_CONFIG),
            ("en", "PRIMARY"),
        )
        self.assertEqual(
            detect_keyword_language("sonidos de broma", "US_EN", BASE_CONFIG),
            ("es", "SECONDARY"),
        )

    def test_non_latin_and_empty_do_not_fallback_to_primary(self):
        self.assertEqual(
            detect_keyword_language("เสียงตลก", "US_EN", BASE_CONFIG),
            ("th", "FOREIGN"),
        )
        self.assertEqual(
            detect_keyword_language("", "US_EN", BASE_CONFIG),
            ("unknown", "UNKNOWN"),
        )
        self.assertEqual(
            detect_keyword_language("!!!", "US_EN", BASE_CONFIG),
            ("unknown", "UNKNOWN"),
        )


if __name__ == "__main__":
    unittest.main()
