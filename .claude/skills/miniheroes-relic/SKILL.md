---
name: miniheroes-relic
description: Run Mini Heroes: Magic Throne Relics (digging feature, e.g. the Magic Jungle map) - spend all shovels digging down, grabbing relic chests, multi-square chests and cheap relic shards with minimum shovel waste, on Nick's MuMuPlayer accounts via ADB or computer use.
---

# Mini Heroes Relics

Use when Nick asks for "relics" or "dig" (not "mining" — that's Excelsior Veins) (map currently shown: "Magic Jungle") on a Mini Heroes account.

1. In `~/projects/chidojiro/miniheroes-auto`, read `CLAUDE.md` and `accounts/<account>.yaml`.
2. Connect (`scripts/boot.sh`, or "ADB alternative" via `scripts/doc.sh`) and open **Relics**.
   Path: main screen → **Relic** (bottom bar, far right) `(972,1788)` → **Lost Continent** map → **Archaeology**
   `(540,1540)` → dig board. Careful: on the map, **Relic Display** sits right where the Relic button was — a late
   Relic tap + a retry lands you in Relic Display (back arrow `(80,1820)`). Screenshot before retrying anything.
3. Dig one tile per tap (only tiles touching an empty cell — else "dig up the adjacent plot first", no shovel used) until the shovel counter (`N/150`, Kong `N/100`, top-left) is 0. Screenshot after every tap
   (`scripts/tap.py X,Y` — its 540-wide screenshot coords ×2 = device coords), re-read the whole board, re-plan.
4. Report per account: items collected (each chest's piece and level), shovels used, units per shovel.

## Board

- 6 columns × 7 visible rows. Device coords (1080×1920): column x = `116, 284, 452, 624, 794, 962`;
  row y = `600, 770, 940, 1110, 1280, 1450, 1620` (row 7 = bottom row, below the yellow % line).
- Dark brown = empty (already dug). **Lit** tiles (tan dirt, light grey stone) touch an empty cell → diggable.
  **Dark** tiles (dark dirt, dark grey stone) aren't reachable yet. Only tiles adjacent to empty cells can be dug.
- Dirt = 1 hit. Light grey stone = 2 hits (cracks after the 1st) — one bottom-row stone stayed cracked after 2 (Dino 2026-10-30), may need 3. Dark grey stone untested — avoid.
- Digging a bottom-row tile scrolls the board up one row (new bottom row appears). Each dig = 1 shovel
  and +1 on the "Mine N more times" bar.

## Value model (Nick's facts 2026-10-30; scoring is Claude's)

Score every target in **lv1-relic units per shovel**, not by fixed rules.
- Relics: lv1 = stone (Limestone), ribs (Beast Bone), green crescent (Bronze Mirror) (20 fragments each); lv2 = axe (Stone Hammer: 2 crescent + 4 stone), saw (Bone Saw:
  4 ribs + 2 stone), sword (Bronze Dagger: 4 crescent + 2 ribs) (30 fragments each). So lv1 fragment = 0.05, lv2 relic = 6,
  lv2 fragment = 0.2. Nothing is lost past a relic's cap.
- Dino 2026-10-30 (71 shovels): lv1 shard = 2–5 fragments (avg 3.7 → **≈ 0.19**), lv2 shard = 1–3 (avg 2 →
  **≈ 0.4**), relic chest = 1 whole relic (3/3 were lv1 → **≈ 1**, more if lv2 ever drops). Run total ≈ 10.5
  units → **r ≈ 0.15 / shovel**. Type/level isn't known until dug (shade of blue may hint — unverified).
- **2/4/6-square chests:** contents not measured — treat as ≥ a relic chest until logged.
- Gold/purple chest (Moon Essence), milestone bar: **0** — a gold/purple chest is just a blocker.

**Real cost** of a target = new tiles to connect it to the dug area (dirt 1, light stone 2, dark stone avoid,
shovel tile 0 net and it opens neighbours). Plan routes to item groups: a shared tunnel splits its cost.
**Check all 4 sides of the target first** — the cheapest route is often a lit dirt tile *beside* it, not a straight
shaft from above: Kong 2026-10-31 dug stone r3c4 (2) + r4c4 (1) down to shard r5c4 when lit dirt r5c3 (1) touched it
— 2 shovels wasted. Write the route + its cost in the log line before the first tap.

**Threshold:** take a target if `units / real cost ≥ r`, where r = average units per shovel from logged runs
(r ≈ 0.15 from Dino 2026-10-30; re-measure). So a relic chest is worth up to ~7 digs, a lone shard ~1–2
(lv1 1, lv2 2–3); shards sharing a tunnel split the cost.

**Every dig needs a target** (Nick 2026-10-31, "gone wild"): each dig is either on the cheapest route to a named item
(log it: `route to <item> rNcM, cost N`) or a bottom-row dig that reveals a new row. Never dig a tile just because it's
reachable — plain dirt/stone off-route, the top rows, or "clearing the row" is waste. Chien Than 2026-10-31 mowed the
whole board (top rows, stones with nothing behind them, ~25 of 37 shovels on no-target tiles, 2 lv1 shard + Moon
Essence). No item reachable for ≤ 7 → dig down in the bottom row.

**Digging down** is the source of new items: once a shaft is in the bottom row, each bottom-row dirt dig reveals
a new 6-tile row for 1 shovel. Run the shaft next to item clusters (cheap side digs later), keep a foothold in
the bottom row, branch off only for targets above the threshold.

**The board keeps its state** — no dig is wasted. Spend every shovel; end on a dig toward the next target.
Dig before the shovel count caps at 150 (regen past the cap is lost).

## Boosters (drill, dynamite) — Nick 2026-10-30

Supply: milestone bar only (≈2 per 500 digs, ~1 per 2–3 days); never buy. Placed on an explored (dug) tile;
auto-collect every item in the area. Dynamite = diamond radius 2 (13 tiles). Drill = its whole column + the whole
bottom row (~12 tiles); does NOT scroll the board.
- **Value** = shovels saved: cheapest hand-dig cost of the same items (shared tunnel) + stone hits avoided.
  Items in shovels: relic chest ≈7, lv2 shard ≈2–3, lv1 shard / shovel tile ≈1, gold/purple chest 0.
- **Use it if it saves ≥ 6 shovels** (≈ 1 per run at a 30 stock). Stock < 10 → raise to 8; stock keeps
  growing → lower to 5. Dynamite for a tight cluster, drill for a column of items / loaded bottom row.
- **Fire late:** shovel-dig first, blast where the most value is left (an early blast clears tiles you'd dig anyway).
- How: tap the booster button (drill `(~150,1855)`, dynamite `(~765,1855)` device), the board shows the area in red,
  check it, then tap the target tile. Screenshot before the placing tap. Log what it collected.

**Milestone bar** ("Mine N more time(s) to claim your reward", top): when N = 0, tap its reward icon
top-right `(~980,250)` — free claim (boosters). Claim every time it's ready.

Log each dig (`cost`, what it gave) to the account log so r and the chest values can be measured.

## Hard rules

- Boosters only by the rule above. Never tap the green **+** on the shovel
  button (buys shovels) — no gem buys at all (the daily 80-gem buy was removed, Nick 2026-10-31), never use **One-Tap Mining**. No gems.
- Never chain taps — a tap you thought was cancelled may still land. Screenshot, then tap.
- Tap looks ignored (counters unchanged)? It may land late — re-screenshot before retrying, or you'll dig twice.
- Unexpected screen/popup → stop and report.
