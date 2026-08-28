import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "book-marginalia-agent" / "scripts" / "vault.py"


class VaultCliTest(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_init_is_idempotent_and_keeps_profile(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory) / "vault"
            first = self.run_cli("init", "--vault", str(vault))
            self.assertEqual(first.returncode, 0, first.stderr)
            profile = vault / "profile.md"
            profile.write_text("my profile\n", encoding="utf-8")

            second = self.run_cli("init", "--vault", str(vault))
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(profile.read_text(encoding="utf-8"), "my profile\n")

    def test_add_and_list_day(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            vault = root / "vault"
            entry_file = root / "entry.json"
            entry_file.write_text(
                json.dumps(
                    {
                        "date": "2026-08-28",
                        "time": "21:30",
                        "book": "Example Book",
                        "chapter": "Beginnings",
                        "location": "Page 12",
                        "mode": "balanced",
                        "quote": "A small, invented example passage.",
                        "marginalia": {
                            "meaning": "A beginning needs action.",
                            "connection": "No personal memory was used.",
                            "challenge": "Action without direction can become motion.",
                            "takeaway": "Define one observable next step.",
                            "short_note": "Movement matters when it changes what you know.",
                        },
                        "memory_sources": [],
                        "reader_response": "Keep this one.",
                    }
                ),
                encoding="utf-8",
            )

            added = self.run_cli("add", "--vault", str(vault), "--entry", str(entry_file))
            self.assertEqual(added.returncode, 0, added.stderr)

            listed = self.run_cli(
                "list-day", "--vault", str(vault), "--date", "2026-08-28"
            )
            self.assertEqual(listed.returncode, 0, listed.stderr)
            self.assertIn("Example Book", listed.stdout)
            self.assertIn("Memory sources: none", listed.stdout)
            self.assertIn("Keep this one.", listed.stdout)

    def test_rejects_empty_quote(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            entry_file = root / "entry.json"
            entry_file.write_text(
                json.dumps(
                    {
                        "date": "2026-08-28",
                        "time": "21:30",
                        "quote": "",
                        "marginalia": {},
                    }
                ),
                encoding="utf-8",
            )
            result = self.run_cli(
                "add", "--vault", str(root / "vault"), "--entry", str(entry_file)
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("quote must not be empty", result.stderr)


if __name__ == "__main__":
    unittest.main()
