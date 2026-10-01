#!/usr/bin/env python3
"""Fetch public YouTube transcripts and save them as Markdown."""

from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Optional
from urllib.parse import parse_qs, urlparse
from xml.etree.ElementTree import ParseError

from requests import RequestException, Session
from youtube_transcript_api import (
    CouldNotRetrieveTranscript,
    NoTranscriptFound,
    TranscriptsDisabled,
    YouTubeTranscriptApi,
    YouTubeTranscriptApiException,
)


VIDEO_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{11}$")


class TimeoutSession(Session):
    def request(self, method: str, url: str, **kwargs: Any):
        kwargs.setdefault("timeout", (5, 30))
        return super().request(method, url, **kwargs)


def extract_video_id(value: str) -> str:
    value = value.strip()

    if VIDEO_ID_PATTERN.fullmatch(value):
        return value

    parsed = urlparse(value if "://" in value else f"https://{value}")
    if parsed.scheme not in {"http", "https"}:
        raise ValueError(f"Invalid URL scheme: {parsed.scheme}")
    host = (parsed.hostname or "").lower()
    path_parts = [part for part in parsed.path.split("/") if part]

    if host == "youtu.be":
        candidate = path_parts[0] if path_parts else ""
    elif host == "youtube.com" or host.endswith(".youtube.com"):
        if parsed.path.rstrip("/") == "/watch":
            candidate = parse_qs(parsed.query).get("v", [""])[0]
        elif path_parts and path_parts[0] in {"shorts", "embed", "live"}:
            candidate = path_parts[1] if len(path_parts) > 1 else ""
        else:
            candidate = ""
    else:
        candidate = ""

    if not VIDEO_ID_PATTERN.fullmatch(candidate):
        raise ValueError(f"Invalid YouTube URL or video ID: {value}")

    return candidate


def fetch_transcript(
    api: YouTubeTranscriptApi,
    video_id: str,
    languages: list[str],
    allow_any_language: bool,
):
    try:
        return api.fetch(video_id, languages=languages)
    except NoTranscriptFound:
        if not allow_any_language:
            raise

        available = api.list(video_id)
        first_transcript = next(iter(available), None)
        if first_transcript is None:
            raise
        return first_transcript.fetch()


