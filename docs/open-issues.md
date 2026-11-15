# Open issues

Every open problem in one place (rules: CLAUDE.md "Docs"). New problem → new row; seen again → add the date; fixed → delete the row (not yet live-tested → `docs/untested.md`). History: `docs/archive/struggles-*.md` and git. Built 2026-11-15 from the 13 struggles files (101 open rows → the ones below; dropped: fixed since, one-day questions that expired, one-offs with no repeat).

## Bugs ❌

| Area | Problem | Seen | Next |
| --- | --- | --- | --- |
| runner: dead input | Game stops taking taps (frozen frame, or renders but ignores every tap) → FAIL / `lost the main screen`; fixed each time by `boot.sh <idx>` + resume by hand | Chloe 11-14 (gate), Tiger 11-14, Chloe 11-15 | runner restarts the game itself when N taps in a row change nothing |
| runner: screencap error | `RuntimeError` in `home()` mid-run isn't caught → traceback, runner dies with steps left (only start-up catches it) | Chloe, Boudior 11-13 | `step()` / `home()` turn it into a FAIL + stop line |
| runner: wrong account | No step compares the on-screen game id with `game_id` (only `stabilize.py`); Kong reopens on S288 after a restart | Kong 11-07, 11-13 | check the id before the first step / after a restart |
| tap lost: lineup Start | Challenge-lineup Start ignored 3× → 180 s FAIL; retry fights fine | Bino 11-05, 11-11, 11-14; Dino 11-14 | cause unseen — screenshot on the 2nd lost tap |
| tap lost: arena Crash | Crash tap doesn't drop the tickets (2 → 2); retry covers | Chien Than, Bino 11-11; xFaktor 11-12; Bino 11-15 | fix only if a retry fails too |
| tap lost: fishing bait | Bait tap opens no popup (`no Swap in 6 s`) / bait title OCR miss; retry covers | Kong 11-09, Cmajor 11-12, Slanesh 11-14, Cmajor + xFaktor (`waited for '^Start$'`) 11-16 | same |
| tap lost: first tap after boot | catch-up `weekly_review`: the ☰ tap right after `boot.sh` opens nothing (`waited 6s for '^Mission$'`); retry covers | Bino, Dino, Dminor, fGotten 11-16 | same |
| tap lost: Veins | `not on the Veins grid` / `unexpected screen`; retry covers | Cmajor 11-13, Chloe 11-14 | same |
| pet_arena | Fights over the Auto Deploy dialog on a busy arena → FAIL; retries cover | Tiger 11-10; Dminor, Cmajor, Chloe, Dino 11-11 | same |
| relic: dig ignored | One dig tap has no effect → cell marked blocked; run still finishes | Aminor 11-05, Chien Than 11-07, Boudior 11-12, Bino + Chloe 11-14 | re-tap once before marking a cell blocked |
| relic: held press | Touch UP lost → held press auto-digs a column (~8 shovels off-plan), `board never settled` | Dminor 11-07 | after a dig whose board keeps changing: send UP, re-read |
| veins_forge: Storage | Forge step landed on Arsenal → Storage bulk-select (Confirm on items); nothing confirmed | Dino 11-07 | forge must never reach a screen with Confirm on items |
| fishing: Auto stops | Auto stops when bread runs out; `fishing` OK only means "started" — no end-of-run check | Kong 11-05; 6–7 accounts 11-04/06/07 | end-of-run Auto check (see ❓ bread) |
| daily_mission 150 | Bread row completes later (Auto fishing) → 150 at the step, 160 only on a re-run | Cmajor 11-14 | re-run `daily_mission` at the end of the run |
| canyon retry | Retry trusts `canyon.taken`, no screen check | Kong 11-12 | read the screen before trusting it |
| sanctuary Sweep | Sweep not read on the first look → climbed instead (screenshot + `entry:` line now saved) | Kong 11-10, Kratos 11-12 | root cause from `v_sanctuary_entry.png` when it repeats |
| events: Storm dot | Storm banner dot stays when tickets are kept at `storm_max_rank` → MANUAL | Tiger 11-14 | ignore the Storm dot when `storm` stopped at the cap |
| events: card-1 dot | `banner 2d 15h`: red 7777 art read as a dot mid-rotation | Tiger, Dminor 11-14 | check `red_dot` against the rotation |
| events: Artifact Wish | Weekly Event "Earn 6000 Points" claim not scripted (runner only does Wish Merchant) | fGotten 11-15 | add the claim |
| weekly statue | Level Up read unreliable (`did not raise the level` with the bar read full) | Dino, Boudior, Kratos 11-15 | statue = unscripted daily row |
| stabilize: Top-up popup | "Top-up Bonus" white X opened the Snow Carnival web page | Chien Than, xFaktor 11-05 | map the popup's close path |
| climb_stage: swap order | 3 swaps flip-flop tabs 1↔2, tab 3 never tried | Kratos 7-6, 11-14 | skip orders already tried on the stage |
| OK without proof | `hero` OK line = `hero upgrade done` (levels only in the body lines); `patrol` `Claim All tapped` not read back; `shop` / `play_pass` don't re-check the red dot after a claim (rest of the 11-03 dod.md list fixed: Daily Mission chests, Trials, Grocery, forge, Stage, Beast lines carry proof now) | dod.md 11-03; Tiger 11-15 | print the proof in the OK line / re-read the dot |
| climb_stage: swap timeout | `TIMEOUT waiting for 'Start'` after a tab tap; yaml not rewritten, tabs unknown | Kratos 6-26, 11-14 | — |
| climb_stage: summary | `still climbing: {}` while accounts are fighting (cosmetic) | 11-14 | — |
| boot.sh | No `ready` line for 2 of 11 instances that were fine | Kong, Kratos 11-14 | — |
| stabilize: Kong switch | Kong on S288 after boot; the switch's ☰ tap (994,1625) opened the event hub (Hero Recruit) → `waited 10s for '^Settings$'` traceback, `popup-stuck`. Back arrow + re-run switched to S220 | Kong 11-15 | check the main screen before the ☰ tap; back out of a hub first |
| layout.js | `execution error … (-1743)` (macOS: not allowed to send Apple events) — windows not tiled, also outside the sandbox | 11-15 (stabilize all) | grant Automation permission to the app running Claude Code (System Settings → Privacy & Security → Automation) |
| tribe.py | Not executable (`permission denied`) | 11-13 | `chmod +x scripts/tribe.py` |
| patrol.py | `--claim-only` still needs `patrol.max_gem_price` | Slanesh 11-14 | skip the cap in claim-only |

