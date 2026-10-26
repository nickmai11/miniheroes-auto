#!/bin/zsh
# Launched daily by ~/Library/LaunchAgents/com.nick.miniheroes-dailies.plist (13:00).
# Headless Claude run of the dailies for every account except Cmajor. Permissions: .claude/settings.json.
REPO=${0:A:h:h}
cd "$REPO" || exit 1
export PATH="/Users/nickm/.nvm/versions/node/v22.20.0/bin:/Users/nickm/Library/Android/sdk/platform-tools:/Library/Frameworks/Python.framework/Versions/3.10/bin:/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"
MODE=${1:-dailies}   # dailies | monday (Storm + Canyon, seasons open Mon 17:00) | extra (21:00 + 05:00 top-up)
LOG="logs/$MODE-$(date +%F).log"
if [[ $MODE == monday ]]; then
  PROMPT="Scheduled Mini Heroes Monday 17:05 run (Storm Battlefield and Canyon Clash seasons just opened). For every account in accounts/*.yaml EXCEPT Cmajor (xFaktor, Aminor, Dminor, Chien Than), RESTART the game first (force-stop + relaunch, needed after 17:00), then do ONLY these two steps from docs/ui-routine.md: (1) Storm Battlefield (full lineup first, play tickets, free video tickets, play again, then lineup to 1 top hero); (2) Canyon Clash (scan the whole map, take an empty platform first: Occupy, then Confirm the delayed Resource popup; else follow the weekday rules). Start stopped MuMu instances, get fresh ADB ports, 1080x1920 display, launch the game. One subagent per instance, own ADB serial and scratch dir under /tmp/miniheroes-\$(date +%F)/<account>, using scripts/tap.py. Workers don't edit the repo; afterwards add new findings to the docs and commit. Report per account: Storm matches played/rank, Canyon spot taken (type, rate) and attempts used."
elif [[ $MODE == extra ]]; then
  PROMPT="Scheduled Mini Heroes top-up run (21:00 / 05:00). For every account in accounts/*.yaml EXCEPT Cmajor (xFaktor, Aminor, Dminor, Chien Than), RESTART the game first (force-stop + relaunch), then do ONLY these steps from docs/ui-routine.md, in this order: (1) Match (exhaust free tickets); (2) Storm Battlefield (skip if its season is closed: Mon 05:00-17:00); (3) Canyon Clash (skip if its season is closed: Mon 06:00-17:00); (4) Fishing (orders, Benefit if red dot, Auto; also claim completed order rewards); (5) Divine Weapon (Benefit, Excelsior Veins, Forge); (6) Patrol (Speed Patrol + Claim All). Same rules as the dailies: free attempts first, paid only within the account config caps. Start stopped MuMu instances, get fresh ADB ports, 1080x1920 display, launch the game. One subagent per instance, own ADB serial and scratch dir under /tmp/miniheroes-\$(date +%F-%H)/<account>, using scripts/tap.py and scripts/storm.py. Workers don't edit the repo; afterwards add new findings to the docs and commit. Report per account: each step done/skipped (and why) and every paid action with its price."
else
  PROMPT="Scheduled Mini Heroes dailies. Run the full dailies for every account in accounts/*.yaml EXCEPT Cmajor (xFaktor, Aminor, Dminor, Chien Than), following .claude/skills/miniheroes-dailies/SKILL.md and the Daily run order in docs/ui-routine.md (Pet Arena first, Mon-Wed only; Canyon Clash skipped on Mondays). Start any stopped MuMu instances with mumu-cli, get fresh ADB ports, set 600x1080 instances to 1080x1920 (wm size/density) and launch the game. Run accounts in parallel: one subagent per instance with its own ADB serial and scratch dir under /tmp/miniheroes-\$(date +%F)/<account>, using scripts/tap.py, scripts/grocery.py, the saved tribe roster and each account's config. Workers don't edit the repo; when all finish, add new coords/gotchas to the docs and commit. End with a per-account report: missions done/skipped and every paid action with its price."
fi
{
  echo "=== $(date) start"
  claude -p "$PROMPT" --output-format text
  echo "=== $(date) exit $?"
  if [[ $MODE == extra ]]; then   # close the instances this run used (every account except Cmajor)
    MUMU="/Applications/MuMuPlayer Pro.app/Contents/MacOS/mumu-cli"
    IDX=$("$MUMU" info all | python3 -c '
import json, re, sys, glob
names = {re.search(r"mumu_instance:\s*(.+?)\s*(#|$)", open(f).read(), re.M).group(1) for f in glob.glob("accounts/*.yaml") if "_template" not in f} - {"Cmajor"}
print(",".join(str(r["index"]) for r in json.load(sys.stdin)["return"]["results"] if r["name"] in names and r["state"] == "running"))')
    [[ -n $IDX ]] && "$MUMU" close "$IDX" && echo "=== closed MuMu instances $IDX"
  fi
} >> "$LOG" 2>&1
osascript -e "display notification \"Done — see $LOG\" with title \"Mini Heroes $MODE\"" 2>/dev/null
