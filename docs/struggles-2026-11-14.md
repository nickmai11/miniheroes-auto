# Struggles — catch-up 06:31 + climb stage (game day 2026-11-13, Saturday)

Source: `/tmp/miniheroes-2026-11-14-06/*.log`, `logs/{kratos,boudior,tiger}/2026-11-13.log` `[climb_stage]` lines. Status: ✅ fixed · 🧪 fixed, waiting for a live test (`docs/untested.md`) · ❌ open · ❓ needs Nick. Last updated: 2026-11-14.

| # | Task | What went wrong | Status |
| --- | --- | --- | --- |
| 1 | climb_stage swap cap | `swaps` was in memory per call and keyed by stage only → cap never hit across 8-min calls; Boudior swapped 4x on 4-15 | ✅ `/tmp/climb_stage_swaps.json`, key `<account> <stage>`; fired live (Boudior exit 2 at 4-15) |
| 2 | climb_stage swap (Kr) | swap at 6-26 died after the fresh setup: `TIMEOUT waiting for 'Start'` after tab tap 540,1088; yaml not rewritten, tab state unknown → Kratos left on setup for Nick | ❌ |
| 3 | tribe_chat (Dino, Dm) | `NOT SENT (cooldown 05:59:59: sent < 6 h ago)` — a timer that fresh = the request just went out; the label is wrong (also feeds a MANUAL in daily.py) | ❌ treat a timer ≥ 05:59:00 as sent |
| 4 | tribe_chat (Kratos) | `NOT SENT (no cooldown timer after 2 taps; rows 2/4, 6/8)` — Request grey not checked by screenshot (untested.md row 2026-11-13) | ❓ |
| 5 | boot.sh (Kong, Kratos) | no "ready" line printed for 2 of 11 instances; both were fine (stabilize.py with NAME: right account, 0 popups) | ❌ |

## Dailies 13:40 (game day 2026-11-14, Saturday)

Source: `/tmp/miniheroes-2026-11-14/*.log`, `logs/claude/2026-11-14.log`.

