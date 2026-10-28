---
name: miniheroes-dailies
description: Run Mini Heroes: Magic Throne daily missions (Land of Trials, Match, Shop/Play Pass freebies, Tower of the Throne, Secret Sanctuary, Gate of Darkness, Beast Realm, free Recruit summons, hero upgrade, Tribe, Fishing, Divine Weapon, Adventure stage, Patrol, rune synthesis, Grocery) on Nick's MuMuPlayer accounts via computer use (or ADB), following per-account configs in the miniheroes-auto repo.
---

# Mini Heroes dailies

Use when Nick asks to run Mini Heroes dailies / a specific mission (e.g. "sweep Land of Trials on Cmajor", "do dailies for all accounts").

The source of truth is the repo on Nick's Mac: `~/projects/chidojiro/miniheroes-auto`. This skill only says how to get there and the rules that never change; mission details, tap coordinates and account configs live in the repo.

## Steps

1. **Get the repo.** Request folder access to `~/projects/chidojiro` (or `~/projects/chidojiro/miniheroes-auto`) on Nick's computer. Read, in order:
   - `CLAUDE.md`
   - Only the `docs/ui-routine.md` sections for the missions you'll run: `scripts/doc.sh <section>...`
     (coordinator: just "Daily run order"; each helper: its missions)
   - `accounts/<account>.yaml` for each requested account (all `enabled: true` accounts if he says "all")
   - `docs/setup.md` only if the emulator/network looks wrong
2. **Get app access (minimum set).** Via computer use: resolve and request access to `MuMuPlayer` and `MuMu Android Device` only. Work in background mode with the `computer_app_*` tools. Don't request full-screen control or other apps unless Nick agrees. If computer-use tools aren't available in the session, use ADB instead (Nick approved this) — see "ADB alternative" in `docs/ui-routine.md`.
3. **Run each account** in its MuMu instance: start the instance if needed, open the game, then run the missions in the **Daily run order** at the top of `docs/ui-routine.md` (Pet Arena [Mon–Wed only] → Storm Battlefield → Match → Fishing → Patrol → Shop → Play Pass → Adventure → Recruit → Hero → Tribe → Divine Weapon → Stage → Patrol claim → Rune → Match → Grocery → Events red dots → Fishing order rewards), skipping any not in the account config.
4. **Report** per account: each mission done/skipped (and why) and every paid action with its price. Don't track gem/resource balances — they change constantly.

**Speed:** tap with `scripts/tap.py` (waits for the screen to settle, ~1 s/tap, no fixed sleeps); chain known taps and only screenshot-check at decision points.

**Cost: one fresh helper per PHASE, not per account (Nick, 2026-10-28 — urgent).** A single helper for the whole
run hit ~850 turns × ~140k avg context (~112M cache-read per account, ~12% weekly for 8 accounts): every turn re-reads
all earlier screenshots. Per account, run these phases **one after another**, each a NEW `mh-helper` (same serial
+ scratch dir, prompt lists only that phase's steps + doc sections); spawn the next phase when the previous one's
notification arrives. Each starts at ~12k context instead of growing to 220k → ~4x cheaper.
- **A:** Pet Arena, Storm, Match, Fishing, Patrol (steps 0–3)
- **B:** Shop, Play Pass, Adventure (steps 4–6)
- **C:** Recruit, Hero, Tribe + Canyon, Divine Weapon (steps 7–10)
- **D:** Adventure stage, Patrol claim, Rune, Match, Grocery (steps 11–15)
- **E:** Events, Fishing order rewards, Daily Mission (steps 16–17 + Daily Mission)
Scripts first: Match = `scripts/match.py <account>`, Land of Trials = `scripts/trials.py <account>`, Patrol, Hero,
Tribe, Tower, Beast = `patrol.py` / `hero.py` / `tribe.py` / `adventure.py`, Storm/Veins/
Grocery/Fishing orders = their scripts (see ui-routine "Speed"); the helper only navigates to the start screen and handles
exit 1. Helper final answers: ≤15 lines (concerns, done/skipped, paid + price) — the coordinator reads them all.

**Several accounts:** run them in parallel, one subagent per instance (`model: "sonnet"`; use `opus` for a step not yet mapped in the docs; own ADB serial + own scratch dir, no repo edits by workers). Set each instance's display to 1080×1920 first (`adb shell wm size 1080x1920 && adb shell wm density 480`, then restart the game) so the documented coords apply.
5. **Keep the repo current.** If you learn something new (new coordinates, a popup, a new mission mapped), update the relevant doc and commit it.

## Missions

Each mission's rules, coords and gotchas are its section in `docs/ui-routine.md` — helpers read them with
`scripts/doc.sh <mission>...` (only the missions in their account config). Don't paste mission details into helper
prompts; the doc is the single source.

## Language

The game UI is **English or Vietnamese** depending on the account (`account.language`; check the first
screenshot if unset). Same layout and coords. Recognise buttons by colour/position and counters, not
English text. Common Vietnamese: Miễn phí = Free, Xác nhận = Confirm, Nhận = Claim, Hủy = Cancel.
A loop or "nothing happens" usually means a text mismatch — check the language first.

## Hard rules

- Configured counts are totals per day **including** free attempts. Use free first; pay with gems only up to the configured total.
- Never pay more than `max_gem_price_per_sweep` (from the account config) for one sweep — stop that mission and report instead. Paid prices escalate within a dungeon each day (80, 160, 240…), so re-read the price on the confirm popup every time.
- Read the attempt counter on screen before and after every sweep; never chain taps blindly. Taps during popup animations are ignored, so screenshot first.
- On-screen counters are the source of truth for what was already done today.
- Touch nothing outside the configured missions (no shop, purchases, settings, events).
- If the screen is in an unexpected state, stop and report what you see.
- **Can't ensure quality → skip it** (Nick): if a step can't be done with confidence (screen unreadable, a tap doesn't
  do what's expected after 2 tries, unclear state), close popups, skip that step, report it as skipped + why. Never loop or guess.
- If a "Match attempts full" popup appears mid-dailies: Confirm, use all Match tickets (Match routine, tribe rules), then resume where you left off.
- Battles: never wait blind for minutes — poll and enforce the time cap given for the mode.
- The back arrow `(92,1810)` overlaps the main screen's Recruit button: screenshot after every back tap.
- If a mission isn't documented in `docs/ui-routine.md` yet, don't improvise it on a gem-spending path — map it with Nick first, then document it.
