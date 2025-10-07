#!/usr/bin/env bash
#
# setup-github.sh - Push to GitHub for the first time
#

set -euo pipefail

echo "🚀 Setting up GitHub repository..."
echo ""
echo "MANUAL STEPS REQUIRED:"
echo "1. Go to: https://github.com/new"
echo "2. Repository name: Parallels_Scripts"
echo "3. Description: Parallels Desktop automation framework for macOS"
echo "4. Make it Public (or Private if you prefer)"
echo "5. Do NOT initialize with README (we already have one)"
echo "6. Click 'Create repository'"
echo ""
read -p "Press Enter when you've created the repo on GitHub..."

# Get username
read -p "Enter your GitHub username (default: UncertainMeow): " GITHUB_USER
GITHUB_USER=${GITHUB_USER:-UncertainMeow}

echo ""
echo "Adding remote and pushing..."

# Add remote
git remote add origin "https://github.com/${GITHUB_USER}/Parallels_Scripts.git"

# Push
git push -u origin main

echo ""
echo "✅ Repository pushed to GitHub!"
echo "🔗 https://github.com/${GITHUB_USER}/Parallels_Scripts"
echo ""
echo "Next: Setting up auto-commit script..."
