import os
import tempfile
import unittest
from pathlib import Path

os.environ["SFOP_DATA_DIR"] = tempfile.mkdtemp()

import config  # noqa: E402
from utils import history_manager, organizer, statistics  # noqa: E402
from utils.file_types import classify  # noqa: E402


def make(folder: Path, *names):
    for name in names:
        (folder / name).write_text(name)


class OrganizerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        config.HISTORY_FILE.unlink(missing_ok=True)

    def test_classify(self):
        self.assertEqual(classify("a.JPG"), "Images")
        self.assertEqual(classify("a.unknown"), "Others")
        self.assertEqual(classify("noext"), "Others")

    def test_scan_does_not_move(self):
        make(self.tmp, "a.png", "b.pdf", "c.xyz")
        stats = organizer.scan(self.tmp)
        self.assertEqual((stats["Images"], stats["Documents"], stats["Others"], stats["Total"]), (1, 1, 1, 3))
        self.assertTrue((self.tmp / "a.png").exists())

    def test_organize_and_undo(self):
        make(self.tmp, "a.png", "b.pdf", "c.xyz", "d.mp3")
        result = organizer.organize(self.tmp)
        self.assertEqual(result.stats["Total"], 4)
        self.assertTrue((self.tmp / "Images" / "a.png").exists())
        restored, skipped = organizer.undo(result.moves)
        self.assertEqual((restored, skipped), (4, 0))
        self.assertTrue((self.tmp / "a.png").exists())
        self.assertFalse((self.tmp / "Images").exists())

    def test_never_overwrites(self):
        (self.tmp / "Images").mkdir()
        (self.tmp / "Images" / "a.png").write_text("old")
        make(self.tmp, "a.png")
        organizer.organize(self.tmp)
        self.assertEqual((self.tmp / "Images" / "a.png").read_text(), "old")
        self.assertEqual((self.tmp / "Images" / "a (1).png").read_text(), "a.png")

    def test_enabled_filter_and_dry_run(self):
        make(self.tmp, "a.png", "b.pdf")
        dry = organizer.organize(self.tmp, enabled=["Images"], dry_run=True)
        self.assertEqual(dry.stats["Total"], 1)
        self.assertTrue((self.tmp / "a.png").exists())
        organizer.organize(self.tmp, enabled=["Images"])
        self.assertTrue((self.tmp / "b.pdf").exists())
        self.assertFalse((self.tmp / "a.png").exists())

    def test_ignores_hidden_and_folders(self):
        make(self.tmp, ".hidden.png", "desktop.ini")
        (self.tmp / "sub").mkdir()
        self.assertEqual(organizer.scan(self.tmp)["Total"], 0)

    def test_progress_callback(self):
        make(self.tmp, "a.png", "b.png")
        seen = []
        organizer.organize(self.tmp, progress=lambda d, t, n: seen.append((d, t)))
        self.assertEqual(seen, [(1, 2), (2, 2)])

    def test_bad_folder(self):
        with self.assertRaises(NotADirectoryError):
            organizer.organize(self.tmp / "missing")


class HistoryTests(unittest.TestCase):
    def setUp(self):
        config.HISTORY_FILE.unlink(missing_ok=True)

    def test_roundtrip_search_undo_flag(self):
        stats = {"Images": 2, "Total": 2}
        entry = history_manager.save_history("C:/x/Downloads", stats, [("a", "b")])
        self.assertEqual(len(history_manager.load_history()), 1)
        self.assertEqual(history_manager.search("downloads")[0]["id"], entry["id"])
        self.assertEqual(history_manager.search("images")[0]["id"], entry["id"])
        self.assertEqual(history_manager.search("videos"), [])
        self.assertEqual(history_manager.last_undoable()["id"], entry["id"])
        history_manager.mark_undone(entry["id"])
        self.assertIsNone(history_manager.last_undoable())
        self.assertEqual(statistics.get_latest_statistics()["Total"], 0)

    def test_lifetime(self):
        history_manager.save_history("a", {"Images": 3, "Total": 3})
        history_manager.save_history("b", {"Music": 2, "Total": 2})
        life = statistics.get_lifetime_statistics()
        self.assertEqual((life["runs"], life["totals"]["Total"]), (2, 5))

    def test_legacy_import(self):
        legacy = Path(tempfile.mkdtemp()) / "history.txt"
        legacy.write_text("=" * 50 + "\nDate: 2026-01-02 03:04:05\nFolder: C:\\Dl\n\nImages: 4\nTotal: 4\n\n", encoding="utf-8")
        old = config.LEGACY_HISTORY_FILES
        config.LEGACY_HISTORY_FILES = (legacy,)
        try:
            entries = history_manager.load_history()
        finally:
            config.LEGACY_HISTORY_FILES = old
        self.assertEqual(entries[0]["stats"]["Images"], 4)
        self.assertEqual(entries[0]["timestamp"], "2026-01-02 03:04:05")

    def test_corrupt_file(self):
        config.DATA_DIR.mkdir(parents=True, exist_ok=True)
        config.HISTORY_FILE.write_text("{not json")
        self.assertEqual(history_manager.load_history(), [])


if __name__ == "__main__":
    unittest.main()
