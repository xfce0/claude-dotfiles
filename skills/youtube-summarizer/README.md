# YouTube Summarizer Skill

Claude Code skill for processing public YouTube videos in two modes:

- Extract a timestamped Markdown transcript.
- Generate an Obsidian Markdown summary note from the transcript.

## Usage

Ask Claude Code with a YouTube URL:

```text
Get the transcript from https://youtu.be/VIDEO_ID and save it as Markdown.
```

```text
Summarize https://youtu.be/VIDEO_ID and save the note in my Obsidian vault.
```

```text
Save the transcript and also create an Obsidian summary.
```

The skill selects the output mode from the request. It does not use authenticated browser cookies or copied internal `curl` requests.

## Manual setup

```bash
PYTHON_BOOTSTRAP=python3 ./scripts/install-dependencies.sh
```

## Direct extractor usage

```bash
DEFAULT_VENV="${YOUTUBE_SUMMARIZER_VENV:-${XDG_CACHE_HOME:-$HOME/.cache}/claude-skills/youtube-summarizer/.venv}"
PYTHON="${YOUTUBE_SUMMARIZER_PYTHON:-$DEFAULT_VENV/bin/python}"
"$PYTHON" scripts/extract-transcript.py \
  --language ru \
  --language en \
  'https://youtu.be/VIDEO_ID' \
  --output-dir transcripts
```

Use `--any-language` to accept the first available subtitle language. Existing files are protected by default; use `--force` only for an explicit replacement.

For Obsidian notes, validate a draft before renaming it to the final note:

```bash
"$PYTHON" scripts/validate-obsidian-note.py \
  --vault "$OBSIDIAN_VAULT" \
  --note "$DRAFT_NOTE" \
  --output "$FINAL_NOTE"
```

## Limitations

- The video must expose manual or auto-generated subtitles.
- The extractor uses an undocumented YouTube web API and may be affected by rate limits or IP blocks.
- Videos without subtitles require a separate audio transcription workflow such as Whisper.
