#!/bin/zsh
# Launched daily by ~/Library/LaunchAgents/com.nick.miniheroes-dailies.plist (13:00).
# Headless Claude run of the dailies for every account except Cmajor. Permissions: .claude/settings.json.
REPO=${0:A:h:h}
cd "$REPO" || exit 1
export PATH="/Users/nickm/.nvm/versions/node/v22.20.0/bin:/Users/nickm/Library/Android/sdk/platform-tools:/Library/Frameworks/Python.framework/Versions/3.10/bin:/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"
LOG="logs/dailies-$(date +%F).log"
{
  echo "=== $(date) start"
  claude -p "Scheduled Mini Heroes dailies. Run the full dailies for every account in accounts/*.yaml EXCEPT Cmajor (xFaktor, Aminor, Dminor, Chien Than), following .claude/skills/miniheroes-dailies/SKILL.md and the Daily run order in docs/ui-routine.md (Pet Arena first, Mon-Wed only). Start any stopped MuMu instances with mumu-cli, get fresh ADB ports, set 600x1080 instances to 1080x1920 (wm size/density) and launch the game. Run accounts in parallel: one subagent per instance with its own ADB serial and scratch dir under /tmp/miniheroes-\$(date +%F)/<account>, using scripts/tap.py, scripts/grocery.py, the saved tribe roster and each account's config. Workers don't edit the repo; when all finish, add new coords/gotchas to the docs and commit. End with a per-account report: missions done/skipped and every paid action with its price." --output-format text
  echo "=== $(date) exit $?"
} >> "$LOG" 2>&1
osascript -e "display notification \"Done — see $LOG\" with title \"Mini Heroes dailies\"" 2>/dev/null
