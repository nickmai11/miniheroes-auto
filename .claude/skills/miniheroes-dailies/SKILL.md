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
   - `docs/ui-routine.md` (and the section for each mission you'll run)
   - `accounts/<account>.yaml` for each requested account (all `enabled: true` accounts if he says "all")
   - `docs/setup.md` only if the emulator/network looks wrong
2. **Get app access (minimum set).** Via computer use: resolve and request access to `MuMuPlayer` and `MuMu Android Device` only. Work in background mode with the `computer_app_*` tools. Don't request full-screen control or other apps unless Nick agrees. If computer-use tools aren't available in the session, use ADB instead (Nick approved this) — see "ADB alternative" in `docs/ui-routine.md`.
3. **Run each account** in its MuMu instance: start the instance if needed, open the game, then run the missions in the **Daily run order** at the top of `docs/ui-routine.md` (Pet Arena [Mon–Wed only] → Storm Battlefield → Match → Fishing → Patrol → Shop → Play Pass → Adventure → Recruit → Hero → Tribe → Divine Weapon → Stage → Patrol claim → Rune → Match → Grocery → Events red dots → Fishing order rewards), skipping any not in the account config.
4. **Report** per account: each mission done/skipped (and why) and every paid action with its price. Don't track gem/resource balances — they change constantly.

**Speed:** tap with `scripts/tap.py` (waits for the screen to settle, ~1 s/tap, no fixed sleeps); chain known taps and only screenshot-check at decision points.

**Several accounts:** run them in parallel, one subagent per instance (`model: "sonnet"`; use `opus` for a step not yet mapped in the docs; own ADB serial + own scratch dir, no repo edits by workers). Set each instance's display to 1080×1920 first (`adb shell wm size 1080x1920 && adb shell wm density 480`, then restart the game) so the documented coords apply.
5. **Keep the repo current.** If you learn something new (new coordinates, a popup, a new mission mapped), update the relevant doc and commit it.

## Missions (details in `docs/ui-routine.md`)

| Mission | What to do |
|---|---|
| Land of Trials | Sweep per config counts (free first, paid ≤ price cap) |
| Match (Arena) | Use the saved tribe roster (`accounts/tribe_<name>.txt`); crash the topmost attackable non-tribe opponent (last row = bot, always attackable) until tickets = 0 (see `/miniheroes-match`) |
| Shop freebies | Value Pack Free Benefits Claim + Hero Pack "Select Hero" (+20 gems) — red dots only |
| Play Pass | Weekly Card day tile + Lifetime Card Claim Reward |
| Tower of the Throne | 3 challenges with the pre-selected lineup (count from config) |
| Adventure stage | Skull bubble next to the hero → Start, 1 run |
| Secret Sanctuary | Sweep if offered; else climb floors 1→10 (Crash/Battle), pick bonus effects per the preferred list then rarity (see ui-routine) |
| Recruit | Free only: 2× Common, 1× Ancestor (then Confirm, never Recruit 1), 1× Artifact with Auto **off** |
| Hero upgrade | Bone Archer (end of hero strip): Level Up ×1, 1st gear Enhance ×1 — never the ↑ quick-level buttons |
| Tribe | Sign-in reward, 1× Tribe Trial (preset lineup), Chat → Request (if off cooldown) + Assist; never send chat messages |
| Fishing | Refresh daily orders until all ≥ `min_order_diamonds` (buy ticket pack 50 gems when out), Benefit only if red dot, start Auto. Order rewards only at the very end of the run |
| Divine Weapon | Benefit Claim Reward, then Excelsior Veins One-Click Mining until pickaxes = 0 (no `+`, no dynamite/drill), then, if no forge is in progress, Forge until all slots (7/8/13 per account) are used or crystals run out |
| Patrol | **Exhaust Match tickets first.** Bag on main screen → Speed Patrol repeatedly until the price shows **100 gems** (don't buy that one), then Claim All |
| Rune synthesis | ☰ → Backpack → Rune → unlocked red rune → Synthesize → Quick Equip → Synthesize (×1) |
| Grocery | ☰ → Grocery → Daily Specials: claim any top-row chest showing Free; wait out cooldowns; repeat until all 4 Sold Out; then buy the config's `grocery_buy` tiles (shop currency only, once each) |
| Events | Top-right event banners (they change): open any with a red dot, claim only free red-dot rewards incl. bottom tabs; never $/gem |
| Pet Arena | **First step; Mon/Tue/Wed only.** 1st event banner → Pet Arena → Join → Auto Deploy per `missions.pet_arena` (now: Stamina order High to Low, 4 sprites, auto-stop ✓) → Start |
| Canyon Clash (Tribe) | **Take a new spot every run, even if one is already held.** Silver spots: only the first 10 from the top. Season Mon 17:00 → next Mon 06:00: **skip on Mondays in the regular run** (`/catch-up` after 17:00). Mon–Fri: purple 9/m spot, prefer empty, else attack a non-tribe (purple name) holder. Sat–Sun: free Glory/Gold only (no attacks for them), else purple/silver — free first, else attack a non-tribemate |
| Storm Battlefield | Season Mon 17:00 → next Mon 05:00: **skip on Mondays in the regular run** (`/catch-up` after 17:00). After Pet Arena. Monday ≥17:00 with game running since before: restart game first. 2nd event card (wait for it to rotate to Storm) → **always** Lineup → Quick Deploy (top 5) → Save first (last run left 1 hero) → `scripts/storm.py` (plays to 0, taps the left green free-ticket button (Free / Miễn phí / Claim + video ad) until grey, plays them, stops; never 30-gem Redeem; don't reopen + or re-run it) → Rewards: claim red-dot rank rewards → Lineup: quick-remove, only top hero, Save |
| Beast Realm | Adventure → Beast Realm → Challenge (keep lineup) → Start, **1 challenge only**, never pay |
| Gate of Darkness | Run once (Confirm wave, never Restart; cap 1m30s, then Pause + quit), then Sweep the remaining chance |

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
