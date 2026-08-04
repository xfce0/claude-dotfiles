---
name: vault-organizer
description: Organize orphaned files from the Obsidian vault root (and optionally non-standard folders) into appropriate directories and add missing frontmatter/tags. Use when the user wants to tidy up the vault, sort newly created files, or when files are sitting in the vault root without a home. If more than 3 non-protected files exist in the vault root, proactively suggest running this skill.
---

# vault-organizer

Scan the vault for orphaned/misplaced files and move them into the correct directory based on content analysis. Add missing frontmatter and tags.

## Triggers

Use this skill when the user says any of:
- "organize vault", "tidy up", "sort files", "clean up root"
- "organize orphan files", "move root files"
- "sort new notes", "file inbox zero"
- "deep clean", "full vault scan"

If more than 3 non-protected files exist in the vault root, proactively suggest: "I see [N] orphan files in the vault root. Want me to run vault-organizer?"

## Modes

- **root** (default): Scan only the vault root for orphan files. Fast, safe, covers the inbox-zero use case.
- **full**: Also scan non-standard top-level folders (any folder not in the known structure list) and flag misplaced files within known folders (e.g. a `.md` in `images/`).

The user can specify mode explicitly ("deep clean" → full, "sort root" → root) or be asked.

## Protected paths (NEVER move)

Do not move files matching any of these patterns:

- `CLAUDE.md`, `README.md` in vault root
- All dotfiles and dotfolders: `.obsidian/`, `.claude/`, `.git/`, `.gitignore`, `.DS_Store`, `.trash/`
- Support folders and their contents: `templates/`, `images/`, `Excalidraw/`
- Any file whose name starts with `.` (iCloud `.icloud` placeholders)

Reference the vault's `CLAUDE.md` "Support folders" section as the authoritative protected list. If CLAUDE.md changes, follow it.

## Known vault structure

These are the recognized destination folders. Read from the vault's `CLAUDE.md` at runtime to stay current:

- `projects/` — managed projects (discover dynamically, see below)
- `sources/` — ingested external content
- `tech/` — tech wiki (`android/`, `linux/`, `macos/`, `windows/`, `docker/`, `networking/`, `web/`, `sap/`)
- `research/` — `ai/`, `bci/`
- `edu/` — `HSE/`, `miit/`
- `writing/` — `fics/`, `lyrics/`
- `things/` — `gadgets/`, `clothing/`, `home/`
- `self/` — personal notes

### Dynamic project discovery

Do NOT hardcode project names. Instead, discover them at runtime:

```
Glob pattern="projects/*/overview.md"
```

Extract project names from the directory paths. Match file tags/content against these names (case-insensitive). This ensures new projects are automatically recognized.

## Routing rules

Analyze each orphan file's content (title, body text, frontmatter, tags, wikilinks) and route to the best-fit directory. Apply rules in priority order:

### Priority 1: Existing frontmatter → direct match

| Signal | Destination |
|--------|-------------|
| `type: source` or tags include `source`, or has Summary/Key Takeaways sections typical of `source-ingest` output | `sources/` |
| Tags match a discovered project name (case-insensitive) | `projects/<Project>/documents/` |
| `type: dossier` or content is clearly a person profile (name as title, personal details) | `Dossier/` or relevant project's `documents/` |
| `type: self` or tags include `self`, `goals`, `reflection` | `self/` |

### Priority 2: Content keywords → topic folder

| Content signals | Destination |
|-----------------|-------------|
| Programming, frameworks, CLI, DevOps, Docker, Linux, networking, web dev, sysadmin, handbook | `tech/<subfolder>/` — pick closest: `android/`, `linux/`, `macos/`, `windows/`, `docker/`, `networking/`, `web/`, `sap/` |
| AI, ML, NLP, neural networks, data science, LLM, transformer, GPT | `research/ai/` |
| BCI, brain-computer interface, neuroscience, EEG | `research/bci/` |
| ВШЭ, HSE, экзамен, лаба, зачёт, семинар, диплом (university context) | `edu/HSE/` |
| МИИТ, МГУПС, ВКР, билеты (university context) | `edu/miit/` |
| Fiction, fanfic, фанфик, рассказ, глава, сюжет | `writing/fics/` |
| Lyrics, текст песни, аккорды, куплет, припев | `writing/lyrics/` |
| Gadget, гаджет, устройство, обзор устройства, спецификации | `things/gadgets/` |
| Одежда, clothing, размер, бренд, стиль | `things/clothing/` |
| Мебель, ремонт, квартира, дом, интерьер | `things/home/` |

### Priority 3: Wikilink context → follow the graph

If the note contains `[[...]]` links to notes in a specific folder, or is referenced by notes in a specific folder, prefer that folder.

### Priority 4: Ambiguous → ask the user

If no clear signal, present the user with the top 2 candidate destinations and ask.

## Confidence scoring

Score each routing signal to make classification reproducible:

| Signal type | Points |
|-------------|--------|
| Frontmatter `type` exact match | 10 |
| Frontmatter `tags` match | 10 |
| Wikilink to/from notes in a specific folder | 7 |
| Title keywords match | 5 |
| Body content keywords match | 3 |

- **high** (≥10 points): single clear winner
- **medium** (7–9 points, or top two within 2 points): present both options, recommend the leader
- **low** (<7 points): must ask user

