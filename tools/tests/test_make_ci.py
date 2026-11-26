import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import make_ci as mc  # noqa: E402


def stub_repo(tools: tuple[str, ...]) -> Path:
    root = Path(tempfile.mkdtemp())
    (root / "apps" / "api").mkdir(parents=True)
    (root / "tools").mkdir()
    for t in tools:
        (root / "tools" / t).write_text("")
    return root


class MakeCi(unittest.TestCase):
    def test_every_action_is_pinned_to_a_commit(self):
        text = mc.render(stub_repo(()))
        uses = re.findall(r"uses: (\S+)", text)
        self.assertTrue(uses)
        for u in uses:
            self.assertRegex(u, r"@[0-9a-f]{40}$", u)

    def test_workflow_can_only_read_the_code(self):
        text = mc.render(stub_repo(()))
        self.assertIn("permissions:\n  contents: read", text)
        self.assertNotIn("write", text.split("jobs:")[0])

    def test_every_job_has_a_timeout(self):
        text = mc.render(stub_repo(()))
        self.assertEqual(text.count("timeout-minutes:"), text.count("runs-on:"))

    def test_only_the_checks_the_repo_has_are_listed(self):
        text = mc.render(stub_repo(("check_docs.py", "scan_secrets.py")))
        self.assertIn("python tools/check_docs.py", text)
        self.assertIn("python tools/scan_secrets.py", text)
        self.assertNotIn("score_seed.py", text)
        self.assertNotIn("__", text.replace("__init__", ""))

    def test_check_mode_reports_a_difference_and_writes_nothing(self):
        repo = stub_repo(())
        self.assertEqual(mc.main([str(repo), "--check"]), 1)
        self.assertFalse((repo / ".github").exists())
        self.assertEqual(mc.main([str(repo)]), 0)
        self.assertEqual(mc.main([str(repo), "--check"]), 0)

    def test_not_a_system_repo_is_refused(self):
        self.assertEqual(mc.main([tempfile.mkdtemp()]), 2)


if __name__ == "__main__":
    unittest.main()
