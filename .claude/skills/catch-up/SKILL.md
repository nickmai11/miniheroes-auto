---
name: catch-up
description: Mini Heroes: Magic Throne catch-up run - Match, Storm, Canyon, Fishing, Divine Weapon, Patrol, Tribe request/assist, free Common Recruitment, event red dots, Daily Mission claims + chests on every account, via ADB.
---

# Mini Heroes catch-up

> **UNTESTED (2026-10-27):** `scripts/boot.sh` Start re-tap (re-taps only while Start is visible; the first version
> hit an event popup's GO and opened a web page). Check the next boot, then delete this note.
> (`scripts/storm.py` lineup handling ran clean on all 9 accounts 2026-10-27 22:10 — reset to 1 hero verified.)

Use when Nick asks for "catch up" / "top-up" on Mini Heroes. Default: every account in `accounts/*.yaml`, unless Nick names accounts.

1. In `~/projects/chidojiro/miniheroes-auto`, read `CLAUDE.md`, `docs/ui-routine.md` and the account files.
2. Start stopped MuMu instances, get fresh ADB ports, 1080x1920 display, **restart** the game (force-stop + relaunch).
   If the game crashes mid-run, workers relaunch it and retry the step (max 3 relaunches) — Nick, 2026-10-27.
3. One subagent per instance (`model: "sonnet"`; use `opus` for a step not yet mapped in the docs), own ADB serial and scratch dir under `/tmp/miniheroes-$(date +%F-%H)/<account>`,
   using `scripts/tap.py` and `scripts/storm.py`. Steps, in this order, ONLY these (see `docs/ui-routine.md`):
   **Red dots only (Nick, 2026-10-27):** for claims (events, Tribe Clash Pack, Daily Mission, rewards icons) open/tap
   only what shows a red dot — no red dot = nothing to collect, don't open it to check.
   1. Match (exhaust free tickets)
   2. Storm Battlefield (skip if its season is closed: Mon 05:00-17:00): run `scripts/storm.py` from the arena
      screen — it sets the full lineup first and resets to 1 hero after (ui-routine Storm steps 2–6); report its output
   3. Canyon Clash (skip if its season is closed: Mon 06:00-17:00): **take a new spot even if one is already held**
   4. Fishing: only start Auto (fishing) and claim completed order rewards — no order refreshing, no Benefit
   5. Divine Weapon: Excelsior Veins until pickaxes = 0, then Forge if available (no forge running, crystals ≥ cost) — no Benefit
   6. Patrol: Claim All only — no Speed Patrol. Claim All often gives Match tickets → re-run Match right after
   7. Tribe chat Request + Assist (Tribe section, step 4 only)
   8. Common Recruitment (Recruit section, step 2 only): draw every **Free** chance available; if it's on
      cooldown or out of chances, skip — don't wait, never pay
   9. Events red dots (Daily run order step 16): open event banners with a red dot, claim only free
      Claim/Free rewards; never a $ or gem price, never draw/spin with paid currency. Never Tribe
      Clash's Treasures or "Enter" (Nick, 2026-10-27); its free Pack claim is fine
   10. Daily Mission (last): tap ONE yellow **Claim** row (claims all rows) and ONE reachable chest (claims all
       reachable chests) — no re-checking the rest, never scroll the list (claimable rows sort to the top) (Nick, 2026-10-27). Before that rule: Claim every yellow row, then every
       reachable Daily Activity Levels chest (40/80/120/160); report chests still locked + activity points
   11. Fishing orders again (very end): claim any order reward that completed during the run (Auto fishing
       keeps filling them) — claim only, no refresh (Nick, 2026-10-27). Also retry Common Recruitment once if its
       free draw was on cooldown earlier (~5 min) — draw if Free, else skip.
4. Workers don't edit the repo; afterwards add new findings to the docs and commit.
5. Close the MuMu instances used: `"/Applications/MuMuPlayer Pro.app/Contents/MacOS/mumu-cli" close <idx,...>`.
6. Report: lead with **Concerns / issues / errors** (see CLAUDE.md "Reporting"), then per account: each step
   done/skipped (and why), every paid action with its price, and which Daily Mission chests are still
   unclaimable (with the activity points shown).

## Helper prompt (use as-is; fill in <…>; add any rule Nick gives mid-run to this file too)

```
Mini Heroes catch-up on ONE account: <Name>, ADB serial <serial>, scratch dir <dir> (save screenshots there as
s1.png, s2.png… — the coordinator watches it). Repo ~/projects/chidojiro/miniheroes-auto: read CLAUDE.md,
.claude/skills/catch-up/SKILL.md (do steps 3.1–3.11 there, in order, ONLY those), docs/ui-routine.md (each step's
section + "ADB alternative" + gotchas) and accounts/<file>.yaml. Don't edit the repo.
Game is at the main screen; close popups with X / Cancel (never GO). Today: <weekday date time> (<Storm/Canyon open?>).
Tools: D=<serial> python3 scripts/tap.py [x,y…] -w 270 -o <dir>/sN.png [--until x,y,r,g,b --timeout s]; -w 270 for
navigation (×4 = device coords), -w 540 only for small text (×2). Storm: scripts/storm.py (handles lineup).
Rules: screenshot before every tap; no gems/money beyond the config; poll waits inside the command (1–2 s), never
background timers or "pausing"; game crash → relaunch (monkey -p com.and.brawlen.web …, Start 540,1508), max 3;
can't do a step after 2 tries → skip + note why. Nick may tap the screen himself — re-screenshot before each tap.
Final answer: CONCERNS/ISSUES/ERRORS first (mis-taps, out-of-scope screens opened, wrong lineup, crashes, anything
left in a bad state), then per step done/skipped (+why), every paid action + price, Daily Mission chests still
locked + points, new findings (coords/behaviour not in the docs).
```

## Hard rules

- Same as the dailies: free attempts first, paid only within the account config caps.
- Screenshot before every tap; unexpected screen → stop and report.
