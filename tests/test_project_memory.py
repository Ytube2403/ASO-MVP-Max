import os
import tempfile
import textwrap
import unittest

from openpyxl import Workbook

from shared.keyword_filter import atomic_write_json
from shared.project_memory import (
    add_project_memory_sheet,
    build_project_memory_for_app,
    load_config_from_app,
    write_project_memory_markdown,
)


class ProjectMemoryTests(unittest.TestCase):
    def test_app_template_memory_loads_competitors(self):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        app_dir = os.path.join(root, "apps", "App_Template")
        memory = build_project_memory_for_app(app_dir, os.path.join(app_dir, "run_pipeline.py"))
        self.assertEqual(memory["identity"]["app_id"], "com.example.mynewapp")
        self.assertGreaterEqual(len(memory["competitor_setup"]["competitor_apps"]), 2)
        self.assertIn("competitor_brands", memory["risk_setup"]["groups"])

    def test_filter_policy_overlays_runner_literal_config(self):
        with tempfile.TemporaryDirectory() as app_dir:
            runner_path = os.path.join(app_dir, "run_pipeline.py")
            with open(runner_path, "w", encoding="utf-8") as handle:
                handle.write("config = {'app_id': 'base.app', 'feature_terms': ['edit'], 'competitor_brands': []}\n")
            with open(os.path.join(app_dir, "app_config.py"), "w", encoding="utf-8") as handle:
                handle.write("FILTER_POLICY = {'semantic_mode': 'ar_filter', 'competitor_brands': ['rival']}\n")
            config, source, notes = load_config_from_app(app_dir, runner_path)
            self.assertEqual(config["app_id"], "base.app")
            self.assertEqual(config["semantic_mode"], "ar_filter")
            self.assertEqual(config["competitor_brands"], ["rival"])
            self.assertIn("FILTER_POLICY", " ".join(notes))
            self.assertEqual(source, runner_path)

    def test_schema_profile_is_adapted_to_competitor_display(self):
        with tempfile.TemporaryDirectory() as app_dir:
            with open(os.path.join(app_dir, "app_config.py"), "w", encoding="utf-8") as handle:
                handle.write(textwrap.dedent("""
                    APP_CONFIG = {
                        'app_id': 'demo.app',
                        'app_name': 'Demo',
                        'semantic_mode': 'generic',
                        'intent_core_terms': ['photo editor', 'crop photo', 'edit photo'],
                        'feature_terms': ['filter', 'retouch', 'collage'],
                        'style_terms': ['aesthetic', 'retro', 'cute'],
                        'competitor_brands': ['rival app']
                    }
                """))
            atomic_write_json(os.path.join(app_dir, "App_Profile.json"), {
                "schema_version": "1",
                "app_identity": {"app_id": "demo.app", "title": "Demo"},
                "live_store_metadata": {"short_description": "Demo short"},
                "competitor_strategy": {
                    "suggested_competitors": [
                        {
                            "package_id": "rival.pkg",
                            "title": "Rival App",
                            "why_relevant": "same feature",
                            "overlap_keywords": ["photo filter"],
                        }
                    ]
                },
            })
            memory = build_project_memory_for_app(app_dir)
            competitors = memory["competitor_setup"]["competitor_apps"]
            self.assertEqual(competitors[0]["title"], "Rival App")
            self.assertIn("photo filter", competitors[0]["desc200"])

    def test_warnings_include_overlap_and_missing_profile(self):
        with tempfile.TemporaryDirectory() as app_dir:
            with open(os.path.join(app_dir, "app_config.py"), "w", encoding="utf-8") as handle:
                handle.write(textwrap.dedent("""
                    APP_CONFIG = {
                        'app_id': 'demo.app',
                        'app_name': 'Demo',
                        'semantic_mode': 'generic',
                        'intent_core_terms': ['photo editor'],
                        'feature_terms': ['rival'],
                        'style_terms': [],
                        'competitor_brands': ['rival']
                    }
                """))
            memory = build_project_memory_for_app(app_dir)
            warning_text = " ".join(memory["warnings"])
            self.assertIn("App_Profile.json not found", warning_text)
            self.assertIn("competitor_brands overlaps feature_terms", warning_text)

    def test_memory_exports_to_workbook_and_markdown(self):
        with tempfile.TemporaryDirectory() as app_dir:
            with open(os.path.join(app_dir, "app_config.py"), "w", encoding="utf-8") as handle:
                handle.write(textwrap.dedent("""
                    APP_CONFIG = {
                        'app_id': 'demo.app',
                        'app_name': 'Demo',
                        'semantic_mode': 'generic',
                        'intent_core_terms': ['photo editor', 'crop photo', 'edit photo'],
                        'feature_terms': ['filter', 'retouch', 'collage'],
                        'style_terms': ['aesthetic', 'retro', 'cute'],
                        'competitor_brands': ['rival']
                    }
                """))
            memory = build_project_memory_for_app(app_dir)
            wb = Workbook()
            wb.remove(wb.active)
            add_project_memory_sheet(wb, memory)
            self.assertEqual(wb.sheetnames[0], "00_Project_Memory")
            markdown_path = write_project_memory_markdown(app_dir, memory)
            self.assertTrue(os.path.exists(markdown_path))
            with open(markdown_path, "r", encoding="utf-8") as handle:
                self.assertIn("# Project Memory", handle.read())


if __name__ == "__main__":
    unittest.main()
