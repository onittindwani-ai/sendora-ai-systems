import json
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))
import combine_scores as cs  # noqa: E402

W = {"fit": 50, "cost": 50}


def tool(i, kind, fit, cost):
    return {"id": i, "name": i.title(), "kind": kind, "scores": {"fit": {"score": fit, "evidence": "x"}, "cost": {"score": cost, "evidence": "x"}}}


class Combine(unittest.TestCase):
    def test_weighted_and_closeness(self):
        d = {"dated": "2026-01-01", "weights": W, "groups": [{"id": "g", "job": "Job", "reference": "paid1", "tools": [tool("paid1", "paid", 80, 40), tool("free1", "open source", 60, 100)]}]}
        text = cs.render([("Demo", "demo", d)])
        self.assertIn("| Job | Paid1 | paid | 60.0 | reference |", text)
        self.assertIn("| Job | Free1 | open source | 80.0 | 75 percent |", text)
        self.assertIn("1 comparison groups and 2 scored tools", text)

    def test_missing_repo_stops(self):
        with tempfile.TemporaryDirectory() as t, self.assertRaises(SystemExit):
            cs.load(Path(t))


if __name__ == "__main__":
    unittest.main()
