import os
import unittest


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class LibreTranslateLauncherTests(unittest.TestCase):
    def test_launcher_defaults_to_daily_low_resource_profile(self):
        path = os.path.join(PROJECT_ROOT, "tools", "start_libretranslate.ps1")
        with open(path, "r", encoding="utf-8") as script_file:
            source = script_file.read()
        self.assertIn('[string]$Profile = "daily"', source)
        self.assertIn("[int]$Threads = 2", source)
        self.assertIn('daily = "en,es,pt,pb,id,hi,tl"', source)
        self.assertIn('"--disable-web-ui"', source)
        self.assertIn('"--disable-files-translation"', source)
        self.assertIn('$env:ARGOS_CHUNK_TYPE = "MINISBD"', source)


if __name__ == "__main__":
    unittest.main()
