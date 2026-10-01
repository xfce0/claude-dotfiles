#!/usr/bin/env bash
# Install YouTube transcript dependencies

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REQUIREMENTS_FILE="$SCRIPT_DIR/../requirements.txt"
DEFAULT_VENV="${XDG_CACHE_HOME:-$HOME/.cache}/claude-skills/youtube-summarizer/.venv"
VENV_DIR="${YOUTUBE_SUMMARIZER_VENV:-$DEFAULT_VENV}"
BOOTSTRAP_PYTHON="${PYTHON_BOOTSTRAP:-${PYTHON:-python3}}"

echo "Installing YouTube transcript dependencies..."

if ! command -v "$BOOTSTRAP_PYTHON" &>/dev/null; then
    echo "Error: Python interpreter not found: $BOOTSTRAP_PYTHON"
    echo "Please install Python pip first:"
    echo "  macOS: brew install python3"
    echo "  Ubuntu/Debian: sudo apt install python3-pip"
    echo "  Fedora: sudo dnf install python3-pip"
    exit 1
fi

mkdir -p "$(dirname "$VENV_DIR")"
"$BOOTSTRAP_PYTHON" -m venv "$VENV_DIR" || {
    echo "Could not create virtual environment: $VENV_DIR"
    exit 1
}

PYTHON="$VENV_DIR/bin/python"
"$PYTHON" -m pip install --require-hashes --only-binary=:all: -r "$REQUIREMENTS_FILE" || {
    echo "Dependency installation failed in $VENV_DIR."
    exit 1
}

# Verify installation
"$PYTHON" -c "import youtube_transcript_api; print('youtube-transcript-api is ready to use!')" 2>/dev/null || {
    echo "Installation completed but verification failed"
    echo "Try running: python3 -c 'import youtube_transcript_api'"
    exit 1
}

echo "Use this interpreter for the skill: $PYTHON"
