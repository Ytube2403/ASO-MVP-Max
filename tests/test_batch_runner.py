import os
import sqlite3
import tempfile
import time
import unittest
from contextlib import closing

from run_aso_batch import effective_worker_count, load_manifest, run_jobs, validate_jobs


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class BatchRunnerTests(unittest.TestCase):
    def test_load_manifest_accepts_utf8_bom(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest_path = os.path.join(temp_dir, "manifest.json")
            with open(manifest_path, "w", encoding="utf-8-sig") as file_handle:
                file_handle.write('{"jobs": []}')
            self.assertEqual(load_manifest(manifest_path), {"jobs": []})

    def test_validate_locale_only_filename_with_registered_app(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = os.path.join(temp_dir, "US_EN.csv")
            with open(csv_path, "w", encoding="utf-8") as file_handle:
                file_handle.write("Keyword\nprank\n")
            jobs = validate_jobs({"jobs": [{"app": "Pranky", "csv": csv_path}]}, PROJECT_ROOT)
            self.assertEqual(jobs[0]["market"], "US_EN")

    def test_validate_rejects_unknown_app(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = os.path.join(temp_dir, "US_EN.csv")
            with open(csv_path, "w", encoding="utf-8") as file_handle:
                file_handle.write("Keyword\nprank\n")
            with self.assertRaises(ValueError):
                validate_jobs({"jobs": [{"app": "Unknown", "csv": csv_path}]}, PROJECT_ROOT)

    def test_partial_failure_report_data_and_concurrency_cap(self):
        active = 0
        peak = 0

        def execute(job):
            nonlocal active, peak
            active += 1
            peak = max(peak, active)
            time.sleep(0.01)
            active -= 1
            return {**job, "status": "FAILED" if job["index"] == 1 else "SUCCESS", "exit_code": job["index"], "output": "", "elapsed_seconds": 0.01, "error_excerpt": ""}

        jobs = [{"index": index, "app": "Pranky", "csv": "", "market": "US_EN"} for index in range(4)]
        results = run_jobs(jobs, PROJECT_ROOT, max_workers=2, executor_fn=execute)
        self.assertEqual(peak, 2)
        self.assertEqual([item["status"] for item in results], ["SUCCESS", "FAILED", "SUCCESS", "SUCCESS"])

    def test_effective_workers_reduce_concurrency_for_cold_libre_cache(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            state, count, workers = effective_worker_count(temp_dir, max_workers=3, cold_cache_workers=1)
            self.assertEqual((state, count, workers), ("COLD", 0, 1))

    def test_effective_workers_use_requested_limit_for_warm_libre_cache(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = os.path.join(temp_dir, ".cache")
            os.makedirs(cache_dir)
            cache_path = os.path.join(cache_dir, "translations.sqlite3")
            with closing(sqlite3.connect(cache_path)) as connection:
                connection.execute(
                    """
                    CREATE TABLE translations (
                        provider TEXT NOT NULL,
                        source_language TEXT NOT NULL,
                        target_language TEXT NOT NULL,
                        normalized_keyword TEXT NOT NULL,
                        translated_text TEXT NOT NULL,
                        updated_at REAL NOT NULL,
                        PRIMARY KEY (provider, source_language, target_language, normalized_keyword)
                    )
                    """
                )
                connection.execute(
                    "INSERT INTO translations VALUES (?, ?, ?, ?, ?, ?)",
                    ("libretranslate_local", "es", "en", "broma", "prank", 1.0),
                )
                connection.commit()
            state, count, workers = effective_worker_count(temp_dir, max_workers=2, cold_cache_workers=1)
            self.assertEqual((state, count, workers), ("WARM", 1, 2))


if __name__ == "__main__":
    unittest.main()
