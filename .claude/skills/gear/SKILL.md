---
name: gear
description: Mini Heroes: Magic Throne gear catch-up - Enhance every gear of the first N heroes (hero list order) up to a target level (e.g. "upgrade all gears of the first 15 heroes to at least 150") on Nick's MuMuPlayer accounts via ADB (scripts/gear.py). Gold only, never gems.
---

# Gear catch-up

Use when Nick says "upgrade all gears of the first N heroes to (at least) L" on an account. Spends **gold** (and
stones), never gems.

1. Account: boot it (`scripts/boot.sh <idx>`; the index from `mumu-cli info all` — the account may have no
   `accounts/*.yaml`, e.g. PuPu = index 11). Check `adb shell wm size` is **1080x1920**: PuPu was 600x1080 and every
   script mis-taps there → `adb -s $D shell wm size 1080x1920; adb -s $D shell wm density 480`, restart the game
   (`force-stop` + launch), Start, `stabilize.py`.
2. Main screen → Hero `scripts/tap.py 274,1810 --until-text '^Level Up$'`.
3. Run, no LLM: `cd <scratch>; D=<serial> scripts/gear.py --heroes N --target L`. Per hero it expands the list
   `(1008,1400)`, taps card i (5 columns, rows y=1250/1490/1690 — only the first 15 are reachable without a scroll),
   closes it, prints `i. <name>: gear [lv1, lv2, lv3, lv4]`, and for every slot below the target opens the popup
   and taps Enhance until `LV.N` reads ≥ target (level re-read after every tap; stops the slot on
   have < need gold, exit 1 if the Enhance button disappears = purchase dialog, never tapped).
4. `None` in the gear list = the slot's level label wasn't read (locked/empty, or an OCR miss: Radiant Paladin
   slot 2 on PuPu 11-06 read None while the hero clearly had 4 gears) → re-run `--heroes` on that hero or open the
   slot by hand `(120, 400/550/700/850)` and check.
   `LV.N unchanged after Enhance; stopped` = a lagging read, not a shortage: re-run (it skips slots already ≥ target).
5. Exit 1 → `v_gear.png` + message; finish that hero by hand or re-run (idempotent: done heroes/slots are skipped).
6. Report per hero: gear levels before, Enhance counts, slots stopped early and why (gold, unreadable); every stop.

More than 15 heroes needs a grid scroll — not mapped (Nick asked for 15, 2026-11-06).
