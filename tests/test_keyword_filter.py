import os
import sys
import tempfile
import unittest


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from shared import keyword_filter


BASE_CONFIG = {
    "app_id": "test.prank",
    "semantic_mode": "prank_sounds",
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
    "risky_ip_terms": ["pokemon"],
    "ambiguous_brand_terms": ["snow"],
    "platform_affiliation_terms": ["official tiktok"],
    "truncation_policy": {"enabled": True, "min_prefix_length": 2},
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

    def test_translated_en_text_drives_row_aware_filters(self):
        self.assertTrue(keyword_filter.is_competitor_keyword(row("editor de fotos", EN="picsart editor"), BASE_CONFIG))
        self.assertTrue(keyword_filter.is_irrelevant_keyword(row("juego divertido", EN="fun game"), BASE_CONFIG))
        self.assertTrue(keyword_filter.is_noise_only(row("gratis", EN="free"), BASE_CONFIG))
        self.assertEqual(keyword_filter.check_naturalness(row("aplicacion", EN="app app"), BASE_CONFIG)[0], "UNNATURAL")

    def test_typo_filter_only_uses_raw_keyword(self):
        self.assertTrue(keyword_filter.is_typo_keyword(row("editer", EN="editor"), BASE_CONFIG))
        self.assertFalse(keyword_filter.is_typo_keyword(row("editor", EN="editer"), BASE_CONFIG))

    def test_raw_and_en_filters_record_source(self):
        flags = keyword_filter.evaluate_hard_filters(row("editor de fotos", EN="picsart editor"), BASE_CONFIG)
        self.assertTrue(flags["is_competitor"])
        self.assertEqual(flags["HardFilterSource"], "EN")
        same_text = keyword_filter.evaluate_hard_filters(row("picsart", EN="picsart"), BASE_CONFIG)
        self.assertEqual(same_text["HardFilterSource"], "raw+EN")

    def test_compiled_runtime_is_cached_by_config_hash(self):
        runtime = keyword_filter.build_filter_runtime(BASE_CONFIG)
        self.assertIs(runtime, keyword_filter.build_filter_runtime(dict(BASE_CONFIG)))
        changed = keyword_filter.build_filter_runtime(dict(BASE_CONFIG, competitor_brands=["canva"]))
        self.assertIsNot(runtime, changed)
        self.assertTrue(keyword_filter.evaluate_hard_filters(row("picsart editor"), runtime)["is_competitor"])

    def test_risky_ip_platform_affiliation_and_ambiguous_brand(self):
        self.assertEqual(keyword_filter.classify_keyword(row("pokemon prank"), BASE_CONFIG)[1], "risky_ip")
        self.assertEqual(keyword_filter.classify_keyword(row("snow prank"), BASE_CONFIG)[1], "ambiguous_brand")
        self.assertEqual(keyword_filter.classify_keyword(row("official tiktok prank"), BASE_CONFIG)[1], "platform_affiliation")
        self.assertEqual(keyword_filter.classify_keyword(row("iphone"), BASE_CONFIG)[1], "platform_only")
        self.assertEqual(keyword_filter.classify_keyword(row("iphone prank"), BASE_CONFIG)[1], "platform_style_risk")

    def test_conservative_truncation_detection(self):
        self.assertTrue(keyword_filter.is_truncated_keyword(row("prank so"), BASE_CONFIG))
        self.assertTrue(keyword_filter.is_truncated_keyword(row("prank sou"), BASE_CONFIG))
        self.assertFalse(keyword_filter.is_truncated_keyword(row("prank sounds"), BASE_CONFIG))

    def test_force_top30_cannot_promote_risk_or_hard_drop(self):
        config = dict(BASE_CONFIG, user_overrides={"force_top30_terms": ["pokemon prank", "picsart prank"]})
        risky = row("pokemon prank", Bucket="Consider Keywords", DecisionRule="risky_ip", Reason="Consider")
        dropped = row("picsart prank", Bucket="Dropped", DecisionRule="competitor_brand", Reason="Dropped")
        self.assertEqual(keyword_filter.apply_user_overrides(risky, config)[0], "Consider Keywords")
        self.assertEqual(keyword_filter.apply_user_overrides(dropped, config)[0], "Dropped")

    def test_validator_rejects_missing_mode_duplicate_and_overlap(self):
        with self.assertRaises(keyword_filter.FilterConfigError):
            keyword_filter.validate_filter_config(dict(BASE_CONFIG, semantic_mode=""))
        with self.assertRaises(keyword_filter.FilterConfigError):
            keyword_filter.validate_filter_config(dict(BASE_CONFIG, competitor_brands=["picsart", "PicsArt"]))
        with self.assertRaises(keyword_filter.FilterConfigError):
            keyword_filter.validate_filter_config(dict(BASE_CONFIG, competitor_brands=["filter"]))

    def test_selection_cache_requires_matching_metadata(self):
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"Keyword,Volume\nprank sounds,100\n")
            tmp_path = tmp.name
        try:
            meta = keyword_filter.build_selection_cache_meta(tmp_path, "PH_FIL", BASE_CONFIG)
            wrapped = keyword_filter.wrap_selection_payload({"core_keywords": ["prank sounds"]}, meta)
            self.assertTrue(keyword_filter.is_selection_cache_valid(wrapped, meta))
            self.assertFalse(keyword_filter.is_selection_cache_valid(wrapped, dict(meta, market="US_EN")))
            changed = keyword_filter.build_selection_cache_meta(tmp_path, "PH_FIL", dict(BASE_CONFIG, semantic_mode="changed"))
            self.assertFalse(keyword_filter.is_selection_cache_valid(wrapped, changed))
            selection, _ = keyword_filter.unwrap_selection_payload(wrapped)
            self.assertEqual(selection["core_keywords"], ["prank sounds"])
            with tempfile.TemporaryDirectory() as cache_root:
                ph_path = keyword_filter.selection_cache_path(cache_root, BASE_CONFIG, tmp_path, "PH_FIL")
                us_path = keyword_filter.selection_cache_path(cache_root, BASE_CONFIG, tmp_path, "US_EN")
                changed_path = keyword_filter.selection_cache_path(cache_root, dict(BASE_CONFIG, app_id="test.other"), tmp_path, "PH_FIL")
                self.assertNotEqual(ph_path, us_path)
                self.assertNotEqual(ph_path, changed_path)
                keyword_filter.atomic_write_json(ph_path, wrapped)
                self.assertTrue(os.path.exists(ph_path))
        finally:
            os.unlink(tmp_path)


if __name__ == "__main__":
    unittest.main()
