import os
import unittest

from shared.app_registry import APP_REGISTRY, resolve_app


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class AppRegistryTests(unittest.TestCase):
    def test_exact_registered_alias(self):
        self.assertEqual(resolve_app("Pranky")["folder"], "apps/Prank_Sounds")
        self.assertEqual(resolve_app("AR_Filter")["folder"], "apps/AR_Filter")

    def test_unknown_alias_does_not_fallback(self):
        with self.assertRaises(KeyError):
            resolve_app("MyNewPrankUtility")

    def test_registered_apps_live_under_apps_and_have_runtime_files(self):
        for app_key, entry in APP_REGISTRY.items():
            with self.subTest(app=app_key):
                resolved = resolve_app(entry["aliases"][0], PROJECT_ROOT)
                self.assertTrue(resolved["folder"].startswith("apps/"))
                self.assertTrue(os.path.isfile(resolved["runner_path"]))
                self.assertTrue(os.path.isfile(resolved["config_path"]))


if __name__ == "__main__":
    unittest.main()
