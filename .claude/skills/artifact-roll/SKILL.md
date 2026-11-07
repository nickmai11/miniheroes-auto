---
name: artifact-roll
description: Mini Heroes: Magic Throne Artifact rolls - Auto Wish on Recruit → Artifact, cancel and restart every 20 s, stop when a new Mythic artifact shows, on Nick's MuMuPlayer accounts via ADB (scripts/artifact_roll.py).
---

# Artifact rolls

Use when Nick says "artifact roll(s)" / "roll artifacts" on one or more accounts. Spends **stars** (200–250 per
wish), never gems.

1. Accounts: the ones named. Not running → `scripts/boot.sh <idx>...`. Running → `home()` (CLAUDE.md), then
   Recruit → Artifact tab: `D=<serial> scripts/tap.py 96,1810 618,1840 --until-text '^Wish$' -w 270`.
   Read the screenshot: **Auto** (bottom right) ticked green, Wish price 200/250 with the star icon. Not ticked →
   tap `(882,1658)` once and re-check.
2. Run, no LLM: `D=<serial> scripts/artifact_roll.py [max_cycles]` (own cwd per account when parallel).
   Each cycle: Wish → Auto Wish box → after 20 s tap outside the box `(540,1092)` → "Congratulations" summary →
   close → Wish again; reaching the Brilliance tier restarts at once. It wishes only at 200/250 stars or 1500 at Holy Light (stops at 280 = gems), retries an ignored cancel tap once, and stops if the gem count drops.
3. A new artifact pops "Congratulations / <name> / Confirm". **Red name = Mythic** → stop. Any other colour (orange =
   Legendary) → the script taps Confirm and goes on. Exit 1 with `found` = red name, box gone with no Confirm, or "Mythic" text → read
   `v_artifact_roll.png`: a new Mythic artifact → report it and leave the screen as is. **Stop only on a new Mythic** (Nick, 2026-11-07): Holy Light
   reached → Wish it (1500 stars) and re-run; other screen (box still open, summary) → clear it and re-run. Stars out → report. Other exit 1 → read the screenshot + message, report.
4. Report per account: cycles run, why it stopped, the artifact shown.

Untested: the live Mythic display (red name check) and the screen after a Legendary's Confirm.