| # | Task | What went wrong | Status |
| --- | --- | --- | --- |
| 6 | arena2 (Bino) | Challenge lineup: Start tapped 3× (incl. the 2 re-taps), lineup still up after 180 s → FAIL; the runner's retry fought fine | ❌ same as Bino 11-05; a Start that doesn't register 3× in a row |
| 7 | gate (Chloe) | game froze mid-battle (static frame, kills 2207, no Pause button, Back ignored) → "no button 'Quit Battle'", home failed, EXIT 1. `boot.sh 6` + resume from `gate` → OK | ❌ runner could restart the game itself on a frozen frame |
| 8 | divine (Chloe) | `veins.py`: not on the Veins grid (Excelsior Veins tap ignored, still on Arsenal) → retry OK | ❌ |
| 9 | events (all) | Crystal Throne banner dot = the Value Pack `tribe_clash_packs` claims next → false MANUAL on 10 accounts; Tiger's Storm dot read as `banner 1d 15h` (rotating card showed Dragon Temple) → no visit; a 1-frame read missed Dino's Dragon Temple dot; claim list in the step line (Nick: report only what's wrong) | ✅ skip Crystal Throne, 8 s multi-frame read, Storm visit on any dot, short line; live on Kratos/Dino/Boudior/Cmajor/Tiger/Dminor |
| 10 | Tiger after the run | game ignored every tap (Storm card, Play Pass, raw `adb input tap`) while still animating → `boot.sh 13`, then `play_pass2` claimed a monthly row | ❌ |
| 11 | arena DoD (all) | Match badge 3 tickets after the run: `patrol_claim` (after `arena3`) refills them; spent by hand-run `arena` on 8 accounts (Bino/Kong/fGotten not: in use / off) | ❓ add an `arena4` after `patrol_claim`? (catch-up spends them otherwise) |
| 12 | daily_mission (Cmajor) | 150 at the step: "Consumed 10 Bread in Fishing" reached only later (Auto fishing) → re-run claimed row + 160 | ❌ re-check the bread row / re-run daily_mission at the end |
| 13 | Dragon Temple (Dminor) | new PvP ladder on the Storm screen's 2nd tab (Challenge players above, 6 tickets); its dot stays → MANUAL | ❓ add to the dailies? |

## Climb stage 16:50 (Tiger, Kratos)

Source: `logs/{tiger,kratos}/2026-11-14.log` `[climb_stage]` lines.

| # | Task | What went wrong | Status |
| --- | --- | --- | --- |
| 14 | climb_stage swap (Kr) | 7-6: 3 swaps only flip-flopped tabs 1<->2 (swap 2 = 2<->1 put back the order that lost wave 1; swap 3 = 1<->2 again = the order swap 1 already lost) → tab 3 (nezha team) never moved, exit 2. `o = (w + k - 1) % 3 + 1` is relative to the current losing wave, not to orders already tried | ❌ skip orders already tried on the stage |
| 15 | climb_stage summary | `still climbing: {}` on exit 0 when every account had just been sent back into a fight (`seen.pop` after Challenge again / swap) — looks like nothing is climbing; both were fighting | ❌ cosmetic |
| 16 | Fishing orders (Boudior) | Dailies 13:45 `OK fishing … orders refreshed` with orders at 2/3/2 diamonds (min 3): at 0 scrolls the Refresh tap did nothing, the runner looped 60 taps and called it OK | ✅ final on-screen diamond check (Stop if a row < min); 🧪 buying via `+` |
| 17 | Fishing scroll buy (Boudior) | First fix bought 6 packs (300 gems) in 70 s: the pack popup stays open after Purchase, the (540,1600) close did nothing, every pass bought again — Nick stopped it | 🧪 close at (540,240) + popup-gone/count+5 check, one pack per empty count, `test_fish_buy.py` |

## Poseidon S221 19:15 + catch-up 19:52 (game day 2026-11-14, Saturday)

Source: `logs/{tiger,kratos,boudior}/2026-11-14.log`, `/tmp/miniheroes-2026-11-14-19/*.log`.

| # | Task | What went wrong | Status |
| --- | --- | --- | --- |
| 18 | poseidon (Kratos, Boudior) | Attempt 3 hit ~3.3M ships (MICHAIL BARRUI 3291k, Zoval 3303k); Kuzann 2704k / TRIDENTE 2752k were picked one round later from the same bottom page — not candidates in round 1 (no red heart then, or not read). No round-1 screenshot kept | ❓ keep a per-round screenshot to tell |
| 19 | events (Tiger) | Storm Battlefield banner "!" stays when tickets are kept at the rank cap (King 1 = `storm_max_rank`, 5/5 tickets): not visit-only like the doc says → MANUAL. Still there after my visit | ❌ ignore the Storm dot when `storm` stopped at the cap |
| 20 | events (Tiger, Dminor) | `banner 2d 15h` (1st card, rotates 7777 Draws / other events): hub tabs had no dot, and 14 frames read afterwards had no dot on card 1 → likely the red 7777 art caught mid-rotation | ❌ check `red_dot` against the card's rotation (1-frame noise) |
| 13 | Dragon Temple (Dminor) | Still MANUAL in this catch-up (tab "!", unmapped) | ❓ (see above) |

## Slanesh rebirth + divinities 21:00 (game day 2026-11-14)

Source: `logs/slanesh/2026-11-14.log`.

| # | Task | What went wrong | Status |
| --- | --- | --- | --- |
| 21 | rebirth_level | Crashed on start: no `accounts/slanesh.yaml` (Slanesh = MuMu 20, no account file) | ✅ missing file = no dailies hero to skip |
| 22 | divinity (Whaley Imp) | `level not readable` stop on purple badge 2 (Warrior HP, Lv.0): stop screenshot showed the popup already closed, badge still 0. `--here` re-run did 0 → 150 there with no stop | ❓ one-off; keep the stop screenshot if it happens again |

## Catch-up 07:40 (game day 2026-11-14, Saturday; local Sun 11-15)

Source: `/tmp/miniheroes-2026-11-15-07/*.log`, `logs/claude/2026-11-15.log`. 11 runners, no helper, no paid action; Storm SKIP (Coming Soon) everywhere.

| # | Task | What went wrong | Status |
| --- | --- | --- | --- |
| 23 | arena2 (Dino) | Same as #6 (3rd time: Bino 11-05, Bino 11-14): challenge lineup Start + 2 re-taps lost, lineup still up after 180 s → FAIL; retry fought fine, tickets 0 | ❌ recurring |
| 24 | common_recruit (xF, Bd) | Ad draw: `ad closed after 62s (3 close taps)` but Chances still 1 / no Confirm → FAIL (15 s wait); retry watched a new ad and drew. Likely the 2nd-try top-right X closed it unrewarded | ❌ check the countdown before the X close tap |
| 25 | relic (Bino, Chloe) | one dig tap ignored each (`r1c2` / `r1c5 D: no effect` → blocked), as on 11-07 / 11-12; both still ran to 0 shovels, exit 0 | ❌ recurring one-off |

## Slanesh catch-up 10:23 (game day 2026-11-14, Saturday; local Sun 11-15)

Source: `/tmp/miniheroes-2026-11-15-10/slanesh*.log`, `logs/slanesh/2026-11-14.log`. First catch-up on Slanesh: created `accounts/slanesh.yaml` (catch-up keys only, no gem caps; not in `accounts/tasks.yaml`). No helper, no paid action.

| # | Task | What went wrong | Status |
| --- | --- | --- | --- |
| 26 | arena (Slanesh) | My inline `# …` comment on `arena: tribe:` became part of the roster file name → arena.py exit 1 twice. Comment removed; arena2 crashed all 7 tickets | ✅ no inline comments on `tribe:` |
| 27 | patrol_claim (Slanesh) | patrol.py reads `patrol.max_gem_price` even with `--claim-only` → AttributeError without the key. Added `max_gem_price: 0`; re-run Claim All OK | ✅ config; ❓ patrol.py could skip the cap in claim-only |
| 28 | fishing_auto (Slanesh) | Auto already running, Bait tap opened no popup (no `Swap` in 6 s); retry swapped Shrimp → Basic Bait and started Auto | ❓ one-off |
| 29 | relic (Slanesh) | `relic_all.sh` printed ` SKIPPED (instance not running)`: my inline `# MuMu 20` on `mumu_instance:` broke the name match (no `strip` of comments). Comment removed; re-run 129 digs, 0/100 left, 80-gem shovel buy | ✅ no inline comments on `mumu_instance:` / `tribe:` |