## Needs Nick ❓

| Topic | Question | Seen |
| --- | --- | --- |
| Old dailies skill | A claude.ai account skill `miniheroes-dailies` (Oct 26, "read all of ui-routine", `enabled: true` accounts) syncs into `~/.claude/skills/synced/…` and lists next to the repo skill; a local delete is re-synced. Remove it in claude.ai Settings → Skills? | 11-16 |
| Monday 150 | Canyon / Storm closed until 17:00 → a Monday daytime dailies run tops out at 150; the evening catch-up adds Canyon → 160. Call 150 "done" on Monday daytime? | dod.md 11-03 |
| Weekly Lucky Stars | The row = 50 casts on Lucky Star bait, and Auto fishing stops at 0 bread, so the Sunday star plan only pays at a fishing start with ≥ 50 bread before 12:00 Monday (11-15: both catch-up starts went to Basic by a `weekly_review` bug, fixed 11-16 06:02 — 18:52 Sunday and 05:40 Monday, the 2nd with the full overnight bread (0/100 at 19:03 → ~2/100 by 06:03); Boudior, Dino, fGotten 170; Kratos, xFaktor 150). Add a late-Sunday fishing restart on accounts still short? | 11-15 |
| Dragon Temple | New PvP ladder (Storm screen tab 2, 6 tickets); its dot → MANUAL on most accounts daily. Should the dailies do it? | 11-14, 11-15 |
| Canyon row | `highest_free` keeps a Glory spot (no Occupy), or no empty platform → Canyon row open, chest 150. Give up the spot / attack, or is 150 fine? | Tiger 11-07, xFaktor 11-10, Kratos 11-13 |
| arena4 | `patrol_claim` (after `arena3`) refills 3 tickets → add an `arena4` after it? | 11-14 |
| Training Program | Free Reward-column Claim (Storm Sage shards) not in `limited_recruitment()`; doc lists Training Program under "Never". Script the free claim? | Tiger 11-13 |
| Play Pass | Chloe, Dminor have `play_pass_claims: true` but Recruit shows the ad button — pass lapsed? | 11-13 |
| Fishing bait | `fishing: bait: Shrimp Bait` in Cmajor / Dino configs? (Shrimp was swapped to Basic) | 11-12 |
| Bread | Auto fishing out of bread by evening on most accounts — expected? | 11-04, 11-06, 11-07 |
| Artifact counter | Aminor's 7482/5000 counter (orange ring) seemed to block Wish — may the roll claim it? | 11-07 |
| Floating Realm maps | Knocked down at 1 kill: use a map at 1 kill on Thu, or after N empty explores Tue–Wed? | Tiger 11-05 |
| Tribe request timing | Catch-up ~07:45 sends the request → dailies hit the 6 h cooldown | 11-12, 11-15 |
| Stopped instances | Instances found stopped mid-day (steps not run) — closed by you? | Kong 11-06; 3 on 11-08; 8 on 11-15 |
| Poseidon pick | Attempt 3 hit ~3.3M ships though ~2.7M ones were on the same page; keep a per-round screenshot? | Kratos, Boudior 11-14 |
| Kong II | A `--server` option on `stabilize.py` if Kong II runs become regular? | 11-14 |
