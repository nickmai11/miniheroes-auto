# Untested changes — pre-flight list for the next dailies

Pre-flight (dailies skill): rows whose Test isn't `passive:` → test on ONE account before the real run; `passive:` rows → after the run, grep the logs for their Pass line. Remove a row once it passed live; add a row for every change that couldn't be tested on the day it was made. Keep rows short: what changed, where to test, what passing looks like (the why goes in the commit).

| Added | Change | Test (where) | Pass = |
| --- | --- | --- | --- |
| 11-15 | `daily.py gate`: result Confirm retried up to 3× until `Chances left today` | passive: next gate fight that runs to the 3-min cap | `OK gate … ['run', 'sweep']`; no `waited 10s for 'Chances left today'` |
| 11-14 | Fishing scroll buying: `+` (272,425) → Purchase → close (540,240, up to 2 taps) → count +5 → use them → next pack; a pack with no refresh = stop | passive: next `fishing` with 0 scrolls and an order below its min | one `bought 5 refresh scrolls for 50 gems (N -> N+5)` per pack, then refreshes; never 2 `bought` lines in a row |
| 11-14 | `hero_faces.py` + `climb_stage.py` by face: swap / `--apply` placing heroes by face, learn-and-retry on an unknown face mid-climb, deep grid rows, `learn` on a real new hero/skin | passive: next climb with a swap or `--apply`; next new hero | `swapped lineups … yaml updated` with hero ids, tabs read back equal; unknown face → `unrecognised faces … -> learn` then read |
| 11-14 | `banner_dots()` skips Crystal Throne | passive: next `events` in a Crystal Throne week | no `banner Crystal Throne` in a MANUAL line |
| 11-13 | `flow.watch_ad()` (11-08 → 11-15): "Close it" after the countdown, top-right X every 2nd close try, force-close only from 60 s, a failed screencap = empty read | passive: next no-pass ads (Boudior, Tiger, xFaktor) | `ad closed after Ns` + reward popup; `OK recruit … common (ad)` first try; no FAIL, never a store/browser left in front |
| 11-12 | `divinity.py`: default start `first_after()` (no `--here`), OCR-name fixes, gold-out stop | next "upgrade divinities": run without `--here`, watch hero N+1 | `first N kept: [...]` = list's first N; no `not listed` for a name in `divinities.yaml` |
| 11-12 | `rebirth_level.py`: `rebirth` phase + `first_after()` on a fresh account | next "reset heroes": watch the first 2 heroes | rebirth then level in list order, `row end: K heroes`; a `--phase level` re-run prints no `-> Lv.` |
| 11-12 | `sanctuary()`: Sweep skipped when yesterday ended MANUAL / FAIL (short of 10/10) → climb | passive: an account whose last sanctuary was MANUAL | `Sweep offered, not used: yesterday MANUAL`; others `swept` |
| 11-12 | `sanctuary_climb()`: strongest lineup = recall ↺ (1006,1082) + Quick Deploy, on the first Battle and after a potion | passive: next climb or potion refight | the top 5 (row 1) ticked |
| 11-11 | Sanctuary weekly modifier card matched by its Confirm (300–780, 1520–1720), not the title | passive: next new-map week | no `no floor popup under the marker` FAIL |
| 11-08 | `relic.py`: area finished ("Area fully excavated.") → `open_board()` and keep digging | passive: next relic run that finishes an area | `area fully excavated, re-entering Archaeology`, more digs, exit 0 |
| 11-08 | `ct_revive.sh`: Free Revive retried ~1 s through the cooldown, popup reopened, stop at 0/5 | passive: next Crystal Throne match | each defeat → `revived` within ~60 s |
| 11-09 | `artifact_roll.py`: a new-artifact popup / Mythic text after Wish counts as the box opened | passive: next roll with a new Legendary | `cycle N: new non-Mythic '…' -> Confirm, go on` |
| 11-06 | `climb_stage.py --stop-next-chapter`: after X-40 → Next chapter, no Start, `STOPPED at (X+1)-1` | next "stop at next chapter" climb | main screen shows (X+1)-1, `STOPPED at` in the log |
| 11-06 | `storm.py cur_rank`: 2× crop OCR for the badge level | passive: next storm on an account at King +10 | `rank read (4, N)` with the right two-digit N; cap stop at +10 |
| 11-06 | `accounts.py <task>` filtering in `catchup_all.sh`, `fr_all.sh`, `survey.py` | next catch-up / fr / survey batch | one line per account of `accounts.py <task>`, no others |
| 11-06 | `gear.py`: out-of-gold stop, Enhance-button-gone exit, `None` slot label | next gear run: PuPu `--heroes 15` | every slot of heroes 1–15 ≥ 150 (no `None`) or a gold-shortage line; no purchase dialog |
| 11-05 | `realm.py`: closes the Exploration Success popup (Lair core break-through) | passive: next Lair stake that breaks through | `lair: … ok`, more explores, no `stamina unreadable` |
| 11-05 | `relic.py` routes: equal cost → route through the bottom row | passive: next `relic_all.sh` | first dig of such a route is a bottom-row tile |
| 11-05 | `realm.py`: Floating Realm banner polled 15 s | passive: Fri 04:30 `fr_all.sh` (Kong) | `kong exit 0` with `start: F…`; no `no Floating Realm banner` |
| 11-03 | `realm.py`: `fight()` accepts `Tap anywhere` straight after Attack; 3× explore | any battle round: `realm.py <account>` | `done: … stamina < cost`; `Confirm ignored 2x` → restart the game and re-run |
| 11-03 | `rune`: swipe to a later page when the first has no unlocked red | an account with only locked reds: `daily.py <acct> rune` | one tap on an unlocked tile, `synthesized -> …` |
| 11-03 | `stage`: a Victory mid-run → close + re-open from the skull | passive: first stage run that wins a fight | `Victory, …` and the fights go on |
| 11-03 | `hero.py` gear: stop when Enhance disappears (out of gold) | passive: an account out of gold | `gear 1: Enhance xN` with N < gear_levels; no price tapped |
| 11-03 | `adventure.py claim_tower`: chest level → Claim Reward → Challenge | passive: first Tower showing Claim Reward | `tower: chest level -> Claim Reward claimed`, then `tower i/n` |
| 11-03 | `events`: unknown hub tab with a dot → `MANUAL … unmapped tab <label>` | passive: next new event tab | MANUAL names it; then map it |
| 11-04 | `relic.py` planner: lit pickaxe first, `via the next row`, row-1 items `before the scroll loses it` | passive: next relics run | those lines match the dig that follows |
| 11-04 | `relic.py` planner: item tiles free in the route search | passive: next relics run | routes take shards on the way; no run ends mid-route on a cost ≥ 2 route |
| 11-04 | `relic.py buy_shovels()`: per-day state file → re-run skips the + tap | next same-day relics re-run | `shovel buy: nothing left today`; a fresh day buys again |
| 11-09 | `treasury.py`: hub → Golden Woods → King's Treasury navigation, Level 7 pick, Level 8+, out-of-keys stop, `milestones()` | next "treasure event" run | `level 7: prize = Level 7 tile`, `milestone … claimed`, `DONE level N, keys 0` |
| 11-11 | `pet_manual()`: short of +40 → deploys Free Attempts cards by hand, checked by "this round k/4" | next catch-up `pet_check` on a short account | `manual deploy xN (free attempts)`, next count +N; never a ticket |
