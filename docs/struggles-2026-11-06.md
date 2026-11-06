# Struggles — catch-up 2026-11-06 06:20 (game day 2026-11-05, 9 accounts)

Source: runner logs `/tmp/miniheroes-catchup/*.log` (scripts/catchup_all.sh), one coordinator screenshot. Ordered by impact. Status: ✅ fixed ·
🧪 fixed, waiting for a live test (`docs/untested.md`) · ❌ open · ❓ needs Nick. Last updated: 2026-11-06.

| #   | Task                 | What went wrong                                                                                                                                                                                                                | Status                                                                            |
| --- | -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------- |
| 1   | Arena2 (Bino)        | Rows 2–5 shielded (crashed in `arena`), the 6th-row Crash bot cut off; `read_dialog` dropped shield rows, so "last row" = row 1 (✨DINO✨, own account, Challenge 4820k > our 4457k) → FAIL twice, 3 tickets left for a helper | 🧪 shield rows kept, fallback always scrolls first; re-run 8 min later used all 3 |
| 2   | Boot (Kong)          | Instance was on another server's account (stabilize: `account switched`, 4 popups) — someone had switched it since the last run                                                                                                | ✅ stabilize switched it back; nothing to do                                      |
| 3   | Fishing (6 accounts) | `AUTO STOPPED, bread 0–1/100` on Bino, Chien Than, Cmajor, Dino, Tiger, xFaktor — out of bread, so the Auto can't be restarted                                                                                                 | ❓ expected at this point of the day? bread refills only with the daily reset     |

## Relics 06:43 (relic_all.sh, 9 accounts, all exit 0)

| #   | Task           | What went wrong                                                                                                                                                                                                      | Status                                                                   |
| --- | -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| 4   | Relics (Tiger) | `drill r1c2 (saves ~6, stock 2->None) -> no banner` then `booster not consumed`: the drill did fire (bottom row dug, new row revealed, badge 2→1 on the coordinator's screenshot); the post-fire badge OCR read None | 🧪 badge re-read once; None + changed board = fired (`docs/untested.md`) |

784 digs, 0 refused / UNKNOWN / no effect; no buys this run (all 9 top-ups were done earlier the same game day, 11-05 18:10–18:19); shovels 0 everywhere.

Everything else: 9 × 13 OK, no helper, no paid action, 0 popups stuck at boot (the Golden Woods "Tap anywhere" fix from 11-05 held: 0 popup-stuck).

## Stabilize + survey 11:00 (boot.sh 9 accounts, mail survey)

| #   | Task              | What went wrong                                                                                                                                                                                                                 | Status                                                                                                                      |
| --- | ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| 5   | Boot (7 accounts) | New "Snow Carnival" (11.5–12.7) popup → `popup-stuck` on all but Dino/Tiger: `close_x` takes the 64px block with the most white pixels, and the snow artwork + the frame's right edge (988,896) out-scored the real X (988,352) | 🧪 `close_x` only lets the rows straddling the topmost X-like block compete (`docs/untested.md`); closed by hand (tick + X) |

Survey: the mail's link is one Google Form (`forms.gle/k7Nkvtkbv7MRHoSL9`, no sign-in); submitted from the Mac with curl once per `game_id`, neutral answers, `n/a` texts — 9 × "Thank you for your sharing!". No game taps needed beyond Kong (link read via `dumpsys activity`).
