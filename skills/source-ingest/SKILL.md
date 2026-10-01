---
name: source-ingest
description: Ingest a non-YouTube web article or PDF into the Obsidian vault as a structured note with frontmatter, summary, key takeaways, and wikilinks to related notes. For YouTube URLs, use youtube-summarizer instead.
---

# source-ingest

Ingest external sources into the Obsidian vault as structured, interlinked notes.

## Supported Sources

| Input | Detection | Extraction method |
|-------|-----------|-------------------|
| Web article URL | Any other `http://` or `https://` URL | `defuddle parse <url> --md` |
| PDF file | Path ends with `.pdf` | Read tool with pages parameter |

## Prerequisites

- **Web articles**: `npm install -g defuddle` (prompt user to install if missing)
- **PDF**: No extra dependencies

## Workflow

### Step 1: Detect source type

Determine the source type from the argument:

```
YouTube host (`youtube.com`, `*.youtube.com`, or `youtu.be`) with `/watch` or `/watch/` plus `v=`, `/shorts/`, `/embed/`, `/live/`, or `youtu.be/<video-id>`  →  youtube-summarizer
*.pdf                               →  PDF
http:// OR https://                 →  WEB_ARTICLE
```

### Step 2: Extract content

**YouTube:** Stop this workflow and invoke `youtube-summarizer`. It is the single source of truth for YouTube URL validation, transcript extraction, language selection, raw Markdown output, and Obsidian summaries.

**Web article:**

```bash
defuddle parse "URL" --md
```

If defuddle is not installed, fall back to `WebFetch`.

**PDF:**

Use the Read tool with `pages` parameter for large PDFs.

### Step 3: Determine vault folder

Save to `sources/` by default. This folder is for ingested article and PDF notes.

Only save elsewhere if the user explicitly specifies a different folder.

### Step 4: Find related notes

Search the vault for notes related to the source content:

1. Extract 3-5 key topics/concepts from the content
2. Use Grep to search for these terms across existing `.md` files
3. Collect matching note names for wikilinks in the Related section

### Step 5: Generate the note

Create the note using this structure:

```markdown
---
type: source
title: <TITLE>
channel: <AUTHOR_OR_CHANNEL>
published: <DATE or DD/MM/YYYY>
source: <URL for article, file path for PDF>
tags:
  - <tag1>
  - <tag2>
last-updated: <TODAY in DD/MM/YYYY>
---

# <TITLE>

## Summary

<2-3 paragraph executive summary in the language matching the source content>

## Key Takeaways

- <takeaway 1>
- <takeaway 2>
- ...

## Detailed Breakdown

### <Section 1>

<detailed analysis>

### <Section 2>

<detailed analysis>

## Concepts & Tools Mentioned

- **<concept>** — <brief definition>
- ...

## Related

- [[<related note 1>]]
- [[<related note 2>]]
- ...
```

### Step 6: Save and confirm

1. Write the file using the Write tool
2. Report the file path and a 1-line summary to the user

## Rules

- Write the summary in the **same language as the source content** (Russian source → Russian summary, English → English)
- Use **wikilinks** (`[[Note Name]]`) for internal references, standard markdown links for external URLs
- Keep frontmatter consistent with the vault's `templates/source.md` template
- Generate 3-7 relevant tags for the `tags` field
- The note title should be descriptive but concise (under 80 chars)
- If the source mentions tools, people, or concepts that exist as notes in the vault, link them with wikilinks in the body text too, not just in Related
