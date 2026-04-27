#!/usr/bin/env bash
# install.sh — install /trino slash command for Claude Code
set -e

INSTALL_DIR="$HOME/.local/share/trino"
COMMANDS_DIR="$HOME/.claude/commands"

echo "Installing /trino command for Claude Code..."

# 1. Copy scripts to a stable location
mkdir -p "$INSTALL_DIR/scripts" "$INSTALL_DIR/templates"
cp scripts/trino          "$INSTALL_DIR/scripts/trino"
cp scripts/trino_client.py "$INSTALL_DIR/scripts/trino_client.py"
cp templates/trino.env    "$INSTALL_DIR/templates/trino.env"
chmod +x "$INSTALL_DIR/scripts/trino"

# 2. Install the slash command
mkdir -p "$COMMANDS_DIR"
cp claude/commands/trino.md "$COMMANDS_DIR/trino.md"
echo "  ✅ /trino command → $COMMANDS_DIR/trino.md"

# 3. Setup .trino.env if missing
if [ ! -f "$HOME/.trino.env" ]; then
    cp templates/trino.env "$HOME/.trino.env"
    echo "  ✅ Created ~/.trino.env — edit it with your Trino connection settings:"
    echo "       nano ~/.trino.env"
else
    echo "  ℹ️  ~/.trino.env already exists, skipping."
fi

# 4. Install Python dependency
if python3 -c "import trino" 2>/dev/null; then
    echo "  ✅ Python trino package already installed."
else
    echo "  Installing Python trino package..."
    pip install trino
fi

echo ""
echo "Done! Restart Claude Code, then use:"
echo "  /trino SHOW CATALOGS"
echo "  /trino list tables in hive.analytics"
echo "  /trino SELECT * FROM tpch.tiny.nation LIMIT 5"
