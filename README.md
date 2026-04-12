# claude-dotfiles

Opinionated Claude Code configuration: global developer standards, custom agents, RFC workflow, skills, and hooks.

## What's included

| Component | Description |
|-----------|-------------|
| **CLAUDE.md** | Global developer standards — architecture, code quality, testing, security, git workflow |
| **agents/** | Custom subagents: `architect`, `code-reviewer`, `hard-critic`, `test-writer` |
| **commands/** | RFC workflow: `rfc-init`, `rfc-review`, `rfc-propose`, `rfc-implement`, `rfc-learn` |
| **skills/** | `markitdown` (file-to-markdown converter), `youtube-summarizer` (transcript extraction + summary) |
| **hooks/** | `hard-critic-check.sh` — auto-triggers hard-critic review on significant changes |
| **statusline-command.sh** | Custom status bar: user@host, cwd, git branch, diff stats, model, context usage |
| **settings.template.json** | Env vars, hooks, statusline, and Obsidian skills plugin from [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) |

## Install

```bash
git clone https://github.com/YOUR_USERNAME/claude-dotfiles.git
cd claude-dotfiles
./install.sh
```

The script:
1. Backs up your existing `~/.claude/settings.json` (if any)
2. Copies all config files to `~/.claude/`
3. Sets up the Obsidian skills plugin marketplace reference (auto-installs on first launch)

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
