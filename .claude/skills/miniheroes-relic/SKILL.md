---
name: miniheroes-relic
description: Run Mini Heroes: Magic Throne Relics (Archaeology dig board, e.g. Blaze Peaks / Shadowlands) - spend all shovels digging for relic chests, multi-square chests and shards with minimum shovel waste, on Nick's MuMuPlayer accounts via ADB (scripts/relic_all.sh / relic.py).
---

# Mini Heroes Relics

Use when Nick asks for "relics" or "dig" (not "mining" — that's Excelsior Veins) on Mini Heroes accounts.

## Run it — script, no helper (Nick 2026-11-03: "a script that reliably does the work")

1. Instances at the main screen (`scripts/boot.sh <mumu index>...`), then **`scripts/relic_all.sh [account ...]`** — runs
   (each account: the free shovels, then — only when the counter hits 0, once per game day — Benefit red dot → Claim
   and the configured shovel buys, then those shovels)
   `relic.py` on every `accounts/*.yaml` account in parallel (~4 s per dig, 150 shovels ≈ 10 min). One line per
   account: `<account> exit 0 (done: N digs, shovels 0/150 left, items: …)`; output + screenshots in
   `/tmp/miniheroes-relic/<account>/`, every dig also in `logs/<account>/<game day>.log`.
   One account: `D=<serial> scripts/relic.py <account> [--dry] [--max-digs N]` — from the main screen, the Lost
   Continent map or the board; `--dry` only prints the board and the next dig.
   Run it in the background with one Monitor on its output for `exit 1` lines and act **the moment one appears** — never
   wait for the whole batch (2026-11-04: 3 accounts failed in the first 15 s, handled 8 min later; Nick: too slow).
2. **`exit 1` = it stopped** (unexpected screen, 3 refused digs, nothing diggable): read `out.txt` + `v_relic.png` there.
   `could not reach the dig board` with the account on some other screen (Tribe after catch-up) → the script now taps
   back itself; if it still stops, go home (back arrow `(80,1820)`) and re-run that account at once. Anything else: a
   helper finishes **that account only** by hand with the board rules below. Never re-run the script blindly on it.
   `UNKNOWN cells rXcY` in the log = a tile the reader has never seen (it digs around them): look at the screenshot,
   teach it — `scripts/relic.py --learn <png> <row> <col> <label>` (labels: `empty pit dirt_lit dirt_dark stone_lit
stone_dark cracked_lit shard_lit shard_dark chest_lit chest_dark gold_lit gold_dark pick_lit pick_dark multi_lit
multi_dark frame`; never learn from r6c1, the % label sits there) — `python3 scripts/test_relic.py` must still pass, then run again.
3. Report per account: the `done:` line (digs, items, shovels left), any `UNKNOWN` / `refused` / `no effect` lines, and
   every `dynamite` / `drill` line (fired by the rule below) or else the `booster hint (not used)` line.

What the script does (details in the `scripts/relic.py` header): matches each of the 42 tiles against the sprite crops in
`scripts/relic_tiles/` (two identical reads needed — banners, dust, scrolling; a tile beside a dug cell counts as diggable
whatever shade it was read as — Kong 2026-11-04, a bottom-row gold chest read dark hid 2 shards); a **lit pickaxe is dug first** (free —
its shovel comes back; in the bottom row it reveals a new row before any route is committed to; Nick 2026-11-04), then
Dijkstra over dig costs from the lit tiles (dirt 1, stone 2, pickaxe 0) over the board **plus the hidden row below it**
(0.99 per tile: a corridor there that could beat a known tunnel through stone makes the first dig the dig-down that
reveals it — `via the next row`, Nick 2026-11-04), target = best value/cost ≥ 0.14 lv1-relic units per shovel (shard
0.28, relic chest 1.6, gold chest 0; **a multi-square chest outranks everything** — Nick 2026-11-04: value 3.2 and its
route is taken first at any cost, a lit one opens free before anything), otherwise the
cheapest bottom-row dig (reveals a new row).
A bottom-row dig scrolls row 1 off for good, so an item there worth its route is dug first (`before the scroll loses
it`; `letting … go` = not worth its route). Every dig is
verified (tile changed / board scrolled / counter), reward popups closed, the milestone reward claimed at "Mine 0 more";
it never taps the shovel **+** or One-Tap Mining; boosters only by the rule below. Proven live 2026-11-03 on all 9 accounts (≈770 digs, 0 refused taps); classifier checked on 65 saved boards (`scripts/test_relic.py`).

## Board (finishing by hand, or changing the script)

Path: main → **Relic** (bottom bar, far right) `(972,1788)` → **Lost Continent** map → **Archaeology** (OCR the label)
→ dig board. On the map, **Relic Display** sits where the Relic button was — a late Relic tap + a retry lands there (back
arrow `(80,1820)`). Screenshot before retrying anything.

- 6 columns × 7 visible rows. Device coords (1080×1920): column x = `116, 284, 452, 624, 794, 962`;
  row y = `600, 770, 940, 1110, 1280, 1450, 1620` (row 7 = bottom row, below the yellow % line; the % label covers the
  lower third of r6c1).
- Dark brown = empty (dug). **Lit** tiles (tan dirt, light grey stone, items on a tan hole) touch an empty cell →
  diggable now. **Dark** tiles (dark brown dirt, dark grey stone) aren't reachable yet — dark grey stone is just unlit
  stone, same 2 hits (Dino 2026-10-31). Only tiles adjacent to empty cells can be dug ("dig up the adjacent plot
  first" toast, no shovel used).
- Dirt = 1 hit. Stone = 2 hits (cracked after the 1st; one stayed cracked after 2 — Dino 2026-10-30). Items = 1 hit.
- Digging a bottom-row tile scrolls the board up one row (new bottom row appears). Each dig = 1 shovel and +1 on
  the "Mine N more times" bar. Shovel cap 150 or 100 per account (the counter shows it); regen past the cap is lost.
- Pickaxe tile = usually a shovel back (net 0); once Legend Spiritstone ×50 for a real shovel (Dminor 2026-10-31).
- **Multi-square chest** = one big golden-framed chest over 2/4/6 tiles. Tap any of its tiles once lit → "Congratulations"
  popup, **Tap anywhere to close** (Aminor 2026-10-31: 104 gems + 1040 red gems + 3 tokens — currency, no relic); the
  area then stays a golden pit that counts as empty. One 2-square chest in the top row never opened (3 taps no-op) —
  leave such a chest after one refused tap. Sprites: `multi_lit` = the tiles carrying the chest art (2×2 silver: its lower
  2 tiles, Aminor 2026-11-04; 2×3 red relic chest: only the bottom-middle tile, Cmajor 2026-11-04; **2×1 wooden chest:
  the art straddles both tiles**, Cmajor 2026-11-05 — `multi_dark.1-2` unlit / `multi_lit.6-7` lit), `frame` = its plain
  gold-frame tiles, which look exactly like the opened pit; `read()` turns a frame block touching an art tile into one
  `M` chest (value once, other tiles cost 0, lit as a whole when any of its tiles is) and a frame block with no art into
  empty. A new shape → the art tile reads `UNKNOWN`: `--learn` it as `multi_lit`/`multi_dark` (it looks different: an
  unlit chest has a dull gold frame, a lit one glows bright yellow), its plain tiles as `frame` if they read `UNKNOWN`
  too. All item shapes seen so far: 2×1, 2×2, 2×3 (Nick 2026-11-05: the 2×1 was the last one).
  Seen on the 2×1 (Cmajor 2026-11-05): unlit = a tap on it is refused like any dark tile (no shovel used); the moment
  it's lit the tiles **beside it** light up too (stone r5c3, shard r6c2 turned bright before the chest was opened);
  opened from a tap on either tile → 75 gems + 750 Mythic Spiritstone (the red gems) + 2 tokens, shovels and Mine bar
  unchanged. **"Tap anywhere to close" — not on the reward icons** (y≈920): a tap at `(540,1000)` opened the
  Spiritstone tooltip; use the top `(540,120)` (the script) or the bottom `(540,1700)`.
  **Opening is always free** — no shovel, no Mine-bar count (Nick 2026-11-04; seen on Cmajor: tap on a frame tile → chest gone,
  shovels 1→1, bar 63→62 over that tap + one real dig) → the script opens a lit one first, like a free pickaxe, and
  logs the reward popup's text (`popup: …`).
- Reward banner ("Bone Saw FragmentX2") crosses row 1 for ~1 s after an item dig; "Limestone X1" (no "Fragment") = a
  whole relic from a relic chest.
- **Top-up, when the shovels are out** (Nick, 2026-11-04: "only when out of shovel, once per day"; `relic.py` `topup()`,
  marker `/tmp/miniheroes-state/<acct>-<day>.relic_topup`): **Benefit** icon top-right of the board `(1015,430)` — open it
  **only with a red dot** (≈ x 1020–1075, y 360–420) → yellow **Claim** at the bottom `(540,1666)` (daily login: 1 dynamite,
  1 drill, 15 shovels on pass accounts; grey "Claimed" = done) → ✕ `(974,240)`. Never its purchase button.
  Then **shovel buys**: the green **+** on the shovel button `(656,1770)` → Tip "Spend N diamonds to buy 10 Shovel?
  (Remaining purchases: k)" → **Confirm** `(540,1162)` only while N is one of the account's `relic_shovel_buys`
  (default `[80]`; Kong `[80, 160, 240]`; Cmajor `[80, 160]`) and the gem counter covers it; any other price → ✕
  `(938,636)` and stop (Aminor 2026-11-04: 320 on screen = the 80 was already bought by hand). The day's buys and the
  last price seen are remembered (`/tmp/miniheroes-state/<acct>-<day>.relic_buys`), so a re-run never opens the Tip
  again (Nick 2026-11-04: every pass re-opening it looked like extra buy taps). Prices escalate
  80 → 160 → 240 → 320 within the day; each buy is verified by the counter (+10).
- **Milestone bar** ("Mine N more time(s) to claim your reward", top): at N = 0 tap its reward icon top-right
  `(1010,280)` → Congratulations popup → tap anywhere. Free (boosters / shovels); claim every time it's ready.

## Value model — game data read 2026-11-04 (Relic Archive / Fusion Archive / Fragment screens, Kong); scoring is Claude's

Facts (Lost Continent map → **Archive** `(470,1810)`; Relic Display → **Fragment**; read-only — never Combine / Quick Combine):

- Tiers: Common (blue) → Rare (purple) → Legend (orange) → Mythic (red) → Eternal (unique). Fragments to assemble one:
  **20** base (Limestone / Beast Bone / Bronze Mirror), **30** fused Common (Stone Hammer / Bone Saw / Bronze Dagger),
  40 Rare, 50 Legend, 60 Mythic and Eternal. The dig yields only the 6 Commons (whole, from relic chests) and their
  fragments (shards); gold/purple chests give Legend Spiritstone ×50 or Moon Essence ×30 (currency).
- Fusion (irreversible; unenhanced, unequipped relics only): Stone Hammer = 2 Bronze Mirror + 4 Limestone; Bone Saw =
  4 Beast Bone + 2 Limestone; Bronze Dagger = 4 Bronze Mirror + 2 Beast Bone; random fused Common = 2 + 2 + 2. Every
  Rare = 3 fused Commons (Mithril Axe = Dagger + 2 Hammer, Tribal Goblet = Saw + 2 Hammer, …; random Rare = Dagger +
  Saw + Hammer); every Legend = 3 Rares; a Mythic (chest) = 3 Legends; an Eternal (chest) = 3 Mythics + a crystal.
- So, in base relics: fused Common = 6, Rare = 18, Legend = 54, Mythic = 162; a base fragment = 1/20 = 0.05, a fused
  Common fragment = 6/30 = 0.2. Base relics stack (Kong shows 7 Limestones) and can't ascend ("At Max Stars").
- Measured 2026-11-04 (713 digs, 10 runs): lv1 shard = 3.3 fragments (0.17 units), lv2 shard = 1.8 (0.36), lv2 = 25 %
  of shards → **mean shard 0.21**; relic chest = 29 base + 4 fused → **mean chest 1.6**; the whole process yielded
  **0.16 units per shovel**, shards 54 % of it, chests 46 %.

Script values (Nick 2026-11-04, "I trust you"): **relic chest 1.6**, **multi-square chest 3.2 and first in line** (Nick
2026-11-04: "most important, more than relic chest" — the planner targets it before any relic chest or shard route
whatever the ratio), gold chest 0, **shard 0.28, threshold r = 0.14** — the shard is kept above the measured 0.21
because every call Nick has made (a lone shard up to 2 digs, two shards sharing a 3–4-dig tunnel, the Kong left
cluster) only holds at ~0.28/0.14; the measured 0.21 would need r ≈ 0.10 to match them and that would send the
planner 16 digs after a chest. At 1.6 a chest pays for up to ~11 digs (was 7).

**Real cost** of a target = new tiles to connect it to the dug area (dirt 1, stone 2, pickaxe tile 0 net).
**Check all 4 sides of the target first** — the cheapest route is often a lit dirt tile _beside_ it, not a straight
shaft from above (Kong 2026-10-31 dug stone r3c4 (2) + r4c4 (1) down to shard r5c4 when lit dirt r5c3 (1) touched it).
Write the route + its cost in the log line before the first tap.

**Look before the hard way** (Nick 2026-11-04): a lit pickaxe tile costs nothing net — take it before committing to any
route; in the bottom row it shows the next row, which may hold a cheaper way to the target (Kong 2026-11-04: the script
dug a 7-shovel tunnel to a relic chest while the free pickaxe it had just uncovered sat lit in the bottom row). The same
for a paid dig-down, shards included: when the route to a target is hard (stone) and the row below the board could hold
a cheaper corridor, dig down first and re-plan on what it shows — a dig-down is a dig we make anyway. A reveal can't
shorten the route to an item high on the board (a new path has to come back up through rows already visible), so there
the known route is taken.

**Top row first** (Nick 2026-11-04): every bottom-row dig scrolls row 1 off the board for good — collect an item there
before any dig-down (free pickaxes included) if it's worth its route; one that isn't (a shard 4 digs away) is let go,
logged `letting … go`. The point is not to lose a shard the planner would have collected anyway — not to chase every
top-row item (Nick, 2026-11-04: row 1 is gone for good once it scrolls off).

**Threshold:** take a target if `units / real cost ≥ r` (r = 0.14): a relic chest is worth up to ~11 digs, a lone
shard 1–2; shards sharing a tunnel split the cost — the script credits every item on or beside a route (Nick 2026-11-03, Bino: a gold chest + a pickaxe tile on the way to 2 shards = 4 digs, worth it).

**Routes collect on the way** (Nick 2026-11-04, Chien Than): of two routes of the same cost, take the one through
shards/chests — the search treats item tiles as free to pass, so a 5-dig bottom row with 2 shards beats a 5-dig tunnel
past 2 gold chests (and bottom-row digs reveal rows on the way). Of two routes of the same cost, the one that digs a **bottom-row** tile wins — it reveals a row as
well (Dminor 2026-11-05, Nick: the dirt above a shard was dug while the bottom tile beside the shaft reached it just the same). **The shovels left never shorten a route** (Nick 2026-11-04: shovels recover over time; a half-dug tunnel is
continued by the next run).

**Every dig needs a target** (Nick 2026-10-31, "gone wild"): each dig is either on the cheapest route to a named item
(log it: `route to <item> rNcM, cost N`) or a bottom-row dig that reveals a new row. Never dig a tile just because it's
reachable — plain dirt/stone off-route, the top rows, or "clearing the row" is waste (Chien Than 2026-10-31 mowed the
whole board: ~25 of 37 shovels on no-target tiles).

**Digging down** is the source of new items: each bottom-row dig reveals a new 6-tile row for 1 shovel. Keep a shaft in
the bottom row, branch off only for targets above the threshold. **The board keeps its state** — no dig is wasted.
Spend every shovel; dig before the count caps.

## Boosters (drill, dynamite) — rule Nick 2026-10-30; mechanics verified on the Kong instance 2026-11-04 (4 firings)

Supply: milestone bar only (≈2 per 500 digs); never buy. Stock = the badge on each button (the script OCRs it, re-reads once when a badge is missed — the OCR is flaky there; a kind with no reading is never fired).

- **How they work:** **drag** the button onto a dug tile (`adb input swipe <bx> 1820 <X> <Y> 700`; drill button x=310,
  dynamite x=766 — a tap does nothing). While dragging, the area shows in **green** under the finger; release = fire,
  no confirm. **Dynamite** digs the diamond of radius 2 around the drop tile (13 tiles). **Drill** highlights its
  column + the whole bottom row but digs **only the bottom row** (6 tiles; the column is just the preview, drop it
  anywhere dug). Stone goes in one hit, every dug tile counts +1 on the milestone bar, pickaxe tiles still refund a
  shovel, items show the usual banner (gold chest = `Legend SpiritstoneX50` / `+30` Moon Essence).
- **A booster that digs any bottom-row tile scrolls the board one row** (once, whether 3 or 6 tiles) — row 1 is lost
  for good; dynamite dropped in rows 1–4 doesn't touch the bottom row and doesn't scroll.
- **Value** = shovels saved: per item collected the cheaper of its hand-dig cost and its worth in shovels (relic chest
  ≈11, shard 2, pickaxe 1, gold chest 0), +1 for the row a scroll reveals, minus the row-1 items the planner would still
  have collected (the scroll loses them). Lit items in the bottom row are worth only 1 each to a drill.
- **Use it if it saves ≥ 6 shovels** — one number, no stock-based adjustments (Nick 2026-11-04). Dynamite for a tight
  cluster; the drill only for a loaded bottom row.
- **Fire late:** `relic.py` does it after the digs (`boosters()`): best candidate first, fired while it saves ≥ 6, each verified by the badge going down by 1 (`dynamite r4c3 (saves ~8, stock 12->11) -> Limestone x1`);
  otherwise `booster hint (not used): best … saves ~N shovels, stock …`.
  `D=<serial> scripts/relic.py <account> --max-digs 0` = boosters only, on the current board.

## Hard rules

- Boosters only by the rule above. The green **+** on the shovel button buys shovels: only the account's
  `relic_shovel_buys` prices (default 80 gems once; Kong 80/160/240; Cmajor 80/160 — Nick 2026-11-04), each confirmed
  only when that exact price is on the Tip popup; any other price → ✕. Never **One-Tap Mining**, no other gems.
- When the shovels run out (once a day): the board's **Benefit** icon with a red dot → Claim (free), never its purchase button.
- By hand: never chain taps — a tap you thought was cancelled may still land. Screenshot, then tap. Tap looks
  ignored (counters unchanged)? Re-screenshot before retrying, or you'll dig twice.
- Unexpected screen/popup → stop and report.
