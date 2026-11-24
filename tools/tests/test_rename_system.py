import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))
import rename_system as rn  # noqa: E402


def w(root: Path, rel: str, text: str | bytes) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(text, bytes):
        p.write_bytes(text)
    else:
        p.write_text(text, encoding="utf-8")


class CaseAware(unittest.TestCase):
    def test_cases(self):
        r = rn.Renamer("Closeline", "Pipecairn")
        self.assertEqual(r.replace_text("Closeline closeline CLOSELINE CLOSELINE_API closeline-web"),
                         "Pipecairn pipecairn PIPECAIRN PIPECAIRN_API pipecairn-web")

    def test_multi_word(self):
        r = rn.Renamer("Rain Maker", "Ring Lark")
        self.assertEqual(r.replace_text("Rain Maker rain-maker rain_maker RAIN_MAKER RainMaker rainmaker"),
                         "Ring Lark ring-lark ring_lark RING_LARK RingLark ringlark")

    def test_folder_name(self):
        r = rn.Renamer("Rainmaker", "Ringlark", "rainmaker-sdr-kit", "ringlark")
        self.assertEqual(r.replace_text("cd rainmaker-sdr-kit && Rainmaker rainmaker_sdr_kit RAINMAKER_SDR_KIT"),
                         "cd ringlark && Ringlark ringlark RINGLARK")

    def test_same_name_refused(self):
        with self.assertRaises(ValueError):
            rn.Renamer("Abc", "abc")


class WholeRepo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        w(self.root, "README.md", "# Closeline\nUse closeline now. alt=\"Closeline screenshot\"\n")
        w(self.root, "apps/api/src/closeline/__init__.py", "from closeline.x import y\nENV = 'CLOSELINE_KEY'\n")
        w(self.root, "apps/api/src/closeline/x.py", "y = 1\n")
        w(self.root, "data/seed.json", '{"brand": "Closeline", "key": "closeline.token"}')
        w(self.root, "BUILD-LEDGER.md", "history Closeline\n")
        w(self.root, "node_modules/p/i.js", "closeline")
        w(self.root, ".git/config", "closeline")
        w(self.root, "img.png", b"\x89PNG\x00closeline")
        w(self.root, "blob.dat", b"\x00\x01closeline")
        w(self.root, "pnpm-lock.yaml", "name: closeline\n  integrity: sha512-closeline==\n")
        w(self.root, "packages/ui-kit/t.tsx", "Closeline")
        w(self.root, "docs/closeline-notes.md", "notes\n")

    def tearDown(self):
        self.tmp.cleanup()

    def run_tool(self, *extra):
        return rn.main([str(self.root), "--old", "Closeline", "--new", "Pipecairn", *extra])

    def test_dry_run_changes_nothing(self):
        self.assertEqual(self.run_tool(), 0)
        self.assertIn("Closeline", (self.root / "README.md").read_text())
        self.assertTrue((self.root / "apps/api/src/closeline").is_dir())

    def test_apply(self):
        self.assertEqual(self.run_tool("--apply"), 0)
        self.assertIn("# Pipecairn", (self.root / "README.md").read_text())
        self.assertIn('alt="Pipecairn screenshot"', (self.root / "README.md").read_text())
        init = (self.root / "apps/api/src/pipecairn/__init__.py").read_text()
        self.assertIn("from pipecairn.x import y", init)
        self.assertIn("PIPECAIRN_KEY", init)
        self.assertIn("Pipecairn", (self.root / "data/seed.json").read_text())
        self.assertTrue((self.root / "docs/pipecairn-notes.md").is_file())
        # untouched
        self.assertEqual((self.root / "BUILD-LEDGER.md").read_text(), "history Closeline\n")
        self.assertEqual((self.root / "node_modules/p/i.js").read_text(), "closeline")
        self.assertEqual((self.root / ".git/config").read_text(), "closeline")
        self.assertEqual((self.root / "img.png").read_bytes(), b"\x89PNG\x00closeline")
        self.assertEqual((self.root / "blob.dat").read_bytes(), b"\x00\x01closeline")
        self.assertEqual((self.root / "packages/ui-kit/t.tsx").read_text(), "Closeline")
        lock = (self.root / "pnpm-lock.yaml").read_text()
        self.assertIn("name: pipecairn", lock)
        self.assertIn("sha512-closeline==", lock)

    def test_check_finds_then_passes(self):
        self.assertEqual(self.run_tool("--check"), 1)
        self.run_tool("--apply")
        self.assertEqual(self.run_tool("--check"), 0)

    def test_check_reports_names(self):
        w(self.root, "docs/Closeline-x.md", "ok")
        self.assertEqual(self.run_tool("--check"), 1)

    def test_idempotent(self):
        self.run_tool("--apply")
        before = (self.root / "README.md").read_text()
        self.run_tool("--apply")
        self.assertEqual(before, (self.root / "README.md").read_text())

    def test_existing_target_refused(self):
        w(self.root, "docs/pipecairn-notes.md", "x")
        with self.assertRaises(FileExistsError):
            self.run_tool("--apply")


if __name__ == "__main__":
    unittest.main()
