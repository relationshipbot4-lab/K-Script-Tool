"""Security regression checks for repository data/secret exclusions."""

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RepositorySecurityTests(unittest.TestCase):
    def test_gitignore_excludes_secrets_sessions_and_personal_exports(self):
        patterns = set((ROOT / ".gitignore").read_text(encoding="utf-8").splitlines())
        required = {
            ".env",
            ".env.*",
            "!.env.example",
            "sessions/",
            "*.session",
            "*.session-journal",
            "data/*",
            "*.csv",
            "*.jsonl",
            "logs/",
            "*.log",
            "*.sqlite3",
            "*.db",
        }
        self.assertTrue(required.issubset(patterns))

    def test_readme_warns_about_spreadsheet_formula_risk(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("formula-like values as executable formulas", text)
        self.assertIn("does not neutralize spreadsheet formulas", text)


if __name__ == "__main__":
    unittest.main()
