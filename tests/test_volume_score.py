import os
import sys
import unittest


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from shared import keyword_filter


class VolumeScoreTests(unittest.TestCase):
    def test_search_popularity_uses_absolute_exponential_curve(self):
        low = keyword_filter.calculate_volume_score(5, 5)
        medium = keyword_filter.calculate_volume_score(21, 21)
        high = keyword_filter.calculate_volume_score(60, 60)
        top = keyword_filter.calculate_volume_score(67, 67)

        self.assertEqual(low, 0.0)
        self.assertLess(low, medium)
        self.assertLess(medium, high)
        self.assertLess(high, top)
        self.assertGreater(top, medium * 5)

    def test_low_tier_is_capped_even_with_strong_historical_peak(self):
        self.assertLessEqual(keyword_filter.calculate_volume_score(5, 100), 0.05)

    def test_historical_peak_is_a_secondary_signal(self):
        current_only = keyword_filter.calculate_volume_score(21, 21)
        with_peak = keyword_filter.calculate_volume_score(21, 67)
        top = keyword_filter.calculate_volume_score(67, 67)

        self.assertGreater(with_peak, current_only)
        self.assertLess(with_peak, top)

    def test_maximum_reach_preserves_exponential_traffic_gap(self):
        top = keyword_filter.calculate_volume_score(67, 67, 130506, 130506)
        high = keyword_filter.calculate_volume_score(60, 60, 34122, 130506)
        medium = keyword_filter.calculate_volume_score(21, 21, 5846, 130506)

        self.assertGreater(top, high)
        self.assertGreater(high, medium)
        self.assertLess(medium, 0.10)

    def test_low_tier_can_fill_metadata_quota_by_default_in_v4_1(self):
        row = {"Volume": 5}
        self.assertTrue(keyword_filter.is_shortlist_volume_eligible(row, "Core Intent Final"))
        self.assertTrue(keyword_filter.is_shortlist_volume_eligible(row, "Broad Expansion"))
        self.assertTrue(keyword_filter.is_shortlist_volume_eligible(row, "Consider Keywords", 998))
        self.assertFalse(keyword_filter.is_shortlist_volume_eligible(row, "Consider Keywords", 999))
        self.assertTrue(keyword_filter.is_shortlist_volume_eligible({"Volume": 6}, "Core Intent Final"))

    def test_low_tier_v4_0_quota_can_still_be_configured_explicitly(self):
        config = {
            "volume_score_policy": {
                "exclude_low_tier_from_metadata_shortlist": True,
                "max_low_tier_consider_keywords": 3,
            }
        }
        row = {"Volume": 5}
        self.assertFalse(keyword_filter.is_shortlist_volume_eligible(row, "Core Intent Final", config=config))
        self.assertFalse(keyword_filter.is_shortlist_volume_eligible(row, "Broad Expansion", config=config))
        self.assertTrue(keyword_filter.is_shortlist_volume_eligible(row, "Consider Keywords", 2, config=config))
        self.assertFalse(keyword_filter.is_shortlist_volume_eligible(row, "Consider Keywords", 3, config=config))


if __name__ == "__main__":
    unittest.main()
