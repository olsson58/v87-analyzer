"""Synthetic fixtures only; no racing-provider data is used."""

import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.convert_excel import FormatError, convert, read_workbook


class ExcelImportTests(unittest.TestCase):
    def test_eight_legs_and_foreign_history_is_not_invented(self):
        sheets = [("Startlista", [["avd", "startnummer", "häst", "kusk"]]
                   + [[str(i), "1", f"Testhäst {i}", f"Testkusk {i}"] for i in range(1, 9)])]
        parsed = convert(sheets, game="V85", date="2026-11-21", track="Jägersro")
        self.assertEqual(len(parsed["races"]), 8)
        self.assertEqual(parsed["races"][7]["starts"][0]["horseName"], "Testhäst 8")
        self.assertEqual(parsed["source"]["permission_status"], "not_verified_for_publication")
        self.assertNotIn("history", parsed["races"][0]["starts"][0])

    def test_requires_explicit_legs_not_track_race_numbers(self):
        with self.assertRaisesRegex(FormatError, "saknar avdelningskolumn"):
            convert([("Lopp 5", [["Nr", "Häst"], ["1", "Test"]])],
                    game="V85", date="2026-11-21", track="Jägersro")

    def test_no_partial_seven_leg_as_eight_leg_round(self):
        data = [["avd", "nr", "häst"]] + [[str(i), "1", f"Häst{i}"] for i in range(1, 8)]
        with self.assertRaisesRegex(FormatError, "Saknade avdelningar: 8"):
            convert([("All", data)], game="V85", date="2026-11-21", track="Jägersro")
        self.assertEqual(len(convert([("All", data)], game="V75", date="2026-11-28", track="Solvalla")["races"]), 7)

    def test_duplicate_numbers_refused(self):
        data = [["avd", "nr", "häst"], ["1", "1", "A"], ["1", "1", "B"]]
        with self.assertRaisesRegex(FormatError, "Dubbelt startnummer"):
            convert([("All", data)], game="V85", date="2026-11-21", track="Jägersro")

    def test_wrong_game_and_invalid_date_refused(self):
        with self.assertRaisesRegex(FormatError, "gäller V75"):
            convert([("V75-1", [["Nr", "Häst"], ["1", "Test"]])],
                    game="V85", date="2026-11-21", track="Jägersro")
        with self.assertRaisesRegex(FormatError, "Ogiltigt kalenderdatum"):
            convert([], game="V85", date="2026-02-31", track="Jägersro")

    def test_read_minimal_xlsx_shared_strings(self):
        # A tiny, in-memory OOXML ZIP checks actual XLSX cell extraction.
        workbook = ('<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
                    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
                    '<sheets><sheet name="V85-1" sheetId="1" r:id="rId1"/></sheets></workbook>')
        rels = ('<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                '<Relationship Id="rId1" Type="worksheet" Target="worksheets/sheet1.xml"/></Relationships>')
        strings = ('<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                   '<si><t>Nr</t></si><si><t>Häst</t></si><si><t>Övningshäst</t></si></sst>')
        sheet = ('<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>'
                 '<row r="1"><c r="A1" t="s"><v>0</v></c><c r="B1" t="s"><v>1</v></c></row>'
                 '<row r="2"><c r="A2"><v>1</v></c><c r="B2" t="s"><v>2</v></c></row>'
                 '</sheetData></worksheet>')
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "test.xlsx"
            with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as out:
                for name, value in [("xl/workbook.xml", workbook),
                                    ("xl/_rels/workbook.xml.rels", rels),
                                    ("xl/sharedStrings.xml", strings),
                                    ("xl/worksheets/sheet1.xml", sheet)]:
                    out.writestr(name, value)
            self.assertEqual(read_workbook(path), [("V85-1", [["Nr", "Häst"], ["1", "Övningshäst"]])])


if __name__ == "__main__":
    unittest.main()
