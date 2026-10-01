#!/usr/bin/env python3
"""Validate the safety-critical structure of a generated Obsidian note."""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse


VIDEO_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{11}$")
TAG_PATTERN = re.compile(r"^[a-z0-9][a-z0-9/_-]*$")
STRING_PROPERTY_PATTERN = re.compile(r'^[a-z_]+: "(?:[^"\\]|\\.)*"$')
WIKILINK_PATTERN = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
MARKDOWN_DESTINATION_PATTERNS = (
    re.compile(r"\]\(([^)]+)\)"),
    re.compile(r"^\s*\[[^\]]+\]:\s*(\S+)", re.MULTILINE),
    re.compile(r"(?i)\bhref\s*=\s*[\"']([^\"']+)[\"']"),
    re.compile(r"<((?:https?|javascript|file|data|obsidian):[^>]+)>", re.IGNORECASE),
)
BARE_URL_PATTERN = re.compile(r"(?<![\"'(])(?:https?://|www\.|//)[^\s<>\])]+")


class ValidationError(ValueError):
    pass


def ensure_inside(path: Path, root: Path) -> Path:
    absolute_root = Path(os.path.abspath(root))
    absolute_path = Path(os.path.abspath(path))
    try:
        relative_parts = absolute_path.relative_to(absolute_root).parts
    except ValueError as error:
        raise ValidationError(f"Path is outside the vault: {path}") from error

    current = absolute_root
    for part in relative_parts:
        current /= part
        if current.is_symlink():
            raise ValidationError(f"Symlinks are not allowed: {current}")

    resolved_root = absolute_root.resolve()
    resolved_path = absolute_path.resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as error:
        raise ValidationError(f"Path is outside the vault: {path}") from error
    return resolved_path


