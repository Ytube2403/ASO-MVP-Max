import time
import unittest

from shared.text_dedup import deduplicate_candidates


class TextDedupBenchmarkTests(unittest.TestCase):
    def test_dedup_10000_rows_under_ten_seconds(self):
        records = [
            {"Keyword": f"camera app style {index}", "Volume": index % 100, "Bucket": "Broad Expansion"}
            for index in range(10000)
        ]
        started = time.perf_counter()
        result = deduplicate_candidates(records, "benchmark", "en")
        elapsed = time.perf_counter() - started
        self.assertEqual(len(result.records), 10000)
        self.assertLess(elapsed, 10.0)


if __name__ == "__main__":
    unittest.main()
