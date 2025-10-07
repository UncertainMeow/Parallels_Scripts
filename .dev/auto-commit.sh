#!/usr/bin/env bash
#
# auto-commit.sh - Automatically commit and push changes every 30 minutes
#

set -euo pipefail

REPO_DIR="/Users/kellen/_kellen/code/Parallels_Scripts"
LOG_FILE="$REPO_DIR/.dev/auto-commit.log"

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Change to repo directory
cd "$REPO_DIR"

# Check if there are changes
if [[ -z $(git status -s) ]]; then
    log "No changes to commit"
    exit 0
fi

# Stage all changes
git add -A

# Create commit with changes summary
CHANGES=$(git status -s | wc -l | tr -d ' ')
FILES_CHANGED=$(git status -s | awk '{print $2}' | head -5 | tr '\n' ', ' | sed 's/,$//')

COMMIT_MSG="Auto-commit: $CHANGES file(s) changed

Modified: $FILES_CHANGED

Generated: $(date '+%Y-%m-%d %H:%M:%S')
"

git commit -m "$COMMIT_MSG"

# Push to GitHub
git push origin main

log "✅ Committed and pushed $CHANGES changes"
log "   Files: $FILES_CHANGED"
