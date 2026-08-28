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
            self.assertTrue((vault / "memories" / "imports").is_dir())

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

    def test_imports_reader_confirmed_context_packet(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            vault = root / "vault"
            packet = root / "reader-context.md"
            packet.write_text(
                "# Reader Context Packet\n\n## Confirmed facts\n- Builds small prototypes.\n",
                encoding="utf-8",
            )

            imported = self.run_cli(
                "import-context",
                "--vault",
                str(vault),
                "--input",
                str(packet),
                "--source",
                "My Long-Used AI",
                "--date",
                "2026-08-28",
                "--confirmed-by-reader",
            )
            self.assertEqual(imported.returncode, 0, imported.stderr)
            result = json.loads(imported.stdout)
            destination = Path(result["imported"])
            self.assertTrue(destination.exists())
            saved = destination.read_text(encoding="utf-8")
            self.assertIn("Status: reader-confirmed", saved)
            self.assertIn("Source: My Long-Used AI", saved)
            self.assertIn("Builds small prototypes", saved)

            duplicate = self.run_cli(
                "import-context",
                "--vault",
                str(vault),
                "--input",
                str(packet),
                "--source",
                "My Long-Used AI",
                "--date",
                "2026-08-28",
                "--confirmed-by-reader",
            )
            self.assertEqual(duplicate.returncode, 2)
            self.assertIn("Refusing to overwrite", duplicate.stderr)

    def test_refuses_unconfirmed_context_packet(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            packet = root / "reader-context.md"
            packet.write_text("A draft context packet.\n", encoding="utf-8")

            result = self.run_cli(
                "import-context",
                "--vault",
                str(root / "vault"),
                "--input",
                str(packet),
                "--source",
                "Example AI",
                "--date",
                "2026-08-28",
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("explicit reader confirmation", result.stderr)

    def test_saves_daily_note(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            vault = root / "vault"
            note = root / "daily-note.md"
            content = "# Reading note · 2026-08-28\n\n## Reading scope\n\nOne book.\n"
            note.write_text(content, encoding="utf-8")

            result = self.run_cli(
                "save-daily",
                "--vault",
                str(vault),
                "--date",
                "2026-08-28",
                "--input",
                str(note),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            destination = vault.resolve() / "daily" / "2026-08-28.md"
            self.assertEqual(Path(json.loads(result.stdout)["saved"]), destination)
            self.assertEqual(destination.read_text(encoding="utf-8"), content)

    def test_save_daily_rejects_invalid_date(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            note = root / "daily-note.md"
            note.write_text("# Reading note\n", encoding="utf-8")

            for invalid_date in ("2026/08/28", "2026-02-30"):
                with self.subTest(date=invalid_date):
                    result = self.run_cli(
                        "save-daily",
                        "--vault",
                        str(root / "vault"),
                        "--date",
                        invalid_date,
                        "--input",
                        str(note),
                    )
                    self.assertEqual(result.returncode, 2)
                    self.assertIn("YYYY-MM-DD", result.stderr)

    def test_save_daily_rejects_missing_input(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            vault = root / "vault"
            result = self.run_cli(
                "save-daily",
                "--vault",
                str(vault),
                "--date",
                "2026-08-28",
                "--input",
                str(root / "missing.md"),
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("input file does not exist", result.stderr)
            self.assertFalse(vault.exists())

    def test_save_daily_refuses_to_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            vault = root / "vault"
            note = root / "daily-note.md"
            note.write_text("first version\n", encoding="utf-8")

            first = self.run_cli(
                "save-daily",
                "--vault",
                str(vault),
                "--date",
                "2026-08-28",
                "--input",
                str(note),
            )
            self.assertEqual(first.returncode, 0, first.stderr)
            note.write_text("second version\n", encoding="utf-8")

            duplicate = self.run_cli(
                "save-daily",
                "--vault",
                str(vault),
                "--date",
                "2026-08-28",
                "--input",
                str(note),
            )
            self.assertEqual(duplicate.returncode, 2)
            self.assertIn("Refusing to overwrite existing daily note", duplicate.stderr)
            self.assertEqual(
                (vault / "daily" / "2026-08-28.md").read_text(encoding="utf-8"),
                "first version\n",
            )

    def test_refuses_vault_inside_skill_or_git_repository(self):
        with tempfile.TemporaryDirectory() as input_directory:
            note = Path(input_directory) / "daily-note.md"
            note.write_text("# Reading note\n", encoding="utf-8")

            with tempfile.TemporaryDirectory(dir=ROOT) as unsafe_vault:
                result = self.run_cli(
                    "save-daily",
                    "--vault",
                    unsafe_vault,
                    "--date",
                    "2026-08-28",
                    "--input",
                    str(note),
                )
                self.assertEqual(result.returncode, 2)
                self.assertIn("skill directory or a Git repository", result.stderr)
                self.assertFalse(Path(unsafe_vault, "daily", "2026-08-28.md").exists())


if __name__ == "__main__":
    unittest.main()
