---
name: miniheroes-relic
description: Run Mini Heroes: Magic Throne Relics (digging feature, e.g. the Magic Jungle map) - spend all shovels digging down, grabbing relic chests, multi-square chests and cheap relic shards with minimum shovel waste, on Nick's MuMuPlayer accounts via ADB or computer use.
---

# Mini Heroes Relics

Use when Nick asks for "relics" or "dig" (not "mining" — that's Excelsior Veins) (map currently shown: "Magic Jungle") on a Mini Heroes account.

1. In `~/projects/chidojiro/miniheroes-auto`, read `CLAUDE.md` and `accounts/<account>.yaml`.
2. Connect (ADB route: see "ADB alternative" in `docs/ui-routine.md`) and open **Relics**.
   Path: main screen → **Relic** (bottom bar, far right) `(972,1788)` → **Lost Continent** map → **Archaeology**
   `(540,1540)` → dig board. Careful: on the map, **Relic Display** sits right where the Relic button was — a late
   Relic tap + a retry lands you in Relic Display (back arrow `(80,1820)`). Screenshot before retrying anything.
3. Dig one tile per tap until the shovel counter (`N/150`, top-left) is 0. Screenshot after every tap
   (`scripts/tap.py X,Y` — its 540-wide screenshot coords ×2 = device coords), re-read the whole board, re-plan.
4. Report: items collected per account, shovels wasted (digs that neither went down nor got an item).

## Board

- 6 columns × 7 visible rows. Device coords (1080×1920): column x = `116, 284, 452, 624, 794, 962`;
  row y = `600, 770, 940, 1110, 1280, 1450, 1620` (row 7 = bottom row, below the yellow % line).
- Dark brown = empty (already dug). **Lit** tiles (tan dirt, light grey stone) touch an empty cell → diggable.
  **Dark** tiles (dark dirt, dark grey stone) aren't reachable yet. Only tiles adjacent to empty cells can be dug.
- Dirt = 1 hit. Light grey stone = 2 hits (cracks after the 1st). Dark grey stone untested — avoid.
- Digging a bottom-row tile scrolls the board up one row (new bottom row appears). Each dig = 1 shovel
  and +1 on the "Mine N more times" bar.

## Priorities (Nick, 2026-10-27)

1. **Dig down.** Default move = cheapest path to the bottom row; new rows bring new items.
2. **Relic chest (silver/blue chest)** — always go for it, even off the path.
3. **2/4/6-square chests** — must get, even off the path.
4. **Shovel tile** — free (costs nothing, refunds 1); take any reachable one.
5. **Relic shard (blue fragment)** — only if on the path down or 1 dig off it. Don't spend 3–4 shovels on a lone shard (a cluster at ~1.5 shovels/shard is fine).
   Grab any 1-dig shard right away — don't defer it.
6. **Gold/purple chest** — ignore (gives Moon Essence, not relics); dig it only if it's on the path anyway.

With the last shovel(s), prefer a dig that opens a reachable item for the next shovel (shovels regenerate).

## Hard rules

- Don't use the drill or bomb boosters (Nick: "no for now"), never tap the green **+** on the shovel
  button (buys shovels), never use **One-Tap Mining**. No gems.
- Never chain taps — a tap you thought was cancelled may still land. Screenshot, then tap.
- Tap looks ignored (counters unchanged)? It may land late — re-screenshot before retrying, or you'll dig twice.
- Unexpected screen/popup → stop and report.
