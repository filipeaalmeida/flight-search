#!/bin/bash
#
# setup.sh — bootstrap a local venv for the flight-search skill
#
# Creates $SKILL_DIR/.venv/ and installs requirements.txt into it.
# Safe to re-run: reuses an existing venv if present.
#
# This avoids PEP 668 "externally-managed-environment" errors on macOS,
# Debian, and other distros that block `pip install` against the system Python.

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
VENV_DIR="$SKILL_DIR/.venv"
REQ_FILE="$SKILL_DIR/requirements.txt"

if [ ! -f "$REQ_FILE" ]; then
    echo "ERROR: requirements.txt not found at $REQ_FILE" >&2
    exit 1
fi

if [ ! -x "$VENV_DIR/bin/python" ]; then
    echo "Creating venv at $VENV_DIR"
    python3 -m venv "$VENV_DIR"
fi

echo "Installing dependencies into $VENV_DIR"
"$VENV_DIR/bin/pip" install -q --upgrade pip
"$VENV_DIR/bin/pip" install -q -r "$REQ_FILE"

CONFIG_DIR="$HOME/.flight-search"
ENV_FILE="$CONFIG_DIR/.env"
PLACEHOLDER="PASTE_YOUR_KEY_HERE"

mkdir -p "$CONFIG_DIR"
if [ ! -f "$ENV_FILE" ]; then
    echo "SERPAPI_API_KEY=$PLACEHOLDER" > "$ENV_FILE"
    echo "Created $ENV_FILE with placeholder."
fi

echo "Venv ready at $VENV_DIR"
echo
echo "================================================================"
echo "ASSISTANT — INSTALL IS NOT DONE YET."
echo
echo "Do NOT conclude with prose like 'paste your key in this file'."
echo "Drive the interactive setup using your structured-question tool:"
echo "  - Claude Code: AskUserQuestion"
echo "  - Codex:       ask_user_question"
echo
echo "Required steps, in order — see $SKILL_DIR/references/setup.md:"
echo "  1. §2 'SerpApi key'      — one structured question with 2 options"
echo "     (paste here / already pasted in the file)."
echo "  2. §3 'Default currency' — ask for preferred currency, write to .env."
echo
echo "Only after both are done should you tell the user the skill is ready."
echo "================================================================"
