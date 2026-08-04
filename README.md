# claude-dotfiles

Opinionated Claude Code configuration: global developer standards, custom agents, RFC workflow, skills, and hooks.

## What's included

| Component | Description |
|-----------|-------------|
| **CLAUDE.md** | Global developer standards — architecture, code quality, testing, security, git workflow |
| **agents/** | Custom subagents: `architect`, `code-reviewer`, `hard-critic`, `test-writer` |
| **commands/** | RFC workflow: `rfc-init`, `rfc-review`, `rfc-propose`, `rfc-implement`, `rfc-learn` |
| **hooks/** | `hard-critic-check.sh` — auto-triggers hard-critic review on significant changes |
| **statusline-command.sh** | Custom status bar: user@host, cwd, git branch, diff stats, model, context usage |
| **settings.template.json** | Env vars, hooks, statusline config |

### Skills

| Skill | Description |
|-------|-------------|
| **markitdown** | Convert files (PDF, DOCX, PPTX, XLSX, HTML, etc.) to Markdown via Microsoft's markitdown CLI |
| **youtube-summarizer** | Extract YouTube transcripts and generate structured summaries |
| **obsidian-markdown** | Create and edit Obsidian Flavored Markdown (wikilinks, callouts, embeds, properties) |
| **obsidian-bases** | Create and edit Obsidian Bases (.base files) — database-like views of notes |
| **json-canvas** | Create and edit JSON Canvas (.canvas) files — visual canvases, mind maps, flowcharts |
| **obsidian-cli** | Interact with Obsidian vaults via CLI — read, search, manage notes, plugins, themes |
| **defuddle** | Extract clean markdown from web pages, removing clutter (token-efficient alternative to WebFetch) |
| **project-manager** | Create and manage projects in Obsidian with structured folders and dashboards |
| **source-ingest** | Ingest YouTube videos, web articles, or PDFs into the vault as structured notes |
| **vault-organizer** | Sort orphaned Obsidian notes into the appropriate folders and add missing metadata |

## Install

```bash
git clone https://github.com/Eflarus/claude-dotfiles.git
cd claude-dotfiles
./install.sh
```

The script:
1. Backs up your existing `~/.claude/settings.json` (if any)
2. Copies all config files to `~/.claude/`
3. Installs all skills (including Obsidian skills) directly — no plugins needed

## Private skills

Put personal or project-specific skills in `private/skills/`:

```
private/
  skills/
    my-private-skill/
      SKILL.md
```

The `private/` directory is `.gitignore`d. `install.sh` will install private skills alongside public ones.

## RFC workflow

A structured approach to planning features before coding:

```
rfc-init <name>     → create RFC from template
rfc-review <name>   → adversarial review (checklist + open questions)
rfc-propose <name>  → propose solutions for open questions
rfc-implement <name> → implement (only after approval)
rfc-learn <name>    → post-mortem: what went wrong, how to prevent it
```

Use as slash commands: `/rfc-init auth-redesign`

## Agents

| Agent | Model | Purpose |
|-------|-------|---------|
| `architect` | opus | System design, architecture review, refactoring plans |
| `code-reviewer` | sonnet | Code quality, security, SOLID compliance |
| `hard-critic` | opus | Ruthless 8-dimension product critique with severity levels |
| `test-writer` | sonnet | Generate unit/integration tests following project patterns |

The `hard-critic` agent is auto-triggered by the Stop hook when changes are significant (3+ files or 50+ lines).

## Customization

- Edit `CLAUDE.md` to adjust developer standards
- Edit `settings.template.json` to change env vars or hooks
- Add new agents to `agents/`
- Add new skills to `skills/`
- Add new slash commands to `commands/`

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview) installed
- Python 3 (for youtube-summarizer)
- `markitdown` CLI (for markitdown skill): `pip3 install 'markitdown[all]'`

## License

MIT
