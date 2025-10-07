# 🚀 First Time Setup - GitHub & Auto-Commit

Follow these steps **once** to get everything configured.

## Step 1: Push to GitHub (Do This Now!)

```bash
./setup-github.sh
```

This will:
1. Prompt you to create the repo on GitHub (https://github.com/new)
2. Add the remote
3. Push the initial commit

**Repository Details:**
- Name: `Parallels_Scripts`
- Description: `Parallels Desktop automation framework for macOS`
- Visibility: Public (or Private if you prefer)

## Step 2: Configure Auto-Commit (After First Push)

```bash
./.dev/setup-auto-commit.sh
```

This will:
- Create a LaunchAgent that runs every 30 minutes
- Auto-commit any changes you or Claude make
- Push to GitHub automatically
- Log all activity to `.dev/auto-commit.log`

## Step 3: Verify It's Working

```bash
# Test the auto-commit manually
./.dev/auto-commit.sh

# Check the logs
tail -f .dev/auto-commit.log

# Check LaunchAgent status
launchctl list | grep parallels
```

## What Happens Next

1. **You create the GitHub repo** (Step 1 above)
2. **You run the setup scripts** (Steps 1-2 above)
3. **Claude takes over** and will:
   - Build production-grade Excel automation
   - Create Packer templates
   - Develop CI/CD scripts
   - Add error handling and logging
   - Write comprehensive tests
   - Iterate and improve autonomously
4. **Every 30 minutes**: Changes auto-commit to GitHub
5. **You can monitor**: Check commits on GitHub, read the logs

## Managing Auto-Commit

```bash
# Stop auto-commits
launchctl unload ~/Library/LaunchAgents/com.uncertainmeow.parallels.autocommit.plist

# Start auto-commits
launchctl load ~/Library/LaunchAgents/com.uncertainmeow.parallels.autocommit.plist

# View recent commits
git log --oneline --graph --all -20

# Rollback if needed
git reset --hard <commit-hash>
git push -f origin main
```

## Ready?

Run this now:
```bash
./setup-github.sh
```

Then after it's pushed:
```bash
./.dev/setup-auto-commit.sh
```

Then let Claude know, and he'll start building! 🚀
