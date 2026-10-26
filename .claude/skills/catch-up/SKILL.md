---
name: catch-up
description: Mini Heroes: Magic Throne catch-up run - Match, Storm, Canyon, Fishing, Divine Weapon, Patrol, Tribe request/assist, free Common Recruitment, event red dots on every account (except Cmajor unless asked), via ADB.
---

# Mini Heroes catch-up

Use when Nick asks for "catch up" / "top-up" on Mini Heroes. Default: every account in `accounts/*.yaml`
EXCEPT Cmajor (xFaktor, Aminor, Dminor, Chien Than), unless Nick names accounts.

1. In `~/projects/chidojiro/miniheroes-auto`, read `CLAUDE.md`, `docs/ui-routine.md` and the account files.
2. Start stopped MuMu instances, get fresh ADB ports, 1080x1920 display, **restart** the game (force-stop + relaunch).
3. One subagent per instance, own ADB serial and scratch dir under `/tmp/miniheroes-$(date +%F-%H)/<account>`,
   using `scripts/tap.py` and `scripts/storm.py`. Steps, in this order, ONLY these (see `docs/ui-routine.md`):
   1. Match (exhaust free tickets)
   2. Storm Battlefield (skip if its season is closed: Mon 05:00-17:00)
   3. Canyon Clash (skip if its season is closed: Mon 06:00-17:00)
   4. Fishing: only start Auto (fishing) and claim completed order rewards — no order refreshing, no Benefit
   5. Divine Weapon: Excelsior Veins until pickaxes = 0, then Forge if available (no forge running, crystals ≥ cost) — no Benefit
   6. Patrol: Claim All only — no Speed Patrol
   7. Tribe chat Request + Assist (Tribe section, step 4 only)
   8. Common Recruitment (Recruit section, step 2 only): draw every **Free** chance available; if it's on
      cooldown or out of chances, skip — don't wait, never pay
   9. Events red dots (Daily run order step 16): open event banners with a red dot, claim only free
      Claim/Free rewards; never a $ or gem price, never draw/spin with paid currency
4. Workers don't edit the repo; afterwards add new findings to the docs and commit.
5. Close the MuMu instances used: `"/Applications/MuMuPlayer Pro.app/Contents/MacOS/mumu-cli" close <idx,...>`.
6. Report per account: each step done/skipped (and why) and every paid action with its price.

## Hard rules

- Same as the dailies: free attempts first, paid only within the account config caps.
- Screenshot before every tap; unexpected screen → stop and report.
