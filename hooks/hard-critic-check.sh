#!/bin/bash
# Check if we're in a git repo
if ! git rev-parse --is-inside-work-tree &>/dev/null; then
  exit 0
fi

# Get diff stats (staged + unstaged)
files_changed=$(git diff --stat HEAD 2>/dev/null | tail -1 | grep -oE '[0-9]+ file' | grep -oE '[0-9]+')
lines_changed=$(git diff --stat HEAD 2>/dev/null | tail -1 | grep -oE '[0-9]+ insertion|[0-9]+ deletion' | grep -oE '[0-9]+' | paste -sd+ - | bc 2>/dev/null || echo 0)

files_changed=${files_changed:-0}
lines_changed=${lines_changed:-0}

if [ "$files_changed" -ge 3 ] || [ "$lines_changed" -ge 50 ]; then
  echo "Detected significant changes: ${files_changed} files, ~${lines_changed} lines changed. Run the hard-critic agent against these changes before considering the task done."
else
  echo "If this was a complex task (multi-file changes, new feature, refactor, architecture work), run the hard-critic agent. Otherwise, no review needed."
fi
