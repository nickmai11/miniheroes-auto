# Struggles — catch-up 2026-11-06 06:20 (game day 2026-11-05, 9 accounts)

Source: runner logs `/tmp/miniheroes-catchup/*.log` (scripts/catchup_all.sh), one coordinator screenshot. Ordered by impact. Status: ✅ fixed ·
🧪 fixed, waiting for a live test (`docs/untested.md`) · ❌ open · ❓ needs Nick. Last updated: 2026-11-06.

| #   | Task                 | What went wrong                                                                                                                                                                                                                | Status                                                                            |
| --- | -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------- |
| 1   | Arena2 (Bino)        | Rows 2–5 shielded (crashed in `arena`), the 6th-row Crash bot cut off; `read_dialog` dropped shield rows, so "last row" = row 1 (✨DINO✨, own account, Challenge 4820k > our 4457k) → FAIL twice, 3 tickets left for a helper | 🧪 shield rows kept, fallback always scrolls first; re-run 8 min later used all 3 |
| 2   | Boot (Kong)          | Instance was on another server's account (stabilize: `account switched`, 4 popups) — someone had switched it since the last run                                                                                                | ✅ stabilize switched it back; nothing to do                                      |
| 3   | Fishing (6 accounts) | `AUTO STOPPED, bread 0–1/100` on Bino, Chien Than, Cmajor, Dino, Tiger, xFaktor — out of bread, so the Auto can't be restarted                                                                                                 | ❓ expected at this point of the day? bread refills only with the daily reset     |

Everything else: 9 × 13 OK, no helper, no paid action, 0 popups stuck at boot (the Golden Woods "Tap anywhere" fix from 11-05 held: 0 popup-stuck).