def extract_video_id(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValidationError("YouTube URL must use HTTP or HTTPS")
    host = (parsed.hostname or "").lower()
    parts = [part for part in parsed.path.split("/") if part]

    if host == "youtu.be":
        candidate = parts[0] if parts else ""
    elif host == "youtube.com" or host.endswith(".youtube.com"):
        if parsed.path.rstrip("/") == "/watch":
            candidate = parse_qs(parsed.query).get("v", [""])[0]
        elif parts and parts[0] in {"shorts", "embed", "live"}:
            candidate = parts[1] if len(parts) > 1 else ""
        else:
            candidate = ""
    else:
        candidate = ""

    if not VIDEO_ID_PATTERN.fullmatch(candidate):
        raise ValidationError("Frontmatter video must be a valid YouTube URL")
    return candidate


def canonical_video_url(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}"


def parse_frontmatter(lines: list[str]) -> tuple[dict[str, str], list[str], int]:
    if len(lines) < 3 or lines[0] != "---":
        raise ValidationError("Frontmatter must start with ---")

    try:
        end = lines.index("---", 1)
    except ValueError as error:
        raise ValidationError("Frontmatter closing --- is missing") from error

    properties: dict[str, str] = {}
    tags: list[str] = []
    in_tags = False

    for line in lines[1:end]:
        if line == "tags:":
            in_tags = True
            continue
        if in_tags and line.startswith("  - "):
            match = re.fullmatch(r'  - "([^"]+)"', line)
            if not match:
                raise ValidationError("Tags must use quoted YAML strings")
            tags.append(match.group(1))
            continue
        in_tags = False
        if not STRING_PROPERTY_PATTERN.fullmatch(line):
            if line == "transcript_generated: true":
                properties["transcript_generated"] = "true"
                continue
            raise ValidationError(f"Unsafe or malformed frontmatter line: {line}")
        key, value = line.split(": ", 1)
        properties[key] = value[1:-1]

    properties["tags"] = "\n".join(tags)
    return properties, tags, end


def validate_note(vault: Path, note: Path) -> str:
    resolved_vault = vault
    resolved_note = ensure_inside(note, resolved_vault)
    if not resolved_note.is_file():
        raise ValidationError(f"Note does not exist: {note}")

    lines = resolved_note.read_text(encoding="utf-8").splitlines()
    properties, tags, frontmatter_end = parse_frontmatter(lines)

    required = {"type", "source", "title", "video", "video_id", "language", "created"}
    missing = required - properties.keys()
    if missing:
        raise ValidationError(f"Missing frontmatter properties: {sorted(missing)}")
    if properties.get("type") != "source" or properties.get("source") != "youtube":
        raise ValidationError("The note must be a YouTube source note")
    if not VIDEO_ID_PATTERN.fullmatch(properties["video_id"]):
        raise ValidationError("Invalid video_id in frontmatter")
    if properties["video"] != canonical_video_url(properties["video_id"]):
        raise ValidationError("video must be the canonical HTTPS YouTube URL")
    if len(tags) < 3 or len(tags) > 7 or any(not TAG_PATTERN.fullmatch(tag) for tag in tags):
        raise ValidationError("Tags must contain 3-7 safe lowercase values")

    body = "\n".join(lines[frontmatter_end + 1 :])
    if re.search(r"<\s*/?\s*[A-Za-z][^>]*>|<!--|<![A-Za-z]|<\?", body):
        raise ValidationError("Raw HTML is not allowed in the note body")
    if re.search(r"(?i)\b(?:javascript|file|data|obsidian):", body):
        raise ValidationError("Unsafe URL scheme in Markdown body")
    for pattern in MARKDOWN_DESTINATION_PATTERNS:
        for external_url in pattern.findall(body):
            if external_url != canonical_video_url(properties["video_id"]):
                raise ValidationError("External Markdown links must point to this YouTube video")
    for external_url in BARE_URL_PATTERN.findall(body):
        if external_url.rstrip(".,;:!?\"") != canonical_video_url(properties["video_id"]):
            raise ValidationError("Bare URLs must point to this YouTube video")

    for target in WIKILINK_PATTERN.findall(body):
        if target.startswith(("/", "http:", "https:")) or ".." in Path(target).parts:
            raise ValidationError(f"Unsafe wikilink: {target}")
        target_path = Path(target)
        if target_path.suffix not in {"", ".md"}:
            raise ValidationError(f"Wikilink must target a Markdown note: {target}")
        linked_note = ensure_inside(resolved_vault / target_path, resolved_vault)
        if linked_note.suffix == "":
            linked_note = linked_note.with_suffix(".md")
        if not linked_note.is_file():
            raise ValidationError(f"Wikilink target does not exist: {target}")

    return properties["video_id"]


def finalize_note(vault: Path, note: Path, output: Path) -> None:
    resolved_note = ensure_inside(note, vault)
    resolved_output = ensure_inside(output, vault)
    output_created = False

    try:
        if not resolved_note.name.startswith("."):
            raise ValidationError("Finalization requires a hidden draft note")
        video_id = validate_note(vault, note)
        if resolved_note.name != f".{video_id}.draft.md":
            raise ValidationError("Draft filename must be .<video_id>.draft.md")
        if resolved_output.name != f"{video_id}.md":
            raise ValidationError("Final note filename must be <video_id>.md")
        if resolved_output.exists():
            raise ValidationError(f"Final note already exists: {output}")

        resolved_output.parent.mkdir(parents=True, exist_ok=True)
        os.link(resolved_note, resolved_output)
        output_created = True
        resolved_note.unlink()
    except ValidationError:
        if output_created:
            try:
                resolved_output.unlink(missing_ok=True)
            except OSError:
                pass
        try:
            resolved_note.unlink(missing_ok=True)
        except OSError:
            pass
        raise
    except OSError:
        if output_created:
            try:
                resolved_output.unlink(missing_ok=True)
            except OSError:
                pass
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an Obsidian YouTube note")
    parser.add_argument("--vault", type=Path, required=True)
    parser.add_argument("--note", type=Path, required=True)
    parser.add_argument(
        "--output",
        type=Path,
        help="Atomically finalize the validated draft at this path without replacing an existing file",
    )
    args = parser.parse_args()

    try:
        if args.output:
            finalize_note(args.vault, args.note, args.output)
        else:
            validate_note(args.vault, args.note)
    except (OSError, ValidationError) as error:
        print(f"Invalid Obsidian note: {error}", file=sys.stderr)
        return 1

    print(f"Valid Obsidian note: {args.note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
