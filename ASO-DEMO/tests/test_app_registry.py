import unittest

from shared.app_registry import resolve_app


class AppRegistryTests(unittest.TestCase):
    def test_exact_registered_alias(self):
        self.assertEqual(resolve_app("Pranky")["folder"], "Prank_Sounds")
        self.assertEqual(resolve_app("AR_Filter")["folder"], "AR_Filter")

    def test_unknown_alias_does_not_fallback(self):
        with self.assertRaises(KeyError):
            resolve_app("MyNewPrankUtility")


if __name__ == "__main__":
    unittest.main()
