import json
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))
import check_base_copies as chk  # noqa: E402
import sync_base as syn  # noqa: E402


def make_hub(root: Path) -> None:
    (root / "packages/core-py/src").mkdir(parents=True)
    (root / "packages/ui-kit/src").mkdir(parents=True)
    (root / "packages/core-py/src/a.py").write_text("print(1)\n")
    (root / "packages/ui-kit/src/b.ts").write_text("export const b = 1;\n")
    (root / "packages/ui-kit/package.json").write_text(json.dumps({"version": "1.2.3"}))
    (root / "packages/ui-kit/node_modules").mkdir()
    (root / "packages/ui-kit/node_modules/skip.js").write_text("x")


class BaseTools(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.hub = Path(self.tmp.name) / "hub"
        self.sys_repo = Path(self.tmp.name) / "system"
        self.sys_repo.mkdir()
        make_hub(self.hub)

    def tearDown(self):
        self.tmp.cleanup()

    def test_sync_then_check_ok_and_ignores_node_modules(self):
        r = syn.sync(self.sys_repo, self.hub)
        self.assertEqual(r["version"], "1.2.3")
        self.assertEqual(r["files"], 3)
        self.assertFalse((self.sys_repo / "packages/ui-kit/node_modules").exists())
        self.assertEqual(chk.check(self.sys_repo, self.hub), [])

    def test_dry_run_changes_nothing(self):
        syn.sync(self.sys_repo, self.hub, dry_run=True)
        self.assertFalse((self.sys_repo / "packages").exists())

    def test_drift_is_found_changed_missing_extra(self):
        syn.sync(self.sys_repo, self.hub)
        (self.sys_repo / "packages/core-py/src/a.py").write_text("print(2)\n")
        (self.sys_repo / "packages/ui-kit/src/b.ts").unlink()
        (self.sys_repo / "packages/ui-kit/src/new.ts").write_text("x")
        probs = chk.check(self.sys_repo, self.hub)
        self.assertIn("changed packages/core-py/src/a.py", probs)
        self.assertIn("missing packages/ui-kit/src/b.ts", probs)
        self.assertIn("extra packages/ui-kit/src/new.ts", probs)

    def test_resync_repairs_drift_and_removes_extras(self):
        syn.sync(self.sys_repo, self.hub)
        (self.sys_repo / "packages/ui-kit/src/new.ts").write_text("x")
        (self.sys_repo / "packages/core-py/src/a.py").write_text("changed")
        r = syn.sync(self.sys_repo, self.hub)
        self.assertEqual(sorted(r["removed"]), ["packages/ui-kit/src/new.ts"])
        self.assertEqual(chk.check(self.sys_repo, self.hub), [])

    def test_version_mismatch_and_missing_manifest(self):
        self.assertTrue(chk.check(self.sys_repo, self.hub)[0].startswith("missing packages/BASE_MANIFEST.json"))
        syn.sync(self.sys_repo, self.hub)
        (self.hub / "packages/ui-kit/package.json").write_text(json.dumps({"version": "1.3.0"}))
        self.assertTrue(any("base version" in p for p in chk.check(self.sys_repo, self.hub)))

    def test_refuses_hub_as_target(self):
        with self.assertRaises(SystemExit):
            syn.sync(self.hub, self.hub)


if __name__ == "__main__":
    unittest.main()
