import unittest

from shared.locale_parser import extract_locale_from_filename, split_app_and_locale


class LocaleParserTests(unittest.TestCase):
    def test_supported_locale_shapes(self):
        self.assertEqual(extract_locale_from_filename("Pranky_PH_FIL.csv"), "PH_FIL")
        self.assertEqual(extract_locale_from_filename("Pranky_BR_PT-BR.csv"), "BR_PT-BR")
        self.assertEqual(extract_locale_from_filename("ARFilter_US_EN_Output.xlsx"), "US_EN")

    def test_split_keeps_app_alias(self):
        self.assertEqual(split_app_and_locale("Pranky_BR_PT-BR.csv"), ("Pranky", "BR_PT-BR"))
        self.assertEqual(split_app_and_locale("US_EN.csv"), (None, "US_EN"))


if __name__ == "__main__":
    unittest.main()
