import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import make_constraints as mk  # noqa: E402

FREEZE = "\n".join([
    "-e file:///work/booklantern/apps/api",
    "sendora-core @ file:///work/booklantern/packages/core-py",
    "Zeta==2.0",
    "alpha==1.0",
    "booklantern==1.0.0",
    "pydantic-core==2.5",
])


def fake_repo() -> Path:
    root = Path(tempfile.mkdtemp()) / "booklantern"
    (root / ".venv" / "bin").mkdir(parents=True)
    (root / ".venv" / "bin" / "python").write_text("")
    return root


def run_with(freeze: str):
    return mock.patch.object(subprocess, "run", return_value=subprocess.CompletedProcess([], 0, stdout=freeze, stderr=""))


class MakeConstraints(unittest.TestCase):
    def test_own_and_editable_packages_are_left_out_and_the_rest_is_sorted(self):
        with run_with(FREEZE):
            self.assertEqual(mk.frozen(fake_repo()), ["alpha==1.0", "pydantic-core==2.5", "Zeta==2.0"])

    def test_check_mode_notices_a_stale_file_and_writes_nothing(self):
        repo = fake_repo()
        with run_with(FREEZE):
            self.assertEqual(mk.main([str(repo), "--check"]), 1)
            self.assertFalse((repo / "constraints.txt").exists())
            self.assertEqual(mk.main([str(repo)]), 0)
            self.assertEqual(mk.main([str(repo), "--check"]), 0)
        with run_with(FREEZE + "\nnewpkg==9"):
            self.assertEqual(mk.main([str(repo), "--check"]), 1)

    def test_a_missing_environment_is_a_clear_error(self):
        with self.assertRaises(SystemExit):
            mk.frozen(Path(tempfile.mkdtemp()) / "x")


if __name__ == "__main__":
    unittest.main()