def format_timestamp(seconds: float) -> str:
    total = max(0, int(seconds))
    hours, remainder = divmod(total, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def escape_markdown(text: str) -> str:
    special_characters = r"\`*_{}[]()#+-.!|><&~"
    return "".join(
        f"\\{character}" if character in special_characters else character
        for character in text
    )


def render_markdown(video_id: str, transcript: Any) -> str:
    lines = [
        "# YouTube Transcript",
        "",
        f"- Source: https://www.youtube.com/watch?v={video_id}",
        f"- Video ID: `{video_id}`",
        f"- Language: {escape_markdown(transcript.language)} "
        f"(`{escape_markdown(transcript.language_code)}`)",
        f"- Generated: `{transcript.is_generated}`",
        "",
        "## Transcript",
        "",
    ]

    for snippet in transcript:
        timestamp = format_timestamp(snippet.start)
        text = escape_markdown(" ".join(snippet.text.split()))
        lines.append(f"- **[{timestamp}]** {text}")

    return "\n".join(lines) + "\n"


def write_atomically(path: Path, content: str, overwrite: bool) -> None:
    temporary_path: Optional[Path] = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            temporary_file.write(content)
            temporary_file.flush()
            os.fsync(temporary_file.fileno())

        if overwrite:
            os.replace(temporary_path, path)
            temporary_path = None
        else:
            try:
                os.link(temporary_path, path)
            finally:
                temporary_path.unlink(missing_ok=True)
                temporary_path = None
    except Exception:
        if temporary_path is not None:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass
        raise


def validate_output_dir(path: Path, vault_root: Optional[Path]) -> Path:
    absolute_path = Path(os.path.abspath(path))
    if vault_root is None:
        if absolute_path.is_symlink():
            raise ValueError(f"Output directory cannot be a symlink: {path}")
        return absolute_path

    absolute_root = Path(os.path.abspath(vault_root))
    try:
        relative_parts = absolute_path.relative_to(absolute_root).parts
    except ValueError as error:
        raise ValueError(f"Output directory is outside the vault: {path}") from error

    current = absolute_root
    for part in relative_parts:
        current /= part
        if current.is_symlink():
            raise ValueError(f"Output path contains a symlink: {current}")

    try:
        absolute_path.resolve().relative_to(absolute_root.resolve())
    except ValueError as error:
        raise ValueError(f"Output directory resolves outside the vault: {path}") from error

    return absolute_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch YouTube transcripts and save them as Markdown."
    )
    parser.add_argument("urls", nargs="+", help="YouTube URLs or video IDs")
    parser.add_argument(
        "--language",
        dest="languages",
        action="append",
        default=None,
        help="Preferred language; repeat for priority order (default: ru, en)",
    )
    parser.add_argument(
        "--any-language",
        action="store_true",
        help="Use the first available language if preferred languages are missing",
    )
    parser.add_argument(
        "--list",
        dest="list_transcripts",
        action="store_true",
        help="List available transcripts instead of downloading them",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing Markdown file",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=Path("transcripts"),
        help="Directory for Markdown files (default: transcripts)",
    )
    parser.add_argument(
        "--vault-root",
        type=Path,
        help="Vault root used to reject symlinked output paths",
    )
    args = parser.parse_args()
    languages = args.languages or ["ru", "en"]
    failed = False
    http_client = TimeoutSession()
    api = YouTubeTranscriptApi(http_client=http_client)

    try:
        try:
            output_dir = validate_output_dir(args.output_dir, args.vault_root)
        except ValueError as error:
            print(f"Invalid output directory: {error}", file=sys.stderr)
            return 1

        if not args.list_transcripts:
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
            except OSError as error:
                print(f"Could not create output directory: {error}", file=sys.stderr)
                return 1

        for video_url in args.urls:
            try:
                video_id = extract_video_id(video_url)
                if args.list_transcripts:
                    print(f"Available transcripts for {video_id}:")
                    for available in api.list(video_id):
                        transcript_type = "auto-generated" if available.is_generated else "manual"
                        print(
                            f"- {available.language} ({available.language_code}), "
                            f"{transcript_type}, "
                            f"translatable={available.is_translatable}"
                        )
                    continue

                transcript = fetch_transcript(
                    api,
                    video_id,
                    languages,
                    args.any_language,
                )
                output_path = output_dir / f"{video_id}.md"
                write_atomically(
                    output_path,
                    render_markdown(video_id, transcript),
                    overwrite=args.force,
                )
                print(f"Saved {output_path} ({transcript.language_code})")
            except ValueError as error:
                print(f"Invalid input: {error}", file=sys.stderr)
                failed = True
            except TranscriptsDisabled:
                print(f"Subtitles are disabled: {video_url}", file=sys.stderr)
                failed = True
            except CouldNotRetrieveTranscript as error:
                print(f"Could not retrieve transcript for {video_url}: {error}", file=sys.stderr)
                failed = True
            except RequestException as error:
                print(f"Network error for {video_url}: {error}", file=sys.stderr)
                failed = True
            except (ParseError, TypeError, KeyError) as error:
                print(f"Could not parse YouTube response for {video_url}: {error}", file=sys.stderr)
                failed = True
            except FileExistsError as error:
                print(f"{error}; use --force to replace it", file=sys.stderr)
                failed = True
            except OSError as error:
                print(f"Could not save transcript for {video_url}: {error}", file=sys.stderr)
                failed = True
            except YouTubeTranscriptApiException as error:
                print(f"YouTube API error for {video_url}: {error}", file=sys.stderr)
                failed = True
    finally:
        http_client.close()

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
