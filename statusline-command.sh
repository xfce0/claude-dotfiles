#!/bin/bash
# Claude Code status line — user@host cwd [branch] | model | ctx

input=$(cat)

cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd // ""')
model=$(echo "$input" | jq -r '.model.display_name // ""')
used_pct=$(echo "$input" | jq -r '.context_window.used_percentage // empty')

# Shorten home directory to ~
home="$HOME"
short_cwd="${cwd/#$home/\~}"

# User and host
user=$(whoami)
host=$(hostname -s)

# Git branch + diff stats
git_branch=""
git_diff=""
if [ -n "$cwd" ] && git -C "$cwd" --no-optional-locks rev-parse --is-inside-work-tree > /dev/null 2>&1; then
  git_branch=$(git -C "$cwd" --no-optional-locks symbolic-ref --short HEAD 2>/dev/null)
  [ -n "$git_branch" ] && git_branch=" [$git_branch]"
  # Added/removed lines (staged + unstaged)
  diff_stat=$(git -C "$cwd" --no-optional-locks diff --shortstat HEAD 2>/dev/null)
  added=$(echo "$diff_stat" | grep -oE '[0-9]+ insertion' | grep -oE '[0-9]+')
  removed=$(echo "$diff_stat" | grep -oE '[0-9]+ deletion' | grep -oE '[0-9]+')
  [ -n "$added" ] || added=0
  [ -n "$removed" ] || removed=0
  if [ "$added" -gt 0 ] || [ "$removed" -gt 0 ]; then
    git_diff=" +${added}/-${removed}"
  fi
fi

# Context usage
ctx_info=""
if [ -n "$used_pct" ]; then
  used_int=$(printf "%.0f" "$used_pct")
  ctx_info=" | ctx: ${used_int}%"
fi

# Output: single line
printf "\033[32m%s@%s\033[0m \033[34m%s\033[0m\033[33m%s\033[32m%s\033[0m\033[2m | %s%s\033[0m\n" \
  "$user" "$host" "$short_cwd" "$git_branch" "$git_diff" "$model" "$ctx_info"
