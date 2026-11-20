import sys
from datetime import datetime, timezone
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_site import validate, build


def game(game_type="V85"):
    return {
        "id": game_type + "_TEST1",
        "type": game_type,
        "date": "2026-11-21",
        "source": {
            "url": "https://example.org/permissioned-start-list",
            "permission_url": "https://example.org/license",
            "rights_status": "approved",
            "verified_at": datetime.now(timezone.utc).isoformat(),
        },
        "races": [{"starts": [{"horse": {"name": "TESTHÄST"}}]} for _ in range(8 if game_type == "V85" else 7)],
    }


class CalendarValidationTests(unittest.TestCase):
    def test_empty_manifest_is_explicitly_unavailable(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "data").mkdir()
            (root / "data" / "calendar-source.json").write_text('{"schema_version":1,"games":[]}', encoding="utf-8")
            (root / "index.html").write_text("<h1>Test site</h1>", encoding="utf-8")
            output = root / "site"
            self.assertEqual(build(root, output)["status"], "unavailable")
            self.assertTrue((output / "data" / "calendar.json").is_file())

    def test_v75_and_v85(self):
        self.assertEqual(len(validate({"schema_version": 1, "games": [game("V75"), game("V85")]})), 2)

    def test_wrong_leg_count(self):
        item = game("V85")
        item["races"].pop()
        with self.assertRaisesRegex(ValueError, "fel antal lopp"):
            validate({"schema_version": 1, "games": [item]})

    def test_unapproved_data_rejected(self):
        item = game()
        item["source"]["rights_status"] = "unknown"
        with self.assertRaisesRegex(ValueError, "återpubliceringsrätt"):
            validate({"schema_version": 1, "games": [item]})

    def test_invalid_date_rejected(self):
        item = game()
        item["date"] = "2026-12-90"
        with self.assertRaisesRegex(ValueError, "omgångsdatum"):
            validate({"schema_version": 1, "games": [item]})

    def test_refuses_build_over_project_root(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "data").mkdir()
            (root / "data" / "calendar-source.json").write_text('{"schema_version":1,"games":[]}', encoding="utf-8")
            (root / "index.html").write_text("<h1>Bevara originalet</h1>", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Utdatakatalogen"):
                build(root, root)
            self.assertTrue((root / "index.html").is_file())

    def test_private_host_headers_and_only_allowlisted_assets(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "data").mkdir()
            (root / "data" / "calendar-source.json").write_text(
                '{"schema_version":1,"games":[]}', encoding="utf-8"
            )
            (root / "index.html").write_text("<h1>Test site</h1>", encoding="utf-8")
            (root / "deploy" / "cloudflare").mkdir(parents=True)
            (root / "deploy" / "cloudflare" / "_headers").write_text(
                "/*\n  Cache-Control: private, no-store\n", encoding="utf-8"
            )
            (root / ".env").write_text("SECRET_API_KEY=not-for-site", encoding="utf-8")
            out = root / "site"
            build(root, out)
            self.assertIn("no-store", (out / "_headers").read_text(encoding="utf-8"))
            self.assertFalse((out / ".env").exists())
            self.assertFalse((out / "data" / "calendar-source.json").exists())


if __name__ == "__main__":
    unittest.main()