## Workflow

### Step 1: Git checkpoint

Before any analysis, create a safety checkpoint:

```bash
git add -A && git commit -m "chore: checkpoint before vault-organizer"
```

If nothing to commit, that's fine — skip silently.

### Step 2: Scan

**Root mode:** Use the Glob tool (NOT `find` via Bash):

```
Glob pattern="*.md" path="<vault_root>"
Glob pattern="*.canvas" path="<vault_root>"
Glob pattern="*.base" path="<vault_root>"
```

Filter out protected files.

**Full mode:** Additionally scan:
- Non-standard top-level folders (any folder not in known structure)
- Files misplaced within known folders (e.g. `.md` in `images/`)

```
Glob pattern="images/**/*.md" path="<vault_root>"
```

If `.icloud` placeholder files are found, warn the user that some files may not be locally available and need to be opened in Finder first.

If no orphan files found, report "Vault is clean, nothing to organize." and stop.

### Step 3: Discover projects

```
Glob pattern="projects/*/overview.md" path="<vault_root>"
```

Build a list of known project names from the paths. This is used for tag-based and content-based project matching.

### Step 4: Analyze each file

For each orphan file:

1. **Read frontmatter** fully (everything between `---` markers)
2. **Read body** — next 100 lines after frontmatter closes (ensures classification signals are captured regardless of frontmatter size)
3. **Extract signals**: `type`, `tags`, title (from `# heading` or filename), wikilinks (`[[...]]`), keywords
4. **Score destinations** using the confidence scoring table
5. **Determine tags** to add based on destination and content
6. **Check for name collisions** in the target directory

Build a move plan as a table:

```
| # | File | Destination | Tags to add | Confidence | Notes |
```

### Step 5: Present plan and confirm

Show the move plan to the user. For **medium** confidence items, show both candidates with recommendation. For **low** confidence items, explicitly ask. Wait for user confirmation before proceeding.

Use `AskUserQuestion`:

```
Here's my plan for organizing [N] files:

[table]

[Questions for low/medium confidence items]

Should I proceed? Any changes?
```

### Step 6: Execute moves

For each confirmed file:

1. **Ensure frontmatter** exists and is complete:
   - Add `type:` if missing (infer from destination: `tech` → `note`, `self` → `self`, `sources` → `source`, project docs → `note`)
   - Add relevant `tags:` if missing or incomplete
   - Preserve ALL existing frontmatter fields — never delete user data
   - Match the date format used in `templates/Default template.md` (check it at runtime)

2. **Move the file** using Bash:
   ```bash
   mv "<source>" "<destination>"
   ```

3. **Check wikilinks** — Obsidian resolves wikilinks by name (not path), so moves usually don't break links. Only flag if there's a name collision in the destination.

Do NOT inject `> See also:` backlinks. Obsidian's native backlinks panel already surfaces connections. Adding blockquote links clutters notes and creates maintenance burden.

### Step 7: Commit and report

Commit the changes:

```bash
git add -A && git commit -m "chore: vault-organizer — organized [N] files"
```

Show a summary:

```
Organized [N] files:
- `filename.md` → `destination/` (added tags: x, y)
- ...

To undo: git revert HEAD
```

Always include the undo instruction.

## Frontmatter conventions

Follow existing vault conventions. Check `templates/Default template.md` at runtime for the canonical field set and date format. Standard fields:

```yaml
---
type: <note|source|self|dossier|project>
title: <note title>
tags:
  - <tag1>
  - <tag2>
---
```

Only add fields that are relevant. Don't add empty placeholder fields (`channel:`, `published:`, `video:`, `raw:`) unless the note is `type: source` and those fields are meaningful.

## Tag conventions

Before applying tags, scan 10–20 existing notes across different folders to detect the dominant tag convention (kebab-case vs camelCase vs single-word). Adopt whatever the vault already uses.

Fallback if no convention detected:
- Lowercase, kebab-case for multi-word: `brain-computer-interface`
- Folder-derived: `tech`, `research`, `edu`, `writing`, `self`
- Topic: `ai`, `ml`, `docker`, `linux`, `web`, etc.

## Edge cases

- **Untitled files** (`Untitled.md`, `Untitled 1.md`, etc.): Read content. If empty or contains only the default template with no user content, ask user whether to delete or keep. If has content, classify normally.
- **Canvas files** (`.canvas`): Parse the JSON to extract `nodes[].file` paths (see `obsidian:json-canvas` skill for schema). Route based on linked notes' locations.
- **Base files** (`.base`): Parse using the schema in `obsidian:obsidian-bases` skill. Route based on the `source` folder path in the base definition.
- **Files with name collisions**: If the target directory already contains a file with the same name, warn the user and ask how to resolve (rename, merge, skip).
- **`.icloud` placeholders**: Warn the user and skip — these files are not locally available.
- **Full mode — non-standard folders**: For files in folders like `Dossier/`, `cource/`, or any unlisted folder, present them as a group and ask the user where they belong. Don't auto-move legacy folder contents without explicit instruction.
- **Excalidraw `.md` wrappers**: Files that start with Excalidraw JSON markers or contain `excalidraw-plugin` in frontmatter must NEVER be moved from `Excalidraw/`. If found elsewhere, flag but don't move.
