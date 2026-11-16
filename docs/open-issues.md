# Open issues

Every open problem in one place (rules: CLAUDE.md "Docs"). New problem → new row; seen again → add the date; fixed → delete the row (not yet live-tested → `docs/untested.md`). History: `docs/archive/struggles-*.md` and git. Built 2026-11-15 from the 13 struggles files (101 open rows → the ones below; dropped: fixed since, one-day questions that expired, one-offs with no repeat).

## Bugs ❌

| Area | Problem | Seen | Next |
| --- | --- | --- | --- |
| runner: dead input | Game stops taking taps (frozen frame, or renders but ignores every tap) → FAIL / `lost the main screen`; fixed each time by `boot.sh <idx>` + resume by hand | Chloe 11-14 (gate), Tiger 11-14, Chloe 11-15 | runner restarts the game itself when N taps in a row change nothing |
| runner: screencap error | `RuntimeError` in `home()` mid-run isn't caught → traceback, runner dies with steps left (only start-up catches it) | Chloe, Boudior 11-13 | `step()` / `home()` turn it into a FAIL + stop line |
| runner: wrong account | No step compares the on-screen game id with `game_id` (only `stabilize.py`); Kong reopens on S288 after a restart | Kong 11-07, 11-13; 11-16: Kong's instance switched to S288 by another session's `daily.py kong_ii` while the dailies session still used its serial (1 stray ☰ tap on Kong II's Fishing screen) | check the id before the first step / after a restart |
| tap lost: lineup Start | Challenge-lineup Start ignored 3× → 180 s FAIL; retry fights fine | Bino 11-05, 11-11, 11-14; Dino 11-14 | cause unseen — screenshot on the 2nd lost tap |
| tap lost: arena Crash | Crash tap doesn't drop the tickets (2 → 2); retry covers | Chien Than, Bino 11-11; xFaktor 11-12; Bino 11-15 | fix only if a retry fails too |
| tap lost: fishing bait | Bait tap opens no popup (`no Swap in 6 s`) / bait title OCR miss; retry covers | Kong 11-09, Cmajor 11-12, Slanesh 11-14, Cmajor + xFaktor (`waited for '^Start$'`) 11-16 | same |
| tap lost: first tap after boot | catch-up `weekly_review`: the ☰ tap right after `boot.sh` opens nothing (`waited 6s for '^Mission$'`); retry covers | Bino, Dino, Dminor, fGotten 11-16 | same |
| tap lost: Veins | `not on the Veins grid` / `unexpected screen`; retry covers | Cmajor 11-13, Chloe 11-14 | same |
| pet_arena | Fights over the Auto Deploy dialog on a busy arena → FAIL; retries cover | Tiger 11-10; Dminor, Cmajor, Chloe, Dino 11-11; 11-16: 7 of 11 at 12:04, then first try `no "Auto Deploying" after Start` on Boudior, Tiger, xFaktor, Bino (retry: `already on`), Chloe, Dminor (2× FAIL, re-run: `no free attempts left`) | same |
| pet_arena: ONCE | `SKIP pet_arena: already OK this game day` although the game was closed after the first start (Auto Deploy gone); `--force` restarted it | Bino 11-16 | look for "Auto Deploying" on screen instead of the state file |
| events before FR packs | `events` runs before `floating_realm_packs`, so the Floating Realm banner dot (free pack) → `MANUAL … banner Floating Realm` on every account; gone once the packs step ran | 11 of 11 on 11-16 | run `floating_realm_packs` before `events` |
| relic: dig ignored | One dig tap has no effect → cell marked blocked; run still finishes | Aminor 11-05, Chien Than 11-07, Boudior 11-12, Bino + Chloe 11-14 | re-tap once before marking a cell blocked |
| relic: held press | Touch UP lost → held press auto-digs a column (~8 shovels off-plan), `board never settled` | Dminor 11-07 | after a dig whose board keeps changing: send UP, re-read |
| veins_forge: Storage | Forge step landed on Arsenal → Storage bulk-select (Confirm on items); nothing confirmed | Dino 11-07 | forge must never reach a screen with Confirm on items |
| fishing: Auto stops | Auto stops when bread runs out; `fishing` OK only means "started" — no end-of-run check | Kong 11-05; 6–7 accounts 11-04/06/07; 10 of 11 on 11-16 (`AUTO STOPPED, bread 3–6/100` at `fishing_rewards`, ~40 min after the start) | end-of-run Auto check (see ❓ bread) |
| daily_mission 150 | Bread row completes later (Auto fishing) → 150 at the step, 160 only on a re-run | Cmajor 11-14, 11-16 (140, bread Claim showed during the step → MANUAL) | re-run `daily_mission` at the end of the run |
| canyon.py: empties missed | `no empty platform found` on 11 of 11 an hour after the season opened; 1–3 min later the helpers occupied empty Silver platforms just below the Gold rows on Bino, Dino, Dminor, fGotten, xFaktor (11 helpers for a free Occupy) | 11-16 | check the detection on the run's `canyon*.png`; else re-scan once before MANUAL |
| daily_mission after Storm | `OK daily_mission: nothing` on 11 of 11 right after `storm` OK (7 matches); the rows + 160 chest were only claimed after Canyon | 11-16 | read the Storm row on screen after the next `storm` |
| canyon retry | Retry trusts `canyon.taken`, no screen check | Kong 11-12 | read the screen before trusting it |
| sanctuary Sweep | Sweep not read on the first look → climbed instead (screenshot + `entry:` line now saved) | Kong 11-10, Kratos 11-12; Boudior 11-16 (`entry: Sweep … (49, 36, 0)`: button found but dimmed → climbed); Kong II 11-16 same line — its `v_sanctuary_entry.png` = the new-map card (Ice Citadel, Confirm) still up over the Sweep, floors 1–10 all open → fresh Monday map, climb was right | root cause from `v_sanctuary_entry.png` when it repeats |
| events: Storm dot | Storm banner dot stays when tickets are kept at `storm_max_rank` → MANUAL | Tiger 11-14 | ignore the Storm dot when `storm` stopped at the cap |
| events: card-1 dot | `banner 2d 15h`: red 7777 art read as a dot mid-rotation | Tiger, Dminor 11-14 | check `red_dot` against the rotation |
| events: Artifact Wish | Weekly Event "Earn 6000 Points" claim not scripted (runner only does Wish Merchant) | fGotten 11-15 | add the claim |
| weekly statue | Level Up read unreliable (`did not raise the level` with the bar read full) | Dino, Boudior, Kratos 11-15 | statue = unscripted daily row |
| stabilize: Top-up popup | "Top-up Bonus" white X opened the Snow Carnival web page | Chien Than, xFaktor 11-05; Kong II (S288, `boot.sh 5`) 11-16: `popup-stuck` on the web page, Back → Snow Carnival popup, `stabilize.py` cleared it | map the popup's close path |
| climb_stage: swap order | 3 swaps flip-flop tabs 1↔2, tab 3 never tried | Kratos 7-6, 11-14 | skip orders already tried on the stage |
| OK without proof | `hero` OK line = `hero upgrade done` (levels only in the body lines); `patrol` `Claim All tapped` not read back; `shop` / `play_pass` don't re-check the red dot after a claim (rest of the 11-03 dod.md list fixed: Daily Mission chests, Trials, Grocery, forge, Stage, Beast lines carry proof now) | dod.md 11-03; Tiger 11-15 | print the proof in the OK line / re-read the dot |
| climb_stage: swap timeout | `TIMEOUT waiting for 'Start'` after a tab tap; yaml not rewritten, tabs unknown | Kratos 6-26, 11-14 | — |
| climb_stage: summary | `still climbing: {}` while accounts are fighting (cosmetic) | 11-14 | — |
| boot.sh | No `ready` line for 2 of 11 instances that were fine | Kong, Kratos 11-14; 11-16 17:47: Cmajor (on a clean main screen), Kratos's line without its name, and a `JSONDecodeError` traceback in the output | — |
| stabilize: Kong switch | Kong on S288 after boot; the switch's ☰ tap (994,1625) opened the event hub (Hero Recruit) → `waited 10s for '^Settings$'` traceback, `popup-stuck`. Back arrow + re-run switched to S220 | Kong 11-15; 11-16 (switch back from Kong II: `popup not closable` with the event hub open, no switch started) | check the main screen before the ☰ tap; back out of a hub first |
| layout.js | `execution error … (-1743)` (macOS: not allowed to send Apple events) — windows not tiled, also outside the sandbox | 11-15 (stabilize all); 11-16: `no window` for all 11 after a re-boot (tiled fine 20 min earlier), again at 17:47, 18:05, 18:14 | grant Automation permission to the app running Claude Code (System Settings → Privacy & Security → Automation) |
| tribe.py | Not executable (`permission denied`) | 11-13 | `chmod +x scripts/tribe.py` |
| patrol.py | `--claim-only` still needs `patrol.max_gem_price` | Slanesh 11-14 | skip the cap in claim-only |

## Needs Nick ❓

| Topic | Question | Seen |
| --- | --- | --- |
| Old dailies skill | A claude.ai account skill `miniheroes-dailies` (Oct 26, "read all of ui-routine", `enabled: true` accounts) syncs into `~/.claude/skills/synced/…` and lists next to the repo skill; a local delete is re-synced. Remove it in claude.ai Settings → Skills? | 11-16 |
| Monday 150 | Canyon / Storm closed until 17:00 → a Monday daytime dailies run tops out at 150; the evening catch-up adds Canyon → 160. Call 150 "done" on Monday daytime? | dod.md 11-03; 11-16 (11 accounts at chests 40/80/120; Kong II 150: Statue, Diamonds, Canyon rows open; evening Storm + Canyon + `daily_mission` → 160 on all 11) |
| Weekly Lucky Stars | The row = 50 casts on Lucky Star bait, and Auto fishing stops at 0 bread, so the Sunday star plan only pays at a fishing start with ≥ 50 bread before 12:00 Monday (11-15: both catch-up starts went to Basic by a `weekly_review` bug, fixed 11-16 06:02 — 18:52 Sunday and 05:40 Monday, the 2nd with the full overnight bread (0/100 at 19:03 → ~2/100 by 06:03); Boudior, Dino, fGotten 170; Kratos, xFaktor 150). Add a late-Sunday fishing restart on accounts still short? | 11-15 |
| Weekly plan | Weekly is planned only on Sunday, too late to spend resources well (Lucky Stars = 50 bread casts; Statue needs a full power bar). The dailies' Sunday `weekly` step also picks stars while daily-capped rows still complete later that day (Bino 170, Chloe 160, Dminor 170 at ~13:00 → 180 by 18:54 without stars). Plan the week from Monday: each run reads missions needed + still-doable rows and starts slow rows early? | 11-15 |
| Dragon Temple | New PvP ladder (Storm screen tab 2, 6 tickets); its dot → MANUAL on most accounts daily. Should the dailies do it? | 11-14, 11-15 |
| Canyon row | `highest_free` keeps a Glory spot (no Occupy) → Canyon row open, chest 150. Give up the spot, or is 150 fine? (No empty platform: decided 11-16 — attack, ui-routine "Canyon Clash") | Tiger 11-07, Kratos 11-13 |
| Canyon by hand? | Monday 18:07–18:09, between `canyon.py` (Unoccupied, Attempts 5) and the helpers: a spot already held ~1 min and attempts spent on Cmajor (Silver, 0 left), Kong (Silver, 1 left), Chloe (Silver, 4, Victory screen up), Tiger / Kratos / Boudior (Gold, 4 / 3 / 4); no line in any log, no other script running; 18:20 Cmajor on a battle lineup screen. Were you playing them, or is another session? | 11-16 |
| arena4 | `patrol_claim` (after `arena3`) refills 3 tickets → add an `arena4` after it? | 11-14 |
| Training Program | Free Reward-column Claim (Storm Sage shards) not in `limited_recruitment()`; doc lists Training Program under "Never". Script the free claim? | Tiger 11-13 |
| Play Pass | Chloe, Dminor have `play_pass_claims: true` but Recruit shows the ad button — pass lapsed? | 11-13 |
| Fishing bait | `fishing: bait: Shrimp Bait` in Cmajor / Dino configs? (Shrimp was swapped to Basic) | 11-12 |
| Bread | Auto fishing out of bread by evening on most accounts — expected? | 11-04, 11-06, 11-07 |
| Artifact counter | Aminor's 7482/5000 counter (orange ring) seemed to block Wish — may the roll claim it? | 11-07 |
| Floating Realm maps | Knocked down at 1 kill: use a map at 1 kill on Thu, or after N empty explores Tue–Wed? | Tiger 11-05 |
| Tribe request timing | Catch-up ~07:45 sends the request → dailies hit the 6 h cooldown | 11-12, 11-15 |
| Stopped instances | Instances found stopped mid-day (steps not run) — closed by you? | Kong 11-06; 3 on 11-08; 8 on 11-15; 9 of 11 on 11-16 ~13:40, right after the dailies runners (Dino, fGotten end re-check not run); 11-16 ~18:04: Bino, Dino, Dminor, fGotten, Chloe back on the Android launcher mid-task (fresh start) and Aminor running, 18:13: Tiger, Kratos, Boudior, Aminor stopped (swap 21.4 of 22.5 GB used — instances crashing?) |
| Poseidon pick | Attempt 3 hit ~3.3M ships though ~2.7M ones were on the same page; keep a per-round screenshot? | Kratos, Boudior 11-14 |
| Kong II | A `--server` option on `stabilize.py` if Kong II runs become regular? (11-16 catch-up: switch in by a patched `stabilize.account` OK; the switch back to S220 hung on the loading screen after Confirm — `waited 60s for '15847271'` — `boot.sh 5` fixed it, then Kong's `fishing_auto` re-run; evening Storm + Canyon run: both switches clean, in by the same patch and back by plain `stabilize.py`) | 11-14, 11-16 |
