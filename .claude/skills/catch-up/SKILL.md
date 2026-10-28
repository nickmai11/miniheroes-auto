---
name: catch-up
description: Mini Heroes: Magic Throne catch-up run - Match, Storm, Canyon, Fishing, Divine Weapon, Patrol, Tribe request/assist, free Common Recruitment, event red dots, Daily Mission claims + chests on every account, via ADB.
---

# Mini Heroes catch-up

Use when Nick asks for "catch up" / "top-up" on Mini Heroes. Default: every account in `accounts/*.yaml`, unless Nick names accounts.

1. In `~/projects/chidojiro/miniheroes-auto`, read the account files (not `docs/ui-routine.md` — helpers read their sections).
2. `scripts/boot.sh <mumu index>...` — boots, **restarts** the game, clears event popups (must print "ready (stable …)").
   If the game crashes mid-run, workers relaunch it and retry the step (max 3 relaunches) — Nick, 2026-10-27.
3. **Runner first (Nick, 2026-10-28 — cost):** all accounts in ONE background Bash command, wait for its notification:
   `for a in <acct>:<serial> ...; do (D=${a#*:} OUT=/tmp/miniheroes-$(date +%F-%H)/${a%%:*} scripts/daily.py ${a%%:*} --catch-up > /tmp/miniheroes-$(date +%F-%H)/${a%%:*}.log 2>&1) & done; wait`
   It does steps 1, 2 (minus Rewards), 4–8, 10, 11 below and ends with `LEFT FOR HELPER:` (Storm Rewards, Match claims,
   Canyon, Events + any FAIL with `v_<step>.png`). Then ONE `mh-helper` per account for only those, prompt below
   trimmed to them. Steps (the spec the runner follows; see `docs/ui-routine.md`):
   **Red dots only (Nick, 2026-10-27):** for claims (events, Tribe Clash Pack, Daily Mission, rewards icons) open/tap
   only what shows a red dot — no red dot = nothing to collect, don't open it to check.
   1. Match (exhaust free tickets): `scripts/match.py <account>` from the Arena screen, then the claims by hand
   2. Storm Battlefield (skip if its season is closed: Mon 05:00-17:00): run `scripts/storm.py` from the arena
      screen — it sets the full lineup first and resets to 1 hero after (ui-routine Storm steps 2–4, 6); report its output.
      Then **Rewards** (left side) if it has a red dot — storm.py does NOT do this (Storm step 5)
   3. Canyon Clash (skip if its season is closed: Mon 06:00-17:00): **take a new spot even if one is already held**
   4. Fishing: only start Auto (fishing) and claim completed order rewards — no order refreshing, no Benefit
   5. Divine Weapon: Excelsior Veins via `scripts/veins.py` (stops at 0 pickaxes), then Forge: fill every free slot (N/M) while crystals ≥ cost, even if a forge is already running (Nick, 2026-10-28) — no Benefit
   6. Patrol: Claim All only (`scripts/patrol.py <account> --claim-only`) — no Speed Patrol. Claim All often gives Match tickets → re-run Match right after
   7. Tribe chat Request + Assist (Tribe section, step 4 only — by hand; `tribe.py` also signs in / fights the Trial)
   8. Common Recruitment (Recruit section, step 2 only): draw every **Free** chance available; if it's on
      cooldown or out of chances, skip — don't wait, never pay
   9. Events red dots (Daily run order step 16): open event banners with a red dot, claim only free
      Claim/Free rewards; never a $ or gem price. **Collect only** (Nick, 2026-10-28): never Open All / draw / spin /
      use any event token, ticket or coin, even free ones (7777 Draws: daily Claim only, no Open All). Never Tribe
      Clash's Treasures or "Enter" (Nick, 2026-10-27); its free Pack claim is fine
   10. Daily Mission (last), only if its menu icon has a red dot: on the **Daily and Weekly** tabs (each with a red dot)
       tap ONE yellow **Claim** row (claims all rows) and ONE reachable chest (claims all reachable chests) — never scroll,
       top row not claimable = done (Nick, 2026-10-27/28); report chests still locked + activity points
   11. Fishing orders again (very end): claim any order reward that completed during the run (Auto fishing
       keeps filling them) — claim only, no refresh, don't touch Auto (Nick, 2026-10-27). Also retry Common Recruitment once if its
       free draw was on cooldown earlier (~5 min) — draw if Free, else skip.
   **After all helpers finish**, one more runner pass on every account (orders keep completing during the helpers;
   Nick, 2026-10-28): `daily.py <acct> --catch-up common_recruit fishing_rewards` (same loop as above).
4. Workers don't edit the repo; afterwards add new findings to the docs and commit.
5. Report: lead with **Concerns / issues / errors** (see CLAUDE.md "Reporting"), then per account: each step
   done/skipped (and why), every paid action with its price, and which Daily Mission chests are still
   unclaimable (with the activity points shown).

## Helper prompt (use as-is; fill in <…>; add any rule Nick gives mid-run to this file too)

```
Mini Heroes catch-up leftovers on ONE account: <Name>, ADB serial <serial>, scratch dir <dir> (save screenshots there as
s1.png, s2.png…). Repo ~/projects/chidojiro/miniheroes-auto: do ONLY these steps from .claude/skills/catch-up/SKILL.md
step 3: <leftover steps + the runner's FAIL lines>, the output of
`scripts/doc.sh Match Storm Canyon Fishing Divine Patrol Tribe Recruit Events "Daily Mission"` (don't read the
whole docs/ui-routine.md) and accounts/<file>.yaml. Don't edit the repo.
Game is at the main screen; close popups with X / Cancel (never GO); tick "Do not remind me today" first if the popup has it. Today: <weekday date time> (<Storm/Canyon open?>).
Tools: D=<serial> python3 scripts/tap.py [x,y…] -w 270 -o <dir>/sN.png [--until x,y,r,g,b --timeout s]; -w 270 for
navigation (×4 = device coords), -w 540 only for small text (×2). Storm: scripts/storm.py (handles lineup). Veins: scripts/veins.py. Match: scripts/match.py <account>.
Rules: look only at decision points — chain a step's fixed taps in one tap.py call with --until on the next
screen's pixel; read a screenshot before prices, target picks, counters, a step's first tap, and after a failed check; no gems/money beyond the config; poll waits inside the command (1–2 s), never
background timers or "pausing"; game crash → relaunch (monkey -p com.and.brawlen.web …, Start 540,1508), max 3;
own loops must re-check the stop condition (counter/popup) every pass — never a fixed-count blind loop;
can't do a step after 2 tries → skip + note why. Nick may tap the screen himself.
Final answer: CONCERNS/ISSUES/ERRORS first (mis-taps, out-of-scope screens opened, wrong lineup, crashes, anything
left in a bad state), then per step done/skipped (+why), every paid action + price, Daily Mission chests still
locked + points, new findings (coords/behaviour not in the docs).
```

**Log (Nick, 2026-10-28):** `daily.py` appends everything to `logs/<account>/<game day>.log` (game day starts 12:00 local).
Append each helper's final answer to the same file (`=== helper` header) — it's the record of what each account did.

## Hard rules

- Same as the dailies: free attempts first, paid only within the account config caps.
- Look at decision points only (CLAUDE.md hard rules); unexpected screen → stop and report.
