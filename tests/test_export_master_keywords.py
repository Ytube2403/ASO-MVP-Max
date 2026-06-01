import os
import tempfile
import unittest

from openpyxl import Workbook

from export_master_keywords import get_excluded_keywords_from_excel


class ExportMasterKeywordsTests(unittest.TestCase):
    def test_reads_any_dropped_audit_suffix_and_excludes_all_rows(self):
        with tempfile.TemporaryDirectory() as app_dir:
            month_dir = os.path.join(app_dir, "Output", "052026")
            os.makedirs(month_dir)
            for sheet_name, filename, keyword in [
                ("04_Dropped_Audit", "ControlWidget_US_EN_Output.xlsx", "noise"),
                ("06_Dropped_Audit", "Pranky_BR_PT-BR_Output.xlsx", "competitor"),
            ]:
                wb = Workbook()
                ws = wb.active
                ws.title = sheet_name
                ws.append(["Keyword", "DecisionRule"])
                ws.append([keyword, "competitor_brand"])
                wb.save(os.path.join(month_dir, filename))
            excluded = get_excluded_keywords_from_excel(app_dir)
            self.assertEqual(excluded["US_EN"], {"noise"})
            self.assertEqual(excluded["BR_PT-BR"], {"competitor"})


if __name__ == "__main__":
    unittest.main()
