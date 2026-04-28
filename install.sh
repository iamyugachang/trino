#!/usr/bin/env bash
# install.sh — install the trino skill / slash command
#
# Targets:
#   --target claude-code   install /trino slash command + client to ~/.local/share/trino,
#                          and the Claude Code skill to ~/.claude/skills/trino
#   --target hermes        install as a Hermes skill at
#                          ~/.hermes/skills/data-science/trino
#   --target both          (default) do both
#
# Package manager: uv preferred, falls back to python3 -m pip.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="both"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --target) TARGET="$2"; shift 2 ;;
        -h|--help)
            sed -n '2,12p' "$0"; exit 0 ;;
        *) echo "Unknown arg: $1" >&2; exit 1 ;;
    esac
done

case "$TARGET" in
    claude-code|hermes|both) ;;
    *) echo "Invalid --target: $TARGET (use claude-code|hermes|both)" >&2; exit 1 ;;
esac

echo "==> Installing trino skill (target: $TARGET)"
echo "    Repo: $REPO_DIR"
echo

# ── 1. Install Python dependency (uv preferred) ──────────────────────────────
install_pkg() {
    if python3 -c "import trino" 2>/dev/null; then
        echo "  ✅ Python 'trino' package already installed."
        return
    fi
    if command -v uv >/dev/null 2>&1; then
        echo "  → installing 'trino' via uv"
        uv pip install --system trino || uv pip install trino
    else
        echo "  → installing 'trino' via python3 -m pip"
        python3 -m pip install trino
    fi
}
install_pkg

# ── 2. Claude Code install ──────────────────────────────────────────────────
install_claude_code() {
    local LIB="$HOME/.local/share/trino"
    local CMDS="$HOME/.claude/commands"
    local SKILL="$HOME/.claude/skills/trino"

    echo
    echo "==> Claude Code"

    mkdir -p "$LIB/scripts" "$LIB/templates" "$CMDS" "$SKILL"

    cp "$REPO_DIR/scripts/trino"            "$LIB/scripts/trino"
    cp "$REPO_DIR/scripts/trino_client.py"  "$LIB/scripts/trino_client.py"
    cp "$REPO_DIR/templates/trino.env"      "$LIB/templates/trino.env"
    cp "$REPO_DIR/templates/trino.env.docker" "$LIB/templates/trino.env.docker"
    chmod +x "$LIB/scripts/trino"
    echo "  ✅ client      → $LIB/scripts/"

    cp "$REPO_DIR/claude/commands/trino.md" "$CMDS/trino.md"
    echo "  ✅ /trino cmd  → $CMDS/trino.md"

    # Mirror the SKILL.md into Claude Code's skill dir so skill-trigger also works.
    cp "$REPO_DIR/SKILL.md" "$SKILL/SKILL.md"
    mkdir -p "$SKILL/scripts" "$SKILL/templates"
    cp "$REPO_DIR/scripts/trino"            "$SKILL/scripts/trino"
    cp "$REPO_DIR/scripts/trino_client.py"  "$SKILL/scripts/trino_client.py"
    cp "$REPO_DIR/templates/trino.env"      "$SKILL/templates/trino.env"
    cp "$REPO_DIR/templates/trino.env.docker" "$SKILL/templates/trino.env.docker"
    chmod +x "$SKILL/scripts/trino"
    echo "  ✅ skill       → $SKILL/"
}

# ── 3. Hermes install ───────────────────────────────────────────────────────
install_hermes() {
    local DEST="$HOME/.hermes/skills/data-science/trino"

    echo
    echo "==> Hermes"

    mkdir -p "$DEST"
    # Copy everything from the repo root, but skip .git
    rsync -a --delete --exclude='.git' --exclude='trino-output' \
        "$REPO_DIR/" "$DEST/"
    chmod +x "$DEST/scripts/trino"
    echo "  ✅ skill       → $DEST/"
}

case "$TARGET" in
    claude-code) install_claude_code ;;
    hermes)      install_hermes ;;
    both)        install_claude_code; install_hermes ;;
esac

# ── 4. Setup ~/.trino.env if missing ───────────────────────────────────────
echo
if [ ! -f "$HOME/.trino.env" ]; then
    cp "$REPO_DIR/templates/trino.env" "$HOME/.trino.env"
    chmod 600 "$HOME/.trino.env"
    echo "  ✅ Created ~/.trino.env — edit it with your Trino connection settings:"
    echo "       \$EDITOR ~/.trino.env"
else
    echo "  ℹ️  ~/.trino.env already exists, skipping."
fi

echo
echo "Done!"
case "$TARGET" in
    claude-code|both) echo "  Restart Claude Code, then try:  /trino SHOW CATALOGS" ;;
esac
case "$TARGET" in
    hermes|both)      echo "  In Hermes, ask: \"use the trino skill to SHOW CATALOGS\"" ;;
esac
