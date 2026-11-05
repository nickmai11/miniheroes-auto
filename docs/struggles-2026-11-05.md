# Struggles — dailies 2026-11-05 (game day 2026-11-05, 9 accounts)

Source: runner logs `/tmp/miniheroes-2026-11-05/*.log`, coordinator screenshots. Ordered by impact. Status: ✅ fixed ·
🧪 fixed, waiting for a live test (`docs/untested.md`) · ❌ open · ❓ needs Nick. Last updated: 2026-11-05.

| #   | Task                   | What went wrong                                                                                                                      | Status                                                                   |
| --- | ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------ |
| 1   | Boot (5 accounts)      | Golden Woods splash has no X, only "Tap anywhere to close" → `popup-stuck` on Chien Than, Bino, Dino, Cmajor, Dminor; closed by hand | 🧪 `stabilize.py` taps the close line                                    |
| 2   | Kong daily chest       | Auto fishing had stopped with 28 bread left → bread row 1/10, chest stuck at 150; runner's `fishing` OK only means "auto started"    | ✅ restarted by hand → 160 · ❌ no end-of-run check that Auto still runs |
| 3   | Storm (Tiger)          | "match 5: 13s", then a fight with 73 s left read as `unexpected screen` → FAIL (retry OK)                                            | 🧪 `storm.py` waits out a running fight                                  |
| 4   | Arena challenge (Bino) | Lineup Start tap lost → waited 180 s → FAIL (retry OK)                                                                               | 🧪 `arena.py` re-taps Start                                              |
| 5   | Gate (Cmajor)          | Chances re-read before the redraw: `1 -> 1`, screenshot showed 0 → FAIL (retry: nothing left)                                        | 🧪 `daily.py gate` polls the counter                                     |
| 6   | Events (Dminor)        | Golden Woods dot left = Sign-In "Continue to claim" with Deluxe shown **Activated** — free claim or the $8.99 buy? Not tapped        | ❓ Nick                                                                  |
