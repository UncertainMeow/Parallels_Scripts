#!/usr/bin/env bash
#
# setup-auto-commit.sh - Configure automatic commits every 30 minutes
#

set -euo pipefail

REPO_DIR="/Users/kellen/_kellen/code/Parallels_Scripts"
PLIST_NAME="com.uncertainmeow.parallels.autocommit"
PLIST_FILE="$HOME/Library/LaunchAgents/${PLIST_NAME}.plist"

echo "🔧 Setting up automatic commits (every 30 minutes)..."

# Create LaunchAgents directory if it doesn't exist
mkdir -p "$HOME/Library/LaunchAgents"

# Create the plist file
cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${PLIST_NAME}</string>

    <key>ProgramArguments</key>
    <array>
        <string>${REPO_DIR}/.dev/auto-commit.sh</string>
    </array>

    <key>StartInterval</key>
    <integer>1800</integer>

    <key>StandardOutPath</key>
    <string>${REPO_DIR}/.dev/auto-commit.log</string>

    <key>StandardErrorPath</key>
    <string>${REPO_DIR}/.dev/auto-commit-error.log</string>

    <key>WorkingDirectory</key>
    <string>${REPO_DIR}</string>

    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
EOF

# Load the launch agent
launchctl unload "$PLIST_FILE" 2>/dev/null || true
launchctl load "$PLIST_FILE"

echo ""
echo "✅ Auto-commit configured!"
echo ""
echo "Details:"
echo "  Frequency: Every 30 minutes"
echo "  Log file: ${REPO_DIR}/.dev/auto-commit.log"
echo "  Error log: ${REPO_DIR}/.dev/auto-commit-error.log"
echo ""
echo "Commands:"
echo "  Stop:    launchctl unload $PLIST_FILE"
echo "  Start:   launchctl load $PLIST_FILE"
echo "  Status:  launchctl list | grep parallels"
echo ""
echo "Test it now:"
echo "  ${REPO_DIR}/.dev/auto-commit.sh"
echo ""
