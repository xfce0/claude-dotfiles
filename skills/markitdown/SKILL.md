---
name: markitdown
description: "Convert files (PDF, DOCX, PPTX, XLSX, HTML, images, audio, ZIP, CSV, JSON, XML, EPUB) to Markdown using Microsoft's markitdown CLI"
category: conversion
risk: safe
source: custom
tags: "[conversion, markdown, pdf, docx, pptx, xlsx, html, epub, markitdown]"
date_added: "2026-04-11"
---

# markitdown

## Purpose

Convert various file formats to clean Markdown text using Microsoft's `markitdown` CLI tool. Useful for extracting text content from documents, spreadsheets, presentations, and other formats for analysis, ingestion into notes, or LLM processing.

## When to Use This Skill

- User provides a file path and wants it converted to Markdown
- User wants to extract text content from PDF, DOCX, PPTX, XLSX, HTML, images, audio, EPUB, CSV, JSON, XML, or ZIP files
- User asks to "convert", "extract text from", "read", or "parse" a non-Markdown file
- User wants to ingest a local document into the Obsidian vault
- User provides a file and asks for a summary or analysis of its contents

## Supported Formats

| Format | Extensions |
|--------|-----------|
| PDF | `.pdf` |
| Word | `.docx` |
| PowerPoint | `.pptx` |
| Excel | `.xlsx`, `.xls` |
| HTML | `.html`, `.htm` |
| CSV | `.csv` |
| JSON | `.json` |
| XML | `.xml` |
| EPUB | `.epub` |
| Images | `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff` |
| Audio | `.mp3`, `.wav`, `.m4a`, `.ogg` |
| Archives | `.zip` |

## Step 0: Verify Installation

```bash
command -v markitdown &>/dev/null && echo "markitdown is installed" || echo "markitdown is NOT installed"
```

If not installed, ask the user for permission, then:

```bash
pip3 install 'markitdown[all]'
```

## Workflow

### Step 1: Validate Input

Verify the file exists and has a supported extension.

```bash
FILE_PATH="$USER_PROVIDED_PATH"

if [ ! -f "$FILE_PATH" ]; then
    echo "File not found: $FILE_PATH"
    exit 1
fi

echo "File found: $FILE_PATH"
echo "Size: $(ls -lh "$FILE_PATH" | awk '{print $5}')"
```

### Step 2: Convert to Markdown

Run `markitdown` on the file.

```bash
markitdown "$FILE_PATH"
```

To save output to a file:

```bash
markitdown "$FILE_PATH" -o "$OUTPUT_PATH"
```

**CLI options:**

| Flag | Purpose |
|------|---------|
| `-o FILE` | Write output to file instead of stdout |
| `-x EXT` | Hint about file extension (useful with stdin) |
| `-m MIME` | Hint about MIME type |
| `-c CHARSET` | Hint about charset (e.g., UTF-8) |
| `-p` | Enable third-party plugins |
| `--keep-data-uris` | Keep base64-encoded images in output |

### Step 3: Present or Save Results

After conversion, either:

1. **Display** the Markdown output directly to the user
2. **Save** to a file if the user requested it
3. **Pipe** into further processing (e.g., summarization, note creation)

When saving to the Obsidian vault, place converted files in the appropriate folder based on content type and add proper frontmatter.

## Examples

**Basic conversion (output to stdout):**
```bash
markitdown document.pdf
```

**Save to file:**
```bash
markitdown presentation.pptx -o presentation.md
```

**Read from stdin with extension hint:**
```bash
cat data.xlsx | markitdown -x .xlsx
```

**Convert and pipe for analysis:**
```bash
markitdown report.pdf | head -100
```

## Error Handling

| Error | Cause | Action |
|-------|-------|--------|
| File not found | Invalid path | Ask user to verify path |
| Unsupported format | Unknown extension | Check supported formats list |
| Empty output | File has no extractable text (e.g., scanned PDF without OCR) | Suggest using `-d` flag with Azure Document Intelligence or an OCR plugin |
| Encoding issues | Non-UTF-8 file | Use `-c` flag to specify charset |

## Version

- **markitdown version:** 0.1.5
- **Skill version:** 1.0.0
- **Last Updated:** 2026-04-11
