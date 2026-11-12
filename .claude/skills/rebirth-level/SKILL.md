---
name: rebirth-level
description: Mini Heroes: Magic Throne hero reset - Rebirth every hero after the first N (hero list order) and level them back to a target level (e.g. "reset all heroes from the 7th and level them back to 160") on Nick's MuMuPlayer accounts via ADB (scripts/rebirth_level.py). Potions only; Rebirth is free and returns 100% of the hero and gear materials.
---

# Rebirth + re-level

Use when Nick says "reset <account> heroes from the Nth (hero) and level them (back) to L". First done on Kratos
2026-11-12 (heroes 7–68 → Lv.160).

1. Boot the account (`scripts/boot.sh <idx>`); main screen or hero screen.
2. `D=<serial> scripts/rebirth_level.py <account> --keep <N-1> --target <L>` (defaults `--keep 6 --target 160`),
   in the background, Monitor its log for `STOP|Traceback|-> Lv\.|row end`. ~1 min per hero for the levelling
   (the game caps a held Level Up at ~1–1.6 levels/s), plus a ~10 s rebirth each.
   - Phase **rebirth** first (all refunds pooled), then **level**; `--phase rebirth|level` runs one. Both re-runnable:
     rebirth skips Lv.1 heroes, level skips heroes at the target and redoes any above it (Rebirth → again).
   - The account's dailies hero (`hero_upgrade.hero`, Bone Archer) is left alone — `hero.py` rebirths it above Lv.135.
3. Done = the level phase's `row end: K heroes after the first N` with no hero left below the target; a
   `--phase level` re-run that prints no `-> Lv.` line is the check (Kratos: 62 heroes, 7.7 min).
4. Report: heroes reset/levelled, the dailies hero skipped, and that their **gear is back to LV.0** (Rebirth returns
   the gear materials too) — `gear.py` re-enhances if Nick wants.

Rules: scroll the row **slowly** (2-card held drags, never flings — Nick); strict order, one card at a time (the
selected card is found by pixels, not by OCR'd labels: OCR missed "Lv.1" labels and skipped heroes); never the
"↑ Lv.N" quick button above Lv.90 (it goes to the top level, 185, not the target). Mechanics:
`scripts/doc.sh "Hero rebirth"`.
