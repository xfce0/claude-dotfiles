#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$HOME/.claude"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info()  { echo -e "${GREEN}[+]${NC} $1"; }
warn()  { echo -e "${YELLOW}[!]${NC} $1"; }
error() { echo -e "${RED}[x]${NC} $1"; }

# Check if Claude Code config directory exists
if [ ! -d "$CLAUDE_DIR" ]; then
    error "~/.claude/ not found. Install Claude Code first: https://docs.anthropic.com/en/docs/claude-code/overview"
    exit 1
fi

# Backup existing settings if present
if [ -f "$CLAUDE_DIR/settings.json" ]; then
    BACKUP="$CLAUDE_DIR/settings.json.bak.$(date +%s)"
    warn "Existing settings.json found — backing up to $BACKUP"
    cp "$CLAUDE_DIR/settings.json" "$BACKUP"
fi

# Copy CLAUDE.md
info "Installing CLAUDE.md"
cp "$SCRIPT_DIR/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"

# Copy settings template
info "Installing settings.json"
cp "$SCRIPT_DIR/settings.template.json" "$CLAUDE_DIR/settings.json"

# Copy statusline
info "Installing statusline-command.sh"
cp "$SCRIPT_DIR/statusline-command.sh" "$CLAUDE_DIR/statusline-command.sh"

# Copy commands
info "Installing commands (RFC workflow)"
mkdir -p "$CLAUDE_DIR/commands"
cp "$SCRIPT_DIR"/commands/*.md "$CLAUDE_DIR/commands/"

# Copy agents
info "Installing agents"
mkdir -p "$CLAUDE_DIR/agents"
cp "$SCRIPT_DIR"/agents/*.md "$CLAUDE_DIR/agents/"

# Copy hooks
info "Installing hooks"
mkdir -p "$CLAUDE_DIR/hooks"
cp "$SCRIPT_DIR"/hooks/*.sh "$CLAUDE_DIR/hooks/"
chmod +x "$CLAUDE_DIR/hooks/"*.sh

# Copy public skills
info "Installing skills"
mkdir -p "$CLAUDE_DIR/skills"
for skill_dir in "$SCRIPT_DIR"/skills/*/; do
    skill_name="$(basename "$skill_dir")"
    mkdir -p "$CLAUDE_DIR/skills/$skill_name"
    cp -r "$skill_dir"* "$CLAUDE_DIR/skills/$skill_name/"
done

# Copy private skills if they exist
if [ -d "$SCRIPT_DIR/private/skills" ] && [ "$(ls -A "$SCRIPT_DIR/private/skills" 2>/dev/null)" ]; then
    info "Installing private skills"
    for skill_dir in "$SCRIPT_DIR"/private/skills/*/; do
        skill_name="$(basename "$skill_dir")"
        mkdir -p "$CLAUDE_DIR/skills/$skill_name"
        cp -r "$skill_dir"* "$CLAUDE_DIR/skills/$skill_name/"
    done
fi

# Make scripts executable
find "$CLAUDE_DIR/skills" -name "*.sh" -exec chmod +x {} \;
find "$CLAUDE_DIR/skills" -name "*.py" -exec chmod +x {} \;

echo ""
info "Done! Claude Code dotfiles installed to $CLAUDE_DIR"
echo ""
echo "  Installed:"
echo "    - CLAUDE.md (global developer standards)"
echo "    - settings.json (env, hooks, plugins, statusline)"
echo "    - commands/rfc-*.md (RFC workflow)"
echo "    - agents/ (architect, code-reviewer, hard-critic, test-writer)"
echo "    - hooks/hard-critic-check.sh"
echo "    - statusline-command.sh"
echo "    - skills/ (markitdown, youtube-summarizer, obsidian-markdown,"
echo "      obsidian-bases, json-canvas, obsidian-cli, defuddle,"
echo "      project-manager, source-ingest)"
echo ""
warn "Review ~/.claude/settings.json and adjust env vars if needed."
