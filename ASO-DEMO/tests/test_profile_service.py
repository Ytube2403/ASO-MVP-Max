import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta

from shared.keyword_filter import atomic_write_json
from shared.profile_service import get_app_profile


CONFIG = {"app_id": "test.app"}


class ProfileServiceTests(unittest.TestCase):
    def test_custom_profile_has_absolute_priority(self):
        with tempfile.TemporaryDirectory() as app_dir:
            atomic_write_json(os.path.join(app_dir, "App_Profile.json"), {"title": "Custom", "competitors": []})
            profile = get_app_profile(CONFIG, "seed", app_dir, fetcher=lambda _: (_ for _ in ()).throw(AssertionError("fetch")))
            self.assertEqual(profile["title"], "Custom")
            self.assertEqual(profile["ProfileStatus"], "CUSTOM")

    def test_stale_generated_profile_is_fallback_when_fetch_fails(self):
        with tempfile.TemporaryDirectory() as app_dir:
            cache_path = os.path.join(app_dir, ".cache", "profiles", "generated_profile.json")
            atomic_write_json(cache_path, {
                "title": "Cached",
                "competitors": [],
                "last_checked": (datetime.now() - timedelta(days=30)).isoformat(),
            })
            profile = get_app_profile(CONFIG, "seed", app_dir, fetcher=lambda _: (_ for _ in ()).throw(OSError("offline")))
            self.assertEqual(profile["title"], "Cached")
            self.assertEqual(profile["ProfileStatus"], "GENERATED_STALE_FALLBACK")

    def test_fresh_generated_profile_skips_fetch(self):
        with tempfile.TemporaryDirectory() as app_dir:
            cache_path = os.path.join(app_dir, ".cache", "profiles", "generated_profile.json")
            atomic_write_json(cache_path, {
                "title": "Cached",
                "competitors": [],
                "last_checked": datetime.now().isoformat(),
            })
            profile = get_app_profile(CONFIG, "seed", app_dir, fetcher=lambda _: (_ for _ in ()).throw(AssertionError("fetch")))
            self.assertEqual(profile["title"], "Cached")
            self.assertEqual(profile["ProfileStatus"], "GENERATED_FRESH")

    def test_empty_profile_when_fetch_fails_without_cache(self):
        with tempfile.TemporaryDirectory() as app_dir:
            profile = get_app_profile(CONFIG, "seed", app_dir, fetcher=lambda _: (_ for _ in ()).throw(OSError("offline")))
            self.assertEqual(profile["ProfileStatus"], "EMPTY_FETCH_FAILED")
            self.assertIn("offline", profile["ProfileError"])


if __name__ == "__main__":
    unittest.main()
