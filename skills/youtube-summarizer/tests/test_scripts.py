import importlib.util
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SKILL_DIR = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


extractor = load_module("extractor", SKILL_DIR / "scripts/extract-transcript.py")
validator = load_module("validator", SKILL_DIR / "scripts/validate-obsidian-note.py")


class ExtractorTests(unittest.TestCase):
    def test_should_extract_supported_video_id_formats(self):
        cases = {
            "https://youtu.be/dQw4w9WgXcQ": "dQw4w9WgXcQ",
            "https://www.youtube.com/watch/?v=dQw4w9WgXcQ&t=10": "dQw4w9WgXcQ",
            "https://youtube.com/shorts/dQw4w9WgXcQ": "dQw4w9WgXcQ",
            "https://m.youtube.com/embed/dQw4w9WgXcQ": "dQw4w9WgXcQ",
        }

        for url, expected in cases.items():
            with self.subTest(url=url):
                self.assertEqual(extractor.extract_video_id(url), expected)

    def test_should_reject_non_youtube_host(self):
        with self.assertRaises(ValueError):
            extractor.extract_video_id("https://example.com/live/dQw4w9WgXcQ")

        with self.assertRaises(ValueError):
            extractor.extract_video_id("javascript://youtube.com/watch?v=dQw4w9WgXcQ")

    def test_should_reject_symlinked_output_directory_inside_vault(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            vault = root / "vault"
            outside = root / "outside"
            vault.mkdir()
            outside.mkdir()
            os.symlink(outside, vault / "linked")

            with self.assertRaises(ValueError):
                extractor.validate_output_dir(vault / "linked/transcripts", vault)

    def test_should_preserve_existing_file_without_force(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "note.md"
            output.write_text("old", encoding="utf-8")

            with self.assertRaises(FileExistsError):
                extractor.write_atomically(output, "new", overwrite=False)

            self.assertEqual(output.read_text(encoding="utf-8"), "old")
            extractor.write_atomically(output, "new", overwrite=True)
            self.assertEqual(output.read_text(encoding="utf-8"), "new")


class ValidatorTests(unittest.TestCase):
    def test_should_validate_and_finalize_safe_note(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory)
            target = vault / "related.md"
            draft = vault / ".dQw4w9WgXcQ.draft.md"
            final = vault / "dQw4w9WgXcQ.md"
            target.write_text("# Related\n", encoding="utf-8")
            draft.write_text(
                "---\n"
                'type: "source"\n'
                'source: "youtube"\n'
                'title: "Video"\n'
                'video: "https://www.youtube.com/watch?v=dQw4w9WgXcQ"\n'
                'video_id: "dQw4w9WgXcQ"\n'
                'language: "en"\n'
                "transcript_generated: true\n"
                'created: "2026-10-01"\n'
                "tags:\n"
                '  - "source/youtube"\n'
                '  - "testing"\n'
                '  - "example"\n'
                "---\n\n"
                "[[related]]\n",
                encoding="utf-8",
            )

            validator.finalize_note(vault, draft, final)

            self.assertTrue(final.exists())
            self.assertFalse(draft.exists())

    def test_should_reject_non_markdown_wikilink(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory)
            note = vault / "note.md"
            note.write_text(
                "---\n"
                'type: "source"\nsource: "youtube"\n'
                'title: "Video"\nvideo: "https://www.youtube.com/watch?v=dQw4w9WgXcQ"\n'
                'video_id: "dQw4w9WgXcQ"\nlanguage: "en"\n'
                "transcript_generated: true\ncreated: "
                '"2026-10-01"\n'
                "tags:\n  - \"source/youtube\"\n  - \"testing\"\n  - \"example\"\n"
                "---\n\n[[related.txt]]\n",
                encoding="utf-8",
            )

            with self.assertRaises(validator.ValidationError):
                validator.validate_note(vault, note)

    def test_should_reject_mismatched_video_url_and_clean_draft(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory)
            draft = vault / ".dQw4w9WgXcQ.draft.md"
            final = vault / "dQw4w9WgXcQ.md"
            draft.write_text(
                "---\n"
                'type: "source"\nsource: "youtube"\n'
                'title: "Video"\nvideo: "https://youtu.be/AAAAAAAAAAA"\n'
                'video_id: "dQw4w9WgXcQ"\nlanguage: "en"\n'
                "transcript_generated: true\ncreated: "
                '"2026-10-01"\n'
                "tags:\n  - \"source/youtube\"\n  - \"testing\"\n  - \"example\"\n"
                "---\n",
                encoding="utf-8",
            )

            with self.assertRaises(validator.ValidationError):
                validator.finalize_note(vault, draft, final)

            self.assertFalse(draft.exists())
            self.assertFalse(final.exists())

    def test_should_reject_noncanonical_url_and_raw_html(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory)
            note = vault / "note.md"
            note.write_text(
                "---\n"
                'type: "source"\nsource: "youtube"\n'
                'title: "Video"\nvideo: "https://www.youtube.com/watch?v=dQw4w9WgXcQ"\n'
                'video_id: "dQw4w9WgXcQ"\nlanguage: "en"\n'
                "transcript_generated: true\ncreated: "
                '"2026-10-01"\n'
                "tags:\n  - \"source/youtube\"\n  - \"testing\"\n  - \"example\"\n"
                "---\n\n<img src=\"https://example.com/tracker\">\n",
                encoding="utf-8",
            )

            with self.assertRaises(validator.ValidationError):
                validator.validate_note(vault, note)

    def test_should_reject_html_metadata_forms(self):
        html_payloads = ["<!-- prompt -->", "<!DOCTYPE html>", "<?xml version=\"1.0\"?>"]

        for payload in html_payloads:
            with self.subTest(payload=payload), tempfile.TemporaryDirectory() as directory:
                vault = Path(directory)
                note = vault / "note.md"
                note.write_text(
                    "---\n"
                    'type: "source"\nsource: "youtube"\n'
                    'title: "Video"\nvideo: "https://www.youtube.com/watch?v=dQw4w9WgXcQ"\n'
                    'video_id: "dQw4w9WgXcQ"\nlanguage: "en"\n'
                    "transcript_generated: true\ncreated: "
                    '"2026-10-01"\n'
                    "tags:\n  - \"source/youtube\"\n  - \"testing\"\n  - \"example\"\n"
                    f"---\n\n{payload}\n",
                    encoding="utf-8",
                )

                with self.assertRaises(validator.ValidationError):
                    validator.validate_note(vault, note)

    def test_should_reject_bare_external_url(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory)
            note = vault / "note.md"
            note.write_text(
                "---\n"
                'type: "source"\nsource: "youtube"\n'
                'title: "Video"\nvideo: "https://www.youtube.com/watch?v=dQw4w9WgXcQ"\n'
                'video_id: "dQw4w9WgXcQ"\nlanguage: "en"\n'
                "transcript_generated: true\ncreated: "
                '"2026-10-01"\n'
                "tags:\n  - \"source/youtube\"\n  - \"testing\"\n  - \"example\"\n"
                "---\n\nhttps://evil.example/exfil\n",
                encoding="utf-8",
            )

            with self.assertRaises(validator.ValidationError):
                validator.validate_note(vault, note)

    def test_should_preserve_draft_when_finalization_has_io_error(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory)
            draft = vault / ".dQw4w9WgXcQ.draft.md"
            final = vault / "dQw4w9WgXcQ.md"
            draft.write_text(
                "---\n"
                'type: "source"\nsource: "youtube"\n'
                'title: "Video"\nvideo: "https://www.youtube.com/watch?v=dQw4w9WgXcQ"\n'
                'video_id: "dQw4w9WgXcQ"\nlanguage: "en"\n'
                "transcript_generated: true\ncreated: "
                '"2026-10-01"\n'
                "tags:\n  - \"source/youtube\"\n  - \"testing\"\n  - \"example\"\n"
                "---\n",
                encoding="utf-8",
            )

            with patch.object(validator.os, "link", side_effect=OSError("disk full")):
                with self.assertRaises(OSError):
                    validator.finalize_note(vault, draft, final)

            self.assertTrue(draft.exists())
            self.assertFalse(final.exists())

    def test_should_reject_symlinked_path_component(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            vault = root / "vault"
            outside = root / "outside"
            vault.mkdir()
            outside.mkdir()
            (outside / "note.md").write_text("outside", encoding="utf-8")
            os.symlink(outside, vault / "linked")

            with self.assertRaises(validator.ValidationError):
                validator.ensure_inside(vault / "linked/note.md", vault)


if __name__ == "__main__":
    unittest.main()
