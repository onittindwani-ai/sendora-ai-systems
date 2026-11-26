import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import check_env as ce  # noqa: E402

EXAMPLE = """# Core
DATABASE_URL=sqlite:///./x.db
SESSION_SECRET=change-me
DEMO_MODE=true

# Email (smtp_imap): all or none
SMTP_HOST=
SMTP_PORT=587
SMTP_PASSWORD=
"""


class CheckEnv(unittest.TestCase):
    def test_complete_demo_file_is_fine(self):
        env = "DATABASE_URL=sqlite:///./x.db\nSESSION_SECRET=change-me\nDEMO_MODE=true\nSMTP_HOST=\nSMTP_PORT=587\nSMTP_PASSWORD=\n"
        self.assertEqual(ce.check(EXAMPLE, env), [])

    def test_missing_name_is_listed(self):
        problems = ce.check(EXAMPLE, "DEMO_MODE=true\n")
        self.assertTrue(any("DATABASE_URL is missing" in p for p in problems))

    def test_live_needs_real_secret(self):
        env = "DATABASE_URL=sqlite:///./x.db\nSESSION_SECRET=change-me\nDEMO_MODE=false\nSMTP_HOST=\nSMTP_PORT=587\nSMTP_PASSWORD=\n"
        self.assertTrue(any("SESSION_SECRET" in p for p in ce.check(EXAMPLE, env)))

    def test_partly_filled_group_is_flagged(self):
        env = "DATABASE_URL=a\nSESSION_SECRET=b\nDEMO_MODE=true\nSMTP_HOST=mail.test\nSMTP_PORT=587\nSMTP_PASSWORD=\n"
        self.assertTrue(any("partly filled" in p and "SMTP_PASSWORD" in p for p in ce.check(EXAMPLE, env)))

    def test_unknown_name_only_in_strict(self):
        env = "DATABASE_URL=a\nSESSION_SECRET=b\nDEMO_MODE=true\nSMTP_HOST=\nSMTP_PORT=587\nSMTP_PASSWORD=\nSMPT_HOST=x\n"
        self.assertEqual(ce.check(EXAMPLE, env), [])
        self.assertTrue(any("SMPT_HOST" in p for p in ce.check(EXAMPLE, env, strict=True)))

    def test_no_file_and_no_shell(self):
        self.assertTrue(any("No environment file" in p for p in ce.check(EXAMPLE, None, {})))

    def test_values_never_printed(self):
        env = "SESSION_SECRET=supersecretvalue\n"
        self.assertFalse(any("supersecretvalue" in p for p in ce.check(EXAMPLE, env)))


if __name__ == "__main__":
    unittest.main()
