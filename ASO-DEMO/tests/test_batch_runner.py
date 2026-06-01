import os
import tempfile
import time
import unittest

from run_aso_batch import load_manifest, run_jobs, validate_jobs


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


if __name__ == "__main__":
    unittest.main()
