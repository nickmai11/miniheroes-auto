---
name: miniheroes-relic
description: Run Mini Heroes: Magic Throne Relics (Archaeology dig board, e.g. Blaze Peaks / Shadowlands) - spend all shovels digging for relic chests, multi-square chests and shards with minimum shovel waste, on Nick's MuMuPlayer accounts via ADB (scripts/relic_all.sh / relic.py).
---

# Mini Heroes Relics

Use when Nick asks for "relics" or "dig" (not "mining" — that's Excelsior Veins) on Mini Heroes accounts.

## Run it — script, no helper (Nick 2026-11-03: "a script that reliably does the work")

1. Instances at the main screen (`scripts/boot.sh <mumu index>...`), then **`scripts/relic_all.sh [account ...]`** — runs
   `relic.py` on every `accounts/*.yaml` account in parallel (~4 s per dig, 150 shovels ≈ 10 min). One line per
   account: `<account> exit 0 (done: N digs, shovels 0/150 left, items: …)`; output + screenshots in
   `/tmp/miniheroes-relic/<account>/`, every dig also in `logs/<account>/<game day>.log`.
   One account: `D=<serial> scripts/relic.py <account> [--dry] [--max-digs N]` — from the main screen, the Lost
   Continent map or the board; `--dry` only prints the board and the next dig.
2. **`exit 1` = it stopped** (unexpected screen, 3 refused digs, nothing diggable): read `out.txt` + `v_relic.png` there,
   then a helper finishes **that account only** by hand with the board rules below. Never re-run the script blindly on it.
   `UNKNOWN cells rXcY` in the log = a tile the reader has never seen (it digs around them): look at the screenshot,
   teach it — `scripts/relic.py --learn <png> <row> <col> <label>` (labels: `empty pit dirt_lit dirt_dark stone_lit
stone_dark cracked_lit shard_lit shard_dark chest_lit chest_dark gold_lit gold_dark pick_lit pick_dark multi_lit
multi_dark`; never learn from r6c1, the % label sits there) — `python3 scripts/test_relic.py` must still pass, then run again.
3. Report per account: the `done:` line (digs, items, shovels left), any `UNKNOWN` / `refused` / `no effect` lines, and
   the `booster hint` line (the script never fires drill/dynamite — Nick decides, rule below).

What the script does (details in the `scripts/relic.py` header): matches each of the 42 tiles against the sprite crops in
`scripts/relic_tiles/` (two identical reads needed — banners, dust, scrolling), Dijkstra over dig costs from the lit
tiles, target = best value/cost ≥ 0.14 lv1-relic units per shovel (shard 0.28, relic chest 1, multi-square chest 1,
pickaxe 0.14 = a shovel back, gold chest 0), otherwise the cheapest bottom-row dig (reveals a new row). Every dig is
verified (tile changed / board scrolled / counter), reward popups closed, the milestone reward claimed at "Mine 0 more";
it never taps the shovel **+**, One-Tap Mining or a booster. Proven live 2026-11-03 on all 9 accounts (≈770 digs, 0 refused taps); classifier checked on 65 saved boards (`scripts/test_relic.py`).

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
  leave such a chest after one refused tap. The script has no sprite for them yet → `UNKNOWN`, teach it (`multi_lit`).
- Reward banner ("Bone Saw FragmentX2") crosses row 1 for ~1 s after an item dig; "Limestone X1" (no "Fragment") = a
  whole relic from a relic chest.
- **Milestone bar** ("Mine N more time(s) to claim your reward", top): at N = 0 tap its reward icon top-right
  `(1010,280)` → Congratulations popup → tap anywhere. Free (boosters / shovels); claim every time it's ready.

## Value model (Nick's facts 2026-10-30; scoring is Claude's)

Score every target in **lv1-relic units per shovel**, not by fixed rules.

- Relics: lv1 = stone (Limestone), ribs (Beast Bone), green crescent (Bronze Mirror) (20 fragments each); lv2 = axe
  (Stone Hammer: 2 crescent + 4 stone), saw (Bone Saw: 4 ribs + 2 stone), sword (Bronze Dagger: 4 crescent + 2 ribs)
  (30 fragments each). So lv1 fragment = 0.05, lv2 relic = 6, lv2 fragment = 0.2. Nothing is lost past a relic's cap.
- Dino 2026-10-30 (71 shovels): lv1 shard = 2–5 fragments (avg 3.7 → **≈ 0.19**), lv2 shard = 1–3 (avg 2 →
  **≈ 0.4**), relic chest = 1 whole relic (29 lv1 + 5 lv2 of 34 on 2026-11-03 → **≈ 1.7**; the script still uses 1.0 until Nick says otherwise). Run total ≈ 10.5
  units → **r ≈ 0.15 / shovel** (xFaktor 2026-10-31: 0.13). Type/level isn't known until dug.
- Multi-square chest: currency, not relics (above) — Nick still wants them ("must get"); scored like a relic chest.
- Gold/purple chest (Legend Spiritstone ×50 or Moon Essence ×30, 2026-11-03), milestone bar: **0** — a gold chest is just a blocker (1 hit, tunnel through it).

**Real cost** of a target = new tiles to connect it to the dug area (dirt 1, stone 2, pickaxe tile 0 net).
**Check all 4 sides of the target first** — the cheapest route is often a lit dirt tile _beside_ it, not a straight
shaft from above (Kong 2026-10-31 dug stone r3c4 (2) + r4c4 (1) down to shard r5c4 when lit dirt r5c3 (1) touched it).
Write the route + its cost in the log line before the first tap.

**Threshold:** take a target if `units / real cost ≥ r` (r ≈ 0.14–0.15): a relic chest is worth up to ~7 digs, a lone
shard 1–2; shards sharing a tunnel split the cost — the script credits every item on or beside a route (Nick 2026-11-03, Bino: a gold chest + a pickaxe tile on the way to 2 shards = 4 digs, worth it).

**Every dig needs a target** (Nick 2026-10-31, "gone wild"): each dig is either on the cheapest route to a named item
(log it: `route to <item> rNcM, cost N`) or a bottom-row dig that reveals a new row. Never dig a tile just because it's
reachable — plain dirt/stone off-route, the top rows, or "clearing the row" is waste (Chien Than 2026-10-31 mowed the
whole board: ~25 of 37 shovels on no-target tiles).

**Digging down** is the source of new items: each bottom-row dig reveals a new 6-tile row for 1 shovel. Keep a shaft in
the bottom row, branch off only for targets above the threshold. **The board keeps its state** — no dig is wasted.
Spend every shovel; dig before the count caps.

## Boosters (drill, dynamite) — Nick 2026-10-30

Supply: milestone bar only (≈2 per 500 digs); never buy. Placed on an explored (dug) tile; auto-collect every item in
the area. Dynamite = diamond radius 2 (13 tiles). Drill = its whole column + the whole bottom row (~12 tiles); does NOT
scroll the board.

- **Value** = shovels saved: cheapest hand-dig cost of the same items (shared tunnel) + stone hits avoided.
  Items in shovels: relic chest ≈7, lv2 shard ≈2–3, lv1 shard / pickaxe tile ≈1, gold/purple chest 0.
- **Use it if it saves ≥ 6 shovels** (≈ 1 per run at a 30 stock). Stock < 10 → raise to 8; stock keeps
  growing → lower to 5. Dynamite for a tight cluster, drill for a column of items / loaded bottom row.
- **Fire late:** shovel-dig first, blast where the most value is left. The script only logs a `booster hint`.
- How (by hand): tap the booster button (drill `(~150,1855)`, dynamite `(~765,1855)` device), the board shows the
  area in red, check it, then tap the target tile. Screenshot before the placing tap. Log what it collected.

## Hard rules

- Boosters only by the rule above. Never tap the green **+** on the shovel button (buys shovels) — no gem buys at all
  (the daily 80-gem buy was removed, Nick 2026-10-31), never **One-Tap Mining**. No gems.
- By hand: never chain taps — a tap you thought was cancelled may still land. Screenshot, then tap. Tap looks
  ignored (counters unchanged)? Re-screenshot before retrying, or you'll dig twice.
- Unexpected screen/popup → stop and report.
