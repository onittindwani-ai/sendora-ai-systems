import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))
import system_names as sn  # noqa: E402


class Resolve(unittest.TestCase):
    def test_old_until_renamed(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self.assertEqual(sn.resolve(root)[0], ("Closeline", "closeline"))
            (root / "pipecairn").mkdir()
            self.assertEqual(sn.resolve(root)[0], ("Pipecairn", "pipecairn"))
            self.assertEqual(sn.resolve(root)[1], ("Rainmaker", "rainmaker-sdr-kit"))

    def test_seven_systems(self):
        self.assertEqual(len(sn.SYSTEMS), 7)
        self.assertEqual(len({s[3] for s in sn.SYSTEMS}), 7)


if __name__ == "__main__":
    unittest.main()
